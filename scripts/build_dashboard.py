from __future__ import annotations

import json
import sqlite3
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
OUTPUT_DIR = ROOT / "output"
DASHBOARD_DIR = ROOT / "dashboard"
DB_PATH = DATA_DIR / "retail_orders.db"
SUMMARY_PATH = OUTPUT_DIR / "kpi_summary.json"
REPORT_PATH = OUTPUT_DIR / "report.md"
DASHBOARD_PATH = DASHBOARD_DIR / "index.html"


def query_all(conn: sqlite3.Connection, sql: str) -> list[dict[str, object]]:
    conn.row_factory = sqlite3.Row
    return [dict(row) for row in conn.execute(sql).fetchall()]


def query_one(conn: sqlite3.Connection, sql: str) -> dict[str, object]:
    conn.row_factory = sqlite3.Row
    return dict(conn.execute(sql).fetchone())


def build_summary() -> dict[str, object]:
    if not DB_PATH.exists():
        raise FileNotFoundError("Database non trovato. Esegui prima scripts/generate_data.py")

    with sqlite3.connect(DB_PATH) as conn:
        overview = query_one(
            conn,
            """
            SELECT
              COUNT(*) AS orders,
              ROUND(SUM(revenue), 2) AS revenue,
              ROUND(SUM(profit), 2) AS profit,
              ROUND(SUM(profit) * 100.0 / SUM(revenue), 2) AS margin_rate,
              ROUND(AVG(revenue), 2) AS avg_order_value,
              ROUND(AVG(returned) * 100.0, 2) AS return_rate,
              ROUND(AVG(delivery_days), 2) AS avg_delivery_days
            FROM orders
            """,
        )
        monthly = query_all(
            conn,
            """
            SELECT
              substr(order_date, 1, 7) AS month,
              COUNT(*) AS orders,
              ROUND(SUM(revenue), 2) AS revenue,
              ROUND(SUM(profit), 2) AS profit,
              ROUND(AVG(returned) * 100.0, 2) AS return_rate
            FROM orders
            GROUP BY month
            ORDER BY month
            """,
        )
        by_channel = query_all(
            conn,
            """
            SELECT
              channel,
              COUNT(*) AS orders,
              ROUND(SUM(revenue), 2) AS revenue,
              ROUND(SUM(profit), 2) AS profit,
              ROUND(SUM(profit) * 100.0 / SUM(revenue), 2) AS margin_rate,
              ROUND(AVG(returned) * 100.0, 2) AS return_rate
            FROM orders
            GROUP BY channel
            ORDER BY revenue DESC
            """,
        )
        by_category = query_all(
            conn,
            """
            SELECT
              category,
              COUNT(*) AS orders,
              ROUND(SUM(revenue), 2) AS revenue,
              ROUND(SUM(profit), 2) AS profit,
              ROUND(SUM(profit) * 100.0 / SUM(revenue), 2) AS margin_rate
            FROM orders
            GROUP BY category
            ORDER BY revenue DESC
            """,
        )
        by_region = query_all(
            conn,
            """
            SELECT
              region,
              COUNT(*) AS orders,
              ROUND(SUM(revenue), 2) AS revenue,
              ROUND(SUM(profit), 2) AS profit
            FROM orders
            GROUP BY region
            ORDER BY revenue DESC
            """,
        )

    return {
        "overview": overview,
        "monthly": monthly,
        "by_channel": by_channel,
        "by_category": by_category,
        "by_region": by_region,
    }


def euro(value: float) -> str:
    return f"EUR {value:,.0f}".replace(",", ".")


def write_report(summary: dict[str, object]) -> None:
    overview = summary["overview"]
    channels = summary["by_channel"]
    categories = summary["by_category"]
    monthly = summary["monthly"]

    top_channel = channels[0]
    top_category = categories[0]
    best_month = max(monthly, key=lambda row: row["revenue"])

    text = f"""# Report operativo - KPI retail

## Sintesi

Il dataset contiene {overview["orders"]} ordini simulati. I ricavi totali sono pari a {euro(overview["revenue"])}, con un profitto lordo di {euro(overview["profit"])} e un margine medio del {overview["margin_rate"]}%.

## KPI principali

- Ricavi totali: {euro(overview["revenue"])}
- Profitto lordo: {euro(overview["profit"])}
- Valore medio ordine: {euro(overview["avg_order_value"])}
- Tasso di reso: {overview["return_rate"]}%
- Giorni medi di consegna: {overview["avg_delivery_days"]}

## Insight

- Il canale con ricavi maggiori e' {top_channel["channel"]}, con {euro(top_channel["revenue"])} di ricavi e margine del {top_channel["margin_rate"]}%.
- La categoria principale per ricavi e' {top_category["category"]}, con {euro(top_category["revenue"])}.
- Il mese migliore per ricavi e' {best_month["month"]}, con {euro(best_month["revenue"])}.
- Il tasso di reso va monitorato insieme al canale e alla categoria, per distinguere crescita dei ricavi da qualita operativa.

## Possibili azioni

- Approfondire categorie ad alto fatturato ma margine piu' basso.
- Monitorare il canale online rispetto a resi e tempi di consegna.
- Usare la vista mensile per pianificare campagne commerciali e stock.
"""
    REPORT_PATH.write_text(text, encoding="utf-8")


