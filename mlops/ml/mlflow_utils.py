"""Shared MLflow configuration for local and remote experiment tracking."""

import os
from pathlib import Path

import mlflow

DEFAULT_EXPERIMENT_NAME = "mlops-iris-classifier"
DEFAULT_TRACKING_DB = Path(__file__).resolve().parents[1] / "mlflow.db"
DEFAULT_TRACKING_URI = f"sqlite:///{DEFAULT_TRACKING_DB.as_posix()}"


def configure_tracking(tracking_uri: str | None = None) -> str:
    """Configure MLflow from an argument, environment variable, or local store."""
    uri = tracking_uri or os.getenv("MLFLOW_TRACKING_URI") or DEFAULT_TRACKING_URI
    mlflow.set_tracking_uri(uri)
    if mlflow.get_experiment_by_name(DEFAULT_EXPERIMENT_NAME) is None:
        mlflow.create_experiment(DEFAULT_EXPERIMENT_NAME)
    mlflow.set_experiment(DEFAULT_EXPERIMENT_NAME)
    return uri
