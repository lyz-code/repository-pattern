import factory

from .model import Author, Book, Genre


class AuthorFactory(factory.Factory):
    """
    Class to generate a fake author.
    """

    id = factory.Faker("word")
    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")
    country = factory.Faker("country")

    class Meta:
        model = Author


class BookFactory(factory.Factory):
    """
    Class to generate a fake book.
    """

    id = factory.Faker("pyint")
    title = factory.Faker("sentence")
    summary = factory.Faker("text")
    released = factory.Faker("date_time")

    class Meta:
        model = Book


class GenreFactory(factory.Factory):
    """
    Class to generate a fake genre.
    """

    id = factory.Faker("pyint")
    name = factory.Faker("name")
    description = factory.Faker("sentence")

    class Meta:
        model = Genre
