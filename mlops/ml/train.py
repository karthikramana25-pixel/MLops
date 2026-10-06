"""Train and persist a reproducible Iris classifier."""

import argparse
from pathlib import Path

import joblib
from sklearn.datasets import load_iris
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

DEFAULT_MODEL_PATH = Path(__file__).resolve().parents[1] / "models" / "iris_pipeline.joblib"
RANDOM_STATE = 42


def build_pipeline():
    return make_pipeline(StandardScaler(), LogisticRegression(max_iter=500, random_state=RANDOM_STATE))


def train(model_path: Path = DEFAULT_MODEL_PATH) -> Path:
    dataset = load_iris()
    x_train, _, y_train, _ = train_test_split(
        dataset.data, dataset.target, test_size=0.2, random_state=RANDOM_STATE, stratify=dataset.target
    )
    pipeline = build_pipeline().fit(x_train, y_train)
    artifact = {"pipeline": pipeline, "class_names": dataset.target_names.tolist(), "features": dataset.feature_names}
    model_path = Path(model_path)
    model_path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(artifact, model_path)
    return model_path


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model-path", type=Path, default=DEFAULT_MODEL_PATH)
    args = parser.parse_args()
    print(f"Saved trained model to {train(args.model_path)}")


if __name__ == "__main__":
    main()
