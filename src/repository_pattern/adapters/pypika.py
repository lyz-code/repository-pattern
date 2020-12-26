"""Define the Pypika Repository."""

import logging
import os
import sqlite3
from typing import Dict, List, Type, Union

from pypika import Query, Table
from yoyo import get_backend, read_migrations

from ..exceptions import EntityNotFoundError
from ..model import Entity
from . import AbstractRepository

log = logging.getLogger(__name__)


class PypikaRepository(AbstractRepository):
    """Implement the repository pattern using the Pypika query builder."""

    def __init__(self, database_url: str) -> None:
        """Initialize the repository attributes."""
        super().__init__(database_url)
        database_file = database_url.replace("sqlite:///", "")
        if not os.path.isfile(database_file):
            raise ConnectionError(f"There is no database file: {database_file}")
        self.connection = sqlite3.connect(database_file)
        self.cursor = self.connection.cursor()

    def _execute(self, query: Query) -> sqlite3.Cursor:
        """Execute an SQL statement from a Pypika query object.

        Args:
            query: Pypika query
        """
        return self.cursor.execute(str(query))

    @staticmethod
    def _table(entity: Entity) -> Table:
        """Return the table of the selected entity object."""
        return Table(entity.__class__.__name__.lower())

    @staticmethod
    def _table_model(entity_model: Type[Entity]) -> Table:
        """Return the table of the selected entity class."""
        return Table(entity_model.__name__.lower())

    def add(self, entity: Entity) -> None:
        """Append an entity to the repository.

        Args:
            entity: Entity to add to the repository.
        """
        table = self._table(entity)
        columns = list(entity.dict().keys())
        columns[columns.index("id_")] = "id"
        values = [value for key, value in entity.dict().items()]
        query = Query.into(table).columns(tuple(columns)).insert(tuple(values))
        self._execute(query)

    def delete(self, entity: Entity) -> None:
        """Delete an entity from the repository.

        Args:
            entity: Entity to remove from the repository.

        Raises:
            EntityNotFoundError: If the entity is not found.
        """
        table = self._table(entity)
        try:
            self.get(type(entity), entity.id_)
        except EntityNotFoundError as error:
            raise EntityNotFoundError(
                f"Unable to delete entity {entity} because it's not in the repository"
            ) from error
        query = Query.from_(table).delete().where(table.id == entity.id_)
        self._execute(query)

    def get(self, entity_model: Type[Entity], entity_id: Union[str, int]) -> Entity:
        """Obtain an entity from the repository by it's ID.

        Args:
            entity_model: Type of entity object to obtain.
            entity_id: ID of the entity object to obtain.

        Returns:
            entity: Entity object that matches the search criteria.

        Raises:
            EntityNotFoundError: If the entity is not found.
        """
        table = self._table_model(entity_model)
        query = Query.from_(table).select("*").where(table.id == entity_id)

        try:
            return self._build_entities(entity_model, query)[0]
        except IndexError as error:
            raise EntityNotFoundError(
                f"There are no {entity_model.__name__}s with id {entity_id} in the"
                " repository."
            ) from error

    def all(self, entity_model: Type[Entity]) -> List[Entity]:
        """Obtain all the entities of a type from the repository.

        Args:
            entity_model: Type of entity objects to obtain.

        Returns:
            entities: List of Entity object that matches the search criteria.

        Raises:
            EntityNotFoundError: If the entities are not found.
        """
        table = self._table_model(entity_model)
        query = Query.from_(table).select("*")

        entities = self._build_entities(entity_model, query)
        if len(entities) == 0:
            raise EntityNotFoundError(
                f"There are no {entity_model.__name__}s entities in the repository"
            )

        return entities

    def _build_entities(self, entity_model: Type[Entity], query: Query) -> List[Entity]:
        """Build Entity objects from the data extracted from the database.

        Args:
            entity_model: The model of the entity to build
            query: pypika query of the entities you want to build
        """
        cursor = self._execute(query)

        entities_data = cursor.fetchall()
        attributes = [description[0] for description in cursor.description]

        entities: List[Entity] = []
        for entity_data in entities_data:
            entity_dict = {
                attributes[index]: entity_data[index]
                for index in range(0, len(entity_data))
            }
            entity_dict["id_"] = entity_dict.pop("id")

            entities.append(entity_model(**entity_dict))
        return entities

    def commit(self) -> None:
        """Persist the changes into the repository."""
        self.connection.commit()

    def search(
        self, entity_model: Type[Entity], fields: Dict[str, Union[str, int]]
    ) -> List[Entity]:
        """Obtain the entities whose attributes match one or several conditions.

        Args:
            entity_model: Type of entity object to obtain.
            fields: Dictionary with the {key}:{value} to search.

        Returns:
            entities: List of Entity object that matches the search criteria.

        Raises:
            EntityNotFoundError: If the entities are not found.
        """
        table = self._table_model(entity_model)
        query = Query.from_(table).select("*")

        for key, value in fields.items():
            if key == "id_":
                key = "id"
            query = query.where(getattr(table, key) == value)

        entities = self._build_entities(entity_model, query)

        if len(entities) == 0:
            raise EntityNotFoundError(
                f"There are no {entity_model.__name__}s that match the search filter"
                f" {fields}"
            )

        return entities

    def apply_migrations(self, migrations_directory: str) -> None:
        """Run the migrations of the repository schema.

        Args:
            migrations_directory: path to the directory containing the migration
                scripts.
        """
        backend = get_backend(self.database_url)
        migrations = read_migrations(migrations_directory)

        with backend.lock():
            log.info("Running database migrations")
            try:
                backend.apply_migrations(backend.to_apply(migrations))
            except Exception as error:  # noqa: W0703
                # We need to add tests for this function and use a less generic
                # exception
                log.error("Error running database migrations")
                log.error(error)

                log.debug("Rolling back the database migrations")
                try:
                    backend.rollback_migrations(backend.to_rollback(migrations))
                except Exception as error:  # noqa: W0703
                    # We need to add tests for this function and use a less generic
                    # exception
                    log.error("Error rolling back database migrations")
                    log.error(error)
                    raise error
            log.debug("Complete running database migrations")
