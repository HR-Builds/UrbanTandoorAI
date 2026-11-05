
from pathlib import Path
import hashlib
import json

import pandas as pd
from docx import Document
from fastembed import TextEmbedding
from sqlalchemy import text

from db_connection import engine

BASE_DIR = Path(__file__).resolve().parent.parent
CSV_DIR = BASE_DIR / "outputs" / "cleaned"
DATA_DIR = BASE_DIR / "data"

MODEL_NAME = "BAAI/bge-small-en-v1.5"


def collect_documents():
    documents = []

    for file in sorted(CSV_DIR.glob("*.csv")):
        df = pd.read_csv(file, encoding="utf-8-sig", dtype=str).fillna("")

        for index, row in df.iterrows():
            content = " | ".join(
                f"{col}: {value}"
                for col, value in row.items()
                if str(value).strip()
            )

            if content.strip():
                documents.append({
                    "source": file.name,
                    "key": str(index),
                    "content": content[:4000]
                })

    for file in DATA_DIR.glob("*.docx"):
        doc = Document(file)
        parts = [p.text.strip() for p in doc.paragraphs if p.text.strip()]

        for table in doc.tables:
            for row in table.rows:
                parts.append(" | ".join(c.text.strip() for c in row.cells))

        content = "\n".join(parts)

        if content.strip():
            documents.append({
                "source": file.name,
                "key": "profile",
                "content": content[:4000]
            })

    return documents


def main():
    documents = collect_documents()

    if not documents:
        raise RuntimeError("No documents found.")

    with engine.begin() as connection:
        connection.execute(text("""
            CREATE TABLE IF NOT EXISTS document_embeddings (
                document_id VARCHAR(64) PRIMARY KEY,
                source_file TEXT NOT NULL,
                record_key TEXT NOT NULL,
                content TEXT NOT NULL,
                metadata JSONB NOT NULL,
                embedding JSONB NOT NULL,
                model_name TEXT NOT NULL,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(source_file, record_key)
            )
        """))

        existing_rows = connection.execute(text("""
            SELECT source_file, record_key, content
            FROM document_embeddings
        """)).fetchall()

        existing = {
            (row.source_file, row.record_key): row.content
            for row in existing_rows
        }

        changed = [
            item for item in documents
            if existing.get((item["source"], item["key"])) != item["content"]
        ]

        unchanged = len(documents) - len(changed)

        print(f"Unchanged documents skipped: {unchanged}")
        print(f"New/modified documents: {len(changed)}")

        if not changed:
            print("All embeddings are up to date!")
            return

        model = TextEmbedding(model_name=MODEL_NAME)

        for start in range(0, len(changed), 32):
            batch = changed[start:start + 32]
            vectors = list(model.embed([item["content"] for item in batch]))

            for item, vector in zip(batch, vectors):
                doc_id = hashlib.sha256(
                    f'{item["source"]}:{item["key"]}'.encode()
                ).hexdigest()

                connection.execute(text("""
                    INSERT INTO document_embeddings
                    (document_id, source_file, record_key, content,
                     metadata, embedding, model_name, updated_at)
                    VALUES (
                        :id, :source, :key, :content,
                        CAST(:metadata AS jsonb),
                        CAST(:embedding AS jsonb),
                        :model, CURRENT_TIMESTAMP
                    )
                    ON CONFLICT (source_file, record_key)
                    DO UPDATE SET
                        document_id = EXCLUDED.document_id,
                        content = EXCLUDED.content,
                        metadata = EXCLUDED.metadata,
                        embedding = EXCLUDED.embedding,
                        model_name = EXCLUDED.model_name,
                        updated_at = CURRENT_TIMESTAMP
                """), {
                    "id": doc_id,
                    "source": item["source"],
                    "key": item["key"],
                    "content": item["content"],
                    "metadata": json.dumps({
                        "source": item["source"],
                        "record_key": item["key"]
                    }),
                    "embedding": json.dumps(vector.tolist()),
                    "model": MODEL_NAME
                })

            print(f"Processed {min(start + 32, len(changed))}/{len(changed)}")

    print("Incremental embeddings completed!")


if __name__ == "__main__":
    main()
