from fastapi.testclient import TestClient

from app.main import app
from app.model import load_model
from ml.train import train


def test_health_reports_missing_model(tmp_path, monkeypatch):
    monkeypatch.setattr("app.main.MODEL_PATH", tmp_path / "missing.joblib")
    load_model.cache_clear()
    response = TestClient(app).get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "model_missing", "model_loaded": False}


def test_prediction_endpoint(tmp_path, monkeypatch):
    model_path = tmp_path / "iris.joblib"
    train(model_path, log_to_mlflow=False)
    monkeypatch.setattr("app.main.MODEL_PATH", model_path)
    load_model.cache_clear()
    with TestClient(app) as client:
        assert client.get("/health").json()["model_loaded"] is True
        response = client.post("/predict", json={
            "sepal_length": 5.1, "sepal_width": 3.5, "petal_length": 1.4, "petal_width": 0.2
        })
    assert response.status_code == 200
    assert response.json()["class_name"] == "setosa"
    assert set(response.json()["probabilities"]) == {"setosa", "versicolor", "virginica"}


def test_prediction_reports_missing_model_without_exposing_path(tmp_path, monkeypatch):
    monkeypatch.setattr("app.main.MODEL_PATH", tmp_path / "missing.joblib")
    load_model.cache_clear()
    response = TestClient(app).post("/predict", json={
        "sepal_length": 5.1, "sepal_width": 3.5, "petal_length": 1.4, "petal_width": 0.2
    })

    assert response.status_code == 503
    assert str(tmp_path) not in response.json()["detail"]


def test_prediction_rejects_invalid_measurements():
    response = TestClient(app).post("/predict", json={
        "sepal_length": -1, "sepal_width": 3.5, "petal_length": 1.4, "petal_width": 0.2
    })
    assert response.status_code == 422


def test_metrics_endpoint_exposes_request_count_and_latency():
    with TestClient(app) as client:
        assert client.get("/health").status_code == 200
        invalid_prediction = client.post("/predict", json={"sepal_length": -1})
        assert invalid_prediction.status_code == 422
        response = client.get("/metrics")

    assert response.status_code == 200
    assert "http_requests_total" in response.text
    assert 'method="GET",route="/health",status_code="200"' in response.text
    assert 'route="/predict",status_code="422"' in response.text
    assert "http_request_duration_seconds_bucket" in response.text
    assert 'http_request_duration_seconds_count{method="POST",route="/predict"}' in response.text
    assert 'route="/metrics"' not in response.text
