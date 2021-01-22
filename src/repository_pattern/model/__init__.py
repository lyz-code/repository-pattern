"""Define the public interface of the model."""

from .entity import Entity, EntityAttrs, EntityID, EntityNotMapped, EntityType
from .relationships import (
    EntityComposition,
    EntityExtension,
    EntityMultipleComposition,
    Mapper,
    Relationship,
    RelationshipType,
)

__all__ = [
    "Entity",
    "EntityAttrs",
    "EntityComposition",
    "EntityExtension",
    "EntityMultipleComposition",
    "EntityID",
    "EntityNotMapped",
    "EntityType",
    "Mapper",
    "Relationship",
    "RelationshipType",
]
