#!/usr/bin/env python3
"""
Database migration script for production
Handles Prisma migrations using Python subprocess
"""

import subprocess
import sys
import os
from pathlib import Path


def run_command(command, cwd=None):
    """Run a shell command and handle errors"""
    try:
        print(f"🔄 Running: {command}")
        result = subprocess.run(
            command, shell=True, check=True, capture_output=True, text=True, cwd=cwd
        )
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error running command: {command}")
        print(f"Return code: {e.returncode}")
        if e.stdout:
            print(f"STDOUT: {e.stdout}")
        if e.stderr:
            print(f"STDERR: {e.stderr}")
        return False


def check_node_availability():
    """Check if Node.js and npm are available"""
    print("🔍 Checking Node.js availability...")

    # Check node
    if not run_command("node --version"):
        print("❌ Node.js not found!")
        return False

    # Check npm
    if not run_command("npm --version"):
        print("❌ npm not found!")
        return False

    print("✅ Node.js and npm are available!")
    return True


def install_prisma_cli():
    """Install Prisma CLI if not available"""
    print("🔄 Installing Prisma CLI...")
    return run_command("npm install -g prisma @prisma/client")


def run_migrations():
    """Run Prisma migrations"""
    print("🔄 Running database migrations...")

    # Change to app directory
    app_dir = Path("/app")

    # Try to run migrate deploy
    if run_command("prisma migrate deploy", cwd=app_dir):
        print("✅ Migrations completed successfully!")
        return True
    else:
        print("❌ Migration failed!")
        return False


def generate_prisma_client():
    """Generate Prisma client"""
    print("🔄 Generating Prisma client...")

    app_dir = Path("/app")

    if run_command("prisma generate", cwd=app_dir):
        print("✅ Prisma client generated successfully!")
        return True
    else:
        print("❌ Prisma client generation failed!")
        return False


def main():
    """Main migration process"""
    print("🚀 Starting database migration process...")

    # Check if we're in the right directory
    if not Path("/app/prisma/schema.prisma").exists():
        print("❌ Prisma schema not found! Make sure you're in the app container.")
        sys.exit(1)

    # Check Node.js availability
    if not check_node_availability():
        print("🔄 Node.js not available, attempting to install Prisma CLI...")
        if not install_prisma_cli():
            print("❌ Failed to install Prisma CLI!")
            sys.exit(1)

    # Generate Prisma client
    if not generate_prisma_client():
        print("❌ Failed to generate Prisma client!")
        sys.exit(1)

    # Run migrations
    if not run_migrations():
        print("❌ Migration process failed!")
        sys.exit(1)

    print("🎉 Migration process completed successfully!")


if __name__ == "__main__":
    main()
