"""
Pydantic v2 request/response schemas for the Digital Twin of the Heart API.

All fields that arrive from the frontend use friendly names (e.g. `systolic_bp`).
The model_loader maps them to whatever alias each sub-model expects internally.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field, model_validator


# ---------------------------------------------------------------------------
# Request models
# ---------------------------------------------------------------------------

class PatientInput(BaseModel):
    """Validated patient vitals and lifestyle data sent to /predict and /simulate."""

    age: float = Field(..., ge=1, le=120, description="Age in years")
    gender: int = Field(..., ge=0, le=1, description="Sex: 1=Male, 0=Female")
    systolic_bp: float = Field(..., ge=60, le=300, description="Systolic blood pressure (mmHg)")
    diastolic_bp: float = Field(..., ge=30, le=200, description="Diastolic blood pressure (mmHg)")
    cholesterol: float = Field(..., ge=100, le=600, description="Total cholesterol (mg/dL)")
    glucose: float = Field(..., ge=50, le=500, description="Fasting glucose (mg/dL)")
    smoking: int = Field(..., ge=0, le=1, description="Current smoker: 1=Yes, 0=No")
    physical_activity: int = Field(..., ge=0, le=1, description="Physically active: 1=Yes, 0=No")
    bmi: float | None = Field(default=None, ge=10, le=70, description="BMI (optional, auto-computed from height/weight)")
    height: float | None = Field(default=None, ge=100, le=250, description="Height in cm (optional)")
    weight: float | None = Field(default=None, ge=20, le=300, description="Weight in kg (optional)")
    alcohol: int = Field(default=0, ge=0, le=1, description="Alcohol use: 1=Yes, 0=No")
    heart_rate: float | None = Field(default=None, ge=30, le=250, description="Resting heart rate (bpm)")

    @model_validator(mode="after")
    def validate_bp_order(self) -> "PatientInput":
        if self.systolic_bp <= self.diastolic_bp:
            raise ValueError("systolic_bp must be greater than diastolic_bp")
        return self

    def to_patient_dict(self) -> dict[str, Any]:
        """Convert to the flat dict that HeartDigitalTwinEnsemble.predict() expects.

        IMPORTANT: We send the ORIGINAL source-dataset column names (before
        standardize_columns renames them) so the rename produces unique canonical
        names. Sending both 'ap_hi' AND 'systolic_bp' would create duplicate columns
        after renaming, breaking pandas operations.
        """
        d: dict[str, Any] = {
            # Age — canonical; cardio dataset will divide by 365 if needed
            "age": self.age,
            # Sex — use 'gender' (renamed → sex by standardize_columns)
            "gender": self.gender,
            # Systolic BP — use 'ap_hi' (renamed → systolic_bp)
            "ap_hi": self.systolic_bp,
            # Diastolic BP — use 'ap_lo' (renamed → diastolic_bp)
            "ap_lo": self.diastolic_bp,
            # Cholesterol — use 'totChol' (renamed → cholesterol)
            "totChol": self.cholesterol,
            # Glucose — use 'gluc' (renamed → glucose)
            "gluc": self.glucose,
            # Smoking — use 'smoke' (renamed → smoker)
            "smoke": self.smoking,
            # Physical activity — use 'active' (renamed → physically_active)
            "active": self.physical_activity,
            # Alcohol — use 'alco' (renamed → alcohol)
            "alco": self.alcohol,
        }
        if self.bmi is not None:
            d["BMI"] = self.bmi
        if self.height is not None:
            d["height"] = self.height
        if self.weight is not None:
            d["weight"] = self.weight
        if self.heart_rate is not None:
            d["heartRate"] = self.heart_rate
            d["thalach"] = self.heart_rate
        return d


class ScenarioDelta(BaseModel):
    """Lifestyle/clinical scenario changes for digital twin simulation."""

    systolic_bp_delta: float | None = Field(default=None, description="Change in systolic BP (e.g. -15)")
    diastolic_bp_delta: float | None = Field(default=None, description="Change in diastolic BP")
    cholesterol_delta: float | None = Field(default=None, description="Change in cholesterol (mg/dL)")
    glucose_delta: float | None = Field(default=None, description="Change in glucose (mg/dL)")
    stop_smoking: bool | None = Field(default=None, description="Set smoking to 0 if True")
    start_exercise: bool | None = Field(default=None, description="Set physical activity to 1 if True")
    bmi_delta: float | None = Field(default=None, description="Change in BMI")
    weight_delta: float | None = Field(default=None, description="Change in weight (kg)")


class SimulateRequest(BaseModel):
    patient: PatientInput
    scenario: ScenarioDelta


# ---------------------------------------------------------------------------
# Response models
# ---------------------------------------------------------------------------

class FeatureContribution(BaseModel):
    feature: str
    contribution: float
    direction: str   # "positive" (increases risk) | "negative" (reduces risk)
    display_value: str | None = None


class PredictResponse(BaseModel):
    HeartRiskScore: float
    RiskCategory: str
    DatasetProbabilities: dict[str, float]
    TopContributingFactors: list[FeatureContribution]
    DiseaseProbability: float


class SimulateResponse(BaseModel):
    before: PredictResponse
    after: PredictResponse
    improvement_percent: float
    scenario_applied: list[str]
    risk_delta: float


class HealthResponse(BaseModel):
    status: str
    model_loaded: bool
    version: str = "1.0.0"
