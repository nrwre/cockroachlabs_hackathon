"""Quick sanity check: list tables and vector indexes after init_db."""

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "src"))

from blackbox.db import connect  # noqa: E402


def main() -> None:
    with connect() as conn, conn.cursor() as cur:
        cur.execute(
            "SELECT table_name FROM information_schema.tables "
            "WHERE table_schema = 'public' ORDER BY table_name"
        )
        print("TABLES:", [r[0] for r in cur.fetchall()])

        cur.execute("SHOW INDEXES FROM incident_memory")
        idx = {r[1] for r in cur.fetchall()}  # index_name column
        print("incident_memory indexes:", sorted(idx))

        cur.execute("SHOW INDEXES FROM runbooks")
        idx = {r[1] for r in cur.fetchall()}
        print("runbooks indexes:", sorted(idx))


if __name__ == "__main__":
    main()
