import numpy as np
import joblib
import os
import tensorflow as tf

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

model = tf.keras.models.load_model(
    os.path.join(BASE_DIR, "models", "pcos_dnn_model.keras"),
    compile=False
)

scaler = joblib.load(os.path.join(BASE_DIR, "models", "scaler.pkl"))

def predict_pcos(input_data):
    input_data = np.array(input_data).reshape(1, -1)

    print("Expected features:", scaler.n_features_in_)

    # Scale input
    input_data = scaler.transform(input_data)

    # Predict
    pred = model.predict(input_data)
    prob = pred[0][0]

    # 🔁 Corrected mapping
    if prob > 0.5:
        return f"Low Risk of PCOS ✅ (Prob: {prob:.2f})"
    else:
        return f"High Risk of PCOS ⚠️ (Prob: {prob:.2f})"