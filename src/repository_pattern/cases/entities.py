"""Gather the cases and fixtures needed to test the model Entities."""

import factory

from repository_pattern import Entity


class EntityCases:
    """Gather all the entities to test."""

    def case_entity(self) -> factory.Factory:
        """Return the basic Entity factory."""
        return EntityFactory


class EntityFactory(factory.Factory):  # type: ignore
    """Factory to generate a fake entity."""

    ID = factory.Faker("word")

    class Meta:
        """Define the entity model object to use."""

        model = Entity
