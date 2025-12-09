import os
import json
import warnings

# Configuration Keras legacy pour compatibilité avec Transformers
os.environ['TF_USE_LEGACY_KERAS'] = '1'
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'
warnings.filterwarnings('ignore', category=UserWarning)

from tensorflow import keras
from transformers import CamembertTokenizer, TFCamembertModel

LABEL_MAPPING_PATH = "../model/camembert/camembert_label_mapping.json"
MODEL_PATH = "../model/camembert/model_camembert_camembert-budgets-participatif.h5"
MAX_LEN_CAMEMBERT = 128

# Charge le modèle CamemBERT, le tokenizer et le label mapping.
def load_camembert_model():
    print("🔄 Chargement du modèle CamemBERT...")
    
    # 1. Charger le label mapping
    with open(LABEL_MAPPING_PATH, "r", encoding="utf-8") as f:
        label_mapping_data = json.load(f)
        num_classes = label_mapping_data["num_classes"]
        label_mapping = label_mapping_data["num_to_label"]
    
    # 2. Charger le tokenizer CamemBERT
    tokenizer_camembert = CamembertTokenizer.from_pretrained("camembert-base")
    
    # 3. Charger le modèle complet depuis le fichier .h5
    print("📥 Chargement du modèle CamemBERT depuis le fichier sauvegardé...")
    
    camembert_model = keras.models.load_model(
        MODEL_PATH,
        custom_objects={'TFCamembertModel': TFCamembertModel},
        compile=False
    )
    print(f"✅ Modèle chargé depuis : {MODEL_PATH}")
    
    # 4. Compiler le modèle
    camembert_model.compile(
        optimizer=keras.optimizers.Adam(learning_rate=label_mapping_data.get('best_learning_rate', 1e-5)),
        loss='sparse_categorical_crossentropy',
        metrics=['accuracy']
    )
    
    print(f"✅ Modèle CamemBERT chargé avec succès !")
    print(f"   Nombre de classes : {num_classes}")
    
    return camembert_model, tokenizer_camembert, label_mapping, num_classes
