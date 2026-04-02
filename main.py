"""
waka-readme — Main entry point.

Flow:
1. Read config from environment.
2. Fetch WakaTime stats (last 7 days + all-time).
3. Fetch GitHub repos and commit history.
4. Build the README stats block.
5. Push the updated README.md back to GitHub.
"""
from __future__ import annotations

import asyncio
import os
import sys
from datetime import datetime, timezone

from github import GithubException
from humanize import intword, naturalsize

from src import config as C
from src.wakatime import WakaTimeClient
from src.github_utils import (
    get_github_client,
    fetch_user_repos,
    fetch_commit_history,
    aggregate_commit_times,
    update_readme,
)
from src.formatters import (
    format_commit_time,
    format_days_of_week,
    format_waka_section,
    format_language_per_repo,
    badge,
)
from src.chart import draw_loc_chart, GRAPH_PATH


def _check_env() -> None:
    missing = []
    if not C.GH_TOKEN:
        missing.append("GH_TOKEN (or INPUT_GH_TOKEN)")
    if not C.WAKATIME_API_KEY:
        missing.append("WAKATIME_API_KEY (or INPUT_WAKATIME_API_KEY)")
    if missing:
        print("[Error] Missing required environment variables:")
        for m in missing:
            print(f"  - {m}")
        sys.exit(1)


async def build_stats(gh, login: str, user_node_id: str) -> str:
    waka = WakaTimeClient()

    # ── fetch data concurrently ──────────────────────────────────────────────
    waka_week_task = asyncio.create_task(waka.get_stats_last_7_days())
    waka_all_task = asyncio.create_task(waka.get_all_time())
    repos_task = asyncio.create_task(fetch_user_repos(login, user_node_id))

    waka_week, waka_all, repos = await asyncio.gather(
        waka_week_task, waka_all_task, repos_task
    )

    # ── commit history (needed for time/DoW stats) ───────────────────────────
    hour_counts: dict[int, int] = {h: 0 for h in range(24)}
    weekday_counts: dict[int, int] = {d: 0 for d in range(7)}

    if C.SHOW_COMMIT or C.SHOW_DAYS_OF_WEEK or C.SHOW_LINES_OF_CODE or C.SHOW_LOC_CHART:
        print(f"[GitHub] Fetching commit history for {len(repos)} repos...")
        all_commits: list[dict] = []
        sem = asyncio.Semaphore(5)  # max 5 concurrent requests

        async def fetch_safe(repo: dict) -> None:
            async with sem:
                owner, name = repo["nameWithOwner"].split("/")
                commits = await fetch_commit_history(owner, name, user_node_id)
                all_commits.extend(commits)

        await asyncio.gather(*[fetch_safe(r) for r in repos])
        h, w = aggregate_commit_times(all_commits, login)
        hour_counts = h
        weekday_counts = w
        print(f"[GitHub] Processed {len(all_commits)} commits total.")

    # ── assemble stats block ─────────────────────────────────────────────────
    parts: list[str] = []

    # Total code time badge
    if C.SHOW_TOTAL_CODE_TIME and waka_all:
        total_text = waka_all.get("text", "Unknown")
        parts.append(badge("Code Time", total_text))
        parts.append("")

    # Lines of code badge
    if C.SHOW_LINES_OF_CODE:
        # rough estimate: sum of all "add" from commits
        total_lines = sum(hour_counts.values())  # placeholder — real impl needs per-commit diff data
        data_str = intword(total_lines, format="%.2f") + " Lines of code"
        parts.append(badge("From Hello World I have written", data_str))
        parts.append("")

    # GitHub short info
    if C.SHOW_SHORT_INFO:
        user = gh.get_user(login)
        disk = naturalsize(user.disk_usage) if user.disk_usage else "?"
        public = user.public_repos
        lines = [
            f"**🐱 My GitHub Data**\n",
            f"> 📦 {disk} used in GitHub's Storage",
            f"> 🏆 Public repos: {public}",
        ]
        if user.hireable:
            lines.append("> 💼 Open to hire")
        else:
            lines.append("> 🚫 Not open to hire")
        parts.append("\n".join(lines))
        parts.append("")

    # Commit time (hour of day)
    if C.SHOW_COMMIT and any(hour_counts.values()):
        parts.append(format_commit_time(hour_counts))
        parts.append("")

    # Days of week
    if C.SHOW_DAYS_OF_WEEK and any(weekday_counts.values()):
        parts.append(format_days_of_week(weekday_counts))
        parts.append("")

    # WakaTime weekly breakdown
    if waka_week and any([C.SHOW_TIMEZONE, C.SHOW_LANGUAGE, C.SHOW_EDITORS, C.SHOW_PROJECTS, C.SHOW_OS]):
        parts.append(format_waka_section(waka_week))
        parts.append("")

    # Language per repo
    if C.SHOW_LANGUAGE_PER_REPO and repos:
        parts.append(format_language_per_repo(repos))
        parts.append("")

    # Updated date
    if C.SHOW_UPDATED_DATE:
        now = datetime.now(timezone.utc).strftime(C.UPDATED_DATE_FORMAT)
        parts.append(f"_Last Updated on {now} UTC_")

    return "\n".join(parts).strip()


async def main() -> None:
    _check_env()

    gh = get_github_client()
    user = gh.get_user()
    login = user.login
    user_node_id = user.node_id
    print(f"[GitHub] Authenticated as: {login}")

    # Determine target repo (profile repo = same name as username)
    profile_repo_name = f"{login}/{login}"
    try:
        profile_repo = gh.get_repo(profile_repo_name)
    except GithubException:
        print(f"[Error] Profile repo '{profile_repo_name}' not found.")
        sys.exit(1)

    stats = await build_stats(gh, login, user_node_id)

    if C.DEBUG_RUN:
        print("\n" + "=" * 60)
        print("DEBUG OUTPUT (README would be updated with):")
        print("=" * 60)
        print(stats)
        # Also write to GitHub Actions output if available
        if os.environ.get("GITHUB_OUTPUT"):
            with open(os.environ["GITHUB_OUTPUT"], "a") as f:
                f.write(f"stats<<EOF\n{stats}\nEOF\n")
    else:
        update_readme(profile_repo, stats, section=C.SECTION_NAME)


if __name__ == "__main__":
    start = datetime.now()
    print(f"[waka-readme] Starting at {start.isoformat()}")
    asyncio.run(main())
    end = datetime.now()
    print(f"[waka-readme] Finished in {end - start}")
