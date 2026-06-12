"""Run patient-level Heart Digital Twin risk prediction."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from .config import MODEL_DIR
from .modeling import HeartDigitalTwinEnsemble
from .utils import load_joblib, setup_logging


EXAMPLE_PATIENT = {
    "age": 58,
    "sex": 1,
    "height": 170,
    "weight": 88,
    "systolic_bp": 148,
    "diastolic_bp": 92,
    "cholesterol": 245,
    "glucose": 118,
    "smoker": 1,
    "alcohol": 0,
    "physically_active": 0,
    "heartRate": 82,
}


def load_patient(path: Path | None) -> dict[str, Any]:
    if path is None:
        return EXAMPLE_PATIENT
    return json.loads(path.read_text(encoding="utf-8"))


def predict(patient: dict[str, Any], model_path: Path = MODEL_DIR / "ensemble_model.pkl") -> dict[str, Any]:
    ensemble: HeartDigitalTwinEnsemble = load_joblib(model_path)
    return ensemble.predict(patient)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--patient-json", type=Path, default=None, help="JSON file containing one patient record.")
    parser.add_argument("--model-path", type=Path, default=MODEL_DIR / "ensemble_model.pkl")
    return parser.parse_args()


def main() -> None:
    setup_logging()
    args = parse_args()
    patient = load_patient(args.patient_json)
    print(json.dumps(predict(patient, args.model_path), indent=2))


if __name__ == "__main__":
    main()

