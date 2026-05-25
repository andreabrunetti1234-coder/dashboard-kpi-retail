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

## Pubblicazione su GitHub

Nome repository consigliato: `dashboard-kpi-retail`

Descrizione breve consigliata:

```text
Dashboard KPI e reporting operativo su dataset retail simulato con Python, SQL/SQLite e HTML/CSS.
```

Il file `data/retail_orders.db` e' generato automaticamente dallo script e non va caricato se si usa Git; viene escluso da `.gitignore`. Per ricrearlo basta eseguire:

```powershell
python scripts/generate_data.py
```

## Insight principali da commentare

- Il canale online genera una quota rilevante dei ricavi, ma va monitorato rispetto a resi e marginalita.
- Le categorie con ricavi piu' alti non coincidono sempre con quelle a margine percentuale maggiore.
- Il tasso di reso e i giorni medi di consegna sono indicatori operativi utili per leggere la qualita del servizio.
- La vista mensile permette di individuare stagionalita, picchi e rallentamenti.

## Frase pronta per il CV

Dashboard KPI e reporting operativo su dataset retail simulato: data cleaning, analisi esplorativa, query SQL, calcolo KPI commerciali e costruzione di una dashboard HTML per monitorare ricavi, margine, ordini, canali e resi.
