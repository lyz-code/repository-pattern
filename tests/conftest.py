"""
Module to store the classes and fixtures used throughout the tests.

Classes:

Fixtures:

"""

import os
import sqlite3
from typing import Generator

import pytest
from py.path import local  # noqa: E0401, E0611, local does exist in py.path

pytest_plugins = ["tests.fixtures"]


@pytest.fixture()
def sqlite_db(tmpdir: local) -> Generator[sqlite3.Cursor, None, None]:
    """Create an SQLite database engine."""
    sqlite_file_path = str(tmpdir.join("sqlite.db"))
    open(sqlite_file_path, "a").close()

    sqlite_url = f"sqlite:///{sqlite_file_path}"
    os.environ["REPOSITORY_DATABASE_URL"] = sqlite_url

    connection = sqlite3.connect(sqlite_file_path)

    yield connection.cursor()

    connection.close()
