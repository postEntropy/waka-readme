"""
GitHub integration: fetching repos, commits, updating README.
"""
from __future__ import annotations

import re
from datetime import datetime, timezone
from typing import Any

import httpx
from github import Github, GithubException
from github.Repository import Repository

from src import config as C

# ── GraphQL helper ─────────────────────────────────────────────────────────────

GRAPHQL_URL = "https://api.github.com/graphql"

_REPO_LIST_QUERY = """
query ($login: String!, $id: ID!, $after: String) {
  user(login: $login) {
    repositories(
      first: 100
      after: $after
      ownerAffiliations: [OWNER, COLLABORATOR, ORGANIZATION_MEMBER]
      orderBy: {field: UPDATED_AT, direction: DESC}
    ) {
      pageInfo { hasNextPage endCursor }
      nodes {
        name
        nameWithOwner
        isFork
        primaryLanguage { name }
        languages(first: 20, orderBy: {field: SIZE, direction: DESC}) {
          edges { size node { name } }
        }
        defaultBranchRef {
          target {
            ... on Commit {
              history(author: { id: $id }) {
                totalCount
              }
            }
          }
        }
      }
    }
  }
}
"""

_COMMIT_HISTORY_QUERY = """
query ($owner: String!, $repo: String!, $authorId: ID!, $after: String) {
  repository(owner: $owner, name: $repo) {
    defaultBranchRef {
      target {
        ... on Commit {
          history(first: 100, author: { id: $authorId }, after: $after) {
            pageInfo { hasNextPage endCursor }
            nodes {
              committedDate
              author { user { login } }
            }
          }
        }
      }
    }
  }
}
"""


async def _graphql(query: str, variables: dict[str, Any], token: str) -> dict:
    headers = {"Authorization": f"bearer {token}", "Content-Type": "application/json"}
    async with httpx.AsyncClient(timeout=60) as client:
        resp = await client.post(
            GRAPHQL_URL,
            json={"query": query, "variables": variables},
            headers=headers,
        )
        resp.raise_for_status()
        data = resp.json()
        if "errors" in data:
            print(f"[GraphQL] Error: {data['errors']}")
        return data


# ── Public API ─────────────────────────────────────────────────────────────────


def get_github_client() -> Github:
    return Github(C.GH_TOKEN)


async def fetch_user_repos(login: str, user_node_id: str) -> list[dict]:
    """Paginates through all user repositories using GraphQL."""
    repos: list[dict] = []
    after: str | None = None
    while True:
        result = await _graphql(
            _REPO_LIST_QUERY,
            {"login": login, "id": user_node_id, "after": after},
            C.GH_TOKEN,
        )
        data = result.get("data") or {}
        user_data = data.get("user") or {}
        repos_data = user_data.get("repositories") or {}
        
        nodes = repos_data.get("nodes") or []
        page_info = repos_data.get("pageInfo") or {"hasNextPage": False}
        
        repos.extend(nodes)
        if C.MAX_REPOS > 0 and len(repos) >= C.MAX_REPOS:
            break
        if not page_info["hasNextPage"]:
            break
        after = page_info["endCursor"]

    # Filter ignored repos and forks
    repos = [r for r in repos if r["name"] not in C.IGNORED_REPOS and not r.get("isFork", False)]
    if C.MAX_REPOS > 0:
        repos = repos[: C.MAX_REPOS]
    return repos


async def fetch_commit_history(owner: str, repo_name: str, author_id: str) -> list[dict]:
    """Returns all commits in the default branch for a given repo authored by the user."""
    commits: list[dict] = []
    after: str | None = None
    while True:
        result = await _graphql(
            _COMMIT_HISTORY_QUERY,
            {"owner": owner, "repo": repo_name, "authorId": author_id, "after": after},
            C.GH_TOKEN,
        )
        data = result.get("data") or {}
        repo_data = data.get("repository") or {}
        ref = repo_data.get("defaultBranchRef")
        if not ref:
            break
        history = ref["target"]["history"]
        commits.extend(history["nodes"])
        if not history["pageInfo"]["hasNextPage"]:
            break
        after = history["pageInfo"]["endCursor"]
    return commits


def aggregate_commit_times(
    commits: list[dict], login: str
) -> tuple[dict[int, int], dict[int, int]]:
    """Returns (hour_counts, weekday_counts) from a flat list of commit dicts."""
    hour_counts: dict[int, int] = {h: 0 for h in range(24)}
    weekday_counts: dict[int, int] = {d: 0 for d in range(7)}

    for c in commits:
        author = c.get("author", {}).get("user")
        if author is None or author.get("login") != login:
            continue
        try:
            dt = datetime.fromisoformat(c["committedDate"].replace("Z", "+00:00"))
            hour_counts[dt.hour] += 1
            weekday_counts[dt.weekday()] += 1
        except Exception:
            pass

    return hour_counts, weekday_counts


def update_readme(repo: Repository, stats: str, section: str = "waka") -> None:
    """Replaces the <!--START_SECTION:{section}-->...<!--END_SECTION:{section}--> block."""
    branch = C.PULL_BRANCH_NAME or repo.default_branch
    push_branch = C.PUSH_BRANCH_NAME or branch

    readme_file = repo.get_contents("README.md", ref=branch)
    old_content = readme_file.decoded_content.decode("utf-8")  # type: ignore[union-attr]

    start_tag = f"<!--START_SECTION:{section}-->"
    end_tag = f"<!--END_SECTION:{section}-->"
    new_block = f"{start_tag}\n{stats.strip()}\n{end_tag}"

    pattern = re.compile(
        rf"{re.escape(start_tag)}.*?{re.escape(end_tag)}", re.DOTALL
    )
    if pattern.search(old_content):
        new_content = pattern.sub(new_block, old_content)
    else:
        print(f"[GitHub] Tags {start_tag} / {end_tag} not found in README.md — skipping update.")
        return

    if new_content == old_content:
        print("[GitHub] README unchanged — no commit needed.")
        return

    repo.update_file(
        path="README.md",
        message=C.COMMIT_MESSAGE,
        content=new_content,
        sha=readme_file.sha,  # type: ignore[union-attr]
        branch=push_branch,
    )
    print(f"[GitHub] README.md updated on branch '{push_branch}'.")
