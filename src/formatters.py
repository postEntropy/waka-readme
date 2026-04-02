"""
Generates the text blocks that go into the README section.
"""
from __future__ import annotations

from collections import Counter
from urllib.parse import quote

from src import config as C

# ── Progress bar helper ────────────────────────────────────────────────────────


def _bar(percent: float, length: int = C.BAR_LENGTH) -> str:
    filled = round(percent / 100 * length)
    return C.BLOCK_CHAR * filled + C.EMPTY_CHAR * (length - filled)


def _make_list(items: list[dict], key_name: str = "name", value_label: str = "text") -> str:
    """Formats a WakaTime list (languages/editors/projects/os) into the bar format."""
    lines: list[str] = []
    for item in items[:10]:
        name = item.get(key_name, "")
        pct = item.get("percent", 0.0)
        label = item.get(value_label, "")
        bar = _bar(pct)
        lines.append(f"{name:<30} {label:<20} {bar}  {pct:.1f}%")
    return "\n".join(lines)


# ── Commit-time stats ──────────────────────────────────────────────────────────

HOUR_GROUPS = {
    "🌞 Morning": range(6, 12),
    "🌆 Daytime": range(12, 18),
    "🌃 Evening": range(18, 24),
    "🌙 Night":   range(0, 6),
}

WEEKDAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


def format_commit_time(hour_counts: dict[int, int]) -> str:
    grouped: dict[str, int] = {}
    for label, hours in HOUR_GROUPS.items():
        grouped[label] = sum(hour_counts.get(h, 0) for h in hours)

    total = sum(grouped.values()) or 1
    lines = []
    for label, count in grouped.items():
        pct = count / total * 100
        bar = _bar(pct)
        lines.append(f"{label:<15} {count:>5} commits   {bar}  {pct:.2f}%")

    best = max(grouped, key=grouped.__getitem__)
    emoji = "🐤" if "Morning" in best or "Daytime" in best else "🦉"
    intro = f"I'm {emoji} {best.split()[1]} person\n\n"
    return intro + "```text\n" + "\n".join(lines) + "\n```"


def format_days_of_week(weekday_counts: dict[int, int]) -> str:
    total = sum(weekday_counts.values()) or 1
    best_day = WEEKDAYS[max(weekday_counts, key=weekday_counts.get)]  # type: ignore[arg-type]
    header = f"📅 I'm Most Productive on **{best_day}**\n\n"
    lines = []
    for i, day in enumerate(WEEKDAYS):
        count = weekday_counts.get(i, 0)
        pct = count / total * 100
        bar = _bar(pct)
        lines.append(f"{day:<12} {count:>5} commits   {bar}  {pct:.2f}%")
    return header + "```text\n" + "\n".join(lines) + "\n```"


# ── WakaTime section ───────────────────────────────────────────────────────────


def format_waka_section(waka_data: dict) -> str:
    parts: list[str] = []
    parts.append("📊 **This Week I Spent My Time On**\n\n```text")

    if C.SHOW_TIMEZONE:
        parts.append(f"🕑︎ Timezone: {waka_data.get('timezone', 'N/A')}\n")

    if C.SHOW_LANGUAGE:
        lang_list = _make_list(waka_data.get("languages", []))
        parts.append(f"💬 Languages:\n{lang_list or 'No Activity Tracked'}\n")

    if C.SHOW_EDITORS:
        edit_list = _make_list(waka_data.get("editors", []))
        parts.append(f"🔥 Editors:\n{edit_list or 'No Activity Tracked'}\n")

    if C.SHOW_PROJECTS:
        proj_list = _make_list(waka_data.get("projects", []))
        parts.append(f"🐱‍💻 Projects:\n{proj_list or 'No Activity Tracked'}\n")

    if C.SHOW_OS:
        os_list = _make_list(waka_data.get("operating_systems", []))
        parts.append(f"💻 OS:\n{os_list or 'No Activity Tracked'}\n")

    parts.append("```")
    return "\n".join(parts)


# ── Language per repo ──────────────────────────────────────────────────────────


def format_language_per_repo(repos: list[dict]) -> str:
    lang_bytes: Counter[str] = Counter()
    for repo in repos:
        for edge in repo.get("languages", {}).get("edges", []):
            lang = edge["node"]["name"]
            size = edge["size"]
            lang_bytes[lang] += size

    total = sum(lang_bytes.values()) or 1
    lines = ["**I Mostly Code in**\n\n```text"]
    for lang, size in lang_bytes.most_common(10):
        pct = size / total * 100
        bar = _bar(pct)
        lines.append(f"{lang:<30} {bar}  {pct:.1f}%")
    lines.append("```")
    return "\n".join(lines)


# ── Badge helpers ──────────────────────────────────────────────────────────────


def badge(label: str, message: str, color: str = "blue") -> str:
    style = quote(C.BADGE_STYLE)
    return f"![{label}](https://img.shields.io/badge/{quote(label)}-{quote(message)}-{color}?style={style})"
