"""
Module to gather the abstract classes used by the rest of the cases and to import the
created cases so they are easily accessible.

Classes:
    EntityCases: Gathers all the entities to test.
    RepositoryCases: Gathers all the repositories to test.

Abstract Classes:
    AbstractRepositoryTester: Define the interface of the repository testers.
"""

import abc
from typing import Tuple, TypeVar

from repository_pattern import AbstractRepository, Entity, FakeRepository

from .entities import EntityCases  # noqa
from .fake_repository import FakeRepositoryTester

RepositoryTester = TypeVar(
    "RepositoryTester", FakeRepositoryTester, FakeRepositoryTester
)


class RepositoryCases:
    """
    Class to gather all the repositories to test.

    Methods:
        case_fake: Test the FakeRepository.
    """

    def case_fake(self, repo_fake) -> Tuple[FakeRepository, FakeRepositoryTester]:
        return repo_fake, FakeRepositoryTester()


class AbstractRepositoryTester(abc.ABC):
    """
    Abstract class to gathers common methods and define the interface of the
    repository testers.

    Abstract Methods:
        get_entity: Get the entity object from the data stored in the repository by it's
            id.
        insert_entity: Insert the data of an entity into the repository.
    """

    @abc.abstractmethod
    def get_entity(self, repo: AbstractRepository, entity: Entity) -> Entity:
        """
        Function to get the entity object from the data stored in the repository by it's
            id.
        """

        raise NotImplementedError

    @abc.abstractmethod
    def insert_entity(self, repo: FakeRepository, entity: Entity) -> None:
        """
        Function to insert the data of an entity into the repository.
        """

        raise NotImplementedError
