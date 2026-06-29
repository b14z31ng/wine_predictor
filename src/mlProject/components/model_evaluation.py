import os
from pathlib import Path
from urllib.parse import urlparse

import joblib
import mlflow
import mlflow.sklearn
import numpy as np
import pandas as pd
from mlflow.models import infer_signature
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

from mlProject.entity.config_entity import ModelEvaluationConfig
from mlProject.utils.common import save_json


class ModelEvaluation:
    def __init__(self, config: ModelEvaluationConfig):
        self.config = config

    def eval_metrics(self, actual, pred):
        rmse = np.sqrt(mean_squared_error(actual, pred))
        mae = mean_absolute_error(actual, pred)
        r2 = r2_score(actual, pred)

        return rmse, mae, r2

    def log_into_mlflow(self):

        # ----------------------------
        # Load test data and model
        # ----------------------------
        test_data = pd.read_csv(self.config.test_data_path)
        model = joblib.load(self.config.model_path)

        test_x = test_data.drop(
            [self.config.target_column],
            axis=1
        )

        test_y = test_data[self.config.target_column]

        # ----------------------------
        # Configure MLflow
        # ----------------------------
        mlflow.set_registry_uri(self.config.mlflow_uri)

        tracking_url_type_store = urlparse(
            mlflow.get_tracking_uri()
        ).scheme

        # Enable system metrics (MLflow 3.x)
        mlflow.enable_system_metrics_logging()

        with mlflow.start_run():

            # ----------------------------
            # Prediction
            # ----------------------------
            predicted = model.predict(test_x)

            rmse, mae, r2 = self.eval_metrics(
                test_y,
                predicted
            )

            # ----------------------------
            # Save metrics locally
            # ----------------------------
            scores = {
                "rmse": rmse,
                "mae": mae,
                "r2": r2,
            }

            save_json(
                path=Path(self.config.metric_file_name),
                data=scores,
            )

            # ----------------------------
            # Log Parameters
            # ----------------------------
            mlflow.log_params(self.config.all_params)

            mlflow.log_param(
                "test_rows",
                test_x.shape[0]
            )

            mlflow.log_param(
                "num_features",
                test_x.shape[1]
            )

            mlflow.log_param(
                "model_type",
                type(model).__name__
            )

            # ----------------------------
            # Log Metrics
            # ----------------------------
            mlflow.log_metrics(
                {
                    "rmse": rmse,
                    "mae": mae,
                    "r2": r2,
                }
            )

            # ----------------------------
            # Log Config Files
            # ----------------------------
            if os.path.exists("config/config.yaml"):
                mlflow.log_artifact("config/config.yaml")

            if os.path.exists("params.yaml"):
                mlflow.log_artifact("params.yaml")

            if os.path.exists("schema.yaml"):
                mlflow.log_artifact("schema.yaml")

            # ----------------------------
            # Set Tags
            # ----------------------------
            mlflow.set_tags(
                {
                    "framework": "Scikit-Learn",
                    "tracking": "DagsHub",
                    "python": "3.11",
                    "author": "Reshad",
                }
            )

            # ----------------------------
            # Model Signature
            # ----------------------------
            signature = infer_signature(
                test_x,
                predicted,
            )

            # ----------------------------
            # Log Model
            # ----------------------------
            if tracking_url_type_store != "file":

                mlflow.sklearn.log_model(
                    sk_model=model,
                    name="model",
                    signature=signature,
                    input_example=test_x.iloc[:5],
                )

            else:

                mlflow.sklearn.log_model(
                    sk_model=model,
                    name="model",
                    signature=signature,
                    input_example=test_x.iloc[:5],
                )