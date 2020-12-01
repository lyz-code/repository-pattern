"""Gather the cases and fixtures needed to test the FakeRepository."""

import pytest

from repository_pattern import Entity, FakeRepository


class FakeRepositoryTester:
    """Gathers methods needed to test the implementation of the FakeRepository."""

    def get_entity(self, repo: FakeRepository, entity: Entity) -> Entity:
        """Get the entity object from the data stored in the repository by it's id."""
        return repo.entities[type(entity)][entity.ID]

    def insert_entity(self, repo: FakeRepository, entity: Entity) -> None:
        """Insert the data of an entity into the repository."""
        try:
            repo.entities[type(entity)]
        except KeyError:
            repo.entities[type(entity)] = {}

        repo.entities[type(entity)][entity.ID] = entity


@pytest.fixture()
def repo_fake() -> FakeRepository:
    """Return an instance of the FakeRepository."""
    return FakeRepository()
