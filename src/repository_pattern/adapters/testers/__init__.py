import abc
from typing import Any, Generic, List, Type

from _pytest.logging import LogCaptureFixture

from repository_pattern import Entity


class AbstractRepositoryTester(abc.ABC, Generic[Repository]):
    """Gather common methods and define the interface of the repository testers."""

    @abc.abstractmethod
    def assert_schema_exists(self, database: Any, caplog: LogCaptureFixture) -> None:
        """Make sure that the repository has a valid schema."""
        raise NotImplementedError

    @abc.abstractmethod
    def apply_migrations(self, repo: Repository) -> None:
        """Apply the repository migrations."""
        raise NotImplementedError

    @abc.abstractmethod
    def get_entity(self, database: Any, entity: Entity) -> Entity:
        """Get the entity object from the data stored in the repository by it's id."""
        raise NotImplementedError

    @abc.abstractmethod
    def get_all(self, database: Any, entity_model: Type[Entity]) -> List[Entity]:
        """Get all the entities of type entity_model from the database."""
        raise NotImplementedError

    @abc.abstractmethod
    def insert_entity(self, database: Any, entity: Entity) -> None:
        """Insert the data of an entity into the repository."""
        raise NotImplementedError
