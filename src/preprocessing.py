"""Data loading, reporting, cleaning, and preprocessing factories."""

from __future__ import annotations

import io
import logging
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from .config import DatasetSpec
from .feature_engineering import add_heart_state_features

LOGGER = logging.getLogger(__name__)


ID_COLUMNS = {"id", "patient_id"}
BP_RANGES = {
    "systolic_bp": (60, 250),
    "diastolic_bp": (30, 150),
}


def load_dataset(spec: DatasetSpec, data_dir: Path) -> pd.DataFrame:
    path = data_dir / spec.filename
    if not path.exists():
        raise FileNotFoundError(f"Dataset not found: {path}")
    return pd.read_csv(path, sep=spec.sep)


def report_dataset(df: pd.DataFrame, target: str, dataset_name: str) -> None:
    """Print the required exploratory diagnostics."""

    LOGGER.info("[%s] shape: %s", dataset_name, df.shape)
    LOGGER.info("[%s] head:\n%s", dataset_name, df.head())
    LOGGER.info("[%s] describe:\n%s", dataset_name, df.describe(include="all").transpose())
    buffer = io.StringIO()
    df.info(buf=buffer)
    LOGGER.info("[%s] info:\n%s", dataset_name, buffer.getvalue())
    LOGGER.info("[%s] missing values:\n%s", dataset_name, df.isna().sum().sort_values(ascending=False))
    if target in df.columns:
        LOGGER.info("[%s] class distribution:\n%s", dataset_name, df[target].value_counts(dropna=False))


def remove_impossible_bp(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    mask = pd.Series(True, index=out.index)
    for col, (low, high) in BP_RANGES.items():
        if col in out.columns:
            values = pd.to_numeric(out[col], errors="coerce")
            mask &= values.between(low, high) | values.isna()
    if {"systolic_bp", "diastolic_bp"}.issubset(out.columns):
        sys_bp = pd.to_numeric(out["systolic_bp"], errors="coerce")
        dia_bp = pd.to_numeric(out["diastolic_bp"], errors="coerce")
        mask &= (sys_bp > dia_bp) | sys_bp.isna() | dia_bp.isna()
    removed = int((~mask).sum())
    if removed:
        LOGGER.info("Removed %s rows with impossible blood pressure values", removed)
    return out.loc[mask].reset_index(drop=True)


def impute_missing_values(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    numeric_cols = out.select_dtypes(include=[np.number]).columns
    categorical_cols = out.columns.difference(numeric_cols)
    for col in numeric_cols:
        if out[col].isna().any():
            out[col] = out[col].fillna(out[col].median())
    for col in categorical_cols:
        if out[col].isna().any():
            mode = out[col].mode(dropna=True)
            out[col] = out[col].fillna(mode.iloc[0] if not mode.empty else "Unknown")
    return out


def remove_iqr_outliers(df: pd.DataFrame, target: str, multiplier: float = 1.5) -> pd.DataFrame:
    out = df.copy()
    numeric_cols = [
        col
        for col in out.select_dtypes(include=[np.number]).columns
        if col != target and out[col].nunique(dropna=True) > 10
    ]
    if not numeric_cols:
        return out

    mask = pd.Series(True, index=out.index)
    for col in numeric_cols:
        q1 = out[col].quantile(0.25)
        q3 = out[col].quantile(0.75)
        iqr = q3 - q1
        if pd.isna(iqr) or iqr == 0:
            continue
        mask &= out[col].between(q1 - multiplier * iqr, q3 + multiplier * iqr)

    removed = int((~mask).sum())
    if removed:
        LOGGER.info("Removed %s rows using IQR outlier filtering", removed)
    return out.loc[mask].reset_index(drop=True)


def prepare_dataset(df: pd.DataFrame, spec: DatasetSpec) -> tuple[pd.DataFrame, pd.Series]:
    """Clean a raw source dataset and return features and binary target."""

    out = df.drop_duplicates().reset_index(drop=True)
    if spec.target_transform is not None:
        out[spec.target] = spec.target_transform(out[spec.target])

    out = add_heart_state_features(out, dataset_name=spec.name)
    out = remove_impossible_bp(out)
    out = impute_missing_values(out)
    out = remove_iqr_outliers(out, target=spec.target)

    y = pd.to_numeric(out[spec.target], errors="coerce").fillna(0).astype(int)
    x = out.drop(columns=[spec.target])
    x = x.drop(columns=[col for col in x.columns if col in ID_COLUMNS], errors="ignore")
    return x, y


def make_preprocessor(x: pd.DataFrame) -> ColumnTransformer:
    numeric_cols = x.select_dtypes(include=[np.number]).columns.tolist()
    categorical_cols = x.columns.difference(numeric_cols).tolist()

    numeric_pipeline = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
        ]
    )
    categorical_pipeline = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="most_frequent")),
            ("onehot", OneHotEncoder(handle_unknown="ignore", sparse_output=False)),
        ]
    )
    return ColumnTransformer(
        transformers=[
            ("num", numeric_pipeline, numeric_cols),
            ("cat", categorical_pipeline, categorical_cols),
        ],
        remainder="drop",
    )

