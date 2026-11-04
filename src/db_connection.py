import os
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL

# Load project environment variables
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

# Read database credentials
database_url = URL.create(
    drivername="postgresql+psycopg",
    username=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    host=os.getenv("DB_HOST"),
    port=int(os.getenv("DB_PORT", "5432")),
    database=os.getenv("DB_NAME"),
)

# Create database engine
engine = create_engine(
    database_url,
    pool_pre_ping=True,
)

def test_connection():
    try:
        with engine.connect() as connection:
            result = connection.execute(
                text("SELECT current_database(), version()")
            )
            database, version = result.fetchone()

            print("Database connection successful!")
            print(f"Database: {database}")
            print(f"PostgreSQL: {version}")

    except Exception as error:
        print("Database connection failed!")
        print(f"Error: {error}")

if __name__ == "__main__":
    test_connection()