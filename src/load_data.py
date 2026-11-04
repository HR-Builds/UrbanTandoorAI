from pathlib import Path
import re

import pandas as pd
from sqlalchemy import text

from db_connection import engine

BASE_DIR = Path(__file__).resolve().parent.parent
CSV_DIR = BASE_DIR / "outputs" / "cleaned"


def load_data():
    csv_files = sorted(CSV_DIR.glob("*.csv"))

    if not csv_files:
        print("No CSV files found!")
        return

    with engine.begin() as connection:
        for csv_file in csv_files:
            table_name = re.sub(
                r"[^a-z0-9_]", "_", csv_file.stem.lower()
            )

            df = pd.read_csv(
                csv_file,
                encoding="utf-8-sig",
                dtype=str
            )

            df = df.where(pd.notna(df), None)

            connection.execute(
                text(f'DELETE FROM "{table_name}"')
            )

            if not df.empty:
                df.to_sql(
                    table_name,
                    con=connection,
                    if_exists="append",
                    index=False,
                    method="multi",
                    chunksize=500
                )

            print(
                f"Loaded {len(df)} records into {table_name}"
            )

    print("\nCSV data loading completed successfully.")


if __name__ == "__main__":
    load_data()