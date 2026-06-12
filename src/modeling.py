"""Model factories and digital-twin ensemble containers."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier, VotingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.neural_network import MLPClassifier
from sklearn.pipeline import Pipeline

from .feature_engineering import engineer_patient_features
from .utils import optional_import


def get_model_grids(random_state: int = 42, fast: bool = False) -> dict[str, tuple[BaseEstimator, dict[str, list[Any]]]]:
    """Return estimators and compact hyperparameter grids."""

    grids: dict[str, tuple[BaseEstimator, dict[str, list[Any]]]] = {
        "logistic_regression": (
            LogisticRegression(max_iter=2000, class_weight="balanced", random_state=random_state),
            {
                "classifier__C": [0.1, 1.0] if fast else [0.01, 0.1, 1.0, 10.0],
                "classifier__solver": ["lbfgs"],
            },
        ),
        "random_forest": (
            RandomForestClassifier(class_weight="balanced", random_state=random_state, n_jobs=-1),
            {
                "classifier__n_estimators": [100] if fast else [100, 250],
                "classifier__max_depth": [None, 8] if fast else [None, 8, 14],
                "classifier__min_samples_leaf": [1, 3],
            },
        ),
        "gradient_boosting": (
            GradientBoostingClassifier(random_state=random_state),
            {
                "classifier__n_estimators": [100] if fast else [100, 200],
                "classifier__learning_rate": [0.05, 0.1],
                "classifier__max_depth": [2, 3],
            },
        ),
        "mlp": (
            MLPClassifier(max_iter=350, early_stopping=True, random_state=random_state),
            {
                "classifier__hidden_layer_sizes": [(64,), (64, 32)] if not fast else [(32,)],
                "classifier__alpha": [0.0001, 0.001],
            },
        ),
    }

    xgb = optional_import("xgboost")
    if xgb is not None:
        grids["xgboost"] = (
            xgb.XGBClassifier(
                objective="binary:logistic",
                eval_metric="logloss",
                random_state=random_state,
                n_jobs=-1,
            ),
            {
                "classifier__n_estimators": [100] if fast else [100, 200],
                "classifier__max_depth": [3, 5],
                "classifier__learning_rate": [0.05, 0.1],
            },
        )

    lgb = optional_import("lightgbm")
    if lgb is not None:
        grids["lightgbm"] = (
            lgb.LGBMClassifier(
                objective="binary",
                class_weight="balanced",
                random_state=random_state,
                n_jobs=-1,
                verbose=-1,
            ),
            {
                "classifier__n_estimators": [100] if fast else [100, 200],
                "classifier__num_leaves": [15, 31],
                "classifier__learning_rate": [0.05, 0.1],
            },
        )

    catboost = optional_import("catboost")
    if catboost is not None:
        grids["catboost"] = (
            catboost.CatBoostClassifier(
                loss_function="Logloss",
                random_seed=random_state,
                verbose=False,
                allow_writing_files=False,
            ),
            {
                "classifier__iterations": [100] if fast else [100, 200],
                "classifier__depth": [4, 6],
                "classifier__learning_rate": [0.05, 0.1],
            },
        )

    return grids


def make_pipeline(preprocessor: Any, classifier: BaseEstimator) -> Pipeline:
    return Pipeline(steps=[("preprocessor", preprocessor), ("classifier", classifier)])


def predict_positive_proba(model: Any, x: pd.DataFrame) -> np.ndarray:
    if hasattr(model, "predict_proba"):
        return model.predict_proba(x)[:, 1]
    decision = model.decision_function(x)
    return 1 / (1 + np.exp(-decision))


@dataclass
class DatasetModelBundle:
    """A fitted model plus metadata needed for heart-state inference."""

    dataset_name: str
    model: Any
    feature_columns: list[str]
    roc_auc: float
    model_name: str

    def prepare_patient(self, patient: dict) -> pd.DataFrame:
        x = engineer_patient_features(patient, self.dataset_name)
        return x.reindex(columns=self.feature_columns)

    def predict_probability(self, patient: dict) -> float:
        x = self.prepare_patient(patient)
        return float(predict_positive_proba(self.model, x)[0])


@dataclass
class HeartDigitalTwinEnsemble:
    """Cross-dataset ensemble for Digital Twin heart state scoring."""

    bundles: dict[str, DatasetModelBundle]

    def predict_probability(self, patient: dict) -> float:
        probabilities = [bundle.predict_probability(patient) for bundle in self.bundles.values()]
        return float(np.mean(probabilities))

    def predict(self, patient: dict) -> dict[str, Any]:
        dataset_probabilities = {
            name: bundle.predict_probability(patient) for name, bundle in self.bundles.items()
        }
        probability = float(np.mean(list(dataset_probabilities.values())))
        score = round(probability * 100, 1)
        return {
            "HeartRiskScore": score,
            "DiseaseProbability": round(probability, 4),
            "HeartStateProbability": round(probability, 4),
            "RiskCategory": risk_category(score),
            "DatasetProbabilities": {k: round(v, 4) for k, v in dataset_probabilities.items()},
            "TopContributingFactors": heuristic_contributing_factors(patient),
        }


def risk_category(score: float) -> str:
    if score >= 70:
        return "High"
    if score >= 40:
        return "Moderate"
    return "Low"


def heuristic_contributing_factors(patient: dict) -> list[str]:
    """Human-readable factors for API output when SHAP values are unavailable at inference."""

    factors: list[str] = []
    systolic = patient.get("systolic_bp", patient.get("ap_hi", patient.get("sysBP", patient.get("trestbps"))))
    diastolic = patient.get("diastolic_bp", patient.get("ap_lo", patient.get("diaBP")))
    cholesterol = patient.get("cholesterol", patient.get("totChol", patient.get("chol")))
    smoker = patient.get("smoker", patient.get("smoke", patient.get("currentSmoker")))
    active = patient.get("physically_active", patient.get("active"))
    glucose = patient.get("glucose", patient.get("gluc"))
    bmi = patient.get("BMI")

    try:
        if systolic is not None and float(systolic) >= 140:
            factors.append("High systolic BP")
        if diastolic is not None and float(diastolic) >= 90:
            factors.append("High diastolic BP")
        if cholesterol is not None and float(cholesterol) >= 240:
            factors.append("High cholesterol")
        if smoker is not None and int(float(smoker)) == 1:
            factors.append("Smoking")
        if active is not None and int(float(active)) == 0:
            factors.append("Low physical activity")
        if glucose is not None and float(glucose) >= 126:
            factors.append("High glucose")
        if bmi is not None and float(bmi) >= 30:
            factors.append("High BMI")
    except Exception:
        pass

    return factors or ["No dominant manual risk factors detected"]


def build_voting_classifier(top_estimators: list[tuple[str, Any]]) -> VotingClassifier | None:
    """Create a soft-voting model from fitted compatible pipelines."""

    if len(top_estimators) < 2:
        return None
    return VotingClassifier(estimators=top_estimators, voting="soft", n_jobs=-1)

