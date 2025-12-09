import pandas as pd
from pathlib import Path

# Chemins des fichiers
input_file = Path(__file__).parent / "data" / "initial-budget-participatif.csv"
output_file = Path(__file__).parent / "data" / "dataset-for-training-completed.csv"

# Lire le fichier CSV d'origine avec le bon délimiteur (point-virgule)
df = pd.read_csv(input_file, delimiter=';', encoding='utf-8')

# Créer une nouvelle colonne en concaténant "Titre du projet lauréat" et "Titre de l'opération"
# Remplir les NaN avec des chaînes vides avant la concaténation
df['Titres opération et projet lauréat'] = (
    df['Titre du projet lauréat'].fillna('') + ' ' + df['Titre de l\'opération'].fillna('')
).str.strip()  # Supprimer les espaces en début/fin

# Sélectionner uniquement les 2 colonnes nécessaires (nouvelle colonne + Thématique)
df_filtered = df[["Titres opération et projet lauréat", "Thématique"]]

# Sauvegarder dans un nouveau fichier CSV
df_filtered.to_csv(output_file, index=False, encoding='utf-8')

print(f"✅ Dataset créé avec succès : {output_file}")
print(f"📊 Nombre de lignes : {len(df_filtered)}")
print(f"📋 Colonnes : {list(df_filtered.columns)}")
print(f"\n📝 Aperçu des premières lignes :")
print(df_filtered.head())
