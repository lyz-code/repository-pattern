"""Initial schema yoyo migrations script."""

from yoyo import step

steps = [
    step(
        "CREATE TABLE author ("
        "id_ VARCHAR(26), "
        "first_name VARCHAR(20), "
        "last_name VARCHAR(20), "
        "country VARCHAR(20), "
        "rating INT, "
        "PRIMARY KEY (id_))",
        "DROP TABLE author",
    ),
    step(
        "CREATE TABLE book ("
        "id_ INT, "
        "title VARCHAR(20), "
        "summary VARCHAR(255), "
        "released DATETIME, "
        "rating INT, "
        "PRIMARY KEY (id_))",
        "DROP TABLE book",
    ),
    step(
        "CREATE TABLE genre ("
        "id_ INT, "
        "name VARCHAR(20), "
        "description VARCHAR(255), "
        "rating INT, "
        "PRIMARY KEY (id_))",
        "DROP TABLE genre",
    ),
    step(
        "CREATE TABLE extendingentity ("
        "id_ VARCHAR(26), "
        "style VARCHAR(20), "
        "PRIMARY KEY (id_), "
        "FOREIGN KEY (id_) REFERENCES author(id_) ON DELETE CASCADE)",
        "DROP TABLE extendingentity",
    ),
    step(
        "CREATE TABLE composingentity ("
        "id_ INT, "
        "name VARCHAR(20), "
        "book_id INT, "
        "PRIMARY KEY (id_), "
        "FOREIGN KEY (book_id) REFERENCES book(id_) ON DELETE SET NULL)",
        "DROP TABLE composingentity",
    ),
    step(
        "CREATE TABLE multiplecomposingentity ("
        "id_ INT, "
        "name VARCHAR(20), "
        "PRIMARY KEY (id_))",
        "DROP TABLE multiplecomposingentity",
    ),
    step(
        "CREATE TABLE multiplecomposingentity_book_relationship ("
        "id_ INTEGER, "
        "multiplecomposingentity_id INT NOT NULL, "
        "book_id INT NOT NULL, "
        "PRIMARY KEY (id_), "
        "FOREIGN KEY (multiplecomposingentity_id) REFERENCES "
        "multiplecomposingentity(id_) ON DELETE CASCADE, "
        "FOREIGN KEY (book_id) REFERENCES book(id_) ON DELETE CASCADE, "
        "UNIQUE(multiplecomposingentity_id, book_id))",
        "DROP TABLE multiplecomposingentity_book_relationship",
    ),
]
