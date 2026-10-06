"""Register a tracked model and optionally promote a version by assigning an alias.

The default local SQLite backend supports the registry. Remote deployments may
use MLFLOW_TRACKING_URI to select a registry-capable tracking server.
"""

import argparse
import os

from ml.mlflow_utils import DEFAULT_EXPERIMENT_NAME, configure_tracking

DEFAULT_MODEL_NAME = "mlops-iris-classifier"


def find_model_run(client, experiment_id: str, run_id: str | None = None):
    """Return a finished run with a logged model URI, newest first by default."""
    if run_id:
        run = client.get_run(run_id)
        candidates = [run]
    else:
        candidates = client.search_runs(
            [experiment_id],
            filter_string="attributes.status = 'FINISHED'",
            order_by=["attributes.start_time DESC"],
            max_results=1000,
        )

    for run in candidates:
        model_uri = run.data.tags.get("model_uri")
        if run.info.experiment_id == experiment_id and run.info.status == "FINISHED" and model_uri:
            return run
    raise ValueError("No finished run with a logged model was found; run `python -m ml.train` first.")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tracking-uri", help="Defaults to MLFLOW_TRACKING_URI or the local SQLite store")
    parser.add_argument(
        "--model-name",
        default=os.getenv("MLFLOW_MODEL_NAME", DEFAULT_MODEL_NAME),
        help="Registered model name (default: MLFLOW_MODEL_NAME or %(default)s)",
    )
    parser.add_argument("--run-id", help="Register a specific finished run instead of the latest eligible run")
    parser.add_argument("--version", help="Existing registered version to promote; does not register a new version")
    parser.add_argument(
        "--promote-alias",
        help="Explicitly assign an alias such as staging or production to this model version",
    )
    args = parser.parse_args()
    if args.version and args.run_id:
        parser.error("--version and --run-id cannot be used together")
    if args.version and not args.promote_alias:
        parser.error("--version requires --promote-alias")

    import mlflow
    from mlflow import MlflowClient
    from mlflow.exceptions import MlflowException

    try:
        tracking_uri = configure_tracking(args.tracking_uri)
        client = MlflowClient(tracking_uri=tracking_uri)
        if args.version:
            model_version = client.get_model_version(args.model_name, args.version)
        else:
            experiment = client.get_experiment_by_name(DEFAULT_EXPERIMENT_NAME)
            run = find_model_run(client, experiment.experiment_id, args.run_id)
            model_version = mlflow.register_model(
                model_uri=run.data.tags["model_uri"],
                name=args.model_name,
            )
            client.set_model_version_tag(
                args.model_name,
                model_version.version,
                "lifecycle_status",
                "pending_review",
            )

        if args.promote_alias:
            client.set_registered_model_alias(args.model_name, args.promote_alias, str(model_version.version))
            client.set_model_version_tag(
                args.model_name,
                model_version.version,
                "lifecycle_status",
                f"alias:{args.promote_alias}",
            )
            print(f"Assigned alias '{args.promote_alias}' to {args.model_name} version {model_version.version}.")
        else:
            print(f"Registered {args.model_name} version {model_version.version} for review.")
            print("After validation, assign a lifecycle alias with --version and --promote-alias.")
        print(f"Registered model URI: models:/{args.model_name}/{model_version.version}")
    except (MlflowException, NotImplementedError) as exc:
        raise SystemExit(
            "Model registration requires a registry-capable MLflow backend. "
            "Use a database-backed backend (the default local SQLite backend supports this) "
            "and configure remote access through MLFLOW_TRACKING_URI. "
            f"MLflow detail: {exc}"
        ) from exc


if __name__ == "__main__":
    main()
