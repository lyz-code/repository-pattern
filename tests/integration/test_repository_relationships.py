"""Test the implementation of how repositories manage relationships between entities."""

from typing import List

import pytest
from tests.cases import (
    Author,
    Book,
    BookFactory,
    ComposingEntity,
    ComposingEntityFactory,
    ExtendingEntity,
    ExtendingEntityFactory,
    MultipleComposingEntity,
    MultipleComposingEntityFactory,
)

from repository_pattern import (
    EntityComposition,
    EntityExtension,
    EntityMultipleComposition,
    EntityNotFoundError,
    Mapper,
    Repository,
)


def test_repo_can_initialize_mapper_at_creation(repo: Repository) -> None:
    """
    Given: A configured mapper
    When: initializing the repository with the mapper
    Then: the mapper is set
    """
    mapper = Mapper()

    result = repo.__class__(database_url=repo.database_url, mapper=mapper)

    assert result.mapper == mapper


def test_repo_saves_entity_extending_relationships(repo: Repository) -> None:
    """
    Given: An EntityExtension object made from a class that extends the Author entity
        class.
    When: EntityExtension object is added with `add` and then retrieved with `get`.
    Then: The retrieved object maintains the attributes.
    """
    repo.mapper = Mapper(
        relationships=[EntityExtension(source=ExtendingEntity, destination=Author)]
    )
    extended_object = ExtendingEntityFactory.create()
    repo.add(extended_object)
    repo.commit()

    result = repo.get(ExtendingEntity, extended_object.id_)

    assert result.first_name == extended_object.first_name


def test_repo_doesnt_return_the_extended_entity_when_querying_for_the_parent_class(
    repo: Repository,
) -> None:
    """
    Given:
        * An EntityExtension object made from a class that extends the Author entity
            class.
        * The EntityExtension object is in the repository.
    When: We retrieve objects of the extended class from the repository.
    Then: As EntityExtension object is of another type, EntityNotFoundError is raised.
    """
    repo.mapper = Mapper(
        relationships=[EntityExtension(source=ExtendingEntity, destination=Author)]
    )
    extended_object = ExtendingEntityFactory.create()
    repo.add(extended_object)
    repo.commit()

    with pytest.raises(
        EntityNotFoundError,
        match="",
    ):
        repo.get(Author, extended_object.id_)


def test_repo_updates_extended_entity_attribute(
    repo: Repository,
) -> None:
    """
    Given:
        * An EntityExtension object made from a class that extends the Author entity
            class.
        * The EntityExtension object is in the repository.
    When: We modify an attribute of the extended entity, and add it back
        to the repository.
    Then: The change is persisted.
    """
    repo.mapper = Mapper(
        relationships=[EntityExtension(source=ExtendingEntity, destination=Author)]
    )
    extended_object = ExtendingEntityFactory.create()
    repo.add(extended_object)
    repo.commit()
    extended_object.first_name = "Alice"
    repo.add(extended_object)
    repo.commit()

    result = repo.get(ExtendingEntity, extended_object.id_)

    assert result.first_name == "Alice"


def test_repo_updates_extending_entity_attribute(
    repo: Repository,
) -> None:
    """
    Given:
        * An EntityExtension object made from a class that extends the Author entity
            class.
        * The EntityExtension object is in the repository.
    When: We modify an attribute of the extending entity not present in the extended
        one, and add it back to the repository.
    Then: The change is persisted.
    """
    repo.mapper = Mapper(
        relationships=[EntityExtension(source=ExtendingEntity, destination=Author)]
    )
    extended_object = ExtendingEntityFactory.create()
    repo.add(extended_object)
    repo.commit()
    extended_object.style = "black"
    repo.add(extended_object)
    repo.commit()

    result = repo.get(ExtendingEntity, extended_object.id_)

    assert result.style == "black"


