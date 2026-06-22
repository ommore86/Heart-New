"""POST /simulate — Digital Twin what-if scenario simulation endpoint."""

from __future__ import annotations

import logging
from copy import deepcopy
from typing import Any

from fastapi import APIRouter, HTTPException

from backend.model_loader import model_service
from backend.routes.predict import predict as _predict_handler
from backend.schemas import (
    FeatureContribution,
    PatientInput,
    PredictResponse,
    ScenarioDelta,
    SimulateRequest,
    SimulateResponse,
)
from backend.shap_explainer import compute_ensemble_contributions

LOGGER = logging.getLogger(__name__)
router = APIRouter(tags=["Simulation"])


def _apply_scenario(patient: PatientInput, scenario: ScenarioDelta) -> PatientInput:
    """
    Apply the what-if scenario deltas to clone the patient.
    Returns a new PatientInput with the changes applied and clamped to valid ranges.
    """
    data = patient.model_dump()

    if scenario.systolic_bp_delta is not None:
        data["systolic_bp"] = max(61, min(300, data["systolic_bp"] + scenario.systolic_bp_delta))

    if scenario.diastolic_bp_delta is not None:
        data["diastolic_bp"] = max(30, min(200, data["diastolic_bp"] + scenario.diastolic_bp_delta))

    if scenario.cholesterol_delta is not None:
        data["cholesterol"] = max(100, min(600, data["cholesterol"] + scenario.cholesterol_delta))

    if scenario.glucose_delta is not None:
        data["glucose"] = max(50, min(500, data["glucose"] + scenario.glucose_delta))

    if scenario.stop_smoking:
        data["smoking"] = 0

    if scenario.start_exercise:
        data["physical_activity"] = 1

    if scenario.bmi_delta is not None and data.get("bmi") is not None:
        data["bmi"] = max(10, min(70, data["bmi"] + scenario.bmi_delta))

    if scenario.weight_delta is not None and data.get("weight") is not None:
        data["weight"] = max(20, min(300, data["weight"] + scenario.weight_delta))

    # Ensure systolic > diastolic after adjustments
    if data["systolic_bp"] <= data["diastolic_bp"]:
        data["systolic_bp"] = data["diastolic_bp"] + 10

    return PatientInput(**data)


def _scenario_description(scenario: ScenarioDelta) -> list[str]:
    """Generate human-readable descriptions of what changed."""
    desc: list[str] = []
    if scenario.systolic_bp_delta is not None:
        direction = "Reduced" if scenario.systolic_bp_delta < 0 else "Increased"
        desc.append(f"{direction} systolic BP by {abs(scenario.systolic_bp_delta):.0f} mmHg")
    if scenario.diastolic_bp_delta is not None:
        direction = "Reduced" if scenario.diastolic_bp_delta < 0 else "Increased"
        desc.append(f"{direction} diastolic BP by {abs(scenario.diastolic_bp_delta):.0f} mmHg")
    if scenario.cholesterol_delta is not None:
        direction = "Reduced" if scenario.cholesterol_delta < 0 else "Increased"
        desc.append(f"{direction} cholesterol by {abs(scenario.cholesterol_delta):.0f} mg/dL")
    if scenario.glucose_delta is not None:
        direction = "Reduced" if scenario.glucose_delta < 0 else "Improved"
        desc.append(f"{direction} glucose by {abs(scenario.glucose_delta):.0f} mg/dL")
    if scenario.stop_smoking:
        desc.append("Stopped smoking")
    if scenario.start_exercise:
        desc.append("Started regular physical exercise")
    if scenario.bmi_delta is not None:
        direction = "Reduced" if scenario.bmi_delta < 0 else "Increased"
        desc.append(f"{direction} BMI by {abs(scenario.bmi_delta):.1f}")
    if scenario.weight_delta is not None:
        direction = "Lost" if scenario.weight_delta < 0 else "Gained"
        desc.append(f"{direction} {abs(scenario.weight_delta):.0f} kg")
    return desc or ["No changes applied"]


async def _run_prediction(patient: PatientInput) -> PredictResponse:
    """Internal helper to get a PredictResponse for a patient."""
    if not model_service.is_loaded:
        raise HTTPException(status_code=503, detail="Model not yet loaded.")

    patient_dict = patient.to_patient_dict()
    try:
        raw = model_service.predict(patient_dict)
    except Exception as exc:
        LOGGER.exception("Simulation prediction error")
        raise HTTPException(status_code=500, detail=f"Prediction failed: {exc}") from exc

    try:
        contributions = compute_ensemble_contributions(
            model_service.ensemble, patient_dict, top_n=8
        )
    except Exception:
        contributions = []

    return PredictResponse(
        HeartRiskScore=raw["HeartRiskScore"],
        RiskCategory=raw["RiskCategory"],
        DatasetProbabilities=raw["DatasetProbabilities"],
        TopContributingFactors=contributions,
        DiseaseProbability=raw["DiseaseProbability"],
    )


@router.post("/simulate", response_model=SimulateResponse, summary="Digital Twin what-if simulation")
async def simulate(request: SimulateRequest) -> SimulateResponse:
    """
    Simulate what-if lifestyle and clinical changes on a digital twin of the patient.

    The **scenario** object accepts deltas (e.g. `systolic_bp_delta: -15`) and boolean
    toggles (e.g. `stop_smoking: true`). The endpoint returns before/after predictions
    and the percentage improvement in heart risk score.
    """
    # Run baseline prediction
    before = await _run_prediction(request.patient)

    # Apply scenario and re-predict
    modified_patient = _apply_scenario(request.patient, request.scenario)
    after = await _run_prediction(modified_patient)

    # Compute improvement
    before_score = before.HeartRiskScore
    after_score = after.HeartRiskScore
    risk_delta = round(before_score - after_score, 1)

    if before_score > 0:
        improvement_pct = round((risk_delta / before_score) * 100, 1)
    else:
        improvement_pct = 0.0

    return SimulateResponse(
        before=before,
        after=after,
        improvement_percent=improvement_pct,
        scenario_applied=_scenario_description(request.scenario),
        risk_delta=risk_delta,
    )
