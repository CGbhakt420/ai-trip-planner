import os
from pathlib import Path

from dotenv import load_dotenv


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def get_api_key(*names: str) -> str | None:
    load_dotenv(PROJECT_ROOT / ".env")
    working_directory_env = Path.cwd() / ".env"
    if working_directory_env != PROJECT_ROOT / ".env":
        load_dotenv(working_directory_env)

    for name in names:
        value = os.getenv(name)
        if value and value.strip():
            return value.strip()
    return None


def require_api_key(name: str) -> str:
    value = get_api_key(name)
    if value is None:
        raise ValueError(
            f"{name} is not configured. Set it as an environment variable "
            "or in the project .env file."
        )
    return value
