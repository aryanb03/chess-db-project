# Chess DB Project (Top Players / Grand Chess Tour)

This repo contains the deliverables for the CS4092 final project adapted to the chess domain.

## Files
- `01_requirements.md` — Requirements doc (export to PDF for submission).
- `02_erd.dbml` — ER diagram (dbdiagram.io DBML). Import into https://dbdiagram.io → export as image/PDF.
- `03_schema_and_sample_data.sql` — Schema + sample data (SQLite-compatible).
- `04_example_queries.sql` — Example analytical SQL queries.
- `05_cli.py` — Python CLI demo (uses SQLite).

## Quick Start (Local)
```bash
# Create a virtual environment if desired (optional)
python3 -m venv .venv && source .venv/bin/activate

# Run the CLI; it will create chess.db and populate sample data
python 05_cli.py

# Example commands inside the CLI
list players
list tournaments
standings Sinquefield Cup
h2h Magnus Carlsen Hikaru Nakamura
games Fabiano Caruana
quit
```

## Export ER Diagram
1. Open https://dbdiagram.io and create a new diagram.
2. Paste contents of `02_erd.dbml`.
3. Use Export → PNG/PDF for the deliverable.

## Porting to PostgreSQL/MySQL
- Replace `INTEGER PRIMARY KEY AUTOINCREMENT` with serial/identity types.
- Ensure `TEXT` maps to suitable `VARCHAR` sizes as needed.
- Keep all foreign keys and uniques; add indexes on FK columns for performance.

## Notes
- Sample scores/ratings are illustrative for the assignment. Replace with authoritative data if required.
- The schema supports adding more events/players easily.
