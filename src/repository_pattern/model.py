from typing import Union

from pydantic import BaseModel


class Entity(BaseModel):
    id: Union[int, str]

    def __lt__(self, other) -> bool:
        """
        Internal Python method to compare class objects.
        """

        return self.id < other.id

    def __gt__(self, other) -> bool:
        """
        Internal Python method to compare class objects.
        """

        return self.id > other.id

    def __hash__(self) -> int:
        """
        Internal Python method to create an unique hash of the class object.
        """

        return hash(self.id)
