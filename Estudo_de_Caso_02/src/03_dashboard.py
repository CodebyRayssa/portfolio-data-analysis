import pandas as pd
from pathlib import Path
import json
import numpy as np

# -------- paths --------
BASE_DIR = Path(__file__).resolve().parents[1]
DATA_PATH = BASE_DIR / "data_clean" / "fitbit_daily_clean.csv"
OUT_DIR = BASE_DIR / "outputs"
OUT_DIR.mkdir(exist_ok=True)

# -------- load --------
df = pd.read_csv(DATA_PATH)

# garantir tipos
df["ActivityDate"] = pd.to_datetime(df["ActivityDate"], errors="coerce")
df = df.dropna(subset=["ActivityDate"])

# -------- KPIs --------
users = int(df["Id"].nunique())
days = int(df["ActivityDate"].nunique())
avg_steps = float(df["TotalSteps"].mean())
avg_cal = float(df["Calories"].mean())
avg_sleep = float(df["TotalMinutesAsleep"].mean())
avg_sedent = float(df["SedentaryMinutes"].mean())
avg_very_active = float(df["VeryActiveMinutes"].mean())

corr_steps_sleep = float(df[["TotalSteps", "TotalMinutesAsleep"]].corr().iloc[0, 1])
corr_steps_cal = float(df[["TotalSteps", "Calories"]].corr().iloc[0, 1])

# -------- aggregations --------
weekday_order = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]

steps_weekday = (
    df.groupby("weekday")["TotalSteps"].mean()
    .reindex(weekday_order)
    .fillna(0)
)

sleep_weekday = (
    df.groupby("weekday")["TotalMinutesAsleep"].mean()
    .reindex(weekday_order)
    .fillna(0)
)

# scatter: downsample para não pesar
scatter = df[["TotalSteps", "Calories", "TotalMinutesAsleep", "SedentaryMinutes", "VeryActiveMinutes"]].copy()
if len(scatter) > 3000:
    scatter = scatter.sample(3000, random_state=42)

scatter_steps_cal = [{"x": int(x), "y": int(y)} for x, y in zip(scatter["TotalSteps"], scatter["Calories"])]

# histogram (passos)
bins = np.linspace(df["TotalSteps"].min(), df["TotalSteps"].max(), 16)
hist_counts, hist_edges = np.histogram(df["TotalSteps"], bins=bins)
hist_labels = [f"{int(hist_edges[i])}–{int(hist_edges[i+1])}" for i in range(len(hist_edges)-1)]

# tabela resumo por usuário
user_summary = (
    df.groupby("Id")
      .agg(
          dias=("ActivityDate", "nunique"),
          passos_medios=("TotalSteps", "mean"),
          calorias_medias=("Calories", "mean"),
          sono_medio_min=("TotalMinutesAsleep", "mean"),
          sedentario_medio_min=("SedentaryMinutes", "mean"),
          muito_ativo_medio_min=("VeryActiveMinutes", "mean")
      )
      .reset_index()
)

# arredondar p/ ficar bonito
user_summary["passos_medios"] = user_summary["passos_medios"].round(0).astype(int)
user_summary["calorias_medias"] = user_summary["calorias_medias"].round(0).astype(int)
user_summary["sono_medio_min"] = user_summary["sono_medio_min"].round(1)
user_summary["sedentario_medio_min"] = user_summary["sedentario_medio_min"].round(1)
user_summary["muito_ativo_medio_min"] = user_summary["muito_ativo_medio_min"].round(1)

# para tabela no HTML
table_rows = user_summary.to_dict(orient="records")

data_payload = {
    "kpis": {
        "users": users,
        "days": days,
        "avg_steps": round(avg_steps, 0),
        "avg_cal": round(avg_cal, 0),
        "avg_sleep": round(avg_sleep, 1),
        "avg_sedent": round(avg_sedent, 1),
        "avg_very_active": round(avg_very_active, 1),
        "corr_steps_sleep": round(corr_steps_sleep, 3),
        "corr_steps_cal": round(corr_steps_cal, 3),
    },
    "steps_weekday": {
        "labels": weekday_order,
        "values": [float(v) for v in steps_weekday.values],
    },
    "sleep_weekday": {
        "labels": weekday_order,
        "values": [float(v) for v in sleep_weekday.values],
    },
    "scatter_steps_cal": scatter_steps_cal,
    "hist_steps": {
        "labels": hist_labels,
        "values": hist_counts.tolist(),
    },
    "table": table_rows,
}

