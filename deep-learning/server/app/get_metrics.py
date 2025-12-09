# Logique de lecture du fichier de stats complet
# fonctions de calculs de metrics (moyen etc...)
# 
# ce seront les fonctions qui seront appelées par l'api pour générer de la donnée à envoyer au user

import pandas as pd
from pathlib import Path
from typing import Optional
from schemas import PredictionInfo


def getMetricsByCategory(prediction_info: PredictionInfo, projectTitle: str, estimatedBudget: int) -> dict:
    # Extraire la catégorie de l'objet prediction_info
    predictedCategory = prediction_info.name
    # Charger le fichier CSV
    csv_path = Path(__file__).parent / "../data/initial-budget-participatif.csv"
    df = pd.read_csv(csv_path, delimiter=';', encoding='utf-8')
    print(f"Colonnes disponibles: {df.columns.tolist()}")
    print(f"Catégorie recherchée: {predictedCategory}")
    # Filtrer les données par la catégorie prédite (colonne "Thématique")
    col_thematique = "Thématique"
    number_of_records = 0

    # Filtrer par catégorie
    category_matches = df[df[col_thematique].str.contains(predictedCategory, case=False, na=False)]
    if (len(category_matches) > 0):
        print(f"✅ {len(category_matches)} projet(s) trouvé(s) pour la catégorie: {predictedCategory}")
        number_of_records = len(category_matches)
    else:
        print(f"0 projet(s) trouvé(s) pour la catégorie: {predictedCategory}, aucune calcul de metrics possibles")
        return {
            "predictedCategory": {
                "name": prediction_info.name,
                "confidence": prediction_info.confidence,
                "analyse": "Aucune donnée disponible pour cette catégorie prédite",
                "projectTitle": projectTitle,
                "estimatedBudget": estimatedBudget,
                "metrics": None
            }
        }
   
    # 1. startingYear: valeur minimale de "Edition" pour la catégorie prédite
    starting_year = int(category_matches['Edition'].min()) if 'Edition' in category_matches.columns and len(category_matches) > 0 else 2000
    # 2. endingYear: valeur maximale de "Edition" pour la catégorie prédite
    ending_year = int(category_matches['Edition'].max()) if 'Edition' in category_matches.columns and len(category_matches) > 0 else 2025
    # 3. breakdownByCategory: tableau des catégories pour piechart
    breakdown_by_category = []
    if col_thematique in df.columns:
        category_counts = df[col_thematique].value_counts()
        total_count = len(df)
        
        for category, count in category_counts.items():
            percentage = int((count / total_count) * 100)
            # selected = True si c'est la catégorie passée en paramètre
            is_selected = category.lower() == predictedCategory.lower() or predictedCategory.lower() in category.lower()
            breakdown_by_category.append({
                "category": category,
                "percentage": percentage,
                "selected": is_selected
            })
    
    # 5. postalCodeDistribution: distribution par arrondissement
    postal_code_distribution = []
    col_arrondissement = "Arrondissement de l'opération"
    if col_arrondissement in category_matches.columns:
        arrond_counts = category_matches[col_arrondissement].value_counts()
        
        for arrondissement, count in arrond_counts.items():
            if pd.notna(arrondissement):  # Ignorer les valeurs NaN
                postal_code_distribution.append({
                    "postalCode": str(arrondissement),
                    "count": int(count)
                })
    
    # 6. statusesPieChart: répartition des statuts d'avancement pour la catégorie prédite
    col_avancement = "Avancement de l'opération"
    abandoned_count = 0
    completed_count = 0
    in_progress_count = 0
    
    if col_avancement in category_matches.columns:
        # Compter les projets abandonnés
        abandoned_count = len(category_matches[category_matches[col_avancement].str.contains("ABANDONNÉ", case=False, na=False)])
        
        # Compter les projets terminés (FIN)
        completed_count = len(category_matches[category_matches[col_avancement].str.contains("FIN", case=False, na=False)])
        
        # Compter les projets en cours (tout sauf ABANDONNÉ et FIN)
        in_progress_count = len(category_matches[
            ~category_matches[col_avancement].str.contains("ABANDONNÉ|FIN", case=False, na=False) & 
            category_matches[col_avancement].notna()
        ])
    
    statusesPieChart = {
        "abandoned": abandoned_count,
        "inProgress": in_progress_count,
        "completed": completed_count
    }
    
    # 7. abandonedExamples: 5 exemples aléatoires de projets abandonnés de la catégorie
    abandonedExamples = []
    col_titre = "Titre de l'opération"
    col_budget = "Budget global du projet lauréat"
    col_edition = "Edition"
    
    if col_avancement in category_matches.columns:
        abandoned_projects = category_matches[category_matches[col_avancement].str.contains("ABANDONNÉ", case=False, na=False)]
        
        # Sélectionner jusqu'à 5 projets aléatoires
        sample_size = min(5, len(abandoned_projects))
        if sample_size > 0:
            random_abandoned = abandoned_projects.sample(n=sample_size)
            
            for _, row in random_abandoned.iterrows():
                abandonedExamples.append({
                    "title": str(row[col_titre]) if col_titre in row and pd.notna(row[col_titre]) else "Titre indisponible",
                    "budget": int(row[col_budget]) if col_budget in row and pd.notna(row[col_budget]) else 0,
                    "year": str(int(row[col_edition])) if col_edition in row and pd.notna(row[col_edition]) else "N/A"
                })
    
    # 8. priorityArea: répartition par quartier populaire
    col_quartier_pop = "Opération en Quartier Populaire"
    high_priority_count = 0
    low_priority_count = 0
    
    if col_quartier_pop in category_matches.columns:
        # Compter les "Oui" (haute priorité = quartiers populaires)
        high_priority_count = len(category_matches[category_matches[col_quartier_pop].str.contains("Oui", case=False, na=False)])
        
        # Compter les "Non" (basse priorité = hors quartiers populaires)
        low_priority_count = len(category_matches[category_matches[col_quartier_pop].str.contains("Non", case=False, na=False)])
    
    priorityArea = {
        "highPriority": high_priority_count,
        "lowPriority": low_priority_count
    }
    
    # 9. budget: statistiques budgétaires pour la catégorie prédite
    budget_data = category_matches[col_budget].dropna()
    
    budget_average = int(budget_data.mean()) if len(budget_data) > 0 else 0
    budget_min = int(budget_data.min()) if len(budget_data) > 0 else 0
    budget_max = int(budget_data.max()) if len(budget_data) > 0 else 0
    
    # 5 projets les plus chers
    fiveMostExpensive = []
    most_expensive = category_matches.nlargest(5, col_budget)
    for _, row in most_expensive.iterrows():
        if pd.notna(row[col_budget]):
            fiveMostExpensive.append({
                "title": str(row[col_titre]) if col_titre in row and pd.notna(row[col_titre]) else "Titre indisponible",
                "budget": int(row[col_budget]),
                "year": str(int(row[col_edition])) if col_edition in row and pd.notna(row[col_edition]) else "N/A"
            })
    
    # 5 projets les moins chers
    fiveLeastExpensive = []
    least_expensive = category_matches[category_matches[col_budget].notna()].nsmallest(5, col_budget)
    for _, row in least_expensive.iterrows():
        if pd.notna(row[col_budget]):
            fiveLeastExpensive.append({
                "title": str(row[col_titre]) if col_titre in row and pd.notna(row[col_titre]) else "Titre indisponible",
                "budget": int(row[col_budget]),
                "year": str(int(row[col_edition])) if col_edition in row and pd.notna(row[col_edition]) else "N/A"
            })
    
    # Calculer les quartiles pour positionner l'estimatedBudget
    position_info = {
        "quartiles": [],
        "estimatedBudgetQuartile": None
    }
    
    if len(budget_data) > 0:
        # Calculer les quartiles (Q1, Q2/médiane, Q3)
        q1 = budget_data.quantile(0.25)
        q2 = budget_data.quantile(0.50)  # médiane
        q3 = budget_data.quantile(0.75)
        
        # Créer les 4 tranches (quartiles)
        position_info["quartiles"] = [
            {
                "quartile": 1,
                "label": "Q1 (0-25%)",
                "min": int(budget_data.min()),
                "max": int(q1),
                "description": "Budget le plus bas"
            },
            {
                "quartile": 2,
                "label": "Q2 (25-50%)",
                "min": int(q1),
                "max": int(q2),
                "description": "Budget inférieur à la moyenne"
            },
            {
                "quartile": 3,
                "label": "Q3 (50-75%)",
                "min": int(q2),
                "max": int(q3),
                "description": "Budget supérieur à la moyenne"
            },
            {
                "quartile": 4,
                "label": "Q4 (75-100%)",
                "min": int(q3),
                "max": int(budget_data.max()),
                "description": "Budget le plus élevé"
            }
        ]
        
        # Déterminer dans quel quartile se trouve l'estimatedBudget
        if estimatedBudget <= q1:
            position_info["estimatedBudgetQuartile"] = 1
        elif estimatedBudget <= q2:
            position_info["estimatedBudgetQuartile"] = 2
        elif estimatedBudget <= q3:
            position_info["estimatedBudgetQuartile"] = 3
        else:
            position_info["estimatedBudgetQuartile"] = 4
    
    budget_info = {
        "median": int(budget_data.median()) if len(budget_data) > 0 else 0,
        "average": budget_average,
        "min": budget_min,
        "max": budget_max,
        "fiveMostExpensive": fiveMostExpensive,
        "fiveLeastExpensive": fiveLeastExpensive,
        "position": position_info
    }

    # Construction de l'objet metrics_data (qui ira dans la clé "metrics")
    metrics_data = {
            "startingYear": starting_year,
            "endingYear": ending_year,
            "numberOfRecords": number_of_records,
            "breakdownByCategory": breakdown_by_category,
            "postalCodeDistribution": postal_code_distribution,
            "statuses": {
                "pieChart": statusesPieChart,
                "abandonedExamples": abandonedExamples
            },
            "priorityArea": priorityArea,
            "budget": budget_info
        }
        
    # Construction de l'objet complet avec predictedCategory en utilisant les infos de prediction_info
    response = {
        "predictedCategory": {
            "name": prediction_info.name,
            "confidence": prediction_info.confidence,
            "analyse": prediction_info.analyse,
            "projectTitle": projectTitle,
            "estimatedBudget": estimatedBudget,
            "metrics": metrics_data
        }
    }
    
    return response


# # Test de la fonction
# if __name__ == "__main__":
#     # Test avec un objet PredictionInfo
#     test_prediction = PredictionInfo(
#         name="Direction des Espaces Verts et de l'Environnement",
#         confidence=0.85,
#         analyse="Test de prédiction"
#     )
#     result = getMetricsByCategory(test_prediction, 50000)
#     print("\n=== RÉSULTAT ===")
#     print(result) 