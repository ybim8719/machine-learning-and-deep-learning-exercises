# Partie Server : modèle de classification CamemBERT pour la prédiction des thématiques de budgets participatifs.

## Architecture

La partie server exploite une api qui expose la route POST "predict-category". Cette route reçoit 2 inputs: 
- le titre du projet dont il faut prédire la catégorie 
- le budget prévisionnel dudit projet 

Ensuite viennent 2 étapes : 

1) prévision de la catégorie d'appartenance 
2) Calculs de statistiques à partir du dataset originel en filtrant les celulles avec la catégorie passée en params (le budget prévisisonnel est utilisé pour être comparé avec ledit corpus)


## Structure des dossiers 

- **/app** : contient de quoi lancer le projet
- **/attempts** : contient les .ipynb qui permettent de dresser un historique du projet. Ils fournissent d'avantage d'éléments de contextualisation et d'exploration des données.   
- **/data** : contient le corpus d'entrainement et de la partie dataviz 
- **/utils** : contient le formateur de csv et une exploration des données du corpus originel
- **/model** : fichiers liés au modèle de prédiction utilisées par fastapi


## PROCESS lancement du back

Par défaut, il vous faut au minimum : 

- python >= 3.9
- pip

1) créer un venv : 

```bash 
python -m venv venv
```

puis l'activer : 

```bash 
source venv/bin/activate
```

2) Installer les libs : 

```bash 
pip install -r requirements.txt
```

3) constuire le dataset qui génère un csv 

```bash 
cd utils
python adapt-dataset-completed.py
```
et doit apparaitre ici : 

```bash 
data/dataset-for-training-completed.csv
```

4) entrainer le model et le sauvegarder 

```bash 
cd app
python train_and_save_model.py
```
=> 2 fichiers apparaissent 

```bash 
model/camembert/camembert_label_mapping.json
model/camembert/model_camembert_camembert-budgets-participatif.h5
```

5) lancer le back 


```bash 
cd app
python api_camembert.py
```

=> votre serveur devrait être live sur localhost:8000

## Processus d'entrainement et de sauvegarde du modèle de classification CamemBERT

Voici ce que fait le script : 

- Charge et nettoie le dataset enrichi (dataset-for-training-completed.csv)
- Prétraite les textes (normalisation français, tokenization CamemBERT)
- Encode les thématiques en labels numériques
- Entraîne un modèle CamemBERT en mode Fine-Tuning complet (learning rate optimisé : 5e-5)
- Évalue les performances sur un test set
- Sauvegarde de 3 fichiers :
- model_camembert_camembert-budgets-participatif.h5 (modèle complet)
- camembert_label_mapping.json (mapping labels)


Configuration :

- Séparation train/val/test : 56% / 14% / 30%
- Séquences de 128 tokens max
- Batch size : 32
- Early stopping & learning rate scheduler
- Environ 110M de paramètres entraînables

Entrainement: 

- Lightingin.ai : 20 par round/ (GPU T4 1 coeur)

## Journal de bord (dossier "/attempts")

### 1° essai: LSTM vs BERT

| Modèle | Test Loss | Test Accuracy |
|--------|-----------|---------------|
| LSTM | 1.244263 | 0.593464 |
| BERT Frozen | 1.496337 | 0.481046 |
| BERT Fine-Tuned | 1.721269 | 0.438562 |

### 2° essai: Feature management (colonne "titre" enrichie)

Fusion de 2 colonnes de titres complémentaires dans le dataset d'entrainement (standard VS enriched)

| Modèle | Test Loss | Test Accuracy |
|--------|-----------|---------------|
| LSTM Standard | 1.244262 | 0.593464 |
| LSTM Enrichi | 0.678509 | 0.855650 |

### 3° essai: CamemBERT Fine-tuned VS Frozen

| Modèle | Test Accuracy |
|--------|---------------|
| CamemBERT Fine-Tuned | 0.909 |
| CamemBERT Frozen | 0.782 |

*(notebook concerné perdu)*

### 4° essai: Learning rate variable

| Modèle | Learning Rate | Test Loss | Test Accuracy |
|--------|---------------|-----------|---------------|
| LR_5e-5 | 0.00005 | 0.331608 | 0.92162 |
| LR_3e-5 | 0.00003 | 0.312942 | 0.91966 |
| LR_1e-5 | 0.00001 | 0.362149 | 0.90921 |
 

## Résultats 

CamemBERT Fine-tuned est le model qui a été conservé en raison de ses performances, et est utilisé comme backend. 
