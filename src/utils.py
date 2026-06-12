"""Utility helpers for logging, persistence, and optional dependencies."""

from __future__ import annotations

import importlib
import logging
from pathlib import Path
from typing import Any

import joblib


def setup_logging(level: int = logging.INFO) -> None:
    """Configure compact, timestamped logging for scripts."""

    logging.basicConfig(
        level=level,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


def save_joblib(obj: Any, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(obj, path)


def load_joblib(path: Path) -> Any:
    return joblib.load(path)


def optional_import(module_name: str) -> Any | None:
    """Import a package if installed; otherwise return None."""

    try:
        return importlib.import_module(module_name)
    except Exception:
        return None

