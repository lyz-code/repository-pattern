"""Tests the integration between the repositories and their storage layer."""

from typing import List

import pytest

from repository_pattern import AbstractRepository, Entity, EntityNotFoundError

from ..cases import AbstractRepositoryTester


class TestRepositories:
    """Test all repositories.

    The tests are all the same for all the repositories. If you want to add a new one
    add them to the cases.
    """

    def test_repository_can_save_an_entity(
        self,
        repo: AbstractRepository,
        repo_tester: AbstractRepositoryTester,
        entity: Entity,
    ) -> None:
        """Saved entities remain in the repository."""
        repo.add(entity)
        repo.commit()

        assert entity == repo_tester.get_entity(repo, entity)

    def test_repository_can_retrieve_an_entity(
        self, repo: AbstractRepository, inserted_entity: Entity,
    ) -> None:
        """Given an entity_id the repository returns the entity object."""
        retrieved_entity = repo.get(type(inserted_entity), inserted_entity.ID)

        assert retrieved_entity == inserted_entity
        assert retrieved_entity.ID == inserted_entity.ID

    def test_repository_raises_error_if_no_entity_found_by_get(
        self, repo: AbstractRepository, entity: Entity,
    ) -> None:
        """As the entity is not inserted into the repository, it shouldn't be found."""
        with pytest.raises(EntityNotFoundError) as error:
            repo.get(type(entity), entity.ID)

        assert (
            f"There are no {entity.__class__.__name__}s with id "
            f"{entity.ID} in the repository" in str(error.value)
        )

    def test_repository_can_retrieve_all_objects(
        self, repo: AbstractRepository, inserted_entities: List[Entity],
    ) -> None:
        """Given an entity type all the entity objects that match should be returned."""
        entity_type = type(inserted_entities[0])

        retrieved_entities = repo.all(entity_type)

        assert retrieved_entities == inserted_entities
        assert len(retrieved_entities) == 3
        assert retrieved_entities[0].ID == inserted_entities[0].ID

    def test_repository_all_raises_error_if_empty_repository(
        self, repo: AbstractRepository, entity: Entity,
    ) -> None:
        """If there are no entities, an error should be raised."""
        with pytest.raises(EntityNotFoundError) as error:
            repo.all(type(entity))

        assert (
            f"There are no {entity.__class__.__name__}s entities in the repository"
            in str(error.value)
        )

    def test_repository_can_search_by_property(
        self, repo: AbstractRepository, inserted_entities: List[Entity],
    ) -> None:
        """Search should return the objects that match the desired property."""
        expected_entity = inserted_entities[1]

        retrieved_entities = repo.search(
            type(expected_entity), {"ID": expected_entity.ID}
        )

        assert retrieved_entities == [expected_entity]

    def test_repository_search_raises_error_if_searching_by_unexistent_field(
        self, repo: AbstractRepository, inserted_entities: List[Entity],
    ) -> None:
        """If no object has the property of the search criteria, raise the desired
        error.
        """
        entity = inserted_entities[0]

        with pytest.raises(EntityNotFoundError) as error:
            repo.search(type(entity), {"unexistent_field": "unexistent_value"})

        assert (
            f"There are no {entity.__class__.__name__}s that match "
            "the search filter {'unexistent_field': 'unexistent_value'}"
            in str(error.value)
        )

    def test_repository_search_raises_error_if_searching_by_unexistent_value(
        self, repo: AbstractRepository, inserted_entities: List[Entity],
    ) -> None:
        """If no object has a value like the search criteria raise the desired error."""
        entity = inserted_entities[0]

        with pytest.raises(EntityNotFoundError) as error:
            repo.search(type(entity), {"ID": "unexistent_value"})

        assert (
            f"There are no {entity.__class__.__name__}s that match "
            "the search filter {'ID': 'unexistent_value'}" in str(error.value)
        )

    def test_repository_can_search_by_multiple_properties(
        self, repo: AbstractRepository, inserted_entities: List[Entity],
    ) -> None:
        """
        Given: a full repository.
        When: a search is performed by multiple properties.
        Then: the matching objects are returned.
        """
        entity = inserted_entities[1]
        search_criteria = entity.dict()

        retrieved_entity = repo.search(type(entity), search_criteria)

        assert retrieved_entity == [entity]

    @pytest.mark.secondary
    def test_repository_can_delete_an_entity(
        self, repo: AbstractRepository, inserted_entities: List[Entity],
    ) -> None:
        """
        Given: a full repository.
        When: an entity is deleted.
        Then: the entity is not longer in the repository.
        """
        entity_to_delete = inserted_entities[1]

        repo.delete(entity_to_delete)

        remaining_entities = repo.all(type(entity_to_delete))

        assert entity_to_delete not in remaining_entities

    def test_repository_raise_error_if_entity_not_found(
        self, repo: AbstractRepository, entity: Entity,
    ) -> None:
        """
        Given: an empty repository.
        When: trying to delete an unexistent entity.
        Then: An EntityNotFoundError error is raised.
        """
        with pytest.raises(EntityNotFoundError) as error:
            repo.delete(entity)

        assert (
            f"Unable to delete entity {entity} because it's not in the repository"
            in str(error.value)
        )
