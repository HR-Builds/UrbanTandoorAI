
from pathlib import Path
import hashlib
import re

import pandas as pd
from sqlalchemy import text

from db_connection import engine

BASE_DIR = Path(__file__).resolve().parent.parent
CSV_DIR = BASE_DIR / "outputs" / "cleaned"


def load_data():
    csv_files = sorted(CSV_DIR.glob("*.csv"))

    with engine.begin() as connection:
        connection.execute(text("""
            CREATE TABLE IF NOT EXISTS pipeline_manifest (
                filename TEXT PRIMARY KEY,
                file_hash TEXT NOT NULL,
                loaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """))

        for csv_file in csv_files:
            table = re.sub(r"[^a-z0-9_]", "_", csv_file.stem.lower())
            file_hash = hashlib.sha256(csv_file.read_bytes()).hexdigest()

            previous = connection.execute(text("""
                SELECT file_hash FROM pipeline_manifest
                WHERE filename = :filename
            """), {"filename": csv_file.name}).scalar()

            if previous == file_hash:
                print(f"Unchanged - skipped: {csv_file.name}")
                continue

            df = pd.read_csv(csv_file, encoding="utf-8-sig", dtype=str)
            df.columns = [
                re.sub(r"[^a-zA-Z0-9_]", "_", str(c).strip())
                for c in df.columns
            ]
            df = df.where(pd.notna(df), None)

            connection.execute(text(f"""
                CREATE TABLE IF NOT EXISTS "{table}" (
                    {', '.join(f'"{c}" TEXT' for c in df.columns)}
                )
            """))

            existing_columns = {
                row[0] for row in connection.execute(text("""
                    SELECT column_name
                    FROM information_schema.columns
                    WHERE table_name = :table
                """), {"table": table})
            }

            for column in df.columns:
                if column not in existing_columns:
                    connection.execute(text(
                        f'ALTER TABLE "{table}" ADD COLUMN "{column}" TEXT'
                    ))

            connection.execute(text(f'DELETE FROM "{table}"'))

            if not df.empty:
                df.to_sql(
                    table,
                    con=connection,
                    if_exists="append",
                    index=False,
                    method="multi",
                    chunksize=500
                )

            connection.execute(text("""
                INSERT INTO pipeline_manifest (filename, file_hash, loaded_at)
                VALUES (:filename, :hash, CURRENT_TIMESTAMP)
                ON CONFLICT (filename)
                DO UPDATE SET
                    file_hash = EXCLUDED.file_hash,
                    loaded_at = CURRENT_TIMESTAMP
            """), {"filename": csv_file.name, "hash": file_hash})

            print(f"Updated {table}: {len(df)} records")

    print("Incremental loading completed!")


if __name__ == "__main__":
    load_data()
