#!/usr/bin/env python3
"""
SOPA Backend Database Management Script
Provides commands for database management and seeding
"""

import argparse
import subprocess
import sys
import os


def run_command(command, description):
    """Run a command and handle errors"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(
            command, shell=True, check=True, capture_output=True, text=True
        )
        print(f"✅ {description} completed successfully")
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed")
        if e.stderr:
            print(e.stderr)
        if e.stdout:
            print(e.stdout)
        return False


def seed_database():
    """Run complete database seeding"""
    print("🌱 Starting complete database seeding...")

    # Run smart seed first (for all tables except subjects)
    if not run_command("python scripts/smart_seed.py", "Running smart seed"):
        return False

    # Run subject sync
    if not run_command("python scripts/sync_subjects.py", "Syncing subjects"):
        return False

    print("✅ Complete database seeding finished!")
    return True


def reset_database():
    """Reset the database"""
    print("🔄 Resetting database...")
    return run_command("python scripts/reset_database.py", "Database reset")


def sync_subjects_only():
    """Sync only subjects"""
    print("📚 Syncing subjects only...")
    return run_command("python scripts/sync_subjects.py", "Subject sync")


def reset_and_seed():
    """Reset database and run complete seeding"""
    print("🔄 Reset and complete seeding...")
    if reset_database():
        return seed_database()
    return False


def main():
    parser = argparse.ArgumentParser(description="SOPA Backend Database Management")
    parser.add_argument(
        "command",
        choices=["seed", "reset", "subjects", "reset-seed"],
        help="Command to execute",
    )

    args = parser.parse_args()

    # Change to script directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(script_dir)
    os.chdir(parent_dir)

    if args.command == "seed":
        success = seed_database()
    elif args.command == "reset":
        success = reset_database()
    elif args.command == "subjects":
        success = sync_subjects_only()
    elif args.command == "reset-seed":
        success = reset_and_seed()
    else:
        print("❌ Unknown command")
        success = False

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
