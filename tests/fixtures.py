"""Gather fixtures used by the tests."""

from typing import List, Tuple

import factory
from pytest_cases import fixture, parametrize_with_cases, unpack_fixture

from repository_pattern import Entity, Repository

from .cases import RepositoryCases, RepositoryTester
from .cases.entities import EntityCases
from .cases.fake_repository import repo_fake  # noqa

# -----------------------
# - Repository fixtures -
# -----------------------


@fixture
@parametrize_with_cases("repo, repo_tester", cases=RepositoryCases)
def repo_test_fixture(
    repo: Repository, repo_tester: RepositoryTester
) -> Tuple[Repository, RepositoryTester]:
    """Generate the repository and tester object tuples for each repository type."""
    return repo, repo_tester


repo, repo_tester = unpack_fixture("repo,repo_tester", repo_test_fixture)  # noqa: W0632
# We know they are going to return two objects.


# -------------------
# - Entity fixtures -
# -------------------


@fixture
@parametrize_with_cases("entity_factory", cases=EntityCases)
def entity(entity_factory: factory.Factory) -> Entity:
    """Return one entity for each entity type defined in the EntityCases."""
    return entity_factory.create()


@fixture
def inserted_entity(
    entity: Entity, repo: Repository, repo_tester: RepositoryTester
) -> Entity:
    """Insert one entity in the repository and return it.

    For each entity type defined in the EntityCases.
    """
    repo_tester.insert_entity(repo, entity)
    return entity


@fixture
@parametrize_with_cases("entity_factory", cases=EntityCases)
def entities(entity_factory: factory.Factory) -> List[Entity]:
    """Return three entities for each entity type defined in the EntityCases."""
    return sorted(entity_factory.create_batch(3))


@fixture
def inserted_entities(
    entities: List[Entity], repo: Repository, repo_tester: RepositoryTester
) -> List[Entity]:
    """Insert three entities in the repository and return them.

    For each entity type defined in the EntityCases.
    """
    for entity in entities:
        repo_tester.insert_entity(repo, entity)
    return entities
