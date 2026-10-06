"""Model loading and prediction helpers."""

from functools import lru_cache
from pathlib import Path

import joblib
import numpy as np

MODEL_PATH = Path(__file__).resolve().parents[1] / "models" / "iris_pipeline.joblib"
CLASS_NAMES = ("setosa", "versicolor", "virginica")


@lru_cache(maxsize=1)
def load_model(model_path: str = str(MODEL_PATH)):
    """Load the trained pipeline, caching it for the lifetime of the process."""
    path = Path(model_path)
    if not path.is_file():
        raise FileNotFoundError(f"Trained model not found at {path}; run `python -m ml.train` first.")
    artifact = joblib.load(path)
    if "pipeline" not in artifact or tuple(artifact.get("class_names", ())) != CLASS_NAMES:
        raise ValueError(f"Model artifact at {path} has an unsupported format.")
    return artifact["pipeline"]


def predict(features: list[float], model_path: str = str(MODEL_PATH)) -> dict:
    """Return class and class probabilities for one flower."""
    pipeline = load_model(model_path)
    values = np.asarray(features, dtype=float).reshape(1, -1)
    class_id = int(pipeline.predict(values)[0])
    probabilities = pipeline.predict_proba(values)[0]
    return {
        "class_id": class_id,
        "class_name": CLASS_NAMES[class_id],
        "probabilities": {name: float(probability) for name, probability in zip(CLASS_NAMES, probabilities)},
    }
