# Iris MLOps Learning Project

A small, reproducible scikit-learn classification project served through FastAPI. It uses scikit-learn's built-in Iris dataset, so training requires no dataset download. The first phase keeps the focus on model training, evaluation, API behavior, tests, and containerization.

## Project layout

```text
app/       FastAPI application, request schemas, model loading
ml/        Reproducible training and held-out evaluation
models/    Locally generated model artifact (ignored by Git)
data/      Reserved for later data workflow exercises
tests/     API and model unit tests
```

## Python setup

Use Python 3.11 or newer. From this directory, create and activate a virtual environment:

```bash
python -m venv .venv
# Windows PowerShell
.venv\Scripts\Activate.ps1
# macOS/Linux: source .venv/bin/activate
```

## Install dependencies

Install runtime dependencies to train and serve the model:

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Install test tools for local development and testing:

```bash
python -m pip install -r requirements-dev.txt
```

To recreate the exact package versions resolved in the working Python 3.13.14 environment, install the lock file in a clean virtual environment instead:

```bash
python -m pip install -r requirements-lock.txt
```

The lock file captures this Python 3.13 environment; `requirements.txt` remains the cross-version runtime dependency specification.

## Train and evaluate

Training uses a stratified split and fixed random seed, then writes `models/iris_pipeline.joblib`:

```bash
python -m ml.train
```

Evaluate the saved model on the same reproducible held-out split:

```bash
python -m ml.evaluate
```

## Run the API locally

Train the model first, then start the development server:

```bash
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

`GET /health` reports whether the trained model is available. `POST /predict` accepts four positive Iris measurements in centimetres and returns a class plus probabilities. The interactive API documentation is at `http://127.0.0.1:8000/docs`.

## Model artifact security

Model files are loaded with `joblib`, which deserializes pickle-based data and can execute code while loading an artifact. Only load model files from trusted, verified sources, such as an artifact produced by this project's training code. Do not download or load models from arbitrary URLs; this application does not fetch model files from URLs.

Example request from Bash (macOS/Linux/Git Bash):

```bash
curl -X POST http://127.0.0.1:8000/predict \
  -H "Content-Type: application/json" \
  -d '{"sepal_length":5.1,"sepal_width":3.5,"petal_length":1.4,"petal_width":0.2}'
```

From Windows PowerShell:

```powershell
Invoke-RestMethod -Method Post -Uri 'http://127.0.0.1:8000/predict' -ContentType 'application/json' -Body '{"sepal_length":5.1,"sepal_width":3.5,"petal_length":1.4,"petal_width":0.2}'
```

## Run tests

Run the complete local test suite from this directory:

```bash
python -m pytest -q
```

## Build the Docker image

The image trains its lightweight model during the build, checks API/model readiness, and runs as a non-root user. From this directory:

```bash
docker build -t iris-mlops:local .
```

## Run the Docker container

```bash
docker run --rm -p 8000:8000 iris-mlops:local
```

## Test the API

With the local server or container running, check readiness and make a prediction:

```bash
curl http://127.0.0.1:8000/health
curl -X POST http://127.0.0.1:8000/predict \
  -H "Content-Type: application/json" \
  -d '{"sepal_length":5.1,"sepal_width":3.5,"petal_length":1.4,"petal_width":0.2}'
```

In Windows PowerShell, check readiness and make a prediction with:

```powershell
Invoke-RestMethod -Method Get -Uri 'http://127.0.0.1:8000/health'
Invoke-RestMethod -Method Post -Uri 'http://127.0.0.1:8000/predict' -ContentType 'application/json' -Body '{"sepal_length":5.1,"sepal_width":3.5,"petal_length":1.4,"petal_width":0.2}'
```

No credentials or external services are required. Docker health status can be inspected with `docker ps` after the container starts.

## Before public exposure

The inference API currently has no authentication or authorization. Add and verify production authentication and authorization before exposing the API to the public internet. **TODO:** implement and configure those controls before any public deployment.

## GitHub Actions CI

The repository workflow at `../.github/workflows/ci.yml` runs on pushes to `main` and pull requests targeting `main`. It sets up Python 3.13, installs the runtime and test requirements with their exact resolved lock, runs pytest, and then builds the Docker image. A failed test stops the job before the image build. The workflow only builds locally on the GitHub-hosted runner; it does not publish an image or require repository secrets.
