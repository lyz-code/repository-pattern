"""Gather the abstract classes used by the rest of the cases.

Import the created cases so they are easily accessible too.
"""

from .entities import EntityCases
from .repositories import RepositoryCases

__all__ = ["RepositoryCases", "EntityCases"]
