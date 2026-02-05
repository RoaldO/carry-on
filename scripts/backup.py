#!/usr/bin/env python3
"""Backup MongoDB database to JSON files.

This script exports all collections from the carryon database to timestamped
JSON files in the backups/ directory.

Usage:
    # Set the backup URI (read-only access is sufficient)
    export MONGODB_BACKUP_URI="mongodb+srv://backup-user:password@cluster.mongodb.net"

    # Run backup
    uv run scripts/backup.py

    # Or specify a custom output directory
    uv run scripts/backup.py --output /path/to/backups
"""

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

from bson import ObjectId
from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()

DATABASE_NAME = "carryon"
COLLECTIONS = ["users", "strokes", "ideas"]


class MongoJSONEncoder(json.JSONEncoder):
    """JSON encoder that handles MongoDB types."""

    def default(self, obj):
        if isinstance(obj, ObjectId):
            return {"$oid": str(obj)}
        if isinstance(obj, datetime):
            return {"$date": obj.isoformat()}
        return super().default(obj)


def get_backup_client() -> MongoClient:
    """Get MongoDB client using backup URI."""
    uri = os.getenv("MONGODB_BACKUP_URI")
    if not uri:
        print("Error: MONGODB_BACKUP_URI environment variable not set")
        print("")
        print("Set it to your MongoDB connection string:")
        print('  export MONGODB_BACKUP_URI="mongodb+srv://..."')
        sys.exit(1)
    return MongoClient(uri)


def backup_collection(db, collection_name: str, output_dir: Path) -> int:
    """Export a collection to a JSON file.

    Returns the number of documents exported.
    """
    collection = db[collection_name]
    documents = list(collection.find())

    output_file = output_dir / f"{collection_name}.json"
    with open(output_file, "w") as f:
        json.dump(documents, f, cls=MongoJSONEncoder, indent=2)

    return len(documents)


def main():
    parser = argparse.ArgumentParser(description="Backup MongoDB database")
    parser.add_argument(
        "--output",
        "-o",
        type=Path,
        default=Path("backups"),
        help="Output directory for backups (default: backups/)",
    )
    args = parser.parse_args()

    print("CarryOn Database Backup")
    print("=" * 40)

    # Create timestamped backup directory
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    backup_dir = args.output / timestamp
    backup_dir.mkdir(parents=True, exist_ok=True)

    print(f"Backup directory: {backup_dir}")
    print("")

    # Connect to database
    client = get_backup_client()
    db = client[DATABASE_NAME]

    # Backup each collection
    total_docs = 0
    for collection_name in COLLECTIONS:
        count = backup_collection(db, collection_name, backup_dir)
        print(f"  {collection_name}: {count} documents")
        total_docs += count

    # Write metadata
    metadata = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "database": DATABASE_NAME,
        "collections": COLLECTIONS,
        "document_counts": {name: len(list(db[name].find())) for name in COLLECTIONS},
    }
    with open(backup_dir / "metadata.json", "w") as f:
        json.dump(metadata, f, indent=2)

    print("")
    print(f"Backup complete: {total_docs} total documents")
    print(f"Location: {backup_dir.absolute()}")

    client.close()


if __name__ == "__main__":
    main()
