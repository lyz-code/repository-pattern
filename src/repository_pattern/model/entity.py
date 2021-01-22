"""Module to store the common business model of all entities."""

import re
from typing import Any, Dict, TypeVar, Union

from pydantic import BaseModel  # noqa: E0611

# E0611: No name 'BaseModel' in module 'pydantic'
# https://github.com/samuelcolvin/pydantic/issues/1961

EntityType = TypeVar("EntityType", bound="Entity")
EntityID = Union[str, int]
EntityAttrs = Dict[str, Any]


class Entity(BaseModel):
    """Model of any object no defined by it's attributes whom instead has an identity.

    Unlike value objects, they have *identity equality*. We can change their values, and
    they are still recognizably the same thing.
    """

    id_: Union[int, str]

    def __lt__(self, other: "Entity") -> bool:
        """Assert if an object is smaller than us.

        Args:
            other: Entity to compare.

        Raises:
            TypeError: If the id type of the objects is not compatible.
        """
        if not isinstance(other.id_, type(self.id_)):
            raise TypeError(f"{self} and {other} have incompatible ID types")
        return self.id_ < other.id_  # type: ignore

    def __gt__(self, other: "Entity") -> bool:
        """Assert if an object is greater than us.

        Args:
            other: Entity to compare.

        Raises:
            TypeError: If the id type of the objects is not compatible.
        """
        if not isinstance(other.id_, type(self.id_)):
            raise TypeError(f"{self} and {other} have incompatible ID types")
        return self.id_ > other.id_  # type: ignore

    def __hash__(self) -> int:
        """Create an unique hash of the class object."""
        return hash(self.id_)

    @classmethod
    def attributes(cls) -> EntityAttrs:
        """Extract the empty entity attribute dictionary.

        Returns:
            entity_attributes: Empty dictionary with the attributes as keys.
        """
        return {key: None for key in cls.schema()["properties"]}

    @classmethod
    def class_name(cls) -> str:
        """Return the class name of an entity.

        Using .__class__.__name__ doesn't work as it gives ModelMetaclass. Using
        .schema()['title'] doesn't work with models that update the references after
        creation.
        """
        return re.sub(r".*\.(\w*).*", r"\1", str(cls)).lower()


class EntityNotMapped(BaseModel):
    """Model the exception of an unloaded entity.

    It usually is the case of loading the entity from a repository without loading
    the mappers.
    """

    id_: Union[int, str]
    model: Any
