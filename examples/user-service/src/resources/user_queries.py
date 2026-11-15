CREATE_USERS_TABLE = """
    CREATE TABLE IF NOT EXISTS users (
        id TEXT PRIMARY KEY,
        email TEXT NOT NULL UNIQUE,
        name TEXT NOT NULL
    )
"""

INSERT_USER = """
    INSERT INTO users (id, email, name)
    VALUES (:id, :email, :name)
"""

FIND_USER_BY_EMAIL = """
    SELECT id, email, name FROM users WHERE email = :email
"""
