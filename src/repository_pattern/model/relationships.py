"""Define the relationships between Entities."""

from typing import Any, Generic, List, Optional, Type, TypeVar, Union

from pydantic import BaseModel, Field, validator  # noqa: E0611
from pydantic.generics import GenericModel

from . import Entity, EntityType

SourceEntity = TypeVar("SourceEntity", bound=Entity)
DestinationEntity = TypeVar("DestinationEntity", bound=Entity)

# E0611: No name 'BaseModel' in module 'pydantic'
# https://github.com/samuelcolvin/pydantic/issues/1961


class Relationship(GenericModel, Generic[SourceEntity, DestinationEntity]):
    """Create the interface of a relationship between two entities.

    Args:
        source: Entity model at the left side of the relationship.
        destination: Entity model at the right side of the relationship.
        source_id: Attribute on the left entity used to do the match.
        destination_id: Attribute on the right entity used to do the match.
        source_attribute: Attribute name on the left entity to store the created
            objects of the right kind that match the criteria.
    """

    source: Type[SourceEntity]
    destination: Type[DestinationEntity]
    source_id: str = None  # type: ignore
    source_attribute: str = None  # type: ignore
    destination_id: str = None  # type: ignore
    destination_attribute: str = None  # type: ignore

    def is_source(self, entity: Union[EntityType, Type[EntityType]]) -> bool:
        """Check if the entity is the source of the relationship."""
        return isinstance(entity, self.source) or entity == self.source

    def is_(self, relationship_type: Any) -> bool:
        """Check we are of type relationship.

        Args:
            relationship_type: Relationship class to compare ourselves with.
        """
        return isinstance(self, relationship_type)


class EntityExtension(Relationship[SourceEntity, DestinationEntity]):
    """Extend the attributes of an entity class with another by inheritance.

    The entity that extends needs the original one to exist, otherwise the pydantic
    validators will fail.

    We need that the source_id == destination_id == 'id_' condition.
    """

    source_id: str = "id_"
    destination_id: str = "id_"

    @validator("source_id", pre=True, always=True)
    @classmethod
    def set_source_id_if_none(cls, source_id: Optional[str]) -> str:
        """Set source_id to 'id_' if None.

        Raises:
            ValueError: if the source_id is not 'id_'.
        """
        if source_id != "id_":
            raise ValueError("source_id must be 'id_' in this type of relationship")
        return source_id

    @validator("destination_id", pre=True, always=True)
    @classmethod
    def destination_id_must_be_id_(cls, destination_id: str) -> str:
        """Force that destination_id is 'id_'."""
        if destination_id != "id_":
            raise ValueError(
                "destination_id must be 'id_' in this type of relationship"
            )
        return destination_id


class EntityComposition(Relationship[SourceEntity, DestinationEntity]):
    """Create a composition relationship between two entities of different types.

    The destination entity is stored in an attribute of the source entity.
    """

    @validator("source_id", pre=True, always=True)
    @classmethod
    def set_source_id_if_none(cls, source_id: Optional[str], values: Any) -> str:
        """Set source_id if None.

        Set to the destination entity type plus the suffix `_id`. Imagine that the
        destination type is Book, then the source_id would be book_id.
        """
        if source_id is None:
            return f"{values['destination'].class_name()}_id"
        return source_id

    @validator("destination_id", pre=True, always=True)
    @classmethod
    def set_destination_id_if_none(cls, destination_id: Optional[str]) -> str:
        """Set destination_id to id_ if None."""
        if destination_id is None:
            return "id_"
        return destination_id

    @validator("source_attribute", pre=True, always=True)
    @classmethod
    def set_source_attribute_if_none(
        cls, source_attribute: Optional[str], values: Any
    ) -> str:
        """Set source_attribute to the destination entity type if None.

        Imagine that the destination type is Book, then the source_attribute would be
        book.
        """
        if source_attribute is None:
            return values["destination"].class_name()
        return source_attribute


class EntityMultipleComposition(Relationship[SourceEntity, DestinationEntity]):
    """Create a composition relationship between an entity with multiple of other type.

    A list of destination entity objects is stored in an attribute of the source entity.
    """

    @validator("source_id", pre=True, always=True)
    @classmethod
    def set_source_id_if_none(cls, source_id: Optional[str]) -> str:
        """Set source_id to id_ if None."""
        if source_id is None:
            return "id_"
        return source_id

    @validator("destination_id", pre=True, always=True)
    @classmethod
    def set_destination_id_if_none(cls, destination_id: Optional[str]) -> str:
        """Set destination_id to id_ if None."""
        if destination_id is None:
            return "id_"
        return destination_id

    @validator("source_attribute", pre=True, always=True)
    @classmethod
    def set_source_attribute_if_none(
        cls, source_attribute: Optional[str], values: Any
    ) -> str:
        """Set source_attribute to the destination entity type if None.

        Imagine that the destination type is Book, then the source_attribute would be
        book.
        """
        if source_attribute is None:
            return f'{values["destination"].class_name()}s'
        return source_attribute


class Mapper(BaseModel):
    """Define the mapper of relationships."""

    relationships: List[Any] = Field(default_factory=list)

    def get_relationships(
        self, entity_model: Union[EntityType, Type[EntityType]]
    ) -> List[Any]:
        """Return the relationships that affect the entity model."""
        object_relationships: List[Any] = []
        for relationship in self.relationships:
            if entity_model.class_name() in [
                relationship.source.class_name(),
                relationship.destination.class_name(),
            ]:
                object_relationships.append(relationship)

        return object_relationships


RelationshipType = Relationship[Any, Any]
