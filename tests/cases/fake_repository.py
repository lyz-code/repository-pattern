"""
Module to gather the cases and fixtures needed to test the FakeRepository.

Classes:
    FakeRepositoryTester: Gather the methods needed to test the particularities
        of the implementation of the FakeRepository.

Fixtures:
    repo_fake: Return an instance of the FakeRepository.
"""

import pytest

from repository_pattern import Entity, FakeRepository


class FakeRepositoryTester:
    """
    Class to gathers methods needed to test the particularities of the implementation of
    the FakeRepository.

    Methods:
        get_entity: Get the entity object from the data stored in the repository by it's
            id.
        insert_entity: Insert the data of an entity into the repository.
    """

    def get_entity(self, repo: FakeRepository, entity: Entity) -> Entity:
        """
        Function to get the entity object from the data stored in the repository by it's
            id.
        """

        return repo.entities[type(entity)][entity.id]

    def insert_entity(self, repo: FakeRepository, entity: Entity) -> None:
        """
        Function to insert the data of an entity into the repository.
        """

        try:
            repo.entities[type(entity)]
        except KeyError:
            repo.entities[type(entity)] = {}

        repo.entities[type(entity)][entity.id] = entity


@pytest.fixture
def repo_fake() -> FakeRepository:
    """
    Function to return an instance of the FakeRepository.
    """
    return FakeRepository()
