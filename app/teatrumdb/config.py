from __future__ import annotations

import os
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]


def _load_env_defaults() -> dict[str, str]:
    env_path = PROJECT_ROOT / ".env"
    if not env_path.exists():
        return {}

    values: dict[str, str] = {}
    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue

        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip("'").strip('"')
        if key and key not in os.environ:
            values[key] = value
    return values


ENV_DEFAULTS = _load_env_defaults()


APP_NAME = "TeatrumDB"
APP_TITLE = "TeatrumDB - semestralni projekt XDBS1"
APP_SUBTITLE = "Divadelni databazova aplikace nad Oracle"
WINDOW_SIZE = "1440x900"
MIN_WINDOW_SIZE = (1280, 780)

DEFAULT_ORACLE_USER = os.getenv("ORA_USER", ENV_DEFAULTS.get("ORA_USER", "teatrum"))
DEFAULT_ORACLE_PASSWORD = os.getenv("ORA_PASS", ENV_DEFAULTS.get("ORA_PASS", ""))
DEFAULT_ORACLE_DSN = os.getenv("ORA_DSN", ENV_DEFAULTS.get("ORA_DSN", "localhost:1521/FREEPDB1"))
AUTO_CONNECT_ON_START = os.getenv("TEATRUMDB_AUTO_CONNECT", "1").lower() not in {"0", "false", "no"}
