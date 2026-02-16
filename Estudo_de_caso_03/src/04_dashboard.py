import pandas as pd
import plotly.express as px
from pathlib import Path

# Caminhos
BASE_DIR = Path(__file__).resolve().parents[2]
DATA = BASE_DIR / "data_clean" / "happiness_final.csv"
OUT = BASE_DIR / "outputs" / "dashboard_happiness.html"
OUT.parent.mkdir(exist_ok=True)

# Ler dados
df = pd.read_csv(DATA)

# ==============================
# 0) KPIs: faixa de felicidade por ano (min / média / max)
# ==============================
kpi_year = (
    df.groupby("year")["score"]
    .agg(["min", "mean", "max", "count"])
    .reset_index()
)

# formatar números
kpi_year["min"] = kpi_year["min"].round(2)
kpi_year["mean"] = kpi_year["mean"].round(2)
kpi_year["max"] = kpi_year["max"].round(2)

# ==============================
# 1️⃣ MÉDIA DE FELICIDADE POR ANO
# ==============================
mean_year = df.groupby("year")["score"].mean().reset_index()

fig1 = px.line(
    mean_year,
    x="year",
    y="score",
    markers=True,
    title="Média Global de Felicidade por Ano",
)
fig1.update_layout(margin=dict(l=30, r=30, t=60, b=30))

# ==============================
# 2️⃣ TOP 10 PAÍSES MAIS FELIZES
# ==============================
top_countries = (
    df.groupby("country")["score"]
    .mean()
    .sort_values(ascending=False)
    .head(10)
    .reset_index()
)

fig2 = px.bar(
    top_countries,
    x="score",
    y="country",
    orientation="h",
    title="Top 10 Países Mais Felizes (Média Geral)",
)
fig2.update_layout(margin=dict(l=30, r=30, t=60, b=30))

# ==============================
# 3️⃣ GDP vs SCORE (dispersão)
# ==============================
fig3 = px.scatter(
    df,
    x="gdp_per_capita",
    y="score",
    color="year",
    hover_data=["country"],
    title="GDP per Capita vs Felicidade (cada ponto = país em um ano)",
)
fig3.update_layout(margin=dict(l=30, r=30, t=60, b=30))

# ==============================
# 4️⃣ MATRIZ DE CORRELAÇÃO
# ==============================
corr_cols = [
    "score",
    "gdp_per_capita",
    "social_support",
    "life_expectancy",
    "freedom",
    "corruption",
    "generosity",
]
corr = df[corr_cols].corr().round(2)

fig4 = px.imshow(
    corr,
    text_auto=True,
    title="Correlação entre Variáveis (quanto mais perto de 1, mais forte a relação)",
)
fig4.update_layout(margin=dict(l=30, r=30, t=60, b=30))

# ==============================
# HTML: cards + resumos + gráficos
# ==============================

def build_kpi_cards_html(kpi_df: pd.DataFrame) -> str:
    cards = []
    for _, row in kpi_df.iterrows():
        year = int(row["year"])
        mn = row["min"]
        md = row["mean"]
        mx = row["max"]
        n = int(row["count"])
        cards.append(f"""
        <div class="card">
            <div class="card-year">{year}</div>
            <div class="card-range">Faixa: <b>{mn}</b> – <b>{mx}</b></div>
            <div class="card-mean">Média: <b>{md}</b></div>
            <div class="card-n">Países no ano: {n}</div>
        </div>
        """)
    return "\n".join(cards)

kpi_cards_html = build_kpi_cards_html(kpi_year)

