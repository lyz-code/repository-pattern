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
    return repo, repo_tester


repo, repo_tester = unpack_fixture("repo,repo_tester", repo_test_fixture)


# -------------------
# - Entity fixtures -
# -------------------


@fixture
@parametrize_with_cases("entity_factory", cases=EntityCases)
def entity(entity_factory: factory.Factory) -> Entity:
    return entity_factory.create()


@fixture
def inserted_entity(
    entity: Entity, repo: Repository, repo_tester: RepositoryTester
) -> Entity:
    repo_tester.insert_entity(repo, entity)
    return entity


@fixture
@parametrize_with_cases("entity_factory", cases=EntityCases)
def entities(entity_factory: factory.Factory) -> List[Entity]:
    return sorted(entity_factory.create_batch(3))


@fixture
def inserted_entities(
    entities: List[Entity], repo: Repository, repo_tester: RepositoryTester
) -> List[Entity]:
    for entity in entities:
        repo_tester.insert_entity(repo, entity)
    return entities
