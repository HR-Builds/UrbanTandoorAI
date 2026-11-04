from pathlib import Path
import re

import pandas as pd
from sqlalchemy import text

from db_connection import engine

BASE_DIR = Path(__file__).resolve().parent.parent
CSV_DIR = BASE_DIR / "outputs" / "cleaned"


def clean_table_name(filename):
    name = Path(filename).stem.lower()
    return re.sub(r"[^a-z0-9_]", "_", name)


def create_tables():
    csv_files = sorted(CSV_DIR.glob("*.csv"))

    if not csv_files:
        print("No CSV files found!")
        return

    with engine.begin() as connection:
        for csv_file in csv_files:
            table_name = clean_table_name(csv_file.name)

            df = pd.read_csv(csv_file, nrows=0, encoding="utf-8-sig")

            columns = []

            for column in df.columns:
                safe_column = re.sub(
                    r"[^a-zA-Z0-9_]", "_", str(column).strip()
                )

                if not safe_column:
                    raise ValueError(f"Invalid column in {csv_file.name}")

                columns.append(f'"{safe_column}" TEXT')

            sql = f"""
                CREATE TABLE IF NOT EXISTS "{table_name}" (
                    {", ".join(columns)}
                );
            """

            connection.execute(text(sql))
            print(f"Created table: {table_name}")

    print("\nDatabase table creation completed.")


if __name__ == "__main__":
    create_tables()