"""Canonical cardiovascular feature engineering."""

from __future__ import annotations

import numpy as np
import pandas as pd


COLUMN_RENAMES = {
    "gender": "sex",
    "male": "sex",
    "ap_hi": "systolic_bp",
    "sysBP": "systolic_bp",
    "trestbps": "systolic_bp",
    "ap_lo": "diastolic_bp",
    "diaBP": "diastolic_bp",
    "totChol": "cholesterol",
    "chol": "cholesterol",
    "gluc": "glucose",
    "currentSmoker": "smoker",
    "smoke": "smoker",
    "active": "physically_active",
    "alco": "alcohol",
}


def standardize_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Map dataset-specific columns into common heart-state terminology."""

    return df.rename(columns={k: v for k, v in COLUMN_RENAMES.items() if k in df.columns})


def encode_common_binary_values(df: pd.DataFrame) -> pd.DataFrame:
    """Normalize obvious binary medical strings while leaving categories intact."""

    out = df.copy()
    binary_maps = {
        True: 1,
        False: 0,
        "TRUE": 1,
        "FALSE": 0,
        "True": 1,
        "False": 0,
        "yes": 1,
        "no": 0,
        "Yes": 1,
        "No": 0,
        "Male": 1,
        "Female": 0,
        "M": 1,
        "F": 0,
    }
    for col in out.columns:
        if out[col].dtype == "object" or str(out[col].dtype) == "boolean":
            mapped = out[col].map(binary_maps)
            if mapped.notna().sum() == out[col].notna().sum() and mapped.notna().sum() > 0:
                out[col] = mapped
    return out


def add_heart_state_features(df: pd.DataFrame, dataset_name: str) -> pd.DataFrame:
    """Create generalized Heart State Model features."""

    out = standardize_columns(df.copy())
    out = encode_common_binary_values(out)

    if dataset_name == "cardio" and "age" in out.columns:
        out["AgeYears"] = pd.to_numeric(out["age"], errors="coerce") / 365.0
    elif "age" in out.columns and "AgeYears" not in out.columns:
        out["AgeYears"] = pd.to_numeric(out["age"], errors="coerce")

    if "BMI" not in out.columns and {"weight", "height"}.issubset(out.columns):
        height_m = pd.to_numeric(out["height"], errors="coerce") / 100.0
        weight_kg = pd.to_numeric(out["weight"], errors="coerce")
        out["BMI"] = weight_kg / np.square(height_m.replace(0, np.nan))

    if {"systolic_bp", "diastolic_bp"}.issubset(out.columns):
        sys_bp = pd.to_numeric(out["systolic_bp"], errors="coerce")
        dia_bp = pd.to_numeric(out["diastolic_bp"], errors="coerce")
        out["PulsePressure"] = sys_bp - dia_bp
        out["MeanArterialPressure"] = (2 * dia_bp + sys_bp) / 3.0

    default_zero = pd.Series(0, index=out.index)
    smoker = pd.to_numeric(out.get("smoker", default_zero), errors="coerce").fillna(0)
    alcohol = pd.to_numeric(out.get("alcohol", default_zero), errors="coerce").fillna(0)
    active = pd.to_numeric(out.get("physically_active", default_zero), errors="coerce").fillna(0)
    out["LifestyleScore"] = (1 - smoker.clip(0, 1)) + (1 - alcohol.clip(0, 1)) + active.clip(0, 1)

    return out


def engineer_patient_features(patient: dict, dataset_name: str) -> pd.DataFrame:
    """Transform one patient dictionary into a model-ready dataframe."""

    return add_heart_state_features(pd.DataFrame([patient]), dataset_name=dataset_name)
