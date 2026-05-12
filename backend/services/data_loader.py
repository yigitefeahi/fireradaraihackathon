from __future__ import annotations

import csv
import os
from datetime import date, datetime
from pathlib import Path
from typing import Any


DATA_DIR = Path(__file__).resolve().parent.parent / "data"


def _parse_value(value: str) -> Any:
    value = value.strip()
    if value == "":
        return None

    for parser in (int, float):
        try:
            return parser(value)
        except ValueError:
            pass

    for fmt in ("%Y-%m-%d", "%d.%m.%Y"):
        try:
            return datetime.strptime(value, fmt).date().isoformat()
        except ValueError:
            pass

    return value


def load_csv(filename: str) -> list[dict[str, Any]]:
    path = DATA_DIR / filename
    if not path.exists():
        return []

    with path.open("r", encoding="utf-8-sig", newline="") as csv_file:
        reader = csv.DictReader(csv_file)
        return [
            {key: _parse_value(value or "") for key, value in row.items()}
            for row in reader
        ]


def load_products() -> list[dict[str, Any]]:
    return load_csv("products.csv")


def load_orders() -> list[dict[str, Any]]:
    return load_csv("orders.csv")


def load_customers() -> list[dict[str, Any]]:
    return load_csv("customers.csv")


def load_sales_history() -> list[dict[str, Any]]:
    return load_csv("sales_history.csv")


def load_messages() -> list[dict[str, Any]]:
    return load_csv("messages.csv")


def load_all_data() -> dict[str, list[dict[str, Any]]]:
    return {
        "products": load_products(),
        "orders": load_orders(),
        "customers": load_customers(),
        "sales_history": load_sales_history(),
        "messages": load_messages(),
    }


def today_iso() -> str:
    demo_today = os.getenv("DEMO_TODAY")
    if demo_today:
        return demo_today
    return date.today().isoformat()


def get_today() -> date:
    return datetime.strptime(today_iso(), "%Y-%m-%d").date()
