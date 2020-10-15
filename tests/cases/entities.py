"""
Module to gather the cases and fixtures needed to test the model Entities.

Classes:
    EntityCases: Gathers all the entities to test.
"""

from tests import factories


class EntityCases:
    """
    Class to gather all the entities to test.

    Methods:
        case_book: Test the Book entity.
        case_author: Test the Author entity.
        case_genre: Test the Genre entity.
    """

    def case_author(self):
        return factories.AuthorFactory

    def case_book(self):
        return factories.BookFactory

    def case_genre(self):
        return factories.GenreFactory
