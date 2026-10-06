"""Evaluate the training workflow's held-out Iris split."""

import argparse
from pathlib import Path

from sklearn.datasets import load_iris
from sklearn.metrics import accuracy_score, classification_report
from sklearn.model_selection import train_test_split

from ml.train import DEFAULT_MODEL_PATH, RANDOM_STATE
from app.model import load_model


def evaluate(model_path: Path = DEFAULT_MODEL_PATH) -> dict:
    dataset = load_iris()
    _, x_test, _, y_test = train_test_split(
        dataset.data, dataset.target, test_size=0.2, random_state=RANDOM_STATE, stratify=dataset.target
    )
    model = load_model(str(Path(model_path).resolve()))
    predictions = model.predict(x_test)
    return {
        "accuracy": float(accuracy_score(y_test, predictions)),
        "classification_report": classification_report(y_test, predictions, target_names=dataset.target_names),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model-path", type=Path, default=DEFAULT_MODEL_PATH)
    result = evaluate(parser.parse_args().model_path)
    print(f"Accuracy: {result['accuracy']:.3f}")
    print(result["classification_report"])


if __name__ == "__main__":
    main()
