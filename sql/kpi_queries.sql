-- KPI generali
SELECT
  COUNT(*) AS ordini,
  ROUND(SUM(revenue), 2) AS ricavi,
  ROUND(SUM(profit), 2) AS profitto,
  ROUND(SUM(profit) * 100.0 / SUM(revenue), 2) AS margine_percentuale,
  ROUND(AVG(revenue), 2) AS valore_medio_ordine,
  ROUND(AVG(returned) * 100.0, 2) AS tasso_reso
FROM orders;

-- Trend mensile
SELECT
  substr(order_date, 1, 7) AS mese,
  COUNT(*) AS ordini,
  ROUND(SUM(revenue), 2) AS ricavi,
  ROUND(SUM(profit), 2) AS profitto,
  ROUND(AVG(returned) * 100.0, 2) AS tasso_reso
FROM orders
GROUP BY mese
ORDER BY mese;

-- Performance per canale
SELECT
  channel AS canale,
  COUNT(*) AS ordini,
  ROUND(SUM(revenue), 2) AS ricavi,
  ROUND(SUM(profit), 2) AS profitto,
  ROUND(SUM(profit) * 100.0 / SUM(revenue), 2) AS margine_percentuale,
  ROUND(AVG(returned) * 100.0, 2) AS tasso_reso
FROM orders
GROUP BY channel
ORDER BY ricavi DESC;

-- Performance per categoria
SELECT
  category AS categoria,
  COUNT(*) AS ordini,
  ROUND(SUM(revenue), 2) AS ricavi,
  ROUND(SUM(profit), 2) AS profitto,
  ROUND(SUM(profit) * 100.0 / SUM(revenue), 2) AS margine_percentuale
FROM orders
GROUP BY category
ORDER BY ricavi DESC;
