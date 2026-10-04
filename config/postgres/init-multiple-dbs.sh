#!/bin/bash
# config/postgres/init-multiple-dbs.sh
# Runs once on first container startup. Creates additional databases
# from the POSTGRES_MULTIPLE_DATABASES env var (comma-separated).
# Skips databases that already exist (e.g., POSTGRES_DB, which the
# official entrypoint creates automatically).

set -e

if [ -n "$POSTGRES_MULTIPLE_DATABASES" ]; then
    echo "Multiple database creation requested: $POSTGRES_MULTIPLE_DATABASES"
    for db in $(echo "$POSTGRES_MULTIPLE_DATABASES" | tr ',' ' '); do
        echo "  Checking database: $db"
        exists=$(psql --username "$POSTGRES_USER" -d postgres -tA -c "SELECT 1 FROM pg_database WHERE datname='$db'")
        if [ "$exists" = "1" ]; then
            echo "    Database $db already exists, skipping."
        else
            echo "    Creating database: $db"
            psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" -d postgres <<-EOSQL
                CREATE DATABASE $db;
EOSQL
        fi
    done
    echo "Database initialization complete."
fi