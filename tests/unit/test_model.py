"""Tests the model layer."""

import pytest

from repository_pattern import Entity


class TestEntity:
    """Test the Entity object."""

    def test_compare_entities(self) -> None:
        """Comparison between entities is done by the ID attribute."""
        small = Entity(ID=1)
        big = Entity(ID=2)

        result = small < big

        assert result

    def test_compare_entities_with_string_ids(self) -> None:
        """Comparison between entities is done by the ID attribute on string IDS."""
        small = Entity(ID="a")
        big = Entity(ID="b")

        result = small < big

        assert result

    def test_compare_entities_cant_compare_string_and_id(self) -> None:
        """Raise TypeError if one object id is a string and the other an int"""
        entity_string = Entity(ID="a")
        entity_int = Entity(ID=1)

        with pytest.raises(TypeError):
            entity_string < entity_int  # noqa: B015, W0104
