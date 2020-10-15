# Repository Pattern

[![Actions Status](https://github.com/lyz-code/repository-pattern/workflows/Python%20package/badge.svg)](https://github.com/lyz-code/repository-pattern/actions)

Library to ease the implementation of the [repository
pattern](https://lyz-code.github.io/blue-book/architecture/repository_pattern/).

One of the disadvantages of using the repository pattern is that developers need
to add and maintain a new abstraction to manage how to persist their models
in the storage. *repository-pattern* aims to mitigate this inconvenient by:

* Supplying classes that already have the common operations for different
    storage solutions.
* Supplying test classes and fixtures so extending the provided repositories is
    easy.

## Help

See [documentation](https://github.io/lyz-code/repository-pattern) for more
details.

## Installing

```bash
pip install repository-pattern
```

## A Simple Example

```python
from repository_pattern import Entity, FakeRepository

repo = FakeRepository()


class Author(Entity):
    id: int
    first_name: str
    last_name: str
    country: str


author = Author(id=0, first_name="Brandon", last_name="Sanderson", country="US")

# Add entities
repo.add(author)
repo.commit()

# Search entities
brandon = repo.search(Author, {"first_name": "Brandon"})[0]
assert brandon == author

# Delete entities
repo.delete(brandon)
repo.commit()
assert len(repo.all(Author)) == 0
```

## Contributing

For guidance on setting up a development environment and how to make
a contribution to *repository-pattern*, see [Contributing to
repository-pattern](https://lyz-code.github.io/blue-book/architecture/repository_pattern/contributing).

## License

GPLv3
