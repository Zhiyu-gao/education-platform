# ========== 修复0【重中之重，第一行执行】：强制重置致命环境变量，根治报错根源
import os
os.environ['TF_USE_LEGACY_KERAS'] = 'False'  # 核心！关闭旧版keras强制模式，启用内置tf.keras

# ========== 修复1：递归深度扩容，解决递归超限问题
import sys
sys.setrecursionlimit(5000)

# ========== 修复2：关闭TF日志冗余输出，可选
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

# ========== 之后再导入tensorflow，此时环境变量已生效，完美加载内置keras
import tensorflow as tf
import pandas as pd
import numpy as np

# ========== 无需再强制加载keras模块，全部删掉，避免冗余
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
import joblib

class PredictionService:
    MODEL_PATH = './models/student_performance_model.keras'
    SCALER_PATH = './models/scaler.save'
    ENCODERS_PATH = './models/encoders.save'
    FEATURE_NAMES_PATH = './models/feature_names.save'
    
    @staticmethod
    def _ensure_directory_exists(path):
        os.makedirs(os.path.dirname(path), exist_ok=True)
    
    @staticmethod
    def _preprocess_data(df):
        df_copy = df.copy()
        target_column = 'Exam_Score'
        
        if target_column not in df_copy.columns:
            raise ValueError(f"数据集中缺少目标列 {target_column}")
        
        df_copy = df_copy.dropna()
        X = df_copy.drop(columns=[target_column])
        y = df_copy[target_column].values
        
        categorical_columns = X.select_dtypes(include=['object', 'category']).columns
        encoders = {}
        
        for col in categorical_columns:
            le = LabelEncoder()
            X[col] = le.fit_transform(X[col])
            encoders[col] = le
        
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        
        return X_scaled, y, X.columns, scaler, encoders
    
    @staticmethod
    def _build_model(input_dim):
        """构建模型，写法完全不变"""
        model = tf.keras.Sequential([
            tf.keras.layers.Dense(64, activation='relu', input_shape=(input_dim,)),
            tf.keras.layers.Dense(32, activation='relu'),
            tf.keras.layers.Dense(16, activation='relu'),
            tf.keras.layers.Dense(1)
        ])
        
        model.compile(
            optimizer=tf.keras.optimizers.Adam(learning_rate=0.001),
            loss='mse',
            metrics=['mae']
        )
        
        return model
    
    @staticmethod
    def train_model_from_csv(file_or_path):
        try:
            PredictionService._ensure_directory_exists(PredictionService.MODEL_PATH)
            
            if isinstance(file_or_path, str):
                df = pd.read_csv(file_or_path)
                print(f"从路径成功读取数据，共 {len(df)} 行")
            else:
                import io
                if hasattr(file_or_path, 'seek'):
                    file_or_path.seek(0)
                content = file_or_path.read()
                if isinstance(content, bytes):
                    content = content.decode('utf-8')
                df = pd.read_csv(io.StringIO(content))
                print(f"从上传文件成功读取数据，共 {len(df)} 行")
            
            X_scaled, y, feature_names, scaler, encoders = PredictionService._preprocess_data(df)
            print(f"特征列: {feature_names}")
            print(f"数据预处理完成，特征维度: {X_scaled.shape}")
            
            X_train, X_test, y_train, y_test = train_test_split(
                X_scaled, y, test_size=0.2, random_state=42
            )
            print(f"训练集大小: {X_train.shape}, 测试集大小: {X_test.shape}")
            
            model = PredictionService._build_model(X_scaled.shape[1])
            print("模型构建完成")
            
            # 训练模型，无任何修改
            history = model.fit(
                X_train, y_train,
                epochs=100,
                batch_size=32,
                validation_split=0.2,
                verbose=1,
                callbacks=[
                    tf.keras.callbacks.EarlyStopping(monitor='val_loss', patience=10, restore_best_weights=True),
                    tf.keras.callbacks.ReduceLROnPlateau(monitor='val_loss', factor=0.5, patience=5)
                ]
            )
            
            test_loss, test_mae = model.evaluate(X_test, y_test, verbose=1)
            print(f"测试集损失: {test_loss:.4f}, 平均绝对误差: {test_mae:.4f}")
            
            # 模型保存，无任何修改
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
                "feature_names": list(feature_names)
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"训练模型时出错: {str(e)}"
            }
    
    @staticmethod
    def predict_student_score(input_data):
        try:
            if not os.path.exists(PredictionService.MODEL_PATH):
                return {
                    "status": "error",
                    "message": "模型不存在，请先训练模型"
                }
            
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
                    df_input[col] = pd.to_numeric(df_input[col], errors='coerce').fillna(0.0)

            # 严格按训练时顺序构造输入，避免StandardScaler因列顺序不一致报错
            df_input = df_input[feature_names]
            
            input_scaled = scaler.transform(df_input)
            prediction = model.predict(input_scaled)[0][0]
            prediction_float = float(prediction)
            
            return {
                "status": "success",
                "predicted_score": round(prediction_float, 2),
                "message": "预测成功"
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"预测时出错: {str(e)}"
            }
    
    @staticmethod
    def get_model_info():
        try:
            if not os.path.exists(PredictionService.MODEL_PATH):
                return {
                    "status": "error",
                    "message": "模型不存在"
                }
            
            model = tf.keras.models.load_model(PredictionService.MODEL_PATH)
            scaler = joblib.load(PredictionService.SCALER_PATH)
            encoders = joblib.load(PredictionService.ENCODERS_PATH)
            
            layers = []
            for layer in model.layers:
                layers.append({
                    "name": layer.name,
                    "units": layer.units if hasattr(layer, 'units') else None,
                    "activation": layer.activation.__name__ if hasattr(layer, 'activation') else None
                })
            
            return {
                "status": "success",
                "model_info": {
                    "layers": layers,
                    "categorical_features": list(encoders.keys()),
                    "input_dim": model.input_shape[1]
                }
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"获取模型信息时出错: {str(e)}"
            }
