from app.model import CLASS_NAMES, predict
from ml.train import train


def test_training_is_reproducible_and_prediction_is_valid(tmp_path):
    model_path = tmp_path / "iris.joblib"
    train(model_path)
    first = predict([5.1, 3.5, 1.4, 0.2], str(model_path))
    second = predict([5.1, 3.5, 1.4, 0.2], str(model_path))

    assert first == second
    assert first["class_name"] == "setosa"
    assert first["class_name"] in CLASS_NAMES
    assert abs(sum(first["probabilities"].values()) - 1.0) < 1e-6
