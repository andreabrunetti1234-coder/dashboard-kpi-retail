# Dashboard KPI e Reporting Operativo

Progetto portfolio junior Data Analyst basato su un dataset retail simulato. L'obiettivo e' costruire un report operativo sintetico per monitorare vendite, marginalita, canali, categorie e resi.

## Obiettivo

Analizzare un flusso ordini e-commerce e trasformarlo in KPI leggibili per supportare decisioni operative:

- ricavi totali e trend mensile;
- margine lordo e margine percentuale;
- valore medio ordine;
- tasso di reso;
- performance per canale, area geografica, categoria e segmento cliente.

## Dataset

Il dataset e' simulato e contiene ordini retail del 2025. Ogni riga rappresenta un ordine con:

- data ordine;
- area geografica;
- canale di vendita;
- categoria prodotto;
- segmento cliente;
- quantita, prezzo, sconto;
- ricavi, costi, profitto;
- eventuale reso;
- giorni di consegna.

Questa scelta rende il progetto condivisibile pubblicamente senza dati personali o aziendali reali.

## Strumenti utilizzati

- Python per generazione dati, aggregazioni e costruzione del report;
- SQLite e SQL per interrogare i dati;
- HTML/CSS/JavaScript per la dashboard;
- CSV come formato dati semplice e leggibile.

## Struttura

```text
portfolio-dashboard-kpi/
  data/orders.csv
  dashboard/index.html
  output/kpi_summary.json
  output/report.md
  scripts/generate_data.py
  scripts/build_dashboard.py
  sql/kpi_queries.sql
```

## Come rigenerare il progetto

Da questa cartella:

```powershell
python scripts/generate_data.py
python scripts/build_dashboard.py
```

Aprire poi `dashboard/index.html` nel browser.


