"""Module to store the common business model of all entities."""

from pydantic import BaseModel


class Entity(BaseModel):
    """Model of any object no defined by it's attributes whom instead has an identity.

    Unlike value objects, they have *identity equality*. We can change their values, and
    they are still recognizably the same thing.

    An entity with a negative id means that the id needs to be set by the repository.
    """

    id_: int = -1

    def __lt__(self, other: "Entity") -> bool:
        """Assert if an object is smaller than us.

        Args:
            other: Entity to compare.

        Raises:
            TypeError: If the id type of the objects is not compatible.
        """
        return self.id_ < other.id_

    def __gt__(self, other: "Entity") -> bool:
        """Assert if an object is greater than us.

        Args:
            other: Entity to compare.

        Raises:
            TypeError: If the id type of the objects is not compatible.
        """
        return self.id_ > other.id_

    def __hash__(self) -> int:
        """Create an unique hash of the class object."""
        return hash(self.id_)
