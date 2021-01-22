"""Store a default model use case to use in the tests."""

from datetime import datetime
from typing import List, Optional

from repository_pattern import Entity

# Basic Entities


class Author(Entity):
    """Entity to model the author of a book."""

    id_: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    country: Optional[str] = None
    rating: Optional[int] = None


class Book(Entity):
    """Entity to model a book."""

    id_: int
    title: Optional[str] = None
    summary: Optional[str] = None
    released: Optional[datetime] = None
    rating: Optional[int] = None


class Genre(Entity):
    """Entity to model the genre of a book."""

    id_: int
    name: Optional[str] = None
    description: Optional[str] = None
    rating: Optional[int] = None


# Relationship entities


class ExtendingEntity(Author):
    """Entity to model an extending entity.

    It is a subclass of other entity to expand it's attributes.
    """

    style: Optional[str] = None


class ComposingEntity(Entity):
    """Entity to model a entity with a single composition relationship.

    It stores a Book object under the book attribute.
    """

    id_: int
    name: Optional[str] = None
    book: Optional[Book] = None


class MultipleSingleComposingEntity(Entity):
    """Entity to model an object with three single composition relationships.

    It's the source of all relationships.
    """

    id_: int
    name: Optional[str] = None
    book: Optional[Book] = None
    author: Optional[Author] = None
    genre: Optional[Genre] = None


class MultipleComposingEntity(Entity):
    """Entity to model a entity with a multiple composition relationship.

    It stores multiple Book objects under the books attribute.
    """

    id_: int
    name: Optional[str] = None
    books: List[Book] = []
