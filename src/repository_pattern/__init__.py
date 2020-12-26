"""Library to ease the implementation of the repository pattern in python projects.."""

from .model import Entity

# from .adapters import (  # AbstractRepositoryTester,; RepositoryTester,
#     AbstractRepository,
#     Repository,
# )
# from .adapters.fake import FakeRepository, FakeRepositoryDB
# from .adapters.pypika import PypikaRepository
# from .exceptions import EntityNotFoundError
#
__all__ = [
    "Entity",
    #     "EntityNotFoundError",
    #     "Repository",
    #     #     "RepositoryTester",
    #     "AbstractRepository",
    #     #     "AbstractRepositoryTester",
    #     "FakeRepositoryDB",
    #     "FakeRepository",
    #     #     "FakeRepositoryTester",
    #     "PypikaRepository",
    #     #     "PypikaRepositoryTester",
]
