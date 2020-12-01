[![Actions Status](https://github.com/lyz-code/repository-pattern/workflows/Tests/badge.svg)](https://github.com/lyz-code/repository-pattern/actions)
[![Actions Status](https://github.com/lyz-code/repository-pattern/workflows/Build/badge.svg)](https://github.com/lyz-code/repository-pattern/actions)
[![Coverage Status](https://coveralls.io/repos/github/lyz-code/repository-pattern/badge.svg?branch=master)](https://coveralls.io/github/lyz-code/repository-pattern?branch=master)

Library to ease the implementation of the [repository
pattern](https://lyz-code.github.io/blue-book/architecture/repository_pattern/)
in python projects.

One of the disadvantages of using the repository pattern is that developers need
to add and maintain a new abstraction to manage how to persist their models
in the storage. *repository-pattern* aims to mitigate this inconvenient by:

* Supplying classes that already have the common operations for different
    storage solutions.
* Supplying test classes and fixtures so extending the provided repositories is
    easy.

# Installing

```bash
pip install repository-pattern
```

# A Simple Example

```python
{! examples/simple-example.py !} # noqa
```

# Usage

The different repositories share the following operations:

`add`
: Add an `Entity` object to the repository.

`delete`
: Remove an `Entity` object form the repository.

`get`
: Obtain an `Entity` from the repository by it's ID.

`commit`
: Persist the changes into the repository.

`all`
: Obtain all the entities of type `Entity` from the repository.

`search`
: Obtain the entities whose attributes match a condition.

!!! note ""
    Changes in the repository aren't persisted until you run `repo.commit()`.

# Contributing

For guidance on setting up a development environment, and how to make
a contribution to *repository-pattern*, see [Contributing to
repository-pattern](https://lyz-code.github.io/repository-pattern/contributing).
