
from pathlib import Path
import pandas as pd
import json

DATA_DIR = Path("data")
OUTPUT_DIR = Path("outputs/cleaned")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

WORKBOOKS = {
    "menu": DATA_DIR / "Urban_Tandoor_Complete_Menu_Catalog.xlsx",
    "inventory": DATA_DIR / "Urban_Tandoor_Two_Branch_Inventory_Dataset.xlsx",
}

def clean_dataframe(df):
    # Remove completely empty rows and columns
    df = df.dropna(how="all").dropna(axis=1, how="all")

    # Normalize column names
    df.columns = [str(col).strip() for col in df.columns]

    # Trim whitespace from text fields
    for column in df.select_dtypes(include="object").columns:
        df[column] = df[column].apply(
            lambda value: value.strip() if isinstance(value, str) else value
        )

    return df

def export_workbook(name, file_path):
    workbook = pd.read_excel(file_path, sheet_name=None)
    exported = {}

    for sheet_name, df in workbook.items():
        if sheet_name in ["START_HERE", "Dashboard"]:
            continue

        cleaned = clean_dataframe(df)

        filename = f"{name}_{sheet_name.lower()}.csv"
        output_path = OUTPUT_DIR / filename

        cleaned.to_csv(output_path, index=False, encoding="utf-8-sig")

        exported[sheet_name] = {
            "file": filename,
            "rows": len(cleaned),
            "columns": len(cleaned.columns),
        }

        print(f"Exported: {filename} | Rows: {len(cleaned)}")

    return exported

def main():
    results = {}

    for name, file_path in WORKBOOKS.items():
        if not file_path.exists():
            raise FileNotFoundError(f"Source file not found: {file_path}")

        print(f"\nProcessing: {file_path.name}")
        results[name] = export_workbook(name, file_path)

    report_path = OUTPUT_DIR / "export_manifest.json"
    report_path.write_text(
        json.dumps(results, indent=4),
        encoding="utf-8"
    )

    print("\nExport completed successfully.")
    print(f"Manifest: {report_path}")

if __name__ == "__main__":
    main()
