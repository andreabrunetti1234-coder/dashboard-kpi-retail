from __future__ import annotations

import csv
import random
import sqlite3
from datetime import date, timedelta
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
DB_PATH = DATA_DIR / "retail_orders.db"
CSV_PATH = DATA_DIR / "orders.csv"


REGIONS = ["Centro", "Nord", "Sud", "Isole"]
CHANNELS = ["Online", "Store", "Partner"]
CATEGORIES = {
    "Elettronica": (65, 420, 0.68),
    "Casa": (20, 160, 0.58),
    "Sport": (25, 190, 0.62),
    "Moda": (18, 130, 0.54),
    "Beauty": (12, 95, 0.50),
}
SEGMENTS = ["Privati", "Studenti", "Professionisti", "PMI"]


def weighted_choice(items: list[tuple[str, float]]) -> str:
    total = sum(weight for _, weight in items)
    pick = random.uniform(0, total)
    current = 0.0
    for item, weight in items:
        current += weight
        if current >= pick:
            return item
    return items[-1][0]


def generate_orders(count: int = 950) -> list[dict[str, object]]:
    random.seed(42)
    start = date(2025, 1, 1)
    end = date(2025, 12, 31)
    days = (end - start).days
    rows: list[dict[str, object]] = []

    for index in range(1, count + 1):
        order_date = start + timedelta(days=random.randint(0, days))
        month_factor = 1.0 + (0.18 if order_date.month in {11, 12} else 0) + (0.10 if order_date.month in {5, 6} else 0)

        category = weighted_choice([
            ("Elettronica", 0.22),
            ("Casa", 0.20),
            ("Sport", 0.18),
            ("Moda", 0.25),
            ("Beauty", 0.15),
        ])
        min_price, max_price, cost_ratio = CATEGORIES[category]

        channel = weighted_choice([("Online", 0.52), ("Store", 0.31), ("Partner", 0.17)])
        region = weighted_choice([("Centro", 0.34), ("Nord", 0.30), ("Sud", 0.24), ("Isole", 0.12)])
        segment = weighted_choice([("Privati", 0.46), ("Studenti", 0.18), ("Professionisti", 0.24), ("PMI", 0.12)])

        quantity = random.choices([1, 2, 3, 4, 5], weights=[50, 28, 13, 6, 3])[0]
        unit_price = round(random.uniform(min_price, max_price) * month_factor, 2)
        discount = random.choice([0, 0, 0, 0.05, 0.10, 0.15])
        gross_revenue = unit_price * quantity
        revenue = round(gross_revenue * (1 - discount), 2)
        cost = round(revenue * cost_ratio * random.uniform(0.95, 1.08), 2)
        profit = round(revenue - cost, 2)

        return_probability = 0.045
        if channel == "Online":
            return_probability += 0.025
        if category in {"Moda", "Elettronica"}:
            return_probability += 0.02
        returned = 1 if random.random() < return_probability else 0

        delivery_base = {"Online": 3.8, "Partner": 4.6, "Store": 1.2}[channel]
        delivery_days = max(1, round(random.gauss(delivery_base, 1.1)))

        rows.append({
            "order_id": f"ORD-{index:05d}",
            "order_date": order_date.isoformat(),
            "region": region,
            "channel": channel,
            "category": category,
            "customer_segment": segment,
            "quantity": quantity,
            "unit_price": unit_price,
            "discount": discount,
            "revenue": revenue,
            "cost": cost,
            "profit": profit,
            "returned": returned,
            "delivery_days": delivery_days,
        })

    return rows


def write_csv(rows: list[dict[str, object]]) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with CSV_PATH.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def write_sqlite(rows: list[dict[str, object]]) -> None:
    if DB_PATH.exists():
        DB_PATH.unlink()

    with sqlite3.connect(DB_PATH) as conn:
        columns = ", ".join(rows[0].keys())
        placeholders = ", ".join("?" for _ in rows[0])
        conn.execute(
            """
            CREATE TABLE orders (
                order_id TEXT PRIMARY KEY,
                order_date TEXT NOT NULL,
                region TEXT NOT NULL,
                channel TEXT NOT NULL,
                category TEXT NOT NULL,
                customer_segment TEXT NOT NULL,
                quantity INTEGER NOT NULL,
                unit_price REAL NOT NULL,
                discount REAL NOT NULL,
                revenue REAL NOT NULL,
                cost REAL NOT NULL,
                profit REAL NOT NULL,
                returned INTEGER NOT NULL,
                delivery_days INTEGER NOT NULL
            )
            """
        )
        conn.executemany(
            f"INSERT INTO orders ({columns}) VALUES ({placeholders})",
            [tuple(row.values()) for row in rows],
        )
        conn.commit()


def main() -> None:
    rows = generate_orders()
    write_csv(rows)
    write_sqlite(rows)
    print(f"Creati {CSV_PATH} e {DB_PATH} con {len(rows)} ordini.")


if __name__ == "__main__":
    main()
