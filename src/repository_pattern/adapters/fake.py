"""
Module to store the fake repository implementation.

Classes:
    FakeRepository: Implement the repository pattern using the SQLAlchemy ORM.
"""


import logging
import re
from typing import Dict, List, Type, Union

from deepdiff import extract, grep
from pydantic import BaseModel, Field

from .. import AbstractRepository
from ..exceptions import EntityNotFoundError
from ..model import Entity

log = logging.getLogger(__name__)


class FakeRepository(BaseModel, AbstractRepository):
    """
    Class to implement the repository pattern using a memory dictionary.

    Abstract Methods:
        add: Append an entity to the repository.
        all: Obtain all the entities of a type from the repository.
        commit: Persist the changes into the repository.
        delete: Remove an entity from the repository.
        get: Obtain an entity from the repository by it's ID.
        search: Obtain the entities whose attribute match a condition.
    """

    entities: Dict[Type[Entity], Dict[Union[int, str], Entity]] = Field(
        default_factory=dict
    )

    def add(self, entity: Entity):
        """
        Method to append an entity to the repository.
        """

        try:
            self.entities[type(entity)]
        except KeyError:
            self.entities[type(entity)] = {}

        self.entities[type(entity)][entity.id] = entity

    def get(self, entity_model: Type[Entity], entity_id: str) -> Entity:
        """
        Method to obtain an entity from the repository by it's ID.
        """
        try:
            entity = self.entities[entity_model][entity_id]
        except KeyError:
            raise EntityNotFoundError(
                f"There are no {entity_model.__name__}s "
                f"with id {entity_id} in the repository."
            )

        return entity

    def all(self, entity_model: Type[Entity]) -> List[Entity]:
        """
        Method to obtain all the entities of a type from the repository.
        """
        try:
            return sorted(
                [entity for entity_id, entity in self.entities[entity_model].items()]
            )
        except KeyError:
            raise EntityNotFoundError(
                f"There are no {entity_model.__name__}s entities in the repository"
            )

    def delete(self, entity: Entity) -> None:
        """
        Method to remove an entity from the repository.
        """
        try:
            self.entities[type(entity)].pop(entity.id, None)
        except KeyError:
            raise EntityNotFoundError(
                f"Unable to delete entity {entity} because it's not in the repository"
            )

    def commit(self) -> None:
        """
        Method to persist the changes into the repository.
        """

        # They are saved when adding them, if we want to mimic the behaviour of the
        # other repositories, we should save the objects in a temporal list and move
        # them to the real set when using this method.
        pass

    def search(self, entity_model: Type[Entity], fields: Dict) -> List[Entity]:
        """
        Method to obtain the entities whose attributes match one or several conditions.

        fields is a dictionary with the `key`:`value` to search.

        It assumes that the attributes of the entities are str.

        If None is found an EntityNotFoundError is raised.
        """
        all_entities = self.all(entity_model)
        entities_dict = {entity.id: entity for entity in all_entities}
        entity_attributes = {entity.id: entity.dict() for entity in all_entities}
        error_msg = (
            f"There are no {entity_model.__name__}s that match "
            f"the search filter {fields}"
        )

        for key, value in fields.items():
            # Get entities that have the value `value`
            entities_with_value = entity_attributes | grep(value)
            matching_entity_attributes = {}

            try:
                entities_with_value["matched_values"]
            except KeyError:
                raise EntityNotFoundError(error_msg)

            for path in entities_with_value["matched_values"]:
                entity_id = re.sub(r"root\[(.*?)\]\[.*", r"\1", path)

                # Convert int ids from str to int
                try:
                    entity_id = int(entity_id)
                except ValueError:
                    entity_id = re.sub(r"'(.*)'", r"\1", entity_id)

                # Add the entity to the matching ones only if the value is of the
                # attribute `key`.
                if re.match(re.compile(fr"root\['?{entity_id}'?\]\['{key}'\]"), path):
                    matching_entity_attributes[entity_id] = extract(
                        entity_attributes, f"root[{entity_id}]"
                    )

            entity_attributes = matching_entity_attributes
        entities = [entities_dict[key] for key in entity_attributes.keys()]

        if len(entities) == 0:
            raise EntityNotFoundError(error_msg)
        else:
            return entities
