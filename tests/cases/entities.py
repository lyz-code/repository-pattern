"""Gather the cases and fixtures needed to test the model Entities."""

import factory

from .model import (
    Author,
    Book,
    ComposingEntity,
    ExtendingEntity,
    Genre,
    MultipleComposingEntity,
)

# Basic Entities


class EntityCases:
    """Gather all the entities to test."""

    def case_author(self) -> factory.Factory:
        """Return the Author factory."""
        return AuthorFactory

    def case_book(self) -> factory.Factory:
        """Return the Book factory."""
        return BookFactory

    def case_genre(self) -> factory.Factory:
        """Return the Genre factory."""
        return GenreFactory


class AuthorFactory(factory.Factory):  # type: ignore
    """Factory to generate fake authors."""

    id_ = factory.Faker("word")
    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")
    country = factory.Faker("country")
    rating = factory.Faker("pyint")

    class Meta:
        """Define the entity model object to use."""

        model = Author


class BookFactory(factory.Factory):  # type: ignore
    """Factory to generate fake books."""

    id_ = factory.Faker("pyint")
    title = factory.Faker("sentence")
    summary = factory.Faker("text")
    released = factory.Faker("date_time")
    rating = factory.Faker("pyint")

    class Meta:
        """Define the entity model object to use."""

        model = Book


class GenreFactory(factory.Factory):  # type: ignore
    """Factory to generate fake genres."""

    id_ = factory.Faker("pyint")
    name = factory.Faker("name")
    description = factory.Faker("sentence")
    rating = factory.Faker("pyint")

    class Meta:
        """Define the entity model object to use."""

        model = Genre


# Relationship entitites


class ExtendingEntityFactory(AuthorFactory):
    """Factory to generate fake ExtendingEntity entities."""

    style = factory.Faker("word")

    class Meta:
        """Define the entity model object to use."""

        model = ExtendingEntity


class ComposingEntityFactory(factory.Factory):  # type: ignore
    """Generate objects that model single composing relationships."""

    id_ = factory.Faker("pyint")
    name = factory.Faker("sentence")

    class Meta:
        """Define the entity model object to use."""

        model = ComposingEntity


class MultipleComposingEntityFactory(factory.Factory):  # type: ignore
    """Generate objects that model multiple composing relationships."""

    id_ = factory.Faker("pyint")
    name = factory.Faker("sentence")

    class Meta:
        """Define the entity model object to use."""

        model = MultipleComposingEntity
