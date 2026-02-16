import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

# Configuração visual
sns.set(style="whitegrid")
plt.rcParams["figure.figsize"] = (10, 6)

BASE_DIR = Path(__file__).resolve().parents[2]
DATA = BASE_DIR / "data_clean" / "happiness_final.csv"
OUTPUT = BASE_DIR / "outputs"
OUTPUT.mkdir(exist_ok=True)

df = pd.read_csv(DATA)

print("\n================ RESUMO GERAL ================")
print(df.info())

print("\n================ MÉDIA DE FELICIDADE POR ANO ================")
print(df.groupby("year")["score"].mean())

print("\n================ TOP 5 PAÍSES MAIS FELIZES (MÉDIA GERAL) ================")
print(
    df.groupby("country")["score"]
    .mean()
    .sort_values(ascending=False)
    .head()
)

print("\n================ CORRELAÇÃO COM SCORE ================")

corr = df[[
    "score",
    "gdp_per_capita",
    "social_support",
    "life_expectancy",
    "freedom",
    "corruption",
    "generosity"
]].corr()

print(corr["score"].sort_values(ascending=False))

# ========================
# 📊 HEATMAP DE CORRELAÇÃO
# ========================

plt.figure()
sns.heatmap(corr, annot=True, cmap="coolwarm", fmt=".2f")
plt.title("Correlação entre variáveis")
plt.tight_layout()
plt.savefig(OUTPUT / "correlation_heatmap.png")
plt.close()

# ========================
# 📊 GDP vs Score
# ========================

plt.figure()
sns.scatterplot(data=df, x="gdp_per_capita", y="score", hue="region", alpha=0.6)
plt.title("GDP per Capita vs Happiness Score")
plt.tight_layout()
plt.savefig(OUTPUT / "gdp_vs_score.png")
plt.close()

# ========================
# 📊 Social Support vs Score
# ========================

plt.figure()
sns.scatterplot(data=df, x="social_support", y="score", hue="region", alpha=0.6)
plt.title("Social Support vs Happiness Score")
plt.tight_layout()
plt.savefig(OUTPUT / "support_vs_score.png")
plt.close()

print("\n✅ Visualizações salvas em /outputs")
