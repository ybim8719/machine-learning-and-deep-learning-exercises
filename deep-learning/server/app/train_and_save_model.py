"""
Script d'entraînement et sauvegarde du modèle CamemBERT
Classification des thématiques de budgets participatifs

Ce script:
- Charge et prépare les données
- Entraîne un modèle CamemBERT en mode Fine-Tuning
- Sauvegarde le modèle et les fichiers nécessaires pour l'API
"""

import os
import json
import numpy as np
import pandas as pd
import re

# Configuration pour Keras 3 avec Transformers
os.environ['TF_USE_LEGACY_KERAS'] = '1'
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

import warnings
warnings.filterwarnings('ignore')

import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau

from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split

from transformers import CamembertTokenizer, TFCamembertModel

# Configuration
SEED = 42
LEARNING_RATE = 5e-5  # Meilleur learning rate identifié
MAX_LENGTH = 128
BATCH_SIZE = 32
EPOCHS = 10

# Reproductibilité
np.random.seed(SEED)
tf.random.set_seed(SEED)
keras.utils.set_random_seed(SEED)

print("=" * 80)
print("🚀 ENTRAÎNEMENT DU MODÈLE CAMEMBERT")
print("=" * 80)

# =============================================================================
# 1. CHARGEMENT ET PRÉPARATION DES DONNÉES
# =============================================================================

print("\n📥 Chargement du dataset...")
df = pd.read_csv('data/dataset-for-training-completed.csv')
print(f"✅ Dataset chargé : {len(df)} lignes")

# Nettoyage
print("🧹 Nettoyage des données...")
df = df.dropna()
df['Thématique'] = df['Thématique'].str.strip()
df = df[df['Thématique'].str.len() > 0]
df = df[~df['Thématique'].str.match(r'^[\W_]+$')]
print(f"✅ Après nettoyage : {len(df)} lignes")

