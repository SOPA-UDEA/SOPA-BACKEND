#!/usr/bin/env python3
"""
Reset Database Seeding Flag
Use this script if you need to force re-seeding of the database
"""

import os
import sys


def reset_seeding_flag():
    """Remove the seeding flag to allow re-seeding"""
    flag_file = "/app/.db_seeded"

    try:
        if os.path.exists(flag_file):
            os.remove(flag_file)
            print(f"✅ Removed seeding flag: {flag_file}")
            print("🔄 Database will be re-seeded on next deployment")
        else:
            print(f"ℹ️ No seeding flag found at: {flag_file}")
            print("🌱 Database will be seeded on next deployment")

    except Exception as e:
        print(f"❌ Error removing seeding flag: {e}")
        sys.exit(1)


if __name__ == "__main__":
    print("🔄 Resetting database seeding flag...")
    reset_seeding_flag()
    print("✅ Reset complete!")
