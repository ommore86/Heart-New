"""
SHAP-based explainability for the Heart Digital Twin ensemble.

Attempts to compute real SHAP values for each dataset sub-model.
Falls back gracefully to the heuristic contributing factors from modeling.py
if SHAP is unavailable or the model type is unsupported.
"""

from __future__ import annotations

import logging
from typing import Any

import numpy as np
import pandas as pd

from backend.schemas import FeatureContribution

LOGGER = logging.getLogger(__name__)

# Friendly display names for engineered / aliased columns
FEATURE_DISPLAY_NAMES: dict[str, str] = {
    "AgeYears": "Age",
    "age": "Age",
    "systolic_bp": "Systolic BP",
    "diastolic_bp": "Diastolic BP",
    "cholesterol": "Cholesterol",
    "glucose": "Glucose",
    "smoker": "Smoking",
    "physically_active": "Physical Activity",
    "BMI": "BMI",
    "PulsePressure": "Pulse Pressure",
    "MeanArterialPressure": "Mean Arterial Pressure",
    "LifestyleScore": "Lifestyle Score",
    "alcohol": "Alcohol Use",
    "sex": "Sex",
    "heartRate": "Heart Rate",
    "thalach": "Max Heart Rate",
}


def _friendly_name(raw: str) -> str:
    return FEATURE_DISPLAY_NAMES.get(raw, raw.replace("_", " ").title())


def _try_shap_values(model: Any, x_row: pd.DataFrame) -> np.ndarray | None:
    """Attempt to compute SHAP values for a single row using the best available explainer."""
    try:
        import shap  # noqa: PLC0415

        # Try TreeExplainer first (fast, works for RF/GBM/XGB/LGB)
        try:
            explainer = shap.TreeExplainer(model.named_steps["classifier"])
            x_transformed = model.named_steps["preprocessor"].transform(x_row)
            shap_vals = explainer.shap_values(x_transformed)
            # For binary classifiers, shap_values returns list[array] (class 0, class 1)
            if isinstance(shap_vals, list):
                return np.array(shap_vals[1]).flatten()
            return np.array(shap_vals).flatten()
        except Exception:
            pass

        # Fallback: LinearExplainer / KernelExplainer (slow but universal)
        try:
            x_transformed = model.named_steps["preprocessor"].transform(x_row)
            background = np.zeros((1, x_transformed.shape[1]))
            classifier = model.named_steps["classifier"]
            explainer = shap.KernelExplainer(
                lambda x: classifier.predict_proba(x)[:, 1], background
            )
            shap_vals = explainer.shap_values(x_transformed, nsamples=50, silent=True)
            return np.array(shap_vals).flatten()
        except Exception:
            pass

    except ImportError:
        pass

    return None


def compute_feature_contributions(
    bundle: Any,
    patient_dict: dict[str, Any],
    top_n: int = 8,
) -> list[FeatureContribution]:
    """
    Compute SHAP-based feature contributions for one dataset bundle.
    Falls back to heuristic if SHAP fails.
    """
    try:
        x_row = bundle.prepare_patient(patient_dict)
        shap_values = _try_shap_values(bundle.model, x_row)

        if shap_values is not None:
            # Get feature names after preprocessing
            try:
                preprocessor = bundle.model.named_steps["preprocessor"]
                feature_names: list[str] = []
                for name, transformer, cols in preprocessor.transformers_:
                    if name == "num":
                        feature_names.extend(cols)
                    elif name == "cat":
                        ohe = transformer.named_steps["onehot"]
                        for i, col in enumerate(cols):
                            for cat in ohe.categories_[i]:
                                feature_names.append(f"{col}_{cat}")
            except Exception:
                feature_names = [f"feature_{i}" for i in range(len(shap_values))]

            n = min(len(shap_values), len(feature_names))
            pairs = list(zip(feature_names[:n], shap_values[:n]))
            pairs.sort(key=lambda p: abs(p[1]), reverse=True)

            results: list[FeatureContribution] = []
            for feat, val in pairs[:top_n]:
                results.append(
                    FeatureContribution(
                        feature=feat,
                        contribution=round(float(abs(val)), 4),
                        direction="positive" if val > 0 else "negative",
                        display_value=_friendly_name(feat),
                    )
                )
            return results

    except Exception as exc:
        LOGGER.debug("SHAP computation failed (%s), using heuristic fallback.", exc)

    # Heuristic fallback
    return _heuristic_contributions(patient_dict, top_n)


