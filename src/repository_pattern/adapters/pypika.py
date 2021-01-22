"""Define the Pypika Repository."""

import logging
import os
import re
import sqlite3
from contextlib import suppress
from typing import Any, Dict, List, Tuple, Type, Union

from pydantic import root_validator
from pypika import Criterion, Field, Query, Table
from yoyo import get_backend, read_migrations

from ..exceptions import EntityNotFoundError
from ..model import (
    EntityAttrs,
    EntityComposition,
    EntityExtension,
    EntityID,
    EntityMultipleComposition,
    EntityType,
    RelationshipType,
)
from . import AbstractRepository

log = logging.getLogger(__name__)

MixedEntityAttrs = Dict[str, Any]


class PypikaRepository(AbstractRepository):
    """Implement the repository pattern using the Pypika query builder."""

    connection: sqlite3.Connection
    cursor: sqlite3.Cursor

    # R0903: too few methods, but it's how pydantic objects are defined.
    class Config:  # noqa: R0903
        """Configure the pydantic model."""

        arbitrary_types_allowed = True

    @root_validator(pre=True)
    @classmethod
    def set_connection(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        """Set the connection to the database.

        Raises:
            ConnectionError: If there is no database file.
        """
        database_file = values["database_url"].replace("sqlite:///", "")
        if not os.path.isfile(database_file):
            raise ConnectionError(f"There is no database file: {database_file}")
        connection = sqlite3.connect(database_file)
        values["connection"] = connection
        values["cursor"] = connection.cursor()

        return values

    def _execute(self, query: Union[Query, str]) -> sqlite3.Cursor:
        """Execute an SQL statement from a Pypika query object.

        Args:
            query: Pypika query
        """
        return self.cursor.execute(str(query))

    def add(self, entity: EntityType) -> None:
        """Append an entity to the repository.

        Args:
            entity: Entity to add to the repository.
        """
        entity_attributes, post_queries = self._clean_relationships(entity)
        self._add_entity(entity, entity_attributes)
        for post_query in post_queries:
            self._execute(post_query)

    def _clean_relationships(self, entity: EntityType) -> Tuple[EntityAttrs, List[str]]:
        """Process relationships to prepare the entity to be added to the repository.

        Modify the entity with each type of relationship removing mapped attributes
        and populate the required ones to be persisted in the repository.

        Args:
            entity: Entity to clean.

        Returns:
            entity_attributes: cleaned entity attributes.
            post_query: Query to be executed after the entity is added.
        """
        entity_attributes = entity.dict()
        post_queries: List[str] = []
        for relationship in self.mapper.get_relationships(entity):
            if not relationship.is_source(entity):
                continue
            if relationship.is_(EntityExtension):
                entity_attributes = self._add_entity_extension(
                    relationship, entity, entity_attributes
                )
            elif relationship.is_(EntityComposition):
                entity_attributes = self._add_single_composition(
                    relationship, entity, entity_attributes
                )
            elif relationship.is_(EntityMultipleComposition):
                entity_attributes, local_post_queries = self._add_multiple_composition(
                    relationship, entity, entity_attributes
                )
                post_queries += local_post_queries
        return entity_attributes, post_queries

    def _add_entity_extension(
        self,
        relationship: RelationshipType,
        entity: EntityType,
        entity_attributes: EntityAttrs,
    ) -> EntityAttrs:
        """Create required objects defined by the EntityExtension relationship.

        As the source_id == destination_id == 'id_' this relationship is meant to
        extend the destination object with the attributes defined in the source object.
        So if we're adding the extending, it makes sense to create the extended too.

        Args:
            relationship: Object containing the relationship information.
            entity: Entity to clean.
            entity_attributes: Entity attributes to clean.

        Returns:
            entity_attributes: Entity attributes without the extended entity attributes.
        """
        if relationship.is_source(entity):
            destination_attributes = {"id_": entity.id_}
            destination_columns = relationship.destination.schema()["properties"].keys()
            for attribute, value in entity_attributes.copy().items():
                if attribute in destination_columns:
                    destination_attributes[attribute] = value
                    if attribute != "id_":
                        del entity_attributes[attribute]
            self.add(relationship.destination(**destination_attributes))
        return entity_attributes

    def _add_single_composition(
        self,
        relationship: RelationshipType,
        entity: EntityType,
        entity_attributes: EntityAttrs,
    ) -> EntityAttrs:
        """Create required objects defined by the EntityComposition relationship.

        Also clean the entity attributes of ORM mapped objects.

        Args:
            relationship: Object containing the relationship information.
            entity: Entity to clean.
            entity_attributes: Entity attributes to clean.

        Returns:
            entity_attributes: Entity attributes without the mapped attribute.
        """
        if relationship.is_source(entity):
            populated_entity = getattr(entity, relationship.source_attribute)
            if populated_entity is not None:
                self.add(populated_entity)
                entity_attributes[relationship.source_id] = populated_entity.id_
            else:
                entity_attributes[relationship.source_id] = None
            del entity_attributes[relationship.source_attribute]
        return entity_attributes

    def _add_multiple_composition(
        self,
        relationship: RelationshipType,
        entity: EntityType,
        entity_attributes: EntityAttrs,
    ) -> Tuple[EntityAttrs, List[str]]:
        """Create required objects defined by the EntityMultipleComposition relationship.

        Also clean the entity attributes of ORM mapped objects.

        Args:
            relationship: Object containing the relationship information.
            entity: Entity to clean.
            entity_attributes: Entity attributes to clean.

        Returns:
            entity_attributes: Entity attributes without the mapped attribute.
            relationship_query: SQL to populate the relationship table.
        """
        # Prepare the queries
        post_queries: List[str] = []
        relationship_table = Table(
            f"{relationship.source.class_name()}_"
            f"{relationship.destination.class_name()}_relationship"
        )
        columns = (
            f"{relationship.source.class_name()}_id",
            f"{relationship.destination.class_name()}_id",
        )
        relationship_source_column = getattr(relationship_table, columns[0])
        relationship_destination_column = getattr(relationship_table, columns[1])
        values = []

        # Extract the persisted referenced objects in the repository
        existing_entities_query = (
            Query()
            .from_(relationship_table)
            .select(relationship_destination_column)
            .where(relationship_source_column == entity.id_)
        )
        existing_entity_ids = [
            data[0] for data in self._execute(existing_entities_query).fetchall()
        ]

        # Persist the current referenced objects
        populated_entities = getattr(entity, relationship.source_attribute)
        if populated_entities is not None:
            for populated_entity in populated_entities:
                self.add(populated_entity)
                if populated_entity.id_ not in existing_entity_ids:
                    values.append((entity.id_, populated_entity.id_))
                with suppress(ValueError):
                    existing_entity_ids.remove(populated_entity.id_)
            query = _upsert(relationship_table, columns, tuple(values), mode="pass")
            if query != "":
                post_queries.append(query)
        del entity_attributes[relationship.source_attribute]

        # Remove the relationship with the entities that are no longer referenced
        if len(existing_entity_ids) > 0:
            query = str(
                Query()
                .from_(relationship_table)
                .delete()
                .where(
                    Criterion.any(
                        [
                            relationship_destination_column == id_
                            for id_ in existing_entity_ids
                        ]
                    )
                )
            )
            post_queries.append(query)

        return entity_attributes, post_queries

    def _add_entity(self, entity: EntityType, entity_attributes: EntityAttrs) -> None:
        """Add an cleaned entity to the repository.

        Args:
            entity: Entity to add to the repository.
            entity_attributes: Changes on the Entity attributes.
        """
        table = _table(entity)
        columns = tuple(entity_attributes.keys())
        values = tuple(value for key, value in entity_attributes.items())
        upsert_query = _upsert(table, columns, values)

        self._execute(upsert_query)

    def get(
        self,
        entity_model: Type[EntityType],
        entity_id: EntityID,
    ) -> EntityType:
        """Obtain an entity from the repository by it's ID.

        Args:
            entity_model: Type of entity object to obtain.
            entity_id: ID of the entity object to obtain.

        Returns:
            entity: Entity object with id entity_id.

        Raises:
            EntityNotFoundError: If the entity is not found.
        """
        query = self._build_get_query(entity_model, entity_id)

        entities_attributes = self._build_entities_attributes(query)

        if len(entities_attributes) == 0:
            raise EntityNotFoundError(
                f"There are no {entity_model.class_name()}s"
                f" with id {entity_id} in the repository."
            )

        return self._load_relationships(entity_model, entities_attributes)

    def _build_get_query(
        self,
        entity_model: Type[EntityType],
        entity_id: EntityID,
    ) -> EntityAttrs:
        """Build the query to return an entity by it's ID.

        Args:
            entity_model: Type of entity object to obtain.
            entity_id: ID of the entity object to obtain.

        Returns:
            query: Query to obtain the Entity data.
        """
        source_table = _table(entity_model)
        columns = _get_select_columns(source_table, entity_model)
        query = Query.from_(source_table)

        for relationship in self.mapper.get_relationships(entity_model):
            if not relationship.is_source(entity_model):
                if relationship.is_(EntityExtension):
                    raise EntityNotFoundError(
                        f"Entity with ID {entity_id} is of type {relationship.source} "
                        f"instead of {relationship.destination}"
                    )

                continue
            if relationship.is_(EntityExtension):
                query, columns = self._build_entity_extension_query(
                    relationship, query, columns
                )
            elif relationship.is_(EntityComposition):
                query, columns = self._build_entity_composition_query(
                    relationship, query, columns
                )
            elif relationship.is_(EntityMultipleComposition):
                query, columns = self._build_entity_multiple_composition_query(
                    relationship, query, columns
                )
        return (
            query.select(*columns).where(source_table.id_ == entity_id).orderby("id_")
        )

    @staticmethod
    def _build_entity_extension_query(
        relationship: RelationshipType,
        query: Query,
        columns: List[Field],
    ) -> Tuple[Query, List[Field]]:
        """Extend query to add the EntityExtension relationship information.

        Args:
            relationship: Object containing the relationship information.
            query: Query to extend.
            columns: List of select columns with the alias set.

        Returns:
            query: Updated query.
            columns: List of select columns with the alias set.
        """
        source_table = _table(relationship.source)
        destination_table = _table(relationship.destination)

        query = query.join(destination_table).using("id_")

        # Rewrite the origin of the extended data table from the extending to the
        # extended.
        for attribute in relationship.destination.attributes().keys():
            columns = _delete_select_column_attribute(
                source_table,
                relationship.source,
                attribute,
                columns,
            )
            columns.append(
                _add_select_column_attribute(
                    destination_table, relationship.destination, attribute
                )
            )

        return query, columns

    @staticmethod
    def _build_entity_composition_query(
        relationship: RelationshipType,
        query: Query,
        columns: List[Field],
    ) -> Query:
        """Extend query to add the EntityComposition relationship information.

        Args:
            relationship: Object containing the relationship information.
            query: Query to extend.
            columns: List of select columns with the alias set.

        Returns:
            query: Updated query.
            columns: List of select columns with the alias set.
        """
        source_table = _table(relationship.source)
        source_join_id = getattr(source_table, relationship.source_id)
        destination_table = _table(relationship.destination)
        destination_join_id = getattr(destination_table, relationship.destination_id)

        query = query.left_join(destination_table).on(
            source_join_id == destination_join_id
        )

        # Load the source entity attribute that links both entities.
        columns.append(
            _add_select_column_attribute(
                source_table, relationship.source, relationship.source_id
            )
        )
        # Load the related entity attributes.
        columns += _get_select_columns(destination_table, relationship.destination)
        # Remove the ORM populated source entity attribute.
        columns = _delete_select_column_attribute(
            source_table, relationship.source, relationship.source_attribute, columns
        )

        return query, columns

    @staticmethod
    def _build_entity_multiple_composition_query(
        relationship: RelationshipType,
        query: Query,
        columns: List[Field],
    ) -> Query:
        """Extend query to add the EntityMultipleComposition relationship information.

        Args:
            relationship: Object containing the relationship information.
            query: Query to extend.
            columns: List of select columns with the alias set.

        Returns:
            query: Updated query.
            columns: List of select columns with the alias set.

        Raises:
            EntityNotFoundError: When asking for the extended entity class with the
                extending entity object id.
        """
        source_table = _table(relationship.source)
        source_join_id = getattr(source_table, relationship.source_id)
        destination_table = _table(relationship.destination)
        destination_join_id = getattr(destination_table, relationship.destination_id)
        join_table = Table(
            f"{relationship.source.class_name()}_"
            f"{relationship.destination.class_name()}_relationship"
        )
        join_table_source_id = getattr(
            join_table, f"{relationship.source.class_name()}_id"
        )
        join_table_destination_id = getattr(
            join_table, f"{relationship.destination.class_name()}_id"
        )

        query = (
            query.left_outer_join(join_table)
            .on(source_join_id == join_table_source_id)
            .left_outer_join(destination_table)
            .on(destination_join_id == join_table_destination_id)
        )

        # Load the related entity attributes.
        columns += _get_select_columns(destination_table, relationship.destination)
        # Remove the ORM populated source entity attribute.
        columns = _delete_select_column_attribute(
            source_table, relationship.source, relationship.source_attribute, columns
        )

        return query, columns

    def _build_entities_attributes(self, query: Query) -> List[MixedEntityAttrs]:
        """Build the attributes of the Entity objects from database data.

        The keys of the mixed_entities_attributes are in the form of
        f"{entity_type}.{entity_attribute}" so we can deserialize it in later steps.

        Args:
            query: pypika query of the entities you want to build

        Returns:
            mixed_entities_attributes: Populated list of entity attributes.
        """
        entities_attributes: List[MixedEntityAttrs] = []

        cursor = self._execute(query)
        entities_data = cursor.fetchall()
        attributes = [description[0] for description in cursor.description]

        for entity_data in entities_data:
            entity_dict = {
                attributes[index]: entity_data[index]
                for index in range(0, len(entity_data))
            }

            entities_attributes.append(entity_dict)

        return entities_attributes

    def _load_relationships(
        self,
        entity_model: Type[EntityType],
        mixed_entities_attributes: List[MixedEntityAttrs],
    ) -> EntityType:
        """Load the information of the relationships and generate the entity.

        Args:
            entity_model: Type of entity object to obtain.
            mixed_entities_attributes: List of serialized Entity attributes to modify.

        Returns:
            entity: Entity with all mappers loaded.
        """
        # The entity attributes are the same for all the rows
        entity_attributes = self._get_entity_attributes(
            entity_model, mixed_entities_attributes[0]
        )
        for mixed_entity_attributes in mixed_entities_attributes:
            for relationship in self.mapper.get_relationships(entity_model):
                if not relationship.is_source(entity_model):
                    continue
                if relationship.is_(EntityExtension):
                    entity_attributes = self._load_entity_extension(
                        relationship, entity_attributes, mixed_entity_attributes
                    )
                elif relationship.is_(EntityComposition):
                    entity_attributes = self._load_entity_single_composition(
                        relationship, entity_attributes, mixed_entity_attributes
                    )
                elif relationship.is_(EntityMultipleComposition):
                    entity_attributes = self._load_entity_multiple_composition(
                        relationship, entity_attributes, mixed_entity_attributes
                    )

        return entity_model(**entity_attributes)

    @staticmethod
    def _get_entity_attributes(
        entity_model: Type[EntityType], entity_attributes: MixedEntityAttrs
    ) -> EntityAttrs:
        """Extract the attributes belonging to an entity type from an EntityAttrs obj.

        Args:
            entity_model: Type of entity object to obtain.
            entity_attributes: Entity attributes to modify.

        Returns:
            entity_attributes: Entity attributes to modify.
        """
        new_attributes = {}

        for attribute, value in entity_attributes.items():
            if re.match(rf"{entity_model.class_name()}.*", attribute):
                new_attribute_name = re.sub(
                    rf"{entity_model.class_name()}.", "", attribute
                )
                new_attributes[new_attribute_name] = value
        return new_attributes

    def _load_entity_extension(
        self,
        relationship: RelationshipType,
        entity_attributes: EntityAttrs,
        mixed_entity_attributes: MixedEntityAttrs,
    ) -> EntityAttrs:
        """Add the information stored in the EntityExtension relationship.

        Args:
            relationship: Object containing the relationship information.
            entity_attributes: Entity attributes to modify.
            mixed_entities_attributes: List of serialized Entity attributes to modify.

        Returns:
            entity_attributes: Modified entity attributes.
        """
        populated_entity_attributes = self._get_entity_attributes(
            relationship.destination, mixed_entity_attributes
        )
        entity_attributes = {**entity_attributes, **populated_entity_attributes}

        return entity_attributes

    def _load_entity_single_composition(
        self,
        relationship: RelationshipType,
        entity_attributes: EntityAttrs,
        mixed_entity_attributes: MixedEntityAttrs,
    ) -> EntityAttrs:
        """Add the information stored in the EntityComposition relationship.

        Args:
            relationship: Object containing the relationship information.
            entity_attributes: Entity attributes to modify.
            mixed_entities_attributes: List of serialized Entity attributes to modify.

        Returns:
            entity_attributes: Modified entity attributes.
        """
        destination_id = entity_attributes[relationship.source_id]

        if destination_id is not None:
            populated_entity_attributes = self._get_entity_attributes(
                relationship.destination, mixed_entity_attributes
            )
            populated_entity = relationship.destination(**populated_entity_attributes)
            entity_attributes[relationship.source_attribute] = populated_entity
        del entity_attributes[relationship.source_id]

        return entity_attributes

    def _load_entity_multiple_composition(
        self,
        relationship: RelationshipType,
        entity_attributes: EntityAttrs,
        mixed_entity_attributes: MixedEntityAttrs,
    ) -> EntityAttrs:
        """Add the information stored in the EntityMultipleComposition relationship.

        Args:
            relationship: Object containing the relationship information.
            entity_attributes: Entity attributes to modify.
            mixed_entities_attributes: List of serialized Entity attributes to modify.

        Returns:
            entity_attributes: Modified entity attributes.
        """
        try:
            entity_attributes[relationship.source_attribute]
        except KeyError:
            entity_attributes[relationship.source_attribute] = []

        populated_entity_attributes = self._get_entity_attributes(
            relationship.destination, mixed_entity_attributes
        )
        if populated_entity_attributes["id_"] is not None:
            populated_entity = relationship.destination(**populated_entity_attributes)
            entity_attributes[relationship.source_attribute].append(populated_entity)

        return entity_attributes

    def _build_entities(
        self, entity_model: Type[EntityType], query: Query
    ) -> List[EntityType]:
        """Build Entity objects from the data extracted from the database.

        Args:
            entity_model: The model of the entity to build
            query: pypika query of the entities you want to build
        """
        entities: List[EntityType] = []
        for entity_attributes in self._build_entities_attributes(query):
            entities.append(entity_model(**entity_attributes))
        return entities

    def delete(self, entity: EntityType) -> None:
        """Delete an entity from the repository.

        Args:
            entity: Entity to remove from the repository.

        Raises:
            EntityNotFoundError: If the entity is not found.
        """
        table = _table(entity)
        try:
            self.get(type(entity), entity.id_)
        except EntityNotFoundError as error:
            raise EntityNotFoundError(
                f"Unable to delete entity {entity} because it's not in the repository"
            ) from error
        query = Query.from_(table).delete().where(table.id_ == entity.id_)
        self._execute(query)

    def all(self, entity_model: Type[EntityType]) -> List[EntityType]:
        """Obtain all the entities of a type from the repository.

        Args:
            entity_model: Type of entity objects to obtain.

        Returns:
            entities: List of Entity object that matches the search criteria.

        Raises:
            EntityNotFoundError: If the entities are not found.
        """
        table = _table(entity_model)
        query = Query.from_(table).select("*")

        entities = self._build_entities(entity_model, query)
        if len(entities) == 0:
            raise EntityNotFoundError(
                f"There are no {entity_model.__name__}s entities in the repository"
            )

        return entities

    def commit(self) -> None:
        """Persist the changes into the repository."""
        self.connection.commit()

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
        table = _table(entity_model)
        query = Query.from_(table).select("*")

        for key, value in fields.items():
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


def _table(entity: Union[EntityType, Type[EntityType]]) -> Table:
    """Return the table of the selected entity object."""
    return Table(entity.class_name())


def _upsert(
    table: Table,
    columns: Tuple[str, ...],
    values: Tuple[Any, ...],
    mode: str = "update",
) -> str:
    """Create an upsert SQL query.

    Until https://github.com/kayak/pypika/issues/535 is solved we need to write
    The upsert statement ourselves.

    Args:
        table: Table to insert the data.
        columns: Table columns to insert the data.
        values: Table data to insert.
        mode: upsert mode, either 'update' or 'pass'.

    Returns:
        upsert_query: SQL query in string format.
    """
    if mode == "update":
        # Until https://github.com/kayak/pypika/issues/535 is solved we need to write
        # The upsert statement ourselves.
        # nosec: B608:hardcoded_sql_expressions, Possible SQL injection vector through
        #   string-based query construction. We're not letting the user define the
        #   values of the query, the only variable inputs are the keys, that are
        #   defined by the developer, so it's not probable that he chooses an
        #   entity attributes that are an SQL injection. Once the #535 issue is
        #   solved, we should get rid of this error too.
        action = "CONFLICT(id_) DO UPDATE SET " + ", ".join(  # nosec
            [f"{key}=excluded.{key}" for key in columns]
        )
    else:
        action = "CONFLICT DO NOTHING"

    insert_query = str(Query.into(table).columns(columns).insert(*values))
    if insert_query == "":
        return insert_query
    return f"{insert_query} ON {action}"


def _get_select_columns(table: Table, entity_model: Type[EntityType]) -> List[Field]:
    """Create the select statement from the attributes of the entity.

    It will iterate over the entity attributes, saving the table column as
    entity.attribute.

    For example, if we have a Task entity with attributes id_ and name, it will return:

    [table.id_.as_('task.id_'), table.name.as_('task.name')]

    Args:
        table: Table to select from
        entity_model: Type of entity object to obtain.

    Returns:
        columns: List of columns with the alias set.
    """
    columns = []
    entity_attributes = list(entity_model.attributes().keys())
    for attribute in entity_attributes:
        columns.append(_add_select_column_attribute(table, entity_model, attribute))
    return columns


def _add_select_column_attribute(
    table: Table, entity_model: Type[EntityType], attribute: str
) -> Field:
    """Create a select column for an entity attribute.

    Useful to add ORM mapped attributes.

    Args:
        table: Table to select from
        entity_model: Type of entity object to obtain.
        attribute: Name of the attribute to remove

    Returns:
        column: Columns with the alias set.
    """
    return getattr(table, attribute).as_(f"{entity_model.class_name()}.{attribute}")


def _delete_select_column_attribute(
    table: Table, entity_model: Type[EntityType], attribute: str, columns: List[Field]
) -> List[Field]:
    """Remove the attribute of the entity model from the select statement.

    Useful to remove ORM mapped attributes.

    Args:
        table: Table to select from
        entity_model: Type of entity object to obtain.
        attribute: Name of the attribute to remove
        columns: List of columns with the alias set.

    Returns:
        columns: List of columns with the alias set.
    """
    column_to_delete = getattr(table, attribute).as_(
        f"{entity_model.class_name()}.{attribute}"
    )

    # Removal with columns.remove(column) doesn't work, it deletes the wrong column.
    # ¯\_(ツ)_/¯

    for column_id in range(len(columns) - 1):
        if (
            columns[column_id].table == column_to_delete.table
            and columns[column_id].name == column_to_delete.name
        ):
            columns.pop(column_id)
            break
    return columns
