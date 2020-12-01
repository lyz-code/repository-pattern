"""Gather the abstract classes used by the rest of the cases.

Import the created cases so they are easily accessible too.
"""

import abc
from typing import Tuple, TypeVar

from repository_pattern import AbstractRepository, Entity, FakeRepository

from .entities import EntityCases  # noqa
from .fake_repository import FakeRepositoryTester

RepositoryTester = TypeVar(
    "RepositoryTester", FakeRepositoryTester, FakeRepositoryTester
)


class RepositoryCases:  # noqa: R0903 Until we have more than one method
    """Gather all the repositories to test."""

    def case_fake(
        self, repo_fake: FakeRepository
    ) -> Tuple[FakeRepository, FakeRepositoryTester]:
        """Return the FakeRepository with it's tester."""
        return repo_fake, FakeRepositoryTester()


class AbstractRepositoryTester(abc.ABC):
    """Gather common methods and define the interface of the repository testers."""

    @abc.abstractmethod
    def get_entity(self, repo: AbstractRepository, entity: Entity) -> Entity:
        """Get the entity object from the data stored in the repository by it's id."""
        raise NotImplementedError

    @abc.abstractmethod
    def insert_entity(self, repo: FakeRepository, entity: Entity) -> None:
        """Insert the data of an entity into the repository."""
        raise NotImplementedError
