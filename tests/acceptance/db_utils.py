"""Database utilities for acceptance tests."""

import os
from datetime import datetime
from typing import Any

from pymongo import MongoClient
from pymongo.database import Database


def get_test_database() -> Database[Any]:
    """Get MongoDB database connection using MONGODB_URI environment variable.

    Returns:
        The 'carryon' database from the MongoDB connection.

    Raises:
        RuntimeError: If MONGODB_URI is not set.
    """
    uri = os.getenv("MONGODB_URI")
    if not uri:
        raise RuntimeError("MONGODB_URI environment variable is not set")
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
    pin_hash: str | None = None,
    activated_at: datetime | str | None = None,
) -> str:
    """Insert a user document into the database.

    Args:
        db: The MongoDB database instance.
        email: User's email address (will be lowercased).
        display_name: User's display name.
        pin_hash: Hashed PIN (None for inactive users).
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
        "pin_hash": pin_hash,
        "activated_at": activated_at,
    }
    result = db.users.insert_one(doc)
    return str(result.inserted_id)