def write_dashboard(summary: dict[str, object]) -> None:
    data_json = json.dumps(summary, ensure_ascii=False)
    html = f"""<!doctype html>
<html lang="it">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Dashboard KPI Retail</title>
  <style>
    :root {{
      --bg: #f5f7fb;
      --panel: #ffffff;
      --ink: #17212b;
      --muted: #5b6673;
      --line: #dde5ef;
      --accent: #0b5cad;
      --accent-2: #16837a;
      --warn: #b45309;
    }}

    * {{ box-sizing: border-box; }}

    body {{
      margin: 0;
      background: var(--bg);
      color: var(--ink);
      font-family: Arial, Helvetica, sans-serif;
      line-height: 1.45;
    }}

    main {{
      width: min(1180px, calc(100% - 32px));
      margin: 0 auto;
      padding: 28px 0 40px;
    }}

    header {{
      display: flex;
      justify-content: space-between;
      gap: 24px;
      align-items: end;
      margin-bottom: 18px;
      border-bottom: 1px solid var(--line);
      padding-bottom: 16px;
    }}

    h1 {{
      margin: 0 0 6px;
      font-size: 30px;
      letter-spacing: 0;
    }}

    .subtitle {{
      margin: 0;
      color: var(--muted);
      max-width: 760px;
    }}

    .badge {{
      border: 1px solid var(--line);
      background: #ffffff;
      color: var(--muted);
      padding: 8px 10px;
      font-size: 13px;
      white-space: nowrap;
    }}

    .kpi-grid {{
      display: grid;
      grid-template-columns: repeat(5, 1fr);
      gap: 12px;
      margin-bottom: 16px;
    }}

    .kpi,
    .panel {{
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 6px;
    }}

    .kpi {{
      padding: 14px;
      min-height: 96px;
    }}

    .kpi span {{
      display: block;
      color: var(--muted);
      font-size: 13px;
      margin-bottom: 8px;
    }}

    .kpi strong {{
      display: block;
      font-size: 24px;
      line-height: 1.1;
    }}

    .layout {{
      display: grid;
      grid-template-columns: 1.45fr 1fr;
      gap: 14px;
      align-items: start;
    }}

    .panel {{
      padding: 16px;
      margin-bottom: 14px;
    }}

    h2 {{
      margin: 0 0 12px;
      font-size: 17px;
      letter-spacing: 0;
    }}

    .chart {{
      display: grid;
      gap: 9px;
    }}

    .bar-row {{
      display: grid;
      grid-template-columns: 74px 1fr 92px;
      gap: 10px;
      align-items: center;
      font-size: 13px;
    }}

    .bar-track {{
      height: 12px;
      background: #e8eef5;
      overflow: hidden;
      border-radius: 999px;
    }}

    .bar {{
      height: 100%;
      background: var(--accent);
      border-radius: 999px;
    }}

    .bar.alt {{ background: var(--accent-2); }}

    table {{
      width: 100%;
      border-collapse: collapse;
      font-size: 13px;
    }}

    th,
    td {{
      padding: 8px 6px;
      border-bottom: 1px solid var(--line);
      text-align: right;
    }}

    th:first-child,
    td:first-child {{
      text-align: left;
    }}

    th {{
      color: var(--muted);
      font-weight: 700;
    }}

    .insights {{
      margin: 0;
      padding-left: 18px;
      color: var(--ink);
    }}

    .insights li {{
      margin: 7px 0;
    }}

    @media (max-width: 900px) {{
      .kpi-grid,
      .layout {{
        grid-template-columns: 1fr;
      }}

      header {{
        display: block;
      }}

      .badge {{
        display: inline-block;
        margin-top: 12px;
      }}
    }}
  </style>
</head>
<body>
  <main>
    <header>
      <div>
        <h1>Dashboard KPI Retail</h1>
        <p class="subtitle">Report operativo su dataset retail simulato: ricavi, marginalita, ordini, canali, categorie, resi e tempi di consegna.</p>
      </div>
      <div class="badge">Dataset simulato | 2025</div>
    </header>

    <section class="kpi-grid" id="kpis"></section>

    <div class="layout">
      <div>
        <section class="panel">
          <h2>Trend mensile ricavi</h2>
          <div class="chart" id="monthlyChart"></div>
        </section>

        <section class="panel">
          <h2>Performance per canale</h2>
          <table id="channelTable"></table>
        </section>
      </div>

      <div>
        <section class="panel">
          <h2>Ricavi per categoria</h2>
          <div class="chart" id="categoryChart"></div>
        </section>

        <section class="panel">
          <h2>Insight operativi</h2>
          <ul class="insights" id="insights"></ul>
        </section>
      </div>
    </div>
  </main>

  <script>
    const data = {data_json};

    const eur = value => new Intl.NumberFormat('it-IT', {{
      style: 'currency',
      currency: 'EUR',
      maximumFractionDigits: 0
    }}).format(value);

    const pct = value => `${{Number(value).toFixed(1)}}%`;

    const overview = data.overview;
    const kpis = [
      ['Ricavi', eur(overview.revenue)],
      ['Profitto lordo', eur(overview.profit)],
      ['Margine', pct(overview.margin_rate)],
      ['Valore medio ordine', eur(overview.avg_order_value)],
      ['Tasso reso', pct(overview.return_rate)]
    ];

    document.querySelector('#kpis').innerHTML = kpis.map(([label, value]) => `
      <article class="kpi"><span>${{label}}</span><strong>${{value}}</strong></article>
    `).join('');

    function renderBars(target, rows, labelKey, valueKey, alt = false) {{
      const max = Math.max(...rows.map(row => row[valueKey]));
      document.querySelector(target).innerHTML = rows.map(row => {{
        const width = Math.max(4, Math.round((row[valueKey] / max) * 100));
        return `
          <div class="bar-row">
            <span>${{row[labelKey]}}</span>
            <div class="bar-track"><div class="bar ${{alt ? 'alt' : ''}}" style="width: ${{width}}%"></div></div>
            <strong>${{eur(row[valueKey])}}</strong>
          </div>
        `;
      }}).join('');
    }}

    renderBars('#monthlyChart', data.monthly, 'month', 'revenue');
    renderBars('#categoryChart', data.by_category, 'category', 'revenue', true);

    document.querySelector('#channelTable').innerHTML = `
      <thead>
        <tr>
          <th>Canale</th>
          <th>Ordini</th>
          <th>Ricavi</th>
          <th>Margine</th>
          <th>Resi</th>
        </tr>
      </thead>
      <tbody>
        ${{data.by_channel.map(row => `
          <tr>
            <td>${{row.channel}}</td>
            <td>${{row.orders}}</td>
            <td>${{eur(row.revenue)}}</td>
            <td>${{pct(row.margin_rate)}}</td>
            <td>${{pct(row.return_rate)}}</td>
          </tr>
        `).join('')}}
      </tbody>
    `;

    const topChannel = data.by_channel[0];
    const topCategory = data.by_category[0];
    const bestMonth = [...data.monthly].sort((a, b) => b.revenue - a.revenue)[0];
    const worstReturn = [...data.by_channel].sort((a, b) => b.return_rate - a.return_rate)[0];

    document.querySelector('#insights').innerHTML = [
      `Il canale principale per ricavi e' <strong>${{topChannel.channel}}</strong> con ${{eur(topChannel.revenue)}}.`,
      `La categoria con ricavi piu' alti e' <strong>${{topCategory.category}}</strong>.`,
      `Il mese migliore e' <strong>${{bestMonth.month}}</strong>, utile per leggere stagionalita e picchi commerciali.`,
      `Il canale da monitorare per i resi e' <strong>${{worstReturn.channel}}</strong>, con tasso reso pari a ${{pct(worstReturn.return_rate)}}.`
    ].map(item => `<li>${{item}}</li>`).join('');
  </script>
</body>
</html>
"""
    DASHBOARD_PATH.write_text(html, encoding="utf-8")


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    DASHBOARD_DIR.mkdir(parents=True, exist_ok=True)
    summary = build_summary()
    SUMMARY_PATH.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    write_report(summary)
    write_dashboard(summary)
    print(f"Creati {SUMMARY_PATH}, {REPORT_PATH} e {DASHBOARD_PATH}.")


if __name__ == "__main__":
    main()