# -------- HTML (Chart.js via CDN) --------
html = f"""<!DOCTYPE html>
<html lang="pt-br">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1"/>
  <title>Bellabeat — Dashboard (Case Study 2)</title>
  <style>
    body {{ font-family: Arial, sans-serif; margin: 28px; color: #111; background: #fff; }}
    h1 {{ margin: 0 0 8px 0; }}
    .sub {{ color:#555; margin:0 0 18px 0; }}
    .grid {{ display:grid; grid-template-columns: repeat(4, minmax(180px, 1fr)); gap: 12px; }}
    .card {{ border: 1px solid #e6e6e6; border-radius: 12px; padding: 14px; background:#fafafa; }}
    .kpi {{ font-size: 22px; font-weight: 700; }}
    .label {{ color:#666; font-size: 13px; margin-top: 4px; }}
    .charts {{ display:grid; grid-template-columns: 1fr 1fr; gap: 14px; margin-top: 14px; }}
    .panel {{ border: 1px solid #e6e6e6; border-radius: 12px; padding: 14px; }}
    canvas {{ width: 100% !important; height: 360px !important; }}
    .row {{ display:flex; gap: 12px; flex-wrap: wrap; margin-top: 14px; }}
    .pill {{ border:1px solid #e6e6e6; border-radius: 999px; padding: 8px 12px; background:#fff; }}
    .insight {{ margin-top:10px; background:#f3f3f3; border-left: 5px solid #111; padding: 10px 12px; border-radius: 8px; }}
    .tools {{ display:flex; gap: 10px; align-items:center; margin: 16px 0 8px 0; }}
    input {{ padding: 10px 12px; border-radius: 10px; border: 1px solid #ddd; width: 320px; }}
    table {{ width: 100%; border-collapse: collapse; font-size: 14px; }}
    th, td {{ border-bottom: 1px solid #eee; padding: 10px 8px; text-align: left; }}
    th {{ cursor: pointer; background: #fafafa; position: sticky; top: 0; }}
    .small {{ color:#666; font-size: 12px; }}
  </style>
</head>
<body>
  <h1>Bellabeat — Dashboard (Case Study 2)</h1>
  <p class="sub">Base: Fitbit (atividade + sono agregado por dia). Objetivo: extrair padrões de uso e recomendações.</p>

  <div class="grid" id="kpis"></div>

  <div class="row">
    <div class="pill"><b>Correlação Passos × Sono:</b> <span id="corr1"></span></div>
    <div class="pill"><b>Correlação Passos × Calorias:</b> <span id="corr2"></span></div>
  </div>

  <div class="insight" id="insightBox"></div>

  <div class="charts">
    <div class="panel">
      <h3>Passos médios por dia da semana</h3>
      <canvas id="chartStepsWeek"></canvas>
      <p class="small">Usar isso para planejar campanhas por dia (ex.: reforço em dias fracos).</p>
    </div>
    <div class="panel">
      <h3>Sono médio por dia da semana</h3>
      <canvas id="chartSleepWeek"></canvas>
      <p class="small">Útil para ações de rotina noturna e bem-estar.</p>
    </div>
    <div class="panel">
      <h3>Distribuição de passos diários</h3>
      <canvas id="chartHistSteps"></canvas>
      <p class="small">Mostra concentração de usuários em faixas de atividade.</p>
    </div>
    <div class="panel">
      <h3>Passos vs Calorias (amostra)</h3>
      <canvas id="chartScatter"></canvas>
      <p class="small">Visualiza relação moderada entre passos e calorias.</p>
    </div>
  </div>

  <h2 style="margin-top:20px;">Tabela: resumo por usuário</h2>
  <div class="tools">
    <input id="search" placeholder="Filtrar por Id (ex: 8877...)"/>
    <span class="small">Clique nos títulos para ordenar.</span>
  </div>

  <div style="max-height: 420px; overflow:auto; border:1px solid #e6e6e6; border-radius: 12px;">
    <table id="tbl">
      <thead>
        <tr>
          <th data-key="Id">Id</th>
          <th data-key="dias">Dias</th>
          <th data-key="passos_medios">Passos médios</th>
          <th data-key="calorias_medias">Calorias médias</th>
          <th data-key="sono_medio_min">Sono médio (min)</th>
          <th data-key="sedentario_medio_min">Sedentário (min)</th>
          <th data-key="muito_ativo_medio_min">Muito ativo (min)</th>
        </tr>
      </thead>
      <tbody></tbody>
    </table>
  </div>

  <p class="small" style="margin-top:16px;">Dashboard gerado automaticamente via Python.</p>

  <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
  <script>
    const DATA = {json.dumps(data_payload)};

    // ---------- KPIs ----------
    const k = DATA.kpis;
    const kpisDiv = document.getElementById("kpis");
    const kpis = [
      {{v: k.users, l:"Usuários únicos"}},
      {{v: k.days, l:"Dias analisados"}},
      {{v: k.avg_steps.toLocaleString('pt-BR'), l:"Passos médios/dia"}},
      {{v: k.avg_cal.toLocaleString('pt-BR'), l:"Calorias médias/dia"}},
      {{v: k.avg_sleep.toLocaleString('pt-BR'), l:"Sono médio (min)"}},
      {{v: k.avg_sedent.toLocaleString('pt-BR'), l:"Sedentário (min)"}},
      {{v: k.avg_very_active.toLocaleString('pt-BR'), l:"Muito ativo (min)"}},
      {{v: "CSV limpo", l:"Entrega"}},
    ];
    kpis.forEach(x => {{
      const el = document.createElement("div");
      el.className = "card";
      el.innerHTML = `<div class="kpi">${{x.v}}</div><div class="label">${{x.l}}</div>`;
      kpisDiv.appendChild(el);
    }});

    document.getElementById("corr1").textContent = k.corr_steps_sleep;
    document.getElementById("corr2").textContent = k.corr_steps_cal;

    // ---------- Insights automáticos ----------
    const insight = document.getElementById("insightBox");
    const corrSleep = k.corr_steps_sleep;
    const corrCal = k.corr_steps_cal;

    let txt = "";
    txt += `<b>Leitura rápida:</b><br/>`;
    txt += `• Passos × Sono: correlação <b>${{corrSleep}}</b> → relação fraca (passos não explicam sono sozinhos).<br/>`;
    txt += `• Passos × Calorias: correlação <b>${{corrCal}}</b> → relação moderada (passos ajudam a explicar gasto calórico).<br/>`;
    txt += `<br/><b>Implicação Bellabeat:</b> atacar sedentarismo (muito alto) + metas progressivas de passos + rotinas de sono (conteúdo e lembretes).`;
    insight.innerHTML = txt;

    // ---------- Charts helpers ----------
    function makeBar(ctx, labels, values, title) {{
      return new Chart(ctx, {{
        type: 'bar',
        data: {{
          labels,
          datasets: [{{ label: title, data: values }}]
        }},
        options: {{
          responsive: true,
          plugins: {{ legend: {{ display:false }} }},
          scales: {{
            y: {{ beginAtZero: true }}
          }}
        }}
      }});
    }}

    // Passos por weekday
    makeBar(
      document.getElementById("chartStepsWeek"),
      DATA.steps_weekday.labels,
      DATA.steps_weekday.values.map(v => Math.round(v)),
      "Passos médios"
    );

    // Sono por weekday
    makeBar(
      document.getElementById("chartSleepWeek"),
      DATA.sleep_weekday.labels,
      DATA.sleep_weekday.values.map(v => Math.round(v)),
      "Sono médio (min)"
    );

    // Hist passos
    new Chart(document.getElementById("chartHistSteps"), {{
      type: 'bar',
      data: {{
        labels: DATA.hist_steps.labels,
        datasets: [{{ label: "Quantidade de dias", data: DATA.hist_steps.values }}]
      }},
      options: {{
        responsive: true,
        plugins: {{ legend: {{ display:false }} }},
        scales: {{ y: {{ beginAtZero:true }} }}
      }}
    }});

    // Scatter passos vs calorias
    new Chart(document.getElementById("chartScatter"), {{
      type: 'scatter',
      data: {{
        datasets: [{{
          label: "Passos vs Calorias",
          data: DATA.scatter_steps_cal
        }}]
      }},
      options: {{
        responsive: true,
        plugins: {{ legend: {{ display:false }} }},
        scales: {{
          x: {{ title: {{ display:true, text:"TotalSteps" }} }},
          y: {{ title: {{ display:true, text:"Calories" }} }}
        }}
      }}
    }});

    // ---------- Table (filter + sort) ----------
    let rows = DATA.table.slice();
    let sortKey = "Id";
    let sortAsc = true;

    const tbody = document.querySelector("#tbl tbody");
    const search = document.getElementById("search");

    function renderTable() {{
      const q = (search.value || "").trim();
      const filtered = rows.filter(r => String(r.Id).includes(q));

      tbody.innerHTML = "";
      filtered.forEach(r => {{
        const tr = document.createElement("tr");
        tr.innerHTML = `
          <td>${{r.Id}}</td>
          <td>${{r.dias}}</td>
          <td>${{r.passos_medios.toLocaleString('pt-BR')}}</td>
          <td>${{r.calorias_medias.toLocaleString('pt-BR')}}</td>
          <td>${{r.sono_medio_min}}</td>
          <td>${{r.sedentario_medio_min}}</td>
          <td>${{r.muito_ativo_medio_min}}</td>
        `;
        tbody.appendChild(tr);
      }});
    }}

    function sortBy(key) {{
      if (sortKey === key) sortAsc = !sortAsc;
      else {{ sortKey = key; sortAsc = true; }}

      rows.sort((a,b) => {{
        const av = a[key];
        const bv = b[key];
        if (av < bv) return sortAsc ? -1 : 1;
        if (av > bv) return sortAsc ? 1 : -1;
        return 0;
      }});
      renderTable();
    }}

    document.querySelectorAll("#tbl th").forEach(th => {{
      th.addEventListener("click", () => sortBy(th.dataset.key));
    }});

    search.addEventListener("input", renderTable);
    renderTable();
  </script>
</body>
</html>
"""

out_path = OUT_DIR / "dashboard_bellabeat.html"
out_path.write_text(html, encoding="utf-8")

print("✅ Dashboard criado:", out_path)
