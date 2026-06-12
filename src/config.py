"""Project configuration and dataset metadata."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Callable

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"
MODEL_DIR = PROJECT_ROOT / "models"
PLOT_DIR = PROJECT_ROOT / "plots"
OUTPUT_DIR = PROJECT_ROOT / "outputs"

RANDOM_STATE = 42
TEST_SIZE = 0.2
CV_FOLDS = 5


@dataclass(frozen=True)
class DatasetSpec:
    """Describes how a source dataset should be loaded and modeled."""

    name: str
    filename: str
    target: str
    sep: str = ","
    target_transform: Callable[[pd.Series], pd.Series] | None = None


DATASET_SPECS = {
    "cardio": DatasetSpec(
        name="cardio",
        filename="cardio_train.csv",
        target="cardio",
        sep=";",
    ),
    "framingham": DatasetSpec(
        name="framingham",
        filename="framingham.csv",
        target="TenYearCHD",
    ),
    "uci": DatasetSpec(
        name="uci",
        filename="heart_disease_uci.csv",
        target="num",
        target_transform=lambda s: (pd.to_numeric(s, errors="coerce") > 0).astype(int),
    ),
}


def ensure_directories() -> None:
    """Create runtime output folders."""

    for directory in (DATA_DIR, MODEL_DIR, PLOT_DIR, OUTPUT_DIR):
        directory.mkdir(parents=True, exist_ok=True)

