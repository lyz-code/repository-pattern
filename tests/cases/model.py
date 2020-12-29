"""Store a default model use case to use in the tests."""

from datetime import datetime

from repository_pattern import Entity


class Author(Entity):
    """Entity to model the author of a book."""

    id_: str
    first_name: str
    last_name: str
    country: str


class Book(Entity):
    """Entity to model a book."""

    id_: int
    title: str
    summary: str
    released: datetime


class Genre(Entity):
    """Entity to model the genre of a book."""

    id_: int
    name: str
    description: str