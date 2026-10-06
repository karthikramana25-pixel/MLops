"""Train and persist a reproducible Iris classifier."""

import argparse
from pathlib import Path

import joblib
from sklearn.datasets import load_iris
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, f1_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

DEFAULT_MODEL_PATH = Path(__file__).resolve().parents[1] / "models" / "iris_pipeline.joblib"
RANDOM_STATE = 42


def build_pipeline():
    return make_pipeline(StandardScaler(), LogisticRegression(max_iter=500, random_state=RANDOM_STATE))


def train(
    model_path: Path = DEFAULT_MODEL_PATH,
    tracking_uri: str | None = None,
    log_to_mlflow: bool = True,
) -> Path:
    """Train, evaluate, save locally, and track one reproducible run in MLflow."""
    dataset = load_iris()
    x_train, x_test, y_train, y_test = train_test_split(
        dataset.data, dataset.target, test_size=0.2, random_state=RANDOM_STATE, stratify=dataset.target
    )
    pipeline = build_pipeline().fit(x_train, y_train)
    artifact = {"pipeline": pipeline, "class_names": dataset.target_names.tolist(), "features": dataset.feature_names}
    model_path = Path(model_path)
    model_path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(artifact, model_path)

    predictions = pipeline.predict(x_test)
    metrics = {
        "accuracy": float(accuracy_score(y_test, predictions)),
        "macro_f1": float(f1_score(y_test, predictions, average="macro")),
    }
    if log_to_mlflow:
        import mlflow
        import mlflow.sklearn

        from ml.mlflow_utils import configure_tracking

        configure_tracking(tracking_uri)
        with mlflow.start_run() as run:
            mlflow.log_params({
                "model": "StandardScaler+LogisticRegression",
                "random_state": RANDOM_STATE,
                "test_size": 0.2,
                "max_iter": 500,
                "solver": "lbfgs",
                "training_rows": len(x_train),
                "test_rows": len(x_test),
            })
            mlflow.log_metrics(metrics)
            model_info = mlflow.sklearn.log_model(pipeline, name="iris_pipeline")
            mlflow.set_tags({
                "dataset": "sklearn_iris",
                "task": "multiclass_classification",
                "model_uri": model_info.model_uri,
            })
            print(f"MLflow run: {run.info.run_id}")
            print(f"MLflow model artifact: {model_info.model_uri}")
            print(f"Evaluation metrics: {metrics}")
    return model_path


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model-path", type=Path, default=DEFAULT_MODEL_PATH)
    parser.add_argument("--tracking-uri", help="MLflow tracking URI; defaults to MLFLOW_TRACKING_URI or local mlflow.db")
    parser.add_argument("--skip-mlflow", action="store_true", help="Save only the local model without tracking a run")
    args = parser.parse_args()
    print(f"Saved trained model to {train(args.model_path, args.tracking_uri, not args.skip_mlflow)}")


if __name__ == "__main__":
    main()
