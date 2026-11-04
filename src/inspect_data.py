
from pathlib import Path
import pandas as pd
from docx import Document

DATA_DIR = Path("data")

def inspect_excel(file_path):
    print(f"\n{'=' * 60}")
    print(f"EXCEL: {file_path.name}")
    print("=" * 60)

    workbook = pd.ExcelFile(file_path)

    for sheet in workbook.sheet_names:
        df = pd.read_excel(file_path, sheet_name=sheet)

        print(f"\nSheet: {sheet}")
        print(f"Rows: {len(df)} | Columns: {len(df.columns)}")
        print("Columns:", list(df.columns))
        print(df.head(3).to_string(index=False))

def inspect_docx(file_path):
    print(f"\n{'=' * 60}")
    print(f"DOCUMENT: {file_path.name}")
    print("=" * 60)

    document = Document(file_path)

    for paragraph in document.paragraphs:
        if paragraph.text.strip():
            print(paragraph.text.strip())

    for number, table in enumerate(document.tables, start=1):
        print(f"\nTable {number}")
        for row in table.rows:
            print(" | ".join(cell.text.strip() for cell in row.cells))

def main():
    for file_path in sorted(DATA_DIR.iterdir()):
        if file_path.suffix.lower() == ".xlsx":
            inspect_excel(file_path)
        elif file_path.suffix.lower() == ".docx":
            inspect_docx(file_path)

if __name__ == "__main__":
    main()
