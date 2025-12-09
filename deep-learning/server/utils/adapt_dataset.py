import pandas as pd
from pathlib import Path

# Chemins des fichiers
input_file = Path(__file__).parent / "data" / "initial-budget-participatif.csv"
output_file = Path(__file__).parent / "data" / "dataset-for-training.csv"

# Lire le fichier CSV d'origine avec le bon délimiteur (point-virgule)
df = pd.read_csv(input_file, delimiter=';', encoding='utf-8')

# Sélectionner uniquement les 2 colonnes nécessaires
df_filtered = df[["Titre de l'opération", "Thématique"]]

# Sauvegarder dans un nouveau fichier CSV
df_filtered.to_csv(output_file, index=False, encoding='utf-8')

print(f"✅ Dataset créé avec succès : {output_file}")
print(f"📊 Nombre de lignes : {len(df_filtered)}")
print(f"📋 Colonnes : {list(df_filtered.columns)}")
