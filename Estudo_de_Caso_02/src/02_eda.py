import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

# Caminho do dataset limpo
BASE_DIR = Path(__file__).resolve().parents[1]
DATA_PATH = BASE_DIR / "data_clean" / "fitbit_daily_clean.csv"

df = pd.read_csv(DATA_PATH)

print("\n================ RESUMO GERAL ================")
df.info()

print("\n================ PASSOS POR USUÁRIO ================")
print(df.groupby("Id")["TotalSteps"].mean().sort_values(ascending=False).head())

print("\n================ CORRELAÇÃO PASSOS x SONO ================")
print(df[["TotalSteps", "TotalMinutesAsleep"]].corr())

print("\n================ CORRELAÇÃO PASSOS x CALORIAS ================")
print(df[["TotalSteps", "Calories"]].corr())

print("\n================ MÉDIAS DE ATIVIDADE ================")
print("SedentaryMinutes média:", df["SedentaryMinutes"].mean())
print("VeryActiveMinutes média:", df["VeryActiveMinutes"].mean())

# ================= VISUALIZAÇÕES =================

sns.set(style="whitegrid")

# Passos vs Calorias
plt.figure(figsize=(8,5))
sns.scatterplot(data=df, x="TotalSteps", y="Calories")
plt.title("Relação entre Passos e Calorias")
plt.tight_layout()
plt.savefig(BASE_DIR / "outputs" / "steps_vs_calories.png")
plt.close()

# Distribuição de passos
plt.figure(figsize=(8,5))
sns.histplot(df["TotalSteps"], bins=30)
plt.title("Distribuição de Passos Diários")
plt.tight_layout()
plt.savefig(BASE_DIR / "outputs" / "distribuicao_passos.png")
plt.close()

print("\n✅ Visualizações salvas na pasta outputs/")


