"""Database utilities for acceptance tests."""

import os
from datetime import datetime
from typing import Any

from pymongo import MongoClient
from pymongo.database import Database


def get_test_database() -> Database[Any]:
    """Get MongoDB database connection for tests.

    Uses MONGODB_TEST_URI if set, otherwise falls back to MONGODB_URI.
    As a safety measure, refuses to run if the URI appears to point to
    a production database (must contain 'test' or 'localhost').

    Returns:
        The 'carryon' database from the MongoDB connection.

    Raises:
        RuntimeError: If no URI is set or if URI appears to be production.
    """
    uri = os.getenv("MONGODB_TEST_URI") or os.getenv("MONGODB_URI")
    if not uri:
        raise RuntimeError(
            "MONGODB_TEST_URI or MONGODB_URI environment variable must be set"
        )

    # Safety check: refuse to run against production databases
    uri_lower = uri.lower()
    is_safe = (
        "test" in uri_lower
        or "localhost" in uri_lower
        or "127.0.0.1" in uri_lower
    )
    if not is_safe:
        raise RuntimeError(
            "DANGER: Refusing to run tests against what appears to be a "
            "production database. Set MONGODB_TEST_URI to a test database, "
            "or ensure your URI contains 'test' or 'localhost'."
        )

    client: MongoClient[Any] = MongoClient(uri)
    return client.carryon


def clear_collections(db: Database[Any]) -> None:
    """Clear test collections to ensure clean state.

    Clears the users, strokes, and ideas collections.

    Args:
        db: The MongoDB database instance.
    """
    db.users.delete_many({})
    db.strokes.delete_many({})
    db.ideas.delete_many({})


def insert_user(
    db: Database[Any],
    email: str,
    display_name: str,
    password_hash: str | None = None,
    activated_at: datetime | str | None = None,
) -> str:
    """Insert a user document into the database.

    Args:
        db: The MongoDB database instance.
        email: User's email address (will be lowercased).
        display_name: User's display name.
        password_hash: Hashed password (None for inactive users).
        activated_at: Activation timestamp (None for inactive users).
            Can be a datetime object or ISO format string.

    Returns:
        The string representation of the inserted user's _id.
    """
    if isinstance(activated_at, datetime):
        activated_at = activated_at.isoformat()

    doc = {
        "email": email.lower(),
        "display_name": display_name,
        "password_hash": password_hash,
        "activated_at": activated_at,
    }
    result = db.users.insert_one(doc)
    return str(result.inserted_id)
