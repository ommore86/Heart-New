"""Train independent heart-state models and a cross-dataset ensemble."""

from __future__ import annotations

import argparse
import json
import logging
from pathlib import Path

import pandas as pd
from sklearn.model_selection import GridSearchCV, StratifiedKFold, cross_val_score, train_test_split

from .config import CV_FOLDS, DATASET_SPECS, MODEL_DIR, PLOT_DIR, RANDOM_STATE, TEST_SIZE, ensure_directories
from .evaluate import (
    evaluate_classifier,
    generate_shap_plots,
    plot_class_distribution,
    plot_correlation_heatmap,
    plot_feature_importance,
    plot_learning_curve,
    plot_missing_values,
    plot_model_curves,
)
from .modeling import DatasetModelBundle, HeartDigitalTwinEnsemble, get_model_grids, make_pipeline
from .preprocessing import load_dataset, make_preprocessor, prepare_dataset, report_dataset
from .utils import save_joblib, setup_logging

LOGGER = logging.getLogger(__name__)


def train_dataset(
    spec_name: str,
    data_dir: Path,
    fast: bool = False,
    sample_size: int | None = None,
    save_artifacts: bool = True,
) -> DatasetModelBundle:
    spec = DATASET_SPECS[spec_name]
    raw = load_dataset(spec, data_dir)
    report_dataset(raw, spec.target, spec.name)
    if save_artifacts:
        plot_missing_values(raw, spec.name, PLOT_DIR)

    x, y = prepare_dataset(raw, spec)
    if sample_size and len(x) > sample_size:
        sampled = x.assign(__target=y).groupby("__target", group_keys=False).sample(
            n=max(1, sample_size // max(y.nunique(), 1)),
            random_state=RANDOM_STATE,
            replace=False,
        )
        y = sampled.pop("__target").astype(int)
        x = sampled

    LOGGER.info("[%s] cleaned feature shape: %s", spec.name, x.shape)
    LOGGER.info("[%s] cleaned class distribution:\n%s", spec.name, y.value_counts(normalize=False))

    if save_artifacts:
        plot_class_distribution(y, spec.name, PLOT_DIR)
        plot_correlation_heatmap(x, spec.name, PLOT_DIR)

    x_train, x_test, y_train, y_test = train_test_split(
        x,
        y,
        test_size=TEST_SIZE,
        random_state=RANDOM_STATE,
        stratify=y,
    )
    cv = StratifiedKFold(n_splits=CV_FOLDS, shuffle=True, random_state=RANDOM_STATE)
    preprocessor = make_preprocessor(x_train)

    results: dict[str, dict] = {}
    fitted_models = []
    grids = get_model_grids(random_state=RANDOM_STATE, fast=fast)

    for model_name, (classifier, grid) in grids.items():
        LOGGER.info("[%s] tuning %s", spec.name, model_name)
        pipeline = make_pipeline(preprocessor, classifier)
        search = GridSearchCV(
            pipeline,
            param_grid=grid,
            scoring="roc_auc",
            cv=cv,
            n_jobs=-1,
            refit=True,
            error_score="raise",
        )
        try:
            search.fit(x_train, y_train)
            cv_scores = cross_val_score(search.best_estimator_, x_train, y_train, cv=cv, scoring="roc_auc", n_jobs=-1)
            metrics = evaluate_classifier(search.best_estimator_, x_test, y_test)
            results[model_name] = {
                "best_params": search.best_params_,
                "best_cv_roc_auc": float(search.best_score_),
                "cv_scores": [float(score) for score in cv_scores],
                "test_metrics": metrics,
            }
            fitted_models.append((model_name, search.best_estimator_, metrics["roc_auc"]))
            LOGGER.info("[%s] %s test ROC-AUC: %.4f", spec.name, model_name, metrics["roc_auc"])
        except Exception as exc:
            LOGGER.exception("[%s] %s failed and will be skipped: %s", spec.name, model_name, exc)

    if not fitted_models:
        raise RuntimeError(f"No models trained successfully for {spec.name}")

    best_name, best_model, best_auc = max(fitted_models, key=lambda item: item[2])
    LOGGER.info("[%s] best model: %s (ROC-AUC %.4f)", spec.name, best_name, best_auc)

    bundle = DatasetModelBundle(
        dataset_name=spec.name,
        model=best_model,
        feature_columns=x.columns.tolist(),
        roc_auc=best_auc,
        model_name=best_name,
    )
    if save_artifacts:
        plot_model_curves(best_model, x_test, y_test, spec.name, PLOT_DIR)
        importance = plot_feature_importance(best_model, spec.name, PLOT_DIR)
        plot_learning_curve(best_model, x_train, y_train, spec.name, PLOT_DIR)
        generate_shap_plots(best_model, x_train, x_test, spec.name, PLOT_DIR)

        output = {
            "dataset": spec.name,
            "best_model": best_name,
            "results": results,
            "feature_importance": importance.to_dict(orient="records"),
        }
        save_joblib(output, MODEL_DIR / f"{spec.name}_training_report.pkl")
        (PLOT_DIR / spec.name).mkdir(parents=True, exist_ok=True)
        (PLOT_DIR / spec.name / "metrics.json").write_text(json.dumps(output, indent=2, default=str), encoding="utf-8")

        model_filename = {
            "cardio": "cardio_model.pkl",
            "framingham": "framingham_model.pkl",
            "uci": "uci_model.pkl",
        }[spec.name]
        save_joblib(bundle, MODEL_DIR / model_filename)
    return bundle


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", type=Path, default=Path(__file__).resolve().parents[1] / "data")
    parser.add_argument("--datasets", nargs="+", choices=DATASET_SPECS.keys(), default=list(DATASET_SPECS.keys()))
    parser.add_argument("--fast", action="store_true", help="Use smaller grids for quick iteration.")
    parser.add_argument("--sample-size", type=int, default=None, help="Optional per-dataset sample cap for smoke tests.")
    parser.add_argument("--no-artifacts", action="store_true", help="Train/evaluate without writing plots or model files.")
    return parser.parse_args()


def main() -> None:
    setup_logging()
    ensure_directories()
    args = parse_args()
    bundles = {}
    for spec_name in args.datasets:
        bundles[spec_name] = train_dataset(
            spec_name,
            args.data_dir,
            fast=args.fast,
            sample_size=args.sample_size,
            save_artifacts=not args.no_artifacts,
        )

    if bundles and not args.no_artifacts:
        ensemble = HeartDigitalTwinEnsemble(bundles=bundles)
        save_joblib(ensemble, MODEL_DIR / "ensemble_model.pkl")
        save_joblib({name: bundle.model.named_steps["preprocessor"] for name, bundle in bundles.items()}, MODEL_DIR / "scaler.pkl")
        save_joblib({name: bundle.feature_columns for name, bundle in bundles.items()}, MODEL_DIR / "feature_columns.pkl")
        LOGGER.info("Saved ensemble and artifact metadata to %s", MODEL_DIR)


if __name__ == "__main__":
    main()
