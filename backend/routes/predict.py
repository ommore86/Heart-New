"""POST /predict — Heart risk prediction endpoint."""

from __future__ import annotations

import logging

from fastapi import APIRouter, HTTPException

from backend.model_loader import model_service
from backend.schemas import FeatureContribution, PatientInput, PredictResponse
from backend.shap_explainer import compute_ensemble_contributions

LOGGER = logging.getLogger(__name__)
router = APIRouter(tags=["Prediction"])


@router.post("/predict", response_model=PredictResponse, summary="Predict heart disease risk")
async def predict(patient: PatientInput) -> PredictResponse:
    """
    Run the Heart Digital Twin ensemble on patient vitals.

    Returns:
    - **HeartRiskScore**: 0–100 composite risk score
    - **RiskCategory**: Low / Moderate / High
    - **DatasetProbabilities**: per-dataset model outputs (cardio, framingham, uci)
    - **TopContributingFactors**: SHAP-based feature attributions (or heuristic fallback)
    - **DiseaseProbability**: raw mean probability (0–1)
    """
    if not model_service.is_loaded:
        raise HTTPException(status_code=503, detail="Model not yet loaded. Try again in a moment.")

    patient_dict = patient.to_patient_dict()

    try:
        raw = model_service.predict(patient_dict)
    except Exception as exc:
        LOGGER.exception("Prediction error")
        raise HTTPException(status_code=500, detail=f"Prediction failed: {exc}") from exc

    # Enrich with SHAP / heuristic contributions
    try:
        contributions = compute_ensemble_contributions(
            model_service.ensemble, patient_dict, top_n=8
        )
    except Exception as exc:
        LOGGER.warning("SHAP contribution computation failed: %s", exc)
        # Fall back to heuristic strings from the raw result
        contributions = [
            FeatureContribution(
                feature=factor,
                contribution=0.10,
                direction="positive",
                display_value=factor,
            )
            for factor in raw.get("TopContributingFactors", [])
        ]

    return PredictResponse(
        HeartRiskScore=raw["HeartRiskScore"],
        RiskCategory=raw["RiskCategory"],
        DatasetProbabilities=raw["DatasetProbabilities"],
        TopContributingFactors=contributions,
        DiseaseProbability=raw["DiseaseProbability"],
    )
