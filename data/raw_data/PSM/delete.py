import pandas as pd

# Chemin vers le fichier original
input_csv = "test_label.csv"

# Chemin vers le nouveau fichier
output_csv = "test_label_4000.csv"

# Lire le CSV
df = pd.read_csv(input_csv)

# Ne garder que les 4000 premières lignes
df_first_4000 = df.head(2000)

# Sauvegarder le nouveau fichier
df_first_4000.to_csv(output_csv, index=False)

print(f"Le nouveau fichier avec les 4000 premières lignes a été sauvegardé dans {output_csv}")
