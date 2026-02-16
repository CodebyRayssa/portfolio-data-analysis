import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]
DATA = BASE_DIR / "data_clean" / "happiness_full.csv"
OUT  = BASE_DIR / "data_clean" / "happiness_final.csv"

df = pd.read_csv(DATA)

# -----------------------------
# 0) Normalizar nomes de colunas
# -----------------------------
df.columns = (
    df.columns.astype(str)
    .str.strip()
    .str.lower()
    .str.replace(" ", "_")
)

# -----------------------------
# 1) Remover colunas lixo
# -----------------------------
drop_cols = [c for c in df.columns if c.startswith("unnamed")]
df = df.drop(columns=drop_cols, errors="ignore")

# -----------------------------
# 2) Padronizar colunas "chave"
#    (mesmos conceitos com nomes diferentes ao longo dos anos)
# -----------------------------

# Country (2019 usa country_or_region)
if "country" not in df.columns and "country_or_region" in df.columns:
    df["country"] = df["country_or_region"]
else:
    # se country existe, tenta completar com country_or_region onde estiver vazio
    if "country_or_region" in df.columns:
        df["country"] = df["country"].fillna(df["country_or_region"])

# Rank (2019 usa overall_rank)
if "rank" not in df.columns and "overall_rank" in df.columns:
    df["rank"] = df["overall_rank"]
else:
    if "overall_rank" in df.columns:
        df["rank"] = df["rank"].fillna(df["overall_rank"])

# Score (2015/2016 às vezes happiness_score; 2017 pode vir happiness.score)
if "score" not in df.columns:
    if "happiness_score" in df.columns:
        df["score"] = df["happiness_score"]
    elif "happiness.score" in df.columns:
        df["score"] = df["happiness.score"]

# GDP per capita (2015/2016: economy_(gdp_per_capita); 2017: economy..gdp.per.capita.)
if "gdp_per_capita" not in df.columns:
    if "economy_(gdp_per_capita)" in df.columns:
        df["gdp_per_capita"] = df["economy_(gdp_per_capita)"]
elif "economy_(gdp_per_capita)" in df.columns:
    df["gdp_per_capita"] = df["gdp_per_capita"].fillna(df["economy_(gdp_per_capita)"])

if "economy..gdp.per.capita." in df.columns:
    df["gdp_per_capita"] = df["gdp_per_capita"].fillna(df["economy..gdp.per.capita."])

# Social support (2015/2016 chamava family; 2019 é social_support)
if "social_support" not in df.columns and "family" in df.columns:
    df["social_support"] = df["family"]
elif "family" in df.columns:
    df["social_support"] = df["social_support"].fillna(df["family"])

# Life expectancy (2015/2016: health_(life_expectancy); 2017: health..life.expectancy.; 2019: healthy_life_expectancy)
if "life_expectancy" not in df.columns:
    if "health_(life_expectancy)" in df.columns:
        df["life_expectancy"] = df["health_(life_expectancy)"]

if "healthy_life_expectancy" in df.columns:
    df["life_expectancy"] = df["life_expectancy"].fillna(df["healthy_life_expectancy"])

if "health..life.expectancy." in df.columns:
    df["life_expectancy"] = df["life_expectancy"].fillna(df["health..life.expectancy."])

# Freedom (2019: freedom_to_make_life_choices)
if "freedom" not in df.columns and "freedom_to_make_life_choices" in df.columns:
    df["freedom"] = df["freedom_to_make_life_choices"]
elif "freedom_to_make_life_choices" in df.columns:
    df["freedom"] = df["freedom"].fillna(df["freedom_to_make_life_choices"])

# Corruption (2015/2016: trust_(government_corruption); 2017: trust..government.corruption.; 2019: perceptions_of_corruption)
if "corruption" not in df.columns:
    if "trust_(government_corruption)" in df.columns:
        df["corruption"] = df["trust_(government_corruption)"]

if "perceptions_of_corruption" in df.columns:
    df["corruption"] = df["corruption"].fillna(df["perceptions_of_corruption"])

if "trust..government.corruption." in df.columns:
    df["corruption"] = df["corruption"].fillna(df["trust..government.corruption."])

# -----------------------------
# 3) Tipagem numérica (pra correlação/gráficos)
# -----------------------------
num_cols = [
    "score", "rank", "gdp_per_capita", "social_support",
    "life_expectancy", "freedom", "corruption", "generosity"
]

for c in num_cols:
    if c in df.columns:
        df[c] = pd.to_numeric(df[c], errors="coerce")

if "year" in df.columns:
    df["year"] = pd.to_numeric(df["year"], errors="coerce").astype("Int64")

# -----------------------------
# 4) Selecionar só as colunas finais (dataset enxuto)
# -----------------------------
final_cols = [
    "year", "country", "region",
    "rank", "score",
    "gdp_per_capita", "social_support", "life_expectancy",
    "freedom", "corruption", "generosity"
]
final_cols = [c for c in final_cols if c in df.columns]
df_final = df[final_cols].copy()

# -----------------------------
# 5) Sanity checks (pegar erros tipo score=71 ou 18)
# -----------------------------
# Score do World Happiness é normalmente entre 0 e 10
df_final.loc[(df_final["score"] < 0) | (df_final["score"] > 10), "score"] = pd.NA

# Rank normalmente positivo
df_final.loc[(df_final["rank"] <= 0) | (df_final["rank"] > 300), "rank"] = pd.NA

# -----------------------------
# 6) Salvar
# -----------------------------
df_final.to_csv(OUT, index=False, encoding="utf-8")
print("✅ happiness_final.csv criado!")
print("Linhas:", len(df_final), "| Colunas:", df_final.shape[1])
print("Colunas finais:", list(df_final.columns))
print("Arquivo:", OUT)
