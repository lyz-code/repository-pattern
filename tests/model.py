"""
Module to store a default model use case to use in the tests.

Classes:
    Author:
    Book:
    Genre:
"""

from datetime import datetime

from repository_pattern import Entity


class Author(Entity):
    id: str
    first_name: str
    last_name: str
    country: str


class Book(Entity):
    id: int
    title: str
    summary: str
    released: datetime


class Genre(Entity):
    id: int
    name: str
    description: str
