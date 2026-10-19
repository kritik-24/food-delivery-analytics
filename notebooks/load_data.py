
import os
from pathlib import Path

import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL

ROOT = Path(__file__).resolve().parent.parent
CSV_PATH = ROOT / "data" / "raw" / "food_delivery_orders.csv"

# Enter your PostgreSQL password when prompted in the terminal.
import getpass
password = getpass.getpass("PostgreSQL password for user postgres: ")

url = URL.create(
    drivername="postgresql+psycopg",
    username="postgres",
    password=password,
    host="localhost",
    port=5432,
    database="food_delivery_analytics",
)

def main():
    if not CSV_PATH.exists():
        raise FileNotFoundError(f"CSV not found: {CSV_PATH}")

    df = pd.read_csv(CSV_PATH)

    print(f"CSV loaded: {len(df)} rows, {len(df.columns)} columns")

    engine = create_engine(url, pool_pre_ping=True)

    try:
        with engine.begin() as connection:
            # Replace any partial/empty table data with the CSV.
            df.head(0).to_sql(
                "food_delivery_orders",
                connection,
                if_exists="replace",
                index=False,
            )

            df.to_sql(
                "food_delivery_orders",
                connection,
                if_exists="append",
                index=False,
                chunksize=100,
                method="multi",
            )

            count = connection.execute(
                text("SELECT COUNT(*) FROM food_delivery_orders")
            ).scalar_one()

        print(f"SUCCESS: {count} rows loaded into PostgreSQL.")

    except Exception as exc:
        print(f"\nDATABASE ERROR: {type(exc).__name__}")
        print(str(exc.orig) if getattr(exc, "orig", None) else str(exc))
        raise SystemExit(1)

    finally:
        engine.dispose()

if __name__ == "__main__":
    main()

