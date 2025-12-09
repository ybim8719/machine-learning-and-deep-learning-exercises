import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from get_metrics import getMetricsByCategory
from schemas import PredictionInfo, PredictRequest, PredictResponse
from load_model import load_camembert_model, MAX_LEN_CAMEMBERT

app = FastAPI()

# Configuration CORS pour permettre les requêtes du frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Autorise toutes les origines en développement
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Chargement du modèle au démarrage
camembert_model, tokenizer_camembert, label_mapping, num_classes = load_camembert_model()

@app.get("/")
def read_main_stats():
    return {"Hello": "World"}

@app.post("/predict-category", response_model=PredictResponse)
def predict_category_camembert(request: PredictRequest) -> PredictResponse:
    project_title = request.projectTitle
    estimated_budget = request.estimatedBudget
    
    # Prétraitement du texte avec le tokenizer CamemBERT
    tokens = tokenizer_camembert(
        [project_title],
        padding='max_length',
        truncation=True,
        max_length=MAX_LEN_CAMEMBERT,
        return_tensors='tf'
    )
    
    # Prédiction avec le modèle CamemBERT
    proba = camembert_model.predict(
        [tokens['input_ids'], tokens['attention_mask']],
        verbose=0
    )[0]
    
    idx = int(proba.argmax())
    confidence = float(proba[idx])
    predicted_category = label_mapping.get(str(idx), "Inconnu")
    analyse = f"Prédiction CamemBERT : {predicted_category} (confiance {confidence:.2f})"

    prediction_info = PredictionInfo(
        name=predicted_category,
        confidence=confidence,
        analyse=analyse
    )
    metrics_data = getMetricsByCategory(prediction_info, project_title, estimated_budget)
    
    return PredictResponse(**metrics_data)

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)