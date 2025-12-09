from pathlib import Path
import sys
import os
import uvicorn
import warnings
import tensorflow as tf
import pickle
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from get_metrics import getMetricsByCategory
from schemas import PredictionInfo, PredictRequest, PredictResponse
from tensorflow.keras.preprocessing.sequence import pad_sequences

# Réduire la verbosité de TensorFlow AVANT l'import
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'  # 0=all, 1=info, 2=warning, 3=error
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'  # Désactiver les messages oneDNN
# Ajouter le répertoire courant au path pour les imports AVANT tous les autres imports
sys.path.insert(0, str(Path(__file__).parent))
# --- Chargement du modèle LSTM et du tokenizer ---
warnings.filterwarnings('ignore', category=UserWarning)  # Ignorer les warnings compilation metrics

# Chemins
MODEL_LSTM_PATH = Path(__file__).parent / "model/lstm2/lstm-titles-budgets-participatif.h5"
TOKENIZER_PATH = Path(__file__).parent / "model/lstm2/lstm_titles_tokenizer.pickle"
LABEL_MAPPING_PATH = Path(__file__).parent / "model/lstm2/lstm_titles_label_mapping.json"
MAX_LEN_LSTM = 51  # Doit correspondre à l'entraînement

app = FastAPI()
# Configuration CORS pour permettre les requêtes du frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Autorise toutes les origines en développement
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Chargement au démarrage du modèle (prédire), du tokenizer (encoder) et du json (décodage prédiction)
lstm_model = tf.keras.models.load_model(MODEL_LSTM_PATH)
with open(TOKENIZER_PATH, "rb") as f:
    tokenizer_lstm = pickle.load(f)
import json
with open(LABEL_MAPPING_PATH, "r", encoding="utf-8") as f:
    label_mapping = json.load(f)["num_to_label"]

@app.get("/")
def read_main_stats():
    return {"Hello": "World"}

@app.post("/predict-category", response_model=PredictResponse)
def predict_category_lstm(request: PredictRequest) -> PredictResponse:
    project_title = request.projectTitle
    estimated_budget = request.estimatedBudget
    # Prétraitement du texte (tokenization + padding)
    seq = tokenizer_lstm.texts_to_sequences([project_title])
    pad = pad_sequences(seq, maxlen=MAX_LEN_LSTM, padding='post')
    # Prédiction
    proba = lstm_model.predict(pad)[0]
    idx = int(proba.argmax())
    confidence = float(proba[idx])
    predicted_category = label_mapping.get(str(idx), "Inconnu")
    analyse = f"Prédiction LSTM : {predicted_category} (confiance {confidence:.2f})"

    prediction_info = PredictionInfo(
        name=predicted_category,
        confidence=confidence,
        analyse=analyse
    )
    metrics_data = getMetricsByCategory(prediction_info, project_title, estimated_budget)
    
    return PredictResponse(**metrics_data)

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)