"""Library to ease the implementation of the repository pattern in python projects.."""

from typing import TypeVar

from .adapters import AbstractRepository
from .adapters.fake import FakeRepository, FakeRepositoryDB
from .adapters.pypika import PypikaRepository
from .exceptions import EntityNotFoundError
from .model import (
    Entity,
    EntityAttrs,
    EntityComposition,
    EntityExtension,
    EntityID,
    EntityMultipleComposition,
    EntityNotMapped,
    EntityType,
    Mapper,
)

Repository = TypeVar("Repository", PypikaRepository, FakeRepository)

__all__ = [
    "AbstractRepository",
    "Entity",
    "EntityID",
    "EntityAttrs",
    "EntityComposition",
    "EntityExtension",
    "EntityMultipleComposition",
    "EntityType",
    "EntityNotFoundError",
    "EntityNotMapped",
    "FakeRepository",
    "FakeRepositoryDB",
    "Mapper",
    "PypikaRepository",
    "Repository",
]
