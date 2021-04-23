"""Store the repository-orm exceptions."""


class EntityNotFoundError(Exception):
    """Raised when the search or retrieve of an entity fails."""


class AutoIncrementError(Exception):
    """Raised when the id_ auto increment repository feature fails."""