def test_repo_get_single_composition_unpopulated_relationships(
    repo: Repository,
) -> None:
    """
    Given: A repository with :
        * The mappers loaded, which define that ComposingEntity has a EntityComposition
            relationship with Book.
        * The relationship is not populated.
    When: We get the ComposingEntity object.
    Then: The object is returned and the populated attribute is none
    """
    repo.mapper = Mapper(
        relationships=[
            EntityComposition(
                source=ComposingEntity,
                destination=Book,
            )
        ]
    )
    single_composition_entity = ComposingEntityFactory.create()
    repo.add(single_composition_entity)
    repo.commit()

    result = repo.get(ComposingEntity, single_composition_entity.id_)

    assert result.id_ == single_composition_entity.id_
    assert result.book is None


def test_repo_saves_single_composition_relationships(
    repo: Repository, book: Book
) -> None:
    """
    Given: A repository with :
        * The mappers loaded, which define that ComposingEntity has a EntityComposition
            relationship with Book.
        * The Book is in the repository.
    When: We get the ComposingEntity object.
    Then: The returned object has the relationship attribute populated (book).
    """
    repo.mapper = Mapper(
        relationships=[
            EntityComposition(
                source=ComposingEntity,
                destination=Book,
            )
        ]
    )
    single_composition_entity = ComposingEntityFactory.create()
    single_composition_entity.book = book
    repo.add(single_composition_entity)
    repo.commit()

    result = repo.get(ComposingEntity, single_composition_entity.id_)

    assert result.book == book


def test_repo_saves_single_composition_referenced_object(
    repo: Repository,
) -> None:
    """
    Given: A repository with:
        * The mappers loaded, which define that ComposingEntity has a EntityComposition
            relationship with Book.
        * The Book object is *not* in the repository.
    When: The ComposingEntity is added with `add` and then retrieved with `get`.
    Then: The referenced object Book is added to the repository.
    """
    repo.mapper = Mapper(
        relationships=[
            EntityComposition(
                source=ComposingEntity,
                destination=Book,
            )
        ]
    )
    single_composition_entity = ComposingEntityFactory.create()
    book = BookFactory.create()
    single_composition_entity.book = book
    repo.add(single_composition_entity)
    repo.commit()

    result = repo.get(Book, book.id_)

    assert result.id_ == book.id_


def test_repo_updates_single_composition_referenced_object(
    repo: Repository, book: Book
) -> None:
    """
    Given: A repository with :
        * The mappers loaded, which define that ComposingEntity has a EntityComposition
            relationship with Book.
        * The Book is in the repository.
    When: We modify the referenced object attributes and add the ComposingEntity
    Then: The returned object has the relationship attribute populated with the
        modified entity (book). And there are no duplicated referenced objects.
    """
    repo.mapper = Mapper(
        relationships=[
            EntityComposition(
                source=ComposingEntity,
                destination=Book,
            )
        ]
    )
    single_composition_entity = ComposingEntityFactory.create()
    single_composition_entity.book = book
    repo.add(single_composition_entity)
    repo.commit()
    single_composition_entity.book.title = "The starless sea"
    repo.add(single_composition_entity)
    repo.commit()

    result = repo.get(ComposingEntity, single_composition_entity.id_)

    assert result.book is not None
    assert result.book.title == "The starless sea"
    books = repo.all(Book)
    assert len(books) == 1


def test_repo_can_change_single_composition_referenced_object(
    repo: Repository, book: Book
) -> None:
    """
    Given: A repository with :
        * The mappers loaded, which define that ComposingEntity has a EntityComposition
            relationship with Book.
        * The Book is in the repository.
    When: We change the referenced object and add the ComposingEntity.
    Then: The returned object has the relationship attribute populated with the
        new entity (book), and now the repository has two books.
    """
    repo.mapper = Mapper(
        relationships=[
            EntityComposition(
                source=ComposingEntity,
                destination=Book,
            )
        ]
    )
    single_composition_entity = ComposingEntityFactory.create()
    single_composition_entity.book = book
    repo.add(single_composition_entity)
    repo.commit()
    new_book = BookFactory.create()
    single_composition_entity.book = new_book
    repo.add(single_composition_entity)
    repo.commit()

    result = repo.get(ComposingEntity, single_composition_entity.id_)

    assert result.book == new_book
    books = repo.all(Book)
    assert len(books) == 2


