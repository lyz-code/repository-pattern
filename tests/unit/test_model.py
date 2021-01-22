"""Tests the model layer."""

import pytest
from tests.cases import (
    Author,
    Book,
    ComposingEntity,
    ExtendingEntity,
    MultipleComposingEntity,
)

from repository_pattern import (
    Entity,
    EntityComposition,
    EntityExtension,
    EntityMultipleComposition,
)


def test_compare_less_than_entities() -> None:
    """Comparison between entities is done by the ID attribute."""
    small = Entity(id_=1)
    big = Entity(id_=2)

    result = small < big

    assert result


def test_compare_greater_than_entities() -> None:
    """Comparison between entities is done by the ID attribute."""
    small = Entity(id_=1)
    big = Entity(id_=2)

    result = big > small

    assert result


def test_compare_less_than_entities_with_string_ids() -> None:
    """Comparison between entities is done by the ID attribute on string IDS."""
    small = Entity(id_="a")
    big = Entity(id_="b")

    result = small < big

    assert result


def test_compare_greater_than_entities_with_string_ids() -> None:
    """Comparison between entities is done by the ID attribute on string IDS."""
    small = Entity(id_="a")
    big = Entity(id_="b")

    result = big > small

    assert result


def test_compare_less_than_entities_cant_compare_string_and_id() -> None:
    """Raise TypeError if one object id is a string and the other an int"""
    entity_string = Entity(id_="a")
    entity_int = Entity(id_=1)

    with pytest.raises(TypeError):
        entity_string < entity_int  # noqa: B015, W0104


def test_compare_greater_than_entities_cant_compare_string_and_id() -> None:
    """Raise TypeError if one object id is a string and the other an int"""
    entity_string = Entity(id_="a")
    entity_int = Entity(id_=1)

    with pytest.raises(TypeError):
        entity_string > entity_int  # noqa: B015, W0104


def test_hash_uses_the_entity_id() -> None:
    """
    Given: A configured entity.
    When: The __hash__ method is used.
    Then: The hash of the identity is used
    """
    entity = Entity(id_=1)

    result = entity.__hash__()

    assert result == hash(1)


def test_extending_entity_raises_error_if_doesnt_use_id_as_source() -> None:
    """
    Given: The EntityExtension class
    When: It's initialized with a source_id that aren't id_
    Then: The ValueError exception is raised
    """
    with pytest.raises(
        ValueError, match="source_id must be 'id_' in this type of relationship"
    ):
        EntityExtension(source=ExtendingEntity, destination=Author, source_id="name")


def test_extending_entity_raises_error_if_doesnt_use_id_as_destination() -> None:
    """
    Given: The EntityExtension class
    When: It's initialized with a destination_id that isn't id_
    Then: The ValueError exception is raised
    """
    with pytest.raises(
        ValueError, match="destination_id must be 'id_' in this type of relationship"
    ):
        EntityExtension(
            source=ExtendingEntity, destination=Author, destination_id="name"
        )


def test_composing_entity_can_define_source_id() -> None:
    """
    Given: The EntityComposition class
    When: It's initialized with a source_id
    Then: The source_id is respected
    """
    result = EntityComposition(  # type: ignore
        source=ComposingEntity, destination=Book, source_id="name"
    )

    assert result.source_id == "name"


def test_composing_entity_can_define_destination_id() -> None:
    """
    Given: The EntityComposition class
    When: It's initialized with a destination_id
    Then: The destination_id is respected
    """
    result = EntityComposition(  # type: ignore
        source=ComposingEntity, destination=Book, destination_id="name"
    )

    assert result.destination_id == "name"


def test_composing_entity_can_define_source_attribute() -> None:
    """
    Given: The EntityComposition class
    When: It's initialized with a source_attribute
    Then: The source_attribute is respected
    """
    result = EntityComposition(  # type: ignore
        source=ComposingEntity, destination=Book, source_attribute="name"
    )

    assert result.source_attribute == "name"


def test_multiple_composing_entity_can_define_source_id() -> None:
    """
    Given: The EntityComposition class
    When: It's initialized with a source_id
    Then: The source_id is respected
    """
    result = EntityMultipleComposition(  # type: ignore
        source=MultipleComposingEntity, destination=Book, source_id="name"
    )

    assert result.source_id == "name"


def test_multiple_composing_entity_can_define_destination_id() -> None:
    """
    Given: The EntityComposition class
    When: It's initialized with a destination_id
    Then: The destination_id is respected
    """
    result = EntityMultipleComposition(  # type: ignore
        source=MultipleComposingEntity, destination=Book, destination_id="name"
    )

    assert result.destination_id == "name"


def test_multiple_composing_entity_can_define_source_attribute() -> None:
    """
    Given: The EntityComposition class
    When: It's initialized with a source_attribute
    Then: The source_attribute is respected
    """
    result = EntityMultipleComposition(  # type: ignore
        source=MultipleComposingEntity, destination=Book, source_attribute="name"
    )

    assert result.source_attribute == "name"
