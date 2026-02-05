#!/usr/bin/env python3
"""Migration script to add user_id to existing strokes and ideas.

This script:
1. Finds existing strokes/ideas without user_id
2. Assigns them to a specified user (prompts for email)
3. Creates compound indexes (user_id, created_at) for query performance

Usage:
    uv run scripts/migrate_user_isolation.py
"""

import os
import sys

from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()


def get_db():
    """Get MongoDB database connection."""
    uri = os.getenv("MONGODB_URI")
    if not uri:
        print("Error: MONGODB_URI environment variable not set")
        sys.exit(1)
    client = MongoClient(uri)
    return client.carryon


def get_user_by_email(db, email: str):
    """Look up user by email."""
    user = db.users.find_one({"email": email.lower()})
    return user


def migrate_collection(db, collection_name: str, user_id: str) -> int:
    """Assign user_id to documents without one.

    Returns the number of documents updated.
    """
    collection = db[collection_name]
    result = collection.update_many(
        {"user_id": {"$exists": False}},
        {"$set": {"user_id": user_id}},
    )
    return result.modified_count


def create_indexes(db):
    """Create compound indexes for efficient user-filtered queries."""
    print("Creating indexes...")

    # Index for strokes: (user_id, created_at)
    db.strokes.create_index([("user_id", 1), ("created_at", -1)])
    print("  - Created index on strokes (user_id, created_at)")

    # Index for ideas: (user_id, created_at)
    db.ideas.create_index([("user_id", 1), ("created_at", -1)])
    print("  - Created index on ideas (user_id, created_at)")


def count_documents_without_user_id(db, collection_name: str) -> int:
    """Count documents that don't have a user_id field."""
    collection = db[collection_name]
    return collection.count_documents({"user_id": {"$exists": False}})


def main():
    """Run the migration."""
    print("User Isolation Migration Script")
    print("=" * 40)

    db = get_db()

    # Count documents without user_id
    strokes_count = count_documents_without_user_id(db, "strokes")
    ideas_count = count_documents_without_user_id(db, "ideas")

    print("\nDocuments without user_id:")
    print(f"  - Strokes: {strokes_count}")
    print(f"  - Ideas: {ideas_count}")

    if strokes_count == 0 and ideas_count == 0:
        print("\nNo documents need migration.")
        print("Creating indexes anyway...")
        create_indexes(db)
        print("\nMigration complete!")
        return

    # Prompt for default user email
    print("\nEnter the email of the user to assign existing data to:")
    email = input("> ").strip()

    if not email:
        print("Error: Email cannot be empty")
        sys.exit(1)

    user = get_user_by_email(db, email)
    if not user:
        print(f"Error: User with email '{email}' not found")
        sys.exit(1)

    user_id = str(user["_id"])
    display_name = user.get("display_name", email)

    print(f"\nWill assign data to: {display_name} ({email})")
    print(f"User ID: {user_id}")
    confirm = input("Proceed? (yes/no): ").strip().lower()

    if confirm != "yes":
        print("Migration cancelled.")
        sys.exit(0)

    # Perform migration
    print("\nMigrating data...")

    if strokes_count > 0:
        updated = migrate_collection(db, "strokes", user_id)
        print(f"  - Updated {updated} strokes")

    if ideas_count > 0:
        updated = migrate_collection(db, "ideas", user_id)
        print(f"  - Updated {updated} ideas")

    # Create indexes
    create_indexes(db)

    print("\nMigration complete!")


if __name__ == "__main__":
    main()
