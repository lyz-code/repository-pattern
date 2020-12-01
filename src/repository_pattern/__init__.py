"""Library to ease the implementation of the repository pattern in python projects.."""

from typing import TypeVar

from .adapters import AbstractRepository
from .adapters.fake import FakeRepository
from .exceptions import EntityNotFoundError
from .model import Entity

# Need to put it twice because TypeVar doesn't support only one argument
Repository = TypeVar("Repository", FakeRepository, FakeRepository)

__all__ = [
    "AbstractRepository",
    "Entity",
    "EntityNotFoundError",
    "FakeRepository",
    "Repository",
]
