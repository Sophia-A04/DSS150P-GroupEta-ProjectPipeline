from __future__ import annotations

import os
from pathlib import Path

import psycopg2


PROJECT_ROOT = Path(__file__).resolve().parents[2]

DEFAULT_SCHEMA_PATH = (
    PROJECT_ROOT
    / "sql"
    / "schema.sql"
)

REQUIRED_TABLES = {
    "countries",
    "fuel_types",
    "power_plants",
    "plant_generation",
    "country_emissions",
    "country_economic_indicators",
    "country_fuel_capacity",
}


def connection_parameters() -> dict:
    """
    Build PostgreSQL connection parameters from environment variables.

    Docker supplies these through .env / docker-compose.
    """
    return {
        "host": os.getenv(
            "POSTGRES_HOST",
            "localhost",
        ),
        "port": int(
            os.getenv(
                "POSTGRES_PORT",
                "5432",
            )
        ),
        "dbname": os.getenv(
            "POSTGRES_DB",
            "dss150p_db",
        ),
        "user": os.getenv(
            "POSTGRES_USER",
            "dss150p_user",
        ),
        "password": os.getenv(
            "POSTGRES_PASSWORD",
            "",
        ),
    }


def get_connection():
    """Open a PostgreSQL connection using project environment settings."""
    return psycopg2.connect(
        **connection_parameters()
    )


def apply_schema(
    connection,
    schema_path: str | Path = DEFAULT_SCHEMA_PATH,
) -> None:
    """Create the project relational schema."""
    schema_path = Path(
        schema_path
    )

    if not schema_path.exists():
        raise FileNotFoundError(
            f"PostgreSQL schema file not found: {schema_path}"
        )

    schema_sql = schema_path.read_text(
        encoding="utf-8"
    )

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                schema_sql
            )

        connection.commit()

    except Exception:
        connection.rollback()
        raise


def existing_project_tables(
    connection,
) -> set[str]:
    """Return project tables currently present in the public schema."""
    query = """
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema = 'public'
          AND table_type = 'BASE TABLE';
    """

    with connection.cursor() as cursor:
        cursor.execute(query)

        rows = cursor.fetchall()

    return {
        row[0]
        for row in rows
    }


def verify_schema(
    connection,
) -> set[str]:
    """
    Verify that all required Group Eta PostgreSQL tables exist.

    Returns the table-name set when validation succeeds.
    """
    tables = existing_project_tables(
        connection
    )

    missing = (
        REQUIRED_TABLES
        - tables
    )

    if missing:
        raise RuntimeError(
            "PostgreSQL schema is missing required tables: "
            + ", ".join(
                sorted(missing)
            )
        )

    return tables


def initialize_database(
    schema_path: str | Path = DEFAULT_SCHEMA_PATH,
) -> set[str]:
    """
    Connect to PostgreSQL, apply the schema,
    verify required tables, and close the connection.
    """
    connection = get_connection()

    try:
        apply_schema(
            connection,
            schema_path,
        )

        return verify_schema(
            connection
        )

    finally:
        connection.close()


def main() -> int:
    try:
        tables = initialize_database()

    except Exception as error:
        print(
            "PostgreSQL schema initialization FAILED:"
        )
        print(error)
        return 1

    print(
        "PostgreSQL schema initialization PASSED"
    )

    print(
        "Tables:",
        ", ".join(
            sorted(
                REQUIRED_TABLES
            )
        ),
    )

    print(
        "Verified table count:",
        len(
            REQUIRED_TABLES
            & tables
        ),
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(
        main()
    )