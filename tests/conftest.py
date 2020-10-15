"""
Module to store the classes and fixtures used throughout the tests.

Classes:

Fixtures:

"""

import os
import sqlite3
from typing import Generator

import pytest

pytest_plugins = ["tests.fixtures"]


@pytest.fixture
def sqlite_db(tmpdir) -> Generator[sqlite3.Cursor, None, None]:
    """
    Fixture to create an SQLite database engine.
    """

    sqlite_file_path = str(tmpdir.join("sqlite.db"))
    open(sqlite_file_path, "a").close()

    sqlite_url = f"sqlite:///{sqlite_file_path}"
    os.environ["REPOSITORY_DATABASE_URL"] = sqlite_url

    connection = sqlite3.connect(sqlite_file_path)

    yield connection.cursor()

    connection.close()
