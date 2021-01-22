"""Module to store the functions shared by the different adapters.

Abstract Classes:
    AbstractRepository: Gathers common methods and define the interface of the
        repositories.

References:
* https://lyz-code.github.io/blue-book/architecture/repository_pattern/
"""

import abc
import logging
from typing import Dict, List, Optional, Type, Union

from pydantic import BaseModel, validator  # pylint: disable=no-name-in-module

from ..model import EntityID, EntityType, Mapper

log = logging.getLogger(__name__)


class AbstractRepository(BaseModel, abc.ABC):
    """Gather common methods and define the interface of the repositories.

    Attributes:
        database_url: URL specifying the connection to the database.
    """

    database_url: str
    mapper: Mapper = None  # type: ignore

    @validator("mapper", pre=True, always=True)
    @classmethod
    def set_mapper(cls, mapper: Optional[Mapper]) -> Mapper:
        """Set the mapper in case it's not specified."""
        if mapper is None:
            return Mapper()
        return mapper

    @abc.abstractmethod
    def add(self, entity: EntityType) -> None:
        """Append an entity to the repository.

        Args:
            entity: Entity to add to the repository.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def get(
        self,
        entity_model: Type[EntityType],
        entity_id: EntityID,
    ) -> EntityType:
        """Obtain an entity from the repository by it's ID.

        Args:
            entity_model: Entity class to generate the object.
            entity_id: ID of the entity object to obtain.

        Returns:
            entity: Entity object with id entity_id.

        Raises:
            EntityNotFoundError: If the entity is not found.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def delete(self, entity: EntityType) -> None:
        """Delete an entity from the repository.

        Args:
            entity: Entity to remove from the repository.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def all(self, entity_model: Type[EntityType]) -> List[EntityType]:
        """Obtain all the entities of a type from the repository.

        Args:
            entity_model: Type of entity objects to obtain.

        Returns:
            entities: List of Entity object that matches the search criteria.

        Raises:
            EntityNotFoundError: If the entities are not found.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def commit(self) -> None:
        """Persist the changes into the repository."""
        raise NotImplementedError

    @abc.abstractmethod
    def search(
        self, entity_model: Type[EntityType], fields: Dict[str, Union[str, int]]
    ) -> List[EntityType]:
        """Obtain the entities whose attributes match one or several conditions.

        Args:
            entity_model: Type of entity object to obtain.
            fields: Dictionary with the {key}:{value} to search.

        Returns:
            entities: List of Entity object that matches the search criteria.

        Raises:
            EntityNotFoundError: If the entities are not found.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def apply_migrations(self, migrations_directory: str) -> None:
        """Run the migrations of the repository schema.

        Args:
            migrations_directory: path to the directory containing the migration
                scripts.
        """
        raise NotImplementedError
