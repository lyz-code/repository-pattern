

Advantages:

* You don't need to define Database related attributes at model level, author_id

Relationship types:

* Extension:


We can't support backref https://github.com/samuelcolvin/pydantic/issues/2279,
if you want them, you'll need to generate them yourself at service level.
