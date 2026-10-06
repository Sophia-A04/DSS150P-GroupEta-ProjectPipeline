from __future__ import annotations

from pathlib import Path

import pytest

from src.load import postgres_loader


class FakeCursor:
    def __init__(
        self,
        rows=None,
    ):
        self.rows = rows or []
        self.executed = []

    def __enter__(self):
        return self

    def __exit__(
        self,
        exc_type,
        exc,
        traceback,
    ):
        return False

    def execute(
        self,
        query,
    ):
        self.executed.append(
            query
        )

    def fetchall(self):
        return self.rows


class FakeConnection:
    def __init__(
        self,
        rows=None,
    ):
        self.cursor_object = FakeCursor(
            rows
        )
        self.committed = False
        self.rolled_back = False
        self.closed = False

    def cursor(self):
        return self.cursor_object

    def commit(self):
        self.committed = True

    def rollback(self):
        self.rolled_back = True

    def close(self):
        self.closed = True


def test_connection_parameters(
    monkeypatch,
):
    monkeypatch.setenv(
        "POSTGRES_HOST",
        "postgres",
    )

    monkeypatch.setenv(
        "POSTGRES_PORT",
        "5432",
    )

    monkeypatch.setenv(
        "POSTGRES_DB",
        "eta",
    )

    monkeypatch.setenv(
        "POSTGRES_USER",
        "eta_user",
    )

    monkeypatch.setenv(
        "POSTGRES_PASSWORD",
        "secret",
    )

    params = (
        postgres_loader
        .connection_parameters()
    )

    assert params == {
        "host": "postgres",
        "port": 5432,
        "dbname": "eta",
        "user": "eta_user",
        "password": "secret",
    }


def test_apply_schema_executes_sql(
    tmp_path,
):
    schema_path = (
        tmp_path
        / "schema.sql"
    )

    schema_path.write_text(
        "CREATE TABLE example (id INTEGER);",
        encoding="utf-8",
    )

    connection = FakeConnection()

    postgres_loader.apply_schema(
        connection,
        schema_path,
    )

    assert connection.committed
    assert not connection.rolled_back

    assert (
        "CREATE TABLE example"
        in connection
        .cursor_object
        .executed[0]
    )


def test_apply_schema_missing_file():
    connection = FakeConnection()

    with pytest.raises(
        FileNotFoundError,
    ):
        postgres_loader.apply_schema(
            connection,
            Path(
                "does-not-exist.sql"
            ),
        )


def test_verify_schema_passes():
    rows = [
        (table,)
        for table in sorted(
            postgres_loader
            .REQUIRED_TABLES
        )
    ]

    connection = FakeConnection(
        rows
    )

    result = (
        postgres_loader
        .verify_schema(
            connection
        )
    )

    assert (
        postgres_loader
        .REQUIRED_TABLES
        <= result
    )


def test_verify_schema_detects_missing():
    connection = FakeConnection(
        [
            ("countries",),
            ("power_plants",),
        ]
    )

    with pytest.raises(
        RuntimeError,
        match="missing required tables",
    ):
        postgres_loader.verify_schema(
            connection
        )