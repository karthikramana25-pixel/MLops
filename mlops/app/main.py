"""HTTP API for Iris flower classification."""

from fastapi import FastAPI, HTTPException

from app.model import MODEL_PATH, load_model, predict
from app.schemas import IrisFeatures, Prediction

# TODO(security): Add production authentication and authorization before public exposure.
app = FastAPI(title="Iris Classifier API", version="1.0.0")


@app.get("/health")
def health() -> dict[str, str | bool]:
    """Report API and model readiness."""
    try:
        load_model(str(MODEL_PATH))
        model_loaded = True
    except FileNotFoundError:
        model_loaded = False
    return {"status": "ok" if model_loaded else "model_missing", "model_loaded": model_loaded}


@app.post("/predict", response_model=Prediction)
def predict_iris(features: IrisFeatures) -> Prediction:
    """Classify one Iris flower from its four measurements."""
    values = [features.sepal_length, features.sepal_width, features.petal_length, features.petal_width]
    try:
        result = predict(values, str(MODEL_PATH))
    except FileNotFoundError as exc:
        raise HTTPException(
            status_code=503,
            detail="Trained model is unavailable; run `python -m ml.train` first.",
        ) from exc
    return Prediction(**result)