html_header = """
<!doctype html>
<html lang="pt-br">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width,initial-scale=1" />
  <title>World Happiness Dashboard</title>
  <style>
    body{
      font-family: Arial, sans-serif;
      background: #0b0f17;
      color: #e8eefc;
      margin: 0;
      padding: 24px;
    }
    .container{
      max-width: 1100px;
      margin: 0 auto;
    }
    h1{
      text-align:center;
      margin: 0 0 18px 0;
      font-size: 28px;
    }
    .subtitle{
      text-align:center;
      color:#b7c3df;
      margin-bottom: 24px;
      line-height: 1.35;
    }
    .cards{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
      gap: 14px;
      margin: 18px 0 26px 0;
    }
    .card{
      background: #121a2a;
      border: 1px solid #22304f;
      border-radius: 14px;
      padding: 14px 14px 12px 14px;
      box-shadow: 0 10px 20px rgba(0,0,0,.25);
    }
    .card-year{
      font-size: 18px;
      font-weight: 700;
      margin-bottom: 8px;
    }
    .card-range, .card-mean, .card-n{
      font-size: 13.5px;
      color:#cfe0ff;
      margin: 3px 0;
    }
    .section{
      background: #0f1624;
      border: 1px solid #22304f;
      border-radius: 16px;
      padding: 16px;
      margin-bottom: 18px;
    }
    .section h2{
      margin: 0 0 8px 0;
      font-size: 18px;
    }
    .section p{
      margin: 0 0 14px 0;
      color:#b7c3df;
      line-height: 1.45;
      font-size: 14px;
    }
    .note{
      color:#93a7d6;
      font-size: 12.5px;
      margin-top: 8px;
    }
    a{ color: #9bd1ff; }
  </style>
</head>
<body>
  <div class="container">
"""

html_intro = """
    <h1>🌍 World Happiness Dashboard (2015–2019)</h1>
    <div class="subtitle">
      Este dashboard resume como a felicidade (score) varia ao longo do tempo e como ela se relaciona com fatores socioeconômicos.<br>
      Interaja com os gráficos (zoom, hover, legenda) para explorar padrões.
    </div>

    <div class="section">
      <h2>📌 KPIs — Faixa de felicidade por ano</h2>
      <p>
        Cada card mostra a <b>faixa (mín–máx)</b> do score de felicidade observada no ano e a <b>média</b>.
        Isso ajuda a perceber se o ano teve dispersão alta/baixa e se o nível médio mudou ao longo do tempo.
      </p>
      <div class="cards">
        {cards}
      </div>
      <div class="note">Observação: o score do World Happiness normalmente varia de 0 a 10.</div>
    </div>
""".replace("{cards}", kpi_cards_html)

sections = []

# Seção 1
sections.append(("""
    <div class="section">
      <h2>1) Média global de felicidade por ano</h2>
      <p>
        Mostra a <b>tendência geral</b> da felicidade média do mundo entre 2015 e 2019.
        Se a linha sobe, indica melhora média global; se desce, piora.
        Oscilações pequenas sugerem estabilidade no período.
      </p>
""", fig1))

# Seção 2
sections.append(("""
    <div class="section">
      <h2>2) Top 10 países mais felizes (média geral)</h2>
      <p>
        Ranking dos países com maior <b>score médio</b> no período.
        Serve para identificar <b>quem consistentemente aparece no topo</b> e comparar a distância entre eles.
      </p>
""", fig2))

# Seção 3
sections.append(("""
    <div class="section">
      <h2>3) GDP per capita vs Felicidade</h2>
      <p>
        Cada ponto é um país em um ano. A posição no eixo X indica <b>PIB per capita</b> e no eixo Y o <b>score de felicidade</b>.
        Padrão inclinado para cima sugere que riqueza está associada a maior felicidade — mas com exceções.
      </p>
""", fig3))

# Seção 4
sections.append(("""
    <div class="section">
      <h2>4) Correlação entre variáveis</h2>
      <p>
        Mapa de calor com correlações. Valores mais próximos de <b>1</b> indicam relação forte (crescem juntos),
        mais próximos de <b>0</b> indicam relação fraca, e negativos indicam relação inversa.
        O foco é ver quais variáveis mais se aproximam do <b>score</b>.
      </p>
""", fig4))

html_footer = """
  </div>
</body>
</html>
"""

# Exportar HTML
with open(OUT, "w", encoding="utf-8") as f:
    f.write(html_header)
    f.write(html_intro)

    # incluir plotlyjs só no primeiro gráfico
    first = True
    for section_html, fig in sections:
        f.write(section_html)
        if first:
            f.write(fig.to_html(full_html=False, include_plotlyjs="cdn"))
            first = False
        else:
            f.write(fig.to_html(full_html=False, include_plotlyjs=False))
        f.write("</div>")  # fecha .section

    f.write(html_footer)

print("✅ Dashboard criado com sucesso!")
print("Arquivo:", OUT)