def test_repo_can_unset_single_composition_referenced_object(
    repo: Repository, book: Book
) -> None:
    """
    Given: A repository with :
        * The mappers loaded, which define that ComposingEntity has a EntityComposition
            relationship with Book.
        * The Book is in the repository.
    When: We remove the referenced object and add the ComposingEntity.
    Then: The returned object doesn't have the relationship attribute populated,
        and now the repository has one books.
    """
    repo.mapper = Mapper(
        relationships=[
            EntityComposition(
                source=ComposingEntity,
                destination=Book,
            )
        ]
    )
    single_composition_entity = ComposingEntityFactory.create()
    single_composition_entity.book = book
    repo.add(single_composition_entity)
    repo.commit()
    single_composition_entity.book = None
    repo.add(single_composition_entity)
    repo.commit()

    result = repo.get(ComposingEntity, single_composition_entity.id_)

    assert result.book is None
    books = repo.all(Book)
    assert len(books) == 1


def test_repo_get_multiple_composition_unpopulated_relationships(
    repo: Repository,
) -> None:
    """
    Given: A repository with :
        * The mappers loaded, which define that MultipleComposingEntity has a
            EntityMultipleComposition relationship with Book.
        * The relationship is not populated.
    When: We get the MultipleComposingEntity object.
    Then: The object is returned and the populated attribute is none
    """
    repo.mapper = Mapper(
        relationships=[
            EntityMultipleComposition(
                source=MultipleComposingEntity,
                destination=Book,
            )
        ]
    )
    multiple_composition_entity = MultipleComposingEntityFactory.create()
    repo.add(multiple_composition_entity)
    repo.commit()

    result = repo.get(MultipleComposingEntity, multiple_composition_entity.id_)

    assert result.id_ == multiple_composition_entity.id_
    assert result.books == []


def test_repo_saves_multiple_composition_relationships(
    repo: Repository, books: List[Book]
) -> None:
    """
    Given: A repository with :
        * The mappers loaded, which define that MultipleComposingEntity has a
            EntityMultipleComposition relationship with Book.
        * Three Book objects are in the repository.
    When: We get the MultipleComposingEntity object.
    Then: The returned object has the relationship attribute populated (books).
    """
    repo.mapper = Mapper(
        relationships=[
            EntityMultipleComposition(
                source=MultipleComposingEntity,
                destination=Book,
            )
        ]
    )
    multiple_composition_entity = MultipleComposingEntityFactory.create()
    multiple_composition_entity.books = books
    repo.add(multiple_composition_entity)
    repo.commit()

    result = repo.get(MultipleComposingEntity, multiple_composition_entity.id_)

    assert result.books == sorted(books)


def test_repo_saves_multiple_composition_referenced_object(
    repo: Repository,
) -> None:
    """
    Given: A repository with:
        * The mappers loaded, which define that MultipleComposingEntity has a
            EntityMultipleComposition relationship with Book.
        * The Book object is *not* in the repository.
    When: The ComposingEntity is added with `add` and then retrieved with `get`.
    Then: The referenced object Book is added to the repository.
    """
    repo.mapper = Mapper(
        relationships=[
            EntityMultipleComposition(
                source=MultipleComposingEntity,
                destination=Book,
            )
        ]
    )
    multiple_composition_entity = MultipleComposingEntityFactory.create()
    book = BookFactory.create()
    multiple_composition_entity.books = [book]
    repo.add(multiple_composition_entity)
    repo.commit()

    result = repo.get(Book, book.id_)

    assert result.id_ == book.id_


