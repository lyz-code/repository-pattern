"""
Module to store the storage repository abstractions.

Abstract Classes:
    AbstractRepository: Gathers common methods and define the interface of the
        repositories.

References:
* https://lyz-code.github.io/blue-book/architecture/repository_pattern/
"""

import abc
import logging
from typing import Dict, List, Optional, Type

from ..model import Entity

log = logging.getLogger(__name__)


class AbstractRepository(abc.ABC):
    """
    Abstract class to gathers common methods and define the interface of the
    repositories.

    Properties:
        database_url: URL specifying the connection to the database.

    Abstract Methods:
        add: Append an entity to the repository.
        all: Obtain all the entities of a type from the repository.
        commit: Persist the changes into the repository.
        delete: Remove an entity from the repository.
        get: Obtain an entity from the repository by it's ID.
        search: Obtain the entities whose attribute match one or several conditions.
    """

    @abc.abstractmethod
    def __init__(self, database_url: Optional[str] = None) -> None:
        self.database_url = database_url

    @abc.abstractmethod
    def add(self, entity: Entity) -> None:
        """
        Method to append an entity to the repository.
        """

        raise NotImplementedError

    @abc.abstractmethod
    def delete(self, entity: Entity) -> None:
        """
        Method to delete an entity from the repository.
        """

        raise NotImplementedError

    @abc.abstractmethod
    def get(self, entity_model: Type[Entity], entity_id: str) -> Entity:
        """
        Method to obtain an entity from the repository by it's ID.
        """

        raise NotImplementedError

    @abc.abstractmethod
    def all(self, entity_model: Type[Entity]) -> List[Entity]:
        """
        Method to obtain all the entities of a type from the repository.
        """

        raise NotImplementedError

    @abc.abstractmethod
    def commit(self) -> None:
        """
        Method to persist the changes into the repository.
        """

        raise NotImplementedError

    @abc.abstractmethod
    def search(self, entity_model: Type[Entity], fields: Dict) -> List[Entity]:
        """
        Method to obtain the entities whose attributes match one or several conditions.

        fields is a dictionary with the {key}:{value} to search.

        If None is found an EntityNotFoundError is raised.
        """

        raise NotImplementedError
