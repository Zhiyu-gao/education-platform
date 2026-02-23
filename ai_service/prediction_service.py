import io
import logging
import os
import sys
from pathlib import Path
from typing import Any, Dict

import joblib
import numpy as np
import pandas as pd
import tensorflow as tf
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler

os.environ.setdefault("TF_USE_LEGACY_KERAS", "False")
os.environ.setdefault("TF_CPP_MIN_LOG_LEVEL", "2")
sys.setrecursionlimit(5000)

LOGGER = logging.getLogger(__name__)
BASE_DIR = Path(__file__).resolve().parent
MODEL_DIR = BASE_DIR / "models"


class PredictionService:
    MODEL_PATH = str(MODEL_DIR / "student_performance_model.keras")
    SCALER_PATH = str(MODEL_DIR / "scaler.save")
    ENCODERS_PATH = str(MODEL_DIR / "encoders.save")
    FEATURE_NAMES_PATH = str(MODEL_DIR / "feature_names.save")
    TARGET_COLUMN = "Exam_Score"

    @staticmethod
    def _ensure_directory_exists(path: str) -> None:
        os.makedirs(os.path.dirname(path), exist_ok=True)

    @staticmethod
    def _error(message: str) -> Dict[str, Any]:
        return {"status": "error", "message": message}

    @staticmethod
    def _preprocess_data(df: pd.DataFrame):
        df_copy = df.copy()
        if PredictionService.TARGET_COLUMN not in df_copy.columns:
            raise ValueError(f"数据集中缺少目标列 {PredictionService.TARGET_COLUMN}")

        df_copy = df_copy.dropna()
        X = df_copy.drop(columns=[PredictionService.TARGET_COLUMN])
        y = df_copy[PredictionService.TARGET_COLUMN].values

        categorical_columns = X.select_dtypes(include=["object", "category"]).columns
        encoders: Dict[str, LabelEncoder] = {}
        for col in categorical_columns:
            encoder = LabelEncoder()
            X[col] = encoder.fit_transform(X[col])
            encoders[col] = encoder

        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        return X_scaled, y, X.columns, scaler, encoders

    @staticmethod
    def _build_model(input_dim: int) -> tf.keras.Model:
        model = tf.keras.Sequential(
            [
                tf.keras.layers.Dense(64, activation="relu", input_shape=(input_dim,)),
                tf.keras.layers.Dense(32, activation="relu"),
                tf.keras.layers.Dense(16, activation="relu"),
                tf.keras.layers.Dense(1),
            ]
        )
        model.compile(
            optimizer=tf.keras.optimizers.Adam(learning_rate=0.001),
            loss="mse",
            metrics=["mae"],
        )
        return model

    @staticmethod
    def _load_train_dataframe(file_or_path: Any) -> pd.DataFrame:
        if isinstance(file_or_path, str):
            df = pd.read_csv(file_or_path)
            LOGGER.info("从路径读取训练数据，行数=%s", len(df))
            return df

        if hasattr(file_or_path, "seek"):
            file_or_path.seek(0)
        content = file_or_path.read()
        if isinstance(content, bytes):
            content = content.decode("utf-8")
        df = pd.read_csv(io.StringIO(content))
        LOGGER.info("从上传文件读取训练数据，行数=%s", len(df))
        return df

    @staticmethod
    def train_model_from_csv(file_or_path):
        try:
            PredictionService._ensure_directory_exists(PredictionService.MODEL_PATH)
            df = PredictionService._load_train_dataframe(file_or_path)

            X_scaled, y, feature_names, scaler, encoders = PredictionService._preprocess_data(df)
            LOGGER.info("数据预处理完成，特征维度=%s", X_scaled.shape)

            X_train, X_test, y_train, y_test = train_test_split(
                X_scaled,
                y,
                test_size=0.2,
                random_state=42,
            )

            model = PredictionService._build_model(X_scaled.shape[1])
            model.fit(
                X_train,
                y_train,
                epochs=100,
                batch_size=32,
                validation_split=0.2,
                verbose=1,
                callbacks=[
                    tf.keras.callbacks.EarlyStopping(
                        monitor="val_loss",
                        patience=10,
                        restore_best_weights=True,
                    ),
                    tf.keras.callbacks.ReduceLROnPlateau(
                        monitor="val_loss",
                        factor=0.5,
                        patience=5,
                    ),
                ],
            )

            test_loss, test_mae = model.evaluate(X_test, y_test, verbose=1)
            LOGGER.info("模型评估完成，loss=%.4f, mae=%.4f", test_loss, test_mae)

            model.save(PredictionService.MODEL_PATH)
            joblib.dump(scaler, PredictionService.SCALER_PATH)
            joblib.dump(encoders, PredictionService.ENCODERS_PATH)
            joblib.dump(list(feature_names), PredictionService.FEATURE_NAMES_PATH)

            return {
                "status": "success",
                "message": "模型训练完成",
                "test_mae": float(test_mae),
                "test_loss": float(test_loss),
                "feature_count": int(len(feature_names)),
                "feature_names": list(feature_names),
            }
        except Exception as e:
            LOGGER.exception("训练模型失败")
            return PredictionService._error(f"训练模型时出错: {str(e)}")

    @staticmethod
    def predict_student_score(input_data):
        try:
            if not os.path.exists(PredictionService.MODEL_PATH):
                return PredictionService._error("模型不存在，请先训练模型")

            model = tf.keras.models.load_model(PredictionService.MODEL_PATH)
            scaler = joblib.load(PredictionService.SCALER_PATH)
            encoders = joblib.load(PredictionService.ENCODERS_PATH)
            feature_names = joblib.load(PredictionService.FEATURE_NAMES_PATH)

            df_input = pd.DataFrame([input_data])
            for col in feature_names:
                if col not in df_input.columns:
                    df_input[col] = np.nan

            for col, encoder in encoders.items():
                if col not in df_input.columns:
                    df_input[col] = encoder.classes_[0]
                df_input[col] = df_input[col].fillna(encoder.classes_[0])
                df_input[col] = df_input[col].map(lambda x: x if x in encoder.classes_ else encoder.classes_[0])
                df_input[col] = encoder.transform(df_input[col])

            for col in feature_names:
                if col not in encoders:
                    df_input[col] = pd.to_numeric(df_input[col], errors="coerce").fillna(0.0)

            df_input = df_input[feature_names]
            input_scaled = scaler.transform(df_input)
            prediction = model.predict(input_scaled)[0][0]
            prediction_float = float(prediction)

            return {
                "status": "success",
                "predicted_score": round(prediction_float, 2),
                "message": "预测成功",
            }
        except Exception as e:
            LOGGER.exception("预测失败")
            return PredictionService._error(f"预测时出错: {str(e)}")

    @staticmethod
    def get_model_info():
        try:
            if not os.path.exists(PredictionService.MODEL_PATH):
                return PredictionService._error("模型不存在")

            model = tf.keras.models.load_model(PredictionService.MODEL_PATH)
            encoders = joblib.load(PredictionService.ENCODERS_PATH)

            layers = [
                {
                    "name": layer.name,
                    "units": layer.units if hasattr(layer, "units") else None,
                    "activation": layer.activation.__name__ if hasattr(layer, "activation") else None,
                }
                for layer in model.layers
            ]

            return {
                "status": "success",
                "model_info": {
                    "layers": layers,
                    "categorical_features": list(encoders.keys()),
                    "input_dim": model.input_shape[1],
                },
            }
        except Exception as e:
            LOGGER.exception("获取模型信息失败")
            return PredictionService._error(f"获取模型信息时出错: {str(e)}")