def compute_ensemble_contributions(
    ensemble: Any,
    patient_dict: dict[str, Any],
    top_n: int = 8,
) -> list[FeatureContribution]:
    """Average SHAP contributions across all dataset bundles."""
    all_contributions: dict[str, list[float]] = {}

    for bundle in ensemble.bundles.values():
        contribs = compute_feature_contributions(bundle, patient_dict, top_n=top_n * 2)
        for c in contribs:
            signed = c.contribution if c.direction == "positive" else -c.contribution
            all_contributions.setdefault(c.feature, []).append(signed)

    # Average across bundles
    averaged = {feat: float(np.mean(vals)) for feat, vals in all_contributions.items()}
    sorted_items = sorted(averaged.items(), key=lambda kv: abs(kv[1]), reverse=True)

    results: list[FeatureContribution] = []
    for feat, val in sorted_items[:top_n]:
        results.append(
            FeatureContribution(
                feature=feat,
                contribution=round(abs(val), 4),
                direction="positive" if val > 0 else "negative",
                display_value=_friendly_name(feat),
            )
        )
    return results


def _heuristic_contributions(patient: dict, top_n: int = 8) -> list[FeatureContribution]:
    """Rule-based contribution list when SHAP is unavailable."""
    items: list[tuple[str, float, str]] = []

    systolic = float(patient.get("systolic_bp", patient.get("ap_hi", 120)))
    diastolic = float(patient.get("diastolic_bp", patient.get("ap_lo", 80)))
    chol = float(patient.get("cholesterol", patient.get("totChol", 200)))
    glucose = float(patient.get("glucose", patient.get("gluc", 90)))
    smoker = int(patient.get("smoker", patient.get("smoke", 0)))
    active = int(patient.get("physically_active", patient.get("active", 1)))
    bmi = patient.get("BMI")
    age = float(patient.get("AgeYears", patient.get("age", 40)))

    if systolic >= 180:
        items.append(("systolic_bp", 0.30, "positive"))
    elif systolic >= 140:
        items.append(("systolic_bp", 0.18, "positive"))
    elif systolic < 120:
        items.append(("systolic_bp", 0.05, "negative"))

    if diastolic >= 100:
        items.append(("diastolic_bp", 0.18, "positive"))
    elif diastolic >= 90:
        items.append(("diastolic_bp", 0.10, "positive"))

    if chol >= 280:
        items.append(("cholesterol", 0.20, "positive"))
    elif chol >= 240:
        items.append(("cholesterol", 0.12, "positive"))
    elif chol < 180:
        items.append(("cholesterol", 0.06, "negative"))

    if smoker == 1:
        items.append(("smoker", 0.15, "positive"))
    else:
        items.append(("smoker", 0.08, "negative"))

    if active == 0:
        items.append(("physically_active", 0.10, "positive"))
    else:
        items.append(("physically_active", 0.08, "negative"))

    if glucose >= 200:
        items.append(("glucose", 0.18, "positive"))
    elif glucose >= 126:
        items.append(("glucose", 0.10, "positive"))

    if bmi is not None:
        bmi = float(bmi)
        if bmi >= 35:
            items.append(("BMI", 0.14, "positive"))
        elif bmi >= 30:
            items.append(("BMI", 0.08, "positive"))

    if age >= 65:
        items.append(("AgeYears", 0.14, "positive"))
    elif age >= 50:
        items.append(("AgeYears", 0.08, "positive"))

    items.sort(key=lambda x: x[1], reverse=True)
    return [
        FeatureContribution(
            feature=feat,
            contribution=val,
            direction=direction,
            display_value=_friendly_name(feat),
        )
        for feat, val, direction in items[:top_n]
    ]
