"""Apply db/schema.sql to your CockroachDB cluster.

Run once after your cluster exists and `.env` is filled in:

    python scripts/init_db.py

It reads the schema file and executes it. Safe to re-run — every statement uses
IF NOT EXISTS.
"""

from __future__ import annotations

import pathlib
import sys

# Make `import blackbox` work when running this script directly.
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "src"))

from blackbox.db import connect  # noqa: E402

SCHEMA_PATH = pathlib.Path(__file__).resolve().parent.parent / "db" / "schema.sql"


def main() -> None:
    sql = SCHEMA_PATH.read_text(encoding="utf-8")
    print(f"Applying {SCHEMA_PATH} ...")
    with connect() as conn:
        with conn.cursor() as cur:
            cur.execute(sql)
        conn.commit()
    print("✅ Schema applied.")


if __name__ == "__main__":
    main()
