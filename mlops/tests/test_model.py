from app.model import CLASS_NAMES, predict
import mlflow.sklearn
from mlflow.tracking import MlflowClient

from ml.mlflow_utils import DEFAULT_EXPERIMENT_NAME
from ml.train import train


def test_training_is_reproducible_and_prediction_is_valid(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    model_path = tmp_path / "iris.joblib"
    tracking_uri = f"sqlite:///{(tmp_path / 'mlflow.db').as_posix()}"
    train(model_path, tracking_uri=tracking_uri)
    first = predict([5.1, 3.5, 1.4, 0.2], str(model_path))
    second = predict([5.1, 3.5, 1.4, 0.2], str(model_path))

    assert first == second
    assert first["class_name"] == "setosa"
    assert first["class_name"] in CLASS_NAMES
    assert abs(sum(first["probabilities"].values()) - 1.0) < 1e-6

    client = MlflowClient(tracking_uri=tracking_uri)
    experiment = client.get_experiment_by_name(DEFAULT_EXPERIMENT_NAME)
    runs = client.search_runs([experiment.experiment_id])
    assert len(runs) == 1
    run = runs[0]
    assert run.data.params["model"] == "StandardScaler+LogisticRegression"
    assert run.data.params["random_state"] == "42"
    assert run.data.metrics["accuracy"] > 0.9
    assert run.data.metrics["macro_f1"] > 0.9
    assert run.data.tags["model_uri"].startswith("models:/")
    tracked_model = mlflow.sklearn.load_model(run.data.tags["model_uri"])
    assert int(tracked_model.predict([[5.1, 3.5, 1.4, 0.2]])[0]) == 0
