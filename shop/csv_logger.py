import csv
import os
from django.conf import settings

CSV_FILE = os.path.join(settings.BASE_DIR, "transactions.csv")


def ensure_csv_exists():
    if not os.path.exists(CSV_FILE):
        with open(CSV_FILE, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["Name", "Action", "Amount", "DateTime"])


def log_transaction(name, action, amount, timestamp):
    ensure_csv_exists()

    with open(CSV_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            name,
            action,
            amount,
            timestamp.isoformat(),
        ])