def test_repo_updates_multiple_composition_relationship_referenced_object(
    repo: Repository, books: List[Book]
) -> None:
    """
    Given: A repository with :
        * The mappers loaded, which define that MultipleComposingEntity has a
            EntityMultipleComposition relationship with Book.
        * Three Book objects are in the repository.
    When: We change the attributes of one of the referenced objects and add the
        MultipleComposingEntity to the repo.
    Then: The returned object has the relationship attribute populated with the
        changed version of the referenced objects (books).
    """
    repo.mapper = Mapper(
        relationships=[
            EntityMultipleComposition(
                source=MultipleComposingEntity,
                destination=Book,
            )
        ]
    )
    multiple_composition_entity = MultipleComposingEntityFactory.create()
    multiple_composition_entity.books = sorted(books)
    repo.add(multiple_composition_entity)
    repo.commit()
    multiple_composition_entity.books[0].title = "The starless sea"
    repo.add(multiple_composition_entity)
    repo.commit()

    result = repo.get(MultipleComposingEntity, multiple_composition_entity.id_)

    assert result.books is not None
    assert result.books[0].title == "The starless sea"


def test_repo_adds_multiple_composition_relationship_referenced_object(
    repo: Repository, books: List[Book]
) -> None:
    """
    Given: A repository with :
        * The mappers loaded, which define that MultipleComposingEntity has a
            EntityMultipleComposition relationship with Book.
        * Three Book objects are in the repository.
    When: We add a new referenced objects and add the MultipleComposingEntity to the
        repo.
    Then: The returned object has the relationship attribute populated with the
        new version of the referenced objects (books).
    """
    repo.mapper = Mapper(
        relationships=[
            EntityMultipleComposition(
                source=MultipleComposingEntity,
                destination=Book,
            )
        ]
    )
    multiple_composition_entity = MultipleComposingEntityFactory.create()
    multiple_composition_entity.books = books
    repo.add(multiple_composition_entity)
    repo.commit()
    new_book = BookFactory.create()
    multiple_composition_entity.books.append(new_book)
    repo.add(multiple_composition_entity)
    repo.commit()

    result = repo.get(MultipleComposingEntity, multiple_composition_entity.id_)

    assert new_book in result.books


def test_repo_removes_multiple_composition_relationship_referenced_object(
    repo: Repository, books: List[Book]
) -> None:
    """
    Given: A repository with :
        * The mappers loaded, which define that MultipleComposingEntity has a
            EntityMultipleComposition relationship with Book.
        * Three Book objects are in the repository.
    When: We remove one of the referenced objects and add the MultipleComposingEntity
        to the repo.
    Then: The returned object doesn't have the removed entity in the relationship
        attribute.
    """
    repo.mapper = Mapper(
        relationships=[
            EntityMultipleComposition(
                source=MultipleComposingEntity,
                destination=Book,
            )
        ]
    )
    multiple_composition_entity = MultipleComposingEntityFactory.create()
    multiple_composition_entity.books = books
    repo.add(multiple_composition_entity)
    repo.commit()
    removed_book = multiple_composition_entity.books.pop(0)
    repo.add(multiple_composition_entity)
    repo.commit()

    result = repo.get(MultipleComposingEntity, multiple_composition_entity.id_)

    assert removed_book not in result.books


def test_repo_unsets_multiple_composition_relationship_referenced_objects(
    repo: Repository, books: List[Book]
) -> None:
    """
    Given: A repository with :
        * The mappers loaded, which define that MultipleComposingEntity has a
            EntityMultipleComposition relationship with Book.
        * Three Book objects are in the repository.
    When: We remove all of the referenced objects and add the MultipleComposingEntity
        to the repo.
    Then: The returned object has an empty relationship attribute.
    """
    repo.mapper = Mapper(
        relationships=[
            EntityMultipleComposition(
                source=MultipleComposingEntity,
                destination=Book,
            )
        ]
    )
    multiple_composition_entity = MultipleComposingEntityFactory.create()
    multiple_composition_entity.books = books
    repo.add(multiple_composition_entity)
    repo.commit()
    multiple_composition_entity.books = []
    repo.add(multiple_composition_entity)
    repo.commit()

    result = repo.get(MultipleComposingEntity, multiple_composition_entity.id_)

    assert result.books == []
