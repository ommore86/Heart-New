"""
Singleton model loader for the Heart Digital Twin ensemble.

Loads the trained HeartDigitalTwinEnsemble from disk once at startup
and exposes a thread-safe interface for inference.
"""

from __future__ import annotations

import logging
import sys
from pathlib import Path
from typing import Any

import joblib

# Add the project root to sys.path so `src` is importable
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Import after path is set
from src.modeling import HeartDigitalTwinEnsemble  # noqa: E402

LOGGER = logging.getLogger(__name__)

MODEL_DIR = PROJECT_ROOT / "models"


class ModelService:
    """Thread-safe singleton that holds the loaded ensemble and exposes inference."""

    _instance: "ModelService | None" = None
    _ensemble: HeartDigitalTwinEnsemble | None = None

    def __new__(cls) -> "ModelService":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    # ------------------------------------------------------------------
    # Loading
    # ------------------------------------------------------------------

    def load(self) -> None:
        """Load ensemble model from disk. Called once at app startup."""
        ensemble_path = MODEL_DIR / "ensemble_model.pkl"
        if not ensemble_path.exists():
            raise FileNotFoundError(
                f"Ensemble model not found at {ensemble_path}. "
                "Please run `python -m src.train` first."
            )
        LOGGER.info("Loading ensemble model from %s …", ensemble_path)
        self._ensemble = joblib.load(ensemble_path)
        LOGGER.info("Model loaded successfully. Bundles: %s", list(self._ensemble.bundles.keys()))

    @property
    def is_loaded(self) -> bool:
        return self._ensemble is not None

    @property
    def ensemble(self) -> HeartDigitalTwinEnsemble:
        if self._ensemble is None:
            raise RuntimeError("Model not loaded. Call ModelService.load() first.")
        return self._ensemble

    # ------------------------------------------------------------------
    # Inference
    # ------------------------------------------------------------------

    def predict(self, patient_dict: dict[str, Any]) -> dict[str, Any]:
        """Run the ensemble prediction and return the raw result dict."""
        try:
            result = self.ensemble.predict(patient_dict)
            return result
        except Exception as exc:
            LOGGER.exception("Prediction failed: %s", exc)
            raise

    def predict_with_features(self, patient_dict: dict[str, Any]) -> dict[str, Any]:
        """Predict and enrich with per-dataset raw probabilities for charting."""
        result = self.predict(patient_dict)
        return result

    # ------------------------------------------------------------------
    # Utility
    # ------------------------------------------------------------------

    def get_bundle_names(self) -> list[str]:
        return list(self.ensemble.bundles.keys())


# Module-level singleton instance
model_service = ModelService()