# Prétraitement du texte
def preprocess_text(text):
    """Normalisation du texte français"""
    text = text.lower()
    text = re.sub(r"[^a-zàâäæçéèêëïîôùûüÿœ'\s]", "", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text

print("🔄 Nettoyage des titres...")
df['Titres opération et projet lauréat'] = df['Titres opération et projet lauréat'].apply(preprocess_text)
print("✅ Titres nettoyés")

# Encodage des labels
print("🔢 Encodage des thématiques...")
label_encoder = LabelEncoder()
label_encoder.fit(df['Thématique'])
y_all_encoded = label_encoder.transform(df['Thématique'])
num_classes = len(label_encoder.classes_)
print(f"✅ {num_classes} thématiques encodées")

# Séparation train/val/test
print("📊 Séparation des données...")
X_all = df['Titres opération et projet lauréat'].values
y_all = y_all_encoded

X_train_all_text, X_test_text, y_train_all, y_test = train_test_split(
    X_all, y_all, test_size=0.3, random_state=SEED, stratify=y_all
)

X_train_text, X_val_text, y_train, y_val = train_test_split(
    X_train_all_text, y_train_all, test_size=0.2, random_state=SEED, stratify=y_train_all
)

print(f"✅ Train: {len(X_train_text)} | Val: {len(X_val_text)} | Test: {len(X_test_text)}")

# =============================================================================
# 2. TOKENIZATION AVEC CAMEMBERT
# =============================================================================

print("\n📥 Chargement du tokenizer CamemBERT...")
tokenizer_camembert = CamembertTokenizer.from_pretrained("camembert-base")
print("✅ Tokenizer chargé")

def tokenize_data(texts, max_length=MAX_LENGTH):
    """Tokenize les textes avec CamemBERT"""
    return tokenizer_camembert(
        texts.tolist(),
        padding='max_length',
        truncation=True,
        max_length=max_length,
        return_tensors='tf'
    )

print("🔄 Tokenization des données...")
X_train_camembert = tokenize_data(X_train_text)
X_val_camembert = tokenize_data(X_val_text)
X_test_camembert = tokenize_data(X_test_text)
print("✅ Tokenization terminée")

# =============================================================================
# 3. CRÉATION DU MODÈLE
# =============================================================================

print("\n🔨 Création du modèle CamemBERT Fine-Tuned...")

def creer_modele_camembert_finetuned():
    """Crée un modèle CamemBERT avec fine-tuning complet"""
    
    # Charger le backbone CamemBERT
    try:
        camembert_backbone = TFCamembertModel.from_pretrained(
            "camembert-base",
            from_pt=True
        )
        camembert_backbone.trainable = True  # Fine-tuning
    except Exception:
        camembert_backbone = TFCamembertModel.from_pretrained(
            "almanach/camembert-base",
            from_pt=True
        )
        camembert_backbone.trainable = True
    
    # Architecture
    input_ids = layers.Input(shape=(MAX_LENGTH,), dtype=tf.int32, name="input_ids")
    attention_mask = layers.Input(shape=(MAX_LENGTH,), dtype=tf.int32, name="attention_mask")
    
    camembert_output = camembert_backbone(input_ids, attention_mask=attention_mask)
    cls_token = camembert_output.last_hidden_state[:, 0, :]
    
    x = layers.Dropout(0.3)(cls_token)
    x = layers.Dense(64, activation='relu')(x)
    x = layers.Dropout(0.3)(x)
    output = layers.Dense(num_classes, activation='softmax')(x)
    
    model = keras.Model(inputs=[input_ids, attention_mask], outputs=output)
    
    return model

model = creer_modele_camembert_finetuned()

# Compilation
model.compile(
    optimizer=keras.optimizers.Adam(learning_rate=LEARNING_RATE),
    loss='sparse_categorical_crossentropy',
    metrics=['accuracy']
)

print(f"✅ Modèle créé et compilé (Learning Rate: {LEARNING_RATE})")
total_params = sum([tf.size(w).numpy() for w in model.trainable_weights])
print(f"📊 Paramètres entraînables: {total_params:,}")

# =============================================================================
# 4. ENTRAÎNEMENT
# =============================================================================

print("\n🚀 Début de l'entraînement...")
print("=" * 80)

# Callbacks
early_stop = EarlyStopping(monitor='val_loss', patience=2, restore_best_weights=True, verbose=0)
reduce_lr = ReduceLROnPlateau(monitor='val_loss', factor=0.5, patience=1, min_lr=1e-7, verbose=0)

# Entraînement
history = model.fit(
    [X_train_camembert['input_ids'], X_train_camembert['attention_mask']],
    y_train,
    validation_data=(
        [X_val_camembert['input_ids'], X_val_camembert['attention_mask']],
        y_val
    ),
    epochs=EPOCHS,
    batch_size=BATCH_SIZE,
    callbacks=[early_stop, reduce_lr],
    verbose=1
)

print("=" * 80)
print("✅ Entraînement terminé")
print(f"📊 Meilleure val_accuracy: {max(history.history['val_accuracy']):.4f}")
print(f"📊 Meilleure val_loss: {min(history.history['val_loss']):.4f}")

# =============================================================================
# 5. ÉVALUATION SUR LE TEST SET
# =============================================================================

print("\n📊 Évaluation sur le test set...")
test_loss, test_acc = model.evaluate(
    [X_test_camembert['input_ids'], X_test_camembert['attention_mask']],
    y_test,
    verbose=0
)
print(f"✅ Test Loss: {test_loss:.4f}")
print(f"✅ Test Accuracy: {test_acc:.4f} ({test_acc*100:.2f}%)")

# =============================================================================
# 6. SAUVEGARDE DU MODÈLE ET DES FICHIERS
# =============================================================================

print("\n💾 Sauvegarde des fichiers...")
print("=" * 80)

# Créer le dossier de sauvegarde
save_dir = '../model/camembert/'
os.makedirs(save_dir, exist_ok=True)

# 1. Sauvegarder le modèle en .h5 (utilisé par l'API FastAPI)
model_h5_path = f'{save_dir}camembert-budgets-participatif.h5'
model.save(model_h5_path)
model_size = os.path.getsize(model_h5_path) / (1024**2)
print(f"✅ Modèle sauvegardé (.h5): {model_h5_path}")
print(f"   Taille: {model_size:.1f} MB")

# 2. Sauvegarder le label mapping en JSON
label_mapping_json_path = f'{save_dir}camembert_label_mapping.json'
mapping_dict = {int(i): str(label) for i, label in enumerate(label_encoder.classes_)}
reverse_mapping = {str(label): int(i) for i, label in enumerate(label_encoder.classes_)}

with open(label_mapping_json_path, 'w', encoding='utf-8') as f:
    json.dump({
        'num_to_label': mapping_dict,
        'label_to_num': reverse_mapping,
        'num_classes': num_classes,
        'learning_rate': LEARNING_RATE,
        'test_accuracy': float(test_acc),
        'test_loss': float(test_loss)
    }, f, ensure_ascii=False, indent=2)

print(f"✅ Label mapping sauvegardé: {label_mapping_json_path}")
print("\n" + "=" * 80)
print("🎉 ENTRAÎNEMENT ET SAUVEGARDE TERMINÉS AVEC SUCCÈS !")
print("=" * 80)
print("\n📋 Fichiers créés:")
print(f"   1. {model_h5_path}")
print(f"   2. {label_mapping_json_path}")

print("\n💡 Le modèle est prêt à être utilisé par l'API FastAPI")
print(f"📊 Performance finale: {test_acc*100:.2f}% d'accuracy sur le test set")
