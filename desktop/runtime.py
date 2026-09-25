from __future__ import annotations

import os
import sys
from pathlib import Path

from dotenv import load_dotenv

APP_NAME = "UFRS Student Desktop"
APP_DIR_NAME = "ufrs_student_desktop"
PROJECT_ROOT = Path(__file__).resolve().parents[1]


def is_frozen() -> bool:
    return bool(getattr(sys, "frozen", False))


def bundle_root() -> Path:
    if is_frozen():
        meipass = getattr(sys, "_MEIPASS", None)
        if meipass:
            return Path(meipass)
        return executable_dir()
    return PROJECT_ROOT


def executable_dir() -> Path:
    if is_frozen():
        return Path(sys.executable).resolve().parent
    return PROJECT_ROOT


def app_data_dir() -> Path:
    base_dir = Path(os.getenv("APPDATA") or executable_dir())
    return base_dir / APP_DIR_NAME


def resource_path(*parts: str) -> Path:
    relative_path = Path(*parts)
    candidates = [
        bundle_root() / relative_path,
        executable_dir() / relative_path,
        PROJECT_ROOT / relative_path,
    ]

    for candidate in candidates:
        if candidate.is_file():
            return candidate
    return candidates[0]


def icon_path() -> Path:
    for icon_name in ("app_icon.ico", "app_icon.svg"):
        candidate = resource_path("desktop", "resources", icon_name)
        if candidate.is_file():
            return candidate
    return resource_path("desktop", "resources", "app_icon.ico")


def iter_env_candidates() -> list[Path]:
    explicit_env = os.getenv("UFRS_ENV_FILE")
    candidates: list[Path] = []

    if explicit_env:
        candidates.append(Path(explicit_env).expanduser())

    candidates.extend(
        [
            executable_dir() / ".env",
            executable_dir() / "desktop.env",
            executable_dir() / "config" / "desktop.env",
            app_data_dir() / "desktop.env",
            PROJECT_ROOT / ".env",
        ]
    )

    unique_candidates: list[Path] = []
    seen: set[Path] = set()
    for candidate in candidates:
        if candidate not in seen:
            unique_candidates.append(candidate)
            seen.add(candidate)
    return unique_candidates


def load_runtime_environment() -> Path | None:
    for env_file in iter_env_candidates():
        if env_file.is_file():
            load_dotenv(env_file, override=False)
            return env_file
    return None
