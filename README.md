# Digital Twin of the Heart ML Pipeline

Production-style machine learning scaffold for:

**Digital Twin of the Heart: AI-Based Simulation for Predicting Individualized Cardiovascular Drug Response**

The pipeline trains independent heart-state models for:

- `cardio_train.csv` as a Heart Risk Predictor
- `framingham.csv` as a 10-Year Cardiovascular Risk Predictor
- `heart_disease_uci.csv` as a Clinical Heart Disease Predictor

It does not concatenate datasets. Each dataset receives its own preprocessing, feature engineering, model search, evaluation plots, explainability artifacts, and saved model bundle. A final `HeartDigitalTwinEnsemble` averages the independent disease probabilities into a generalized `HeartRiskScore`.

## Structure

```text
heart_digital_twin_project/
  data/
  models/
  plots/
  outputs/
  src/
    train.py
    predict.py
    preprocessing.py
    feature_engineering.py
    evaluate.py
    modeling.py
    utils.py
    config.py
  requirements.txt
  README.md
```

## Setup

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

Optional model libraries are imported defensively. If `xgboost`, `lightgbm`, `catboost`, or `shap` are not installed, the pipeline skips the unavailable component and continues.

## Data

Place the CSV files in `data/`:

```text
data/cardio_train.csv
data/framingham.csv
data/heart_disease_uci.csv
```

Or point training at the original folder:

```bash
python -m src.train --data-dir "C:\Users\Piyush J. Patil\Desktop\VESIT\IEEE\Heart New"
```

## Train

Full run:

```bash
python -m src.train --data-dir "C:\Users\Piyush J. Patil\Desktop\VESIT\IEEE\Heart New"
```

Quick smoke-test run:

```bash
python -m src.train --data-dir "C:\Users\Piyush J. Patil\Desktop\VESIT\IEEE\Heart New" --fast --sample-size 600
```

Smoke test without writing artifacts, useful in restricted sandboxes:

```bash
python -m src.train --data-dir "C:\Users\Piyush J. Patil\Desktop\VESIT\IEEE\Heart New" --datasets cardio --fast --sample-size 200 --no-artifacts
```

The training script prints:

- shape
- `head()`
- `describe()`
- `info()`
- missing values
- class distribution

It then removes duplicates, imputes missing values, removes impossible blood pressure values, removes IQR outliers, creates common cardiovascular features, runs 5-fold cross-validation and `GridSearchCV`, and saves artifacts.

## Saved Artifacts

```text
models/cardio_model.pkl
models/framingham_model.pkl
models/uci_model.pkl
models/ensemble_model.pkl
models/scaler.pkl
models/feature_columns.pkl
```

Plots are written under `plots/<dataset>/`, including:

- class distribution
- missing values
- correlation heatmap
- ROC curve
- precision-recall curve
- confusion matrix
- feature importance
- learning curve
- SHAP plots when available

## Predict

Use the built-in example patient:

```bash
python -m src.predict
```

Or pass a patient JSON file:

```bash
python -m src.predict --patient-json patient.json
```

Example output:

```json
{
  "HeartRiskScore": 84.3,
  "DiseaseProbability": 0.91,
  "HeartStateProbability": 0.91,
  "RiskCategory": "High",
  "DatasetProbabilities": {
    "cardio": 0.88,
    "framingham": 0.82,
    "uci": 0.94
  },
  "TopContributingFactors": [
    "High systolic BP",
    "High cholesterol",
    "Smoking",
    "Low physical activity"
  ]
}
```
