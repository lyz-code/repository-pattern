import pytest

from repository_pattern import EntityNotFoundError


class TestRepositories:
    def test_repository_can_save_an_entity(self, repo, repo_tester, entity):
        repo.add(entity)
        repo.commit()

        assert entity == repo_tester.get_entity(repo, entity)

    def test_repository_can_retrieve_an_entity(
        self, repo, repo_tester, inserted_entity
    ):
        retrieved_entity = repo.get(type(inserted_entity), inserted_entity.id)

        assert retrieved_entity == inserted_entity
        assert retrieved_entity.id == inserted_entity.id

    def test_repository_raises_error_if_no_entity_found_by_get(self, repo, entity):
        """
        As the entity is not inserted into the repository, it shouldn't be found.
        """

        with pytest.raises(EntityNotFoundError) as error:
            repo.get(type(entity), entity.id)

        assert (
            f"There are no {entity.__class__.__name__}s with id "
            f"{entity.id} in the repository" in str(error.value)
        )

    def test_repository_can_retrieve_all_objects(self, repo, inserted_entities):
        entity_type = type(inserted_entities[0])

        retrieved_entities = repo.all(entity_type)

        assert retrieved_entities == inserted_entities
        assert len(retrieved_entities) == 3
        assert retrieved_entities[0].id == inserted_entities[0].id

    def test_repository_all_raises_error_if_empty_repository(self, repo, entity):

        with pytest.raises(EntityNotFoundError) as error:
            repo.all(type(entity))
        assert (
            f"There are no {entity.__class__.__name__}s entities in the repository"
            in str(error.value)
        )

    def test_repository_can_search_by_property(self, repo, inserted_entities):
        expected_entity = inserted_entities[1]

        retrieved_entities = repo.search(
            type(expected_entity), {"id": expected_entity.id}
        )

        assert retrieved_entities == [expected_entity]

    def test_repository_search_raises_error_if_searching_by_unexistent_field(
        self, repo, inserted_entities
    ):
        entity = inserted_entities[0]

        with pytest.raises(EntityNotFoundError) as error:
            repo.search(type(entity), {"unexistent_field": "unexistent_value"})
        assert (
            f"There are no {entity.__class__.__name__}s that match "
            "the search filter {'unexistent_field': 'unexistent_value'}"
            in str(error.value)
        )

    def test_repository_search_raises_error_if_searching_by_unexistent_value(
        self, repo, inserted_entities
    ):
        entity = inserted_entities[0]

        with pytest.raises(EntityNotFoundError) as error:
            repo.search(type(entity), {"id": "unexistent_value"})
        assert (
            f"There are no {entity.__class__.__name__}s that match "
            "the search filter {'id': 'unexistent_value'}" in str(error.value)
        )

    def test_repository_can_search_by_multiple_properties(
        self, repo, inserted_entities
    ):
        entity = inserted_entities[1]
        filter = entity.dict()

        retrieved_entity = repo.search(type(entity), filter)

        assert retrieved_entity == [entity]

    @pytest.mark.secondary
    def test_repository_can_delete_an_entity(self, repo, inserted_entities):
        entity_to_delete = inserted_entities[1]

        repo.delete(entity_to_delete)

        remaining_entities = repo.all(type(entity_to_delete))

        assert entity_to_delete not in remaining_entities

    def test_repository_raise_error_if_entity_not_found(self, repo, entity):

        with pytest.raises(EntityNotFoundError) as error:
            repo.delete(entity)

        assert (
            f"Unable to delete entity {entity} because it's not in the repository"
            in str(error.value)
        )
