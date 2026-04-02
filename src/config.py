"""
Configuration manager: reads all env vars set by action.yml inputs.
"""
import os


def _bool(key: str, default: bool = True) -> bool:
    val = os.environ.get(key, str(default)).strip().lower()
    return val not in ("false", "0", "no")


def _str(key: str, default: str = "") -> str:
    return os.environ.get(key, default).strip()


def _int(key: str, default: int = 0) -> int:
    try:
        return int(os.environ.get(key, str(default)).strip())
    except ValueError:
        return default


# ── Credentials ───────────────────────────────────────────────────────────────
GH_TOKEN: str = _str("INPUT_GH_TOKEN") or _str("GH_TOKEN")
WAKATIME_API_KEY: str = _str("INPUT_WAKATIME_API_KEY") or _str("WAKATIME_API_KEY")
WAKATIME_API_URL: str = _str("INPUT_WAKATIME_API_URL", "https://wakatime.com/api/v1/")

# ── README targeting ───────────────────────────────────────────────────────────
SECTION_NAME: str = _str("INPUT_SECTION_NAME", "waka")
PULL_BRANCH_NAME: str = _str("INPUT_PULL_BRANCH_NAME", "")
PUSH_BRANCH_NAME: str = _str("INPUT_PUSH_BRANCH_NAME", "")

# ── Feature flags ─────────────────────────────────────────────────────────────
SHOW_COMMIT: bool = _bool("INPUT_SHOW_COMMIT")
SHOW_DAYS_OF_WEEK: bool = _bool("INPUT_SHOW_DAYS_OF_WEEK")
SHOW_LANGUAGE: bool = _bool("INPUT_SHOW_LANGUAGE")
SHOW_EDITORS: bool = _bool("INPUT_SHOW_EDITORS")
SHOW_PROJECTS: bool = _bool("INPUT_SHOW_PROJECTS")
SHOW_OS: bool = _bool("INPUT_SHOW_OS")
SHOW_TIMEZONE: bool = _bool("INPUT_SHOW_TIMEZONE")
SHOW_LINES_OF_CODE: bool = _bool("INPUT_SHOW_LINES_OF_CODE", False)
SHOW_LOC_CHART: bool = _bool("INPUT_SHOW_LOC_CHART")
SHOW_LANGUAGE_PER_REPO: bool = _bool("INPUT_SHOW_LANGUAGE_PER_REPO")
SHOW_PROFILE_VIEWS: bool = _bool("INPUT_SHOW_PROFILE_VIEWS")
SHOW_SHORT_INFO: bool = _bool("INPUT_SHOW_SHORT_INFO")
SHOW_UPDATED_DATE: bool = _bool("INPUT_SHOW_UPDATED_DATE")
SHOW_TOTAL_CODE_TIME: bool = _bool("INPUT_SHOW_TOTAL_CODE_TIME")

# ── Commit settings ───────────────────────────────────────────────────────────
COMMIT_BY_ME: bool = _bool("INPUT_COMMIT_BY_ME", False)
COMMIT_MESSAGE: str = _str("INPUT_COMMIT_MESSAGE", "Updated with Dev Metrics")
COMMIT_USERNAME: str = _str("INPUT_COMMIT_USERNAME", "readme-bot")
COMMIT_EMAIL: str = _str("INPUT_COMMIT_EMAIL", "41898282+github-actions[bot]@users.noreply.github.com")
COMMIT_SINGLE: bool = _bool("INPUT_COMMIT_SINGLE", False)

# ── Display options ────────────────────────────────────────────────────────────
MAX_REPOS: int = _int("INPUT_MAX_REPOS", 0)
IGNORED_REPOS: list[str] = [r.strip() for r in _str("INPUT_IGNORED_REPOS").split(",") if r.strip()]
SYMBOL_VERSION: int = _int("INPUT_SYMBOL_VERSION", 1)
BADGE_STYLE: str = _str("INPUT_BADGE_STYLE", "flat")
UPDATED_DATE_FORMAT: str = _str("INPUT_UPDATED_DATE_FORMAT", "%d/%m/%Y %H:%M:%S")
DEBUG_RUN: bool = _bool("INPUT_DEBUG_RUN", False)

# ── Progress bar symbols ───────────────────────────────────────────────────────
_BLOCK_CHARS = {
    1: ("█", "░"),
    2: ("⣿", "⣀"),
    3: ("⬛", "⬜"),
}
BLOCK_CHAR, EMPTY_CHAR = _BLOCK_CHARS.get(SYMBOL_VERSION, ("█", "░"))
BAR_LENGTH: int = 25
