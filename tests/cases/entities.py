"""Gather the cases and fixtures needed to test the model Entities."""

import factory
from tests import factories


class EntityCases:
    """Gather all the entities to test."""

    def case_author(self) -> factory.Factory:
        """Return the Author factory."""
        return factories.AuthorFactory

    def case_book(self) -> factory.Factory:
        """Return the Book factory."""
        return factories.BookFactory

    def case_genre(self) -> factory.Factory:
        """Return the Genre factory."""
        return factories.GenreFactory
