"""Evaluation metrics, plots, and explainability utilities."""

from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import Any

os.environ.setdefault("MPLBACKEND", "Agg")
os.environ.setdefault(
    "MPLCONFIGDIR",
    str(Path(__file__).resolve().parents[1] / "outputs"),
)
Path(os.environ["MPLCONFIGDIR"]).mkdir(parents=True, exist_ok=True)

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.metrics import (
    ConfusionMatrixDisplay,
    PrecisionRecallDisplay,
    RocCurveDisplay,
    average_precision_score,
    classification_report,
    confusion_matrix,
    precision_recall_curve,
    roc_auc_score,
    roc_curve,
)
from sklearn.model_selection import LearningCurveDisplay, learning_curve

from .modeling import predict_positive_proba
from .utils import optional_import

LOGGER = logging.getLogger(__name__)


def _save_current(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    plt.tight_layout()
    plt.savefig(path, dpi=180, bbox_inches="tight")
    plt.close()


def plot_class_distribution(y: pd.Series, dataset_name: str, plot_dir: Path) -> None:
    y.value_counts().sort_index().plot(kind="bar", color=["#4c78a8", "#f58518"])
    plt.title(f"{dataset_name} class distribution")
    plt.xlabel("Class")
    plt.ylabel("Count")
    _save_current(plot_dir / dataset_name / "class_distribution.png")


def plot_missing_values(df: pd.DataFrame, dataset_name: str, plot_dir: Path) -> None:
    missing = df.isna().sum().sort_values(ascending=False)
    missing = missing[missing > 0]
    if missing.empty:
        missing = pd.Series({"No missing values": 0})
    missing.plot(kind="bar", color="#54a24b")
    plt.title(f"{dataset_name} missing values")
    plt.ylabel("Missing count")
    _save_current(plot_dir / dataset_name / "missing_values.png")


def plot_correlation_heatmap(x: pd.DataFrame, dataset_name: str, plot_dir: Path) -> None:
    corr = x.select_dtypes(include=[np.number]).corr()
    if corr.empty:
        return
    fig, ax = plt.subplots(figsize=(max(8, len(corr) * 0.55), max(6, len(corr) * 0.45)))
    im = ax.imshow(corr, cmap="coolwarm", vmin=-1, vmax=1)
    ax.set_xticks(range(len(corr.columns)), corr.columns, rotation=90)
    ax.set_yticks(range(len(corr.columns)), corr.columns)
    fig.colorbar(im, ax=ax, shrink=0.75)
    ax.set_title(f"{dataset_name} correlation heatmap")
    _save_current(plot_dir / dataset_name / "correlation_heatmap.png")


def evaluate_classifier(model: Any, x_test: pd.DataFrame, y_test: pd.Series) -> dict[str, Any]:
    proba = predict_positive_proba(model, x_test)
    pred = (proba >= 0.5).astype(int)
    return {
        "roc_auc": float(roc_auc_score(y_test, proba)),
        "average_precision": float(average_precision_score(y_test, proba)),
        "classification_report": classification_report(y_test, pred, output_dict=True),
        "confusion_matrix": confusion_matrix(y_test, pred).tolist(),
    }


def plot_model_curves(model: Any, x_test: pd.DataFrame, y_test: pd.Series, dataset_name: str, plot_dir: Path) -> None:
    proba = predict_positive_proba(model, x_test)
    fpr, tpr, _ = roc_curve(y_test, proba)
    precision, recall, _ = precision_recall_curve(y_test, proba)
    pred = (proba >= 0.5).astype(int)

    RocCurveDisplay(fpr=fpr, tpr=tpr, roc_auc=roc_auc_score(y_test, proba)).plot()
    plt.title(f"{dataset_name} ROC curve")
    _save_current(plot_dir / dataset_name / "roc_curve.png")

    PrecisionRecallDisplay(
        precision=precision,
        recall=recall,
        average_precision=average_precision_score(y_test, proba),
    ).plot()
    plt.title(f"{dataset_name} precision-recall curve")
    _save_current(plot_dir / dataset_name / "pr_curve.png")

    ConfusionMatrixDisplay.from_predictions(y_test, pred)
    plt.title(f"{dataset_name} confusion matrix")
    _save_current(plot_dir / dataset_name / "confusion_matrix.png")


def transformed_feature_names(model: Any) -> list[str]:
    preprocessor = model.named_steps.get("preprocessor")
    if preprocessor is None:
        return []
    try:
        return preprocessor.get_feature_names_out().tolist()
    except Exception:
        return []


def plot_feature_importance(model: Any, dataset_name: str, plot_dir: Path, top_n: int = 20) -> pd.DataFrame:
    classifier = model.named_steps.get("classifier") if hasattr(model, "named_steps") else None
    names = transformed_feature_names(model)
    importance = None

    if classifier is not None and hasattr(classifier, "feature_importances_"):
        importance = classifier.feature_importances_
    elif classifier is not None and hasattr(classifier, "coef_"):
        importance = np.abs(classifier.coef_).ravel()

    if importance is None or not names:
        return pd.DataFrame()

    values = pd.DataFrame({"feature": names, "importance": importance})
    values = values.sort_values("importance", ascending=False).head(top_n)
    values.iloc[::-1].plot(kind="barh", x="feature", y="importance", legend=False, color="#4c78a8")
    plt.title(f"{dataset_name} feature importance")
    plt.xlabel("Importance")
    _save_current(plot_dir / dataset_name / "feature_importance.png")
    return values


def plot_learning_curve(model: Any, x: pd.DataFrame, y: pd.Series, dataset_name: str, plot_dir: Path) -> None:
    try:
        train_sizes, train_scores, test_scores = learning_curve(
            model,
            x,
            y,
            cv=3,
            scoring="roc_auc",
            n_jobs=-1,
            train_sizes=np.linspace(0.2, 1.0, 5),
        )
        LearningCurveDisplay(train_sizes=train_sizes, train_scores=train_scores, test_scores=test_scores).plot()
        plt.title(f"{dataset_name} learning curve")
        _save_current(plot_dir / dataset_name / "learning_curve.png")
    except Exception as exc:
        LOGGER.warning("[%s] learning curve skipped: %s", dataset_name, exc)


def generate_shap_plots(model: Any, x_train: pd.DataFrame, x_test: pd.DataFrame, dataset_name: str, plot_dir: Path) -> None:
    shap = optional_import("shap")
    if shap is None:
        LOGGER.warning("[%s] SHAP is not installed; skipping SHAP plots", dataset_name)
        return

    try:
        sample_train = x_train.sample(min(len(x_train), 300), random_state=42)
        sample_test = x_test.sample(min(len(x_test), 100), random_state=42)
        transformed_train = model.named_steps["preprocessor"].transform(sample_train)
        transformed_test = model.named_steps["preprocessor"].transform(sample_test)
        feature_names = transformed_feature_names(model)
        classifier = model.named_steps["classifier"]
        explainer = shap.Explainer(classifier, transformed_train, feature_names=feature_names)
        shap_values = explainer(transformed_test)

        shap.summary_plot(shap_values, transformed_test, feature_names=feature_names, show=False)
        _save_current(plot_dir / dataset_name / "shap_summary.png")

        shap.plots.waterfall(shap_values[0], show=False)
        _save_current(plot_dir / dataset_name / "shap_waterfall.png")

        if feature_names:
            shap.dependence_plot(0, shap_values.values, transformed_test, feature_names=feature_names, show=False)
            _save_current(plot_dir / dataset_name / "shap_dependence.png")
    except Exception as exc:
        LOGGER.warning("[%s] SHAP plots skipped: %s", dataset_name, exc)
