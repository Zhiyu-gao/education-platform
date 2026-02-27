import os
from pathlib import Path

import dashscope

BASE_DIR = Path(__file__).resolve().parent
ENV_FILE_PATH = BASE_DIR / ".env"


def _parse_env_file(path: Path) -> dict[str, str]:
    if not path.exists():
        return {}

    parsed: dict[str, str] = {}
    with path.open("r", encoding="utf-8", errors="ignore") as env_file:
        for raw_line in env_file:
            line = raw_line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            if key:
                parsed[key] = value
    return parsed


def get_env_value(*keys: str) -> str:
    for key in keys:
        value = os.getenv(key, "").strip()
        if value:
            return value

    env_mapping = _parse_env_file(ENV_FILE_PATH)
    for key in keys:
        value = env_mapping.get(key, "").strip()
        if value:
            return value
    return ""


def load_dashscope_api_key() -> str:
    return get_env_value("DASHSCOPE_API_KEY", "QWEN_API_KEY")


def ensure_dashscope_api_key() -> bool:
    api_key = load_dashscope_api_key()
    if api_key:
        dashscope.api_key = api_key
        os.environ["DASHSCOPE_API_KEY"] = api_key
        return True
    return bool(getattr(dashscope, "api_key", ""))


def get_database_url() -> str:
    direct_url = get_env_value("EDU_DATABASE_URL", "DATABASE_URL")
    if direct_url:
        return direct_url

    host = get_env_value("EDU_DB_HOST", "MYSQL_HOST") or "localhost"
    port = get_env_value("EDU_DB_PORT", "MYSQL_PORT") or "3306"
    database = get_env_value("EDU_DB_NAME", "MYSQL_DATABASE") or "ry-vue"
    username = get_env_value("EDU_DB_USER", "MYSQL_USER") or "root"
    password = get_env_value("EDU_DB_PASSWORD", "MYSQL_PASSWORD")
    return f"mysql+pymysql://{username}:{password}@{host}:{port}/{database}"
