## Contexte et dataset 

Source : https://www.kaggle.com/datasets/joniarroba/noshowappointments/data

Ce fichier de + de 100.000 lignes est une étude qui recense les rdv médicaux honorés ou non (show/no-show).

## Nature des features et du label

 Plusieurs features d'intérêt parmi sont: 

- le sexe
- l'âge
- la région (au Brésil)
- un niveau d'études (oui/non)
- une pathologie donnée (Hipertension	Diabetes	Alcoholism)
- une présence de handicap
- le jour/heure de prise de rdv
- le jour/heure de rdv


## Objectif : 

Nous allons appliquer toutes les étapes vues en séance pour entrainer un modèle de prédiction sur le label "No-show" et en gros de prédire pour chaque RDV si No-show == True/False.


## Executer le notebook

run all 

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

3) Exécuter les notebook : 

cliquer sur le bouton : RUN ALL 



## Journal de bord (et choix techniques)

### 1° Essai 1 : Random Forest Classifier

- **Accuracy Test de 77.35%** : Performance correcte pour une première approche
  - Recall de **91%** : le modèle identifie correctement 91% des patients qui se présentent
  - Precision de **83%** : quand le modèle prédit "honoré", il a raison 83% du temps
  - Accuracy Train (95.64%) >> Accuracy Test (77.35%) : **Overfitting significatif** :
  
- **Faible détection des No-Show** :
  - Recall de seulement **4%** 

**Impact sur le modèle** : Le modèle a tendance à **sur-prédire la classe majoritaire** (RDV honorés) :

**Accuracy seule** = insuffisante, elle cache le déséquilibre des classes


### 2° essai: Adaboost

Aucune amélioration significative


### 3° essai: Gradient Boost + SMOTE + ajustement du seuil de décision

En poussant le seuil au minimum, on a : 

- Precision : 0.2845  
- Recall :  0.9019             
- F1-Score: 0.4326   
- Accuracy : 0.5223          
                           

## Conclusions 

Gradient Boost semble être le meilleur compromis pour augmtner le recall et le F1-score de la classe 1 (rdv manqué), mais ceci se fait au détriment de l'accuracy générale.
