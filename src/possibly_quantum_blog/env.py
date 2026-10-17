import os
from pathlib import Path

from dotenv import dotenv_values, load_dotenv

PACKAGE_ENV_PATH = Path(__file__).with_name(".env")
PROJECT_ENV_PATH = Path(__file__).resolve().parents[2] / ".env"


def _is_valid_candidate(api_key: str) -> bool:
    return bool(api_key) and api_key not in {"123", "your_openai_api_key"} and api_key.startswith("sk-")


def load_environment() -> None:
    load_dotenv(dotenv_path=PACKAGE_ENV_PATH, override=False)
    load_dotenv(dotenv_path=PROJECT_ENV_PATH, override=False)

    candidates = [
        os.environ.get("OPENAI_API_KEY", ""),
        dotenv_values(PACKAGE_ENV_PATH).get("OPENAI_API_KEY") or "",
        dotenv_values(PROJECT_ENV_PATH).get("OPENAI_API_KEY") or "",
    ]
    selected_api_key = next((key.strip() for key in candidates if _is_valid_candidate(key.strip())), "")
    if not selected_api_key:
        raise ValueError(
            "OPENAI_API_KEY is missing, placeholder, or malformed. "
            "Set a valid key in the package .env or your process environment."
        )
    os.environ["OPENAI_API_KEY"] = selected_api_key
