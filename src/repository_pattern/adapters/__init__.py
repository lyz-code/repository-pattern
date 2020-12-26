from typing import TypeVar

from .repositories.fake import FakeRepository
from .repositories.pypika import PypikaRepository

Repository = TypeVar("Repository", PypikaRepository, FakeRepository)
# RepositoryTester = TypeVar(
#     "RepositoryTester",
#     FakeRepositoryTester,
#     PypikaRepositoryTester,
# )
