#!/usr/bin/env python3
"""Restore MongoDB database from JSON backup files.

This script imports collections from a backup directory into the carryon database.

WARNING: This will DELETE all existing data in the target collections before
restoring. Use with caution!

Usage:
    # Set the backup URI (needs write access)
    export MONGODB_BACKUP_URI="mongodb+srv://backup-user:password@cluster.mongodb.net"

    # List available backups
    uv run scripts/restore.py --list

    # Restore from a specific backup
    uv run scripts/restore.py backups/20240115_120000

    # Restore without confirmation prompt (for automation)
    uv run scripts/restore.py backups/20240115_120000 --yes
"""

import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path

from bson import ObjectId
from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()

DATABASE_NAME = "carryon"
COLLECTIONS = ["users", "strokes", "ideas"]


def decode_mongo_types(obj):
    """Decode MongoDB extended JSON types back to native types."""
    if isinstance(obj, dict):
        if "$oid" in obj:
            return ObjectId(obj["$oid"])
        if "$date" in obj:
            return datetime.fromisoformat(obj["$date"].replace("Z", "+00:00"))
        return {k: decode_mongo_types(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [decode_mongo_types(item) for item in obj]
    return obj


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


def list_backups(backup_root: Path):
    """List all available backups."""
    if not backup_root.exists():
        print(f"No backups directory found at: {backup_root}")
        return

    backups = sorted(backup_root.iterdir(), reverse=True)
    backups = [b for b in backups if b.is_dir() and (b / "metadata.json").exists()]

    if not backups:
        print("No backups found.")
        return

    print("Available backups:")
    print("")
    for backup_dir in backups:
        with open(backup_dir / "metadata.json") as f:
            metadata = json.load(f)
        counts = metadata.get("document_counts", {})
        total = sum(counts.values())
        print(f"  {backup_dir.name}  ({total} documents)")
        for collection, count in counts.items():
            print(f"    - {collection}: {count}")
        print("")


def restore_collection(db, collection_name: str, backup_dir: Path) -> int:
    """Restore a collection from a JSON file.

    Returns the number of documents restored.
    """
    input_file = backup_dir / f"{collection_name}.json"
    if not input_file.exists():
        print(f"  Warning: {input_file} not found, skipping {collection_name}")
        return 0

    with open(input_file) as f:
        documents = json.load(f)

    # Decode MongoDB types
    documents = decode_mongo_types(documents)

    if not documents:
        return 0

    collection = db[collection_name]

    # Delete existing documents
    deleted = collection.delete_many({})

    # Insert restored documents
    collection.insert_many(documents)

    return len(documents)


def main():
    parser = argparse.ArgumentParser(description="Restore MongoDB database from backup")
    parser.add_argument(
        "backup_dir",
        type=Path,
        nargs="?",
        help="Backup directory to restore from",
    )
    parser.add_argument(
        "--list",
        "-l",
        action="store_true",
        help="List available backups",
    )
    parser.add_argument(
        "--yes",
        "-y",
        action="store_true",
        help="Skip confirmation prompt",
    )
    parser.add_argument(
        "--backup-root",
        type=Path,
        default=Path("backups"),
        help="Root directory for backups (default: backups/)",
    )
    args = parser.parse_args()

    if args.list:
        list_backups(args.backup_root)
        return

    if not args.backup_dir:
        parser.print_help()
        print("")
        print("Error: backup_dir is required (or use --list to see available backups)")
        sys.exit(1)

    if not args.backup_dir.exists():
        print(f"Error: Backup directory not found: {args.backup_dir}")
        sys.exit(1)

    if not (args.backup_dir / "metadata.json").exists():
        print(f"Error: Invalid backup directory (missing metadata.json): {args.backup_dir}")
        sys.exit(1)

    print("CarryOn Database Restore")
    print("=" * 40)

    # Show backup info
    with open(args.backup_dir / "metadata.json") as f:
        metadata = json.load(f)

    print(f"Backup: {args.backup_dir}")
    print(f"Created: {metadata.get('timestamp', 'unknown')}")
    print("")
    print("Documents to restore:")
    for collection, count in metadata.get("document_counts", {}).items():
        print(f"  - {collection}: {count}")
    print("")

    # Confirm
    if not args.yes:
        print("WARNING: This will DELETE all existing data in these collections!")
        print("")
        confirm = input("Type 'restore' to confirm: ").strip()
        if confirm != "restore":
            print("Restore cancelled.")
            sys.exit(0)
        print("")

    # Connect to database
    client = get_backup_client()
    db = client[DATABASE_NAME]

    # Restore each collection
    print("Restoring...")
    total_docs = 0
    for collection_name in COLLECTIONS:
        count = restore_collection(db, collection_name, args.backup_dir)
        print(f"  {collection_name}: {count} documents")
        total_docs += count

    print("")
    print(f"Restore complete: {total_docs} total documents")

    client.close()


if __name__ == "__main__":
    main()
