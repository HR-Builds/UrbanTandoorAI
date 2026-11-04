# UrbanTandoorAI - Restaurant Data Engineering Pipeline

## Project Overview
UrbanTandoorAI is a restaurant data engineering project designed to ingest, validate, clean, and load restaurant menu and inventory datasets into PostgreSQL.

The project uses source Excel and Word documents provided for Urban Tandoor & Grill.

## Phase 01 — Data Engineering Pipeline

### Features
- Excel and Word source data inspection
- Data quality validation
- CSV data extraction and cleaning
- PostgreSQL database integration
- Automated database table creation
- CSV-to-PostgreSQL data loading
- End-to-end pipeline execution

### Technologies
- Python 3
- Pandas
- PostgreSQL 18
- SQLAlchemy
- Psycopg
- python-dotenv
- OpenPyXL
- python-docx

## Project Structure

```text
UrbanTandoorAI/
├── data/
├── src/
│   ├── ingestion/
│   ├── validation/
│   ├── inspect_data.py
│   ├── validate_data.py
│   ├── export_data.py
│   ├── db_connection.py
│   ├── create_tables.py
│   ├── load_data.py
│   └── run_pipeline.py
├── outputs/
│   └── cleaned/
├── reports/
├── .env
├── .gitignore
└── README.md
```

## Database
Database: `urban_tandoor_ai`

Database tables: 19

## Data Processing Results

| Dataset | Records |
|---|---:|
| Menu Items | 118 |
| Ingredients | 60 |
| Recipes | 130 |
| Branches | 2 |
| Variants | 148 |
| Add-ons | 10 |

- CSV exports generated: 19
- Validation errors: 0
- Validation warnings: 0
- PostgreSQL connection: Successful
- Full pipeline execution: Successful

## Run the Project

Install dependencies:

```bash
pip install pandas openpyxl sqlalchemy "psycopg[binary]" python-dotenv python-docx
```

Configure your `.env` file:

```env
DB_HOST=localhost
DB_PORT=5432
DB_NAME=urban_tandoor_ai
DB_USER=postgres
DB_PASSWORD=your_password
```

Run the complete pipeline:

```bash
python src/run_pipeline.py
```

## Important Notes
- Source datasets are retained separately from cleaned exports.
- Database staging tables currently use TEXT columns.
- Inventory snapshots are not live stock guarantees.
- Menu orderability requires branch, variant, and inventory checks.
- Restaurant prices and operational information are illustrative and require verification before production use.

## Project Status
**Phase 01 — Data Engineering Pipeline: Completed**

Future phases can include structured database schemas, live inventory management, restaurant APIs, and AI-powered ordering assistance.
