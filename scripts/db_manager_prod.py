#!/usr/bin/env python3
"""
Production-ready database management script with proper Prisma handling
"""

import argparse
import subprocess
import sys
import os
import shutil


def get_python_command():
    """Get the correct Python command for this environment"""
    if shutil.which('python3'):
        return 'python3'
    elif shutil.which('python'):
        return 'python'
    else:
        raise RuntimeError("No Python interpreter found")


def setup_prisma_environment():
    """Setup proper Prisma environment variables"""
    # Get current user
    import getpass
    current_user = getpass.getuser()
    
    # Set environment variables to handle permission issues
    user_cache_dir = f'/home/{current_user}/.cache/prisma-python'
    os.environ.setdefault('PRISMA_QUERY_ENGINE_LIBRARY', f'{user_cache_dir}/query-engine')
    os.environ.setdefault('PRISMA_SCHEMA_ENGINE_BINARY', f'{user_cache_dir}/schema-engine')
    os.environ.setdefault('PRISMA_CLIENT_ENGINE_TYPE', 'binary')
    
    # Create user-specific cache directories
    try:
        os.makedirs(user_cache_dir, exist_ok=True)
        os.makedirs('/tmp/prisma-user-cache', exist_ok=True)
    except PermissionError:
        # If we can't create in standard locations, use temporary directory
        import tempfile
        temp_dir = tempfile.mkdtemp(prefix='prisma-cache-')
        os.environ['PRISMA_QUERY_ENGINE_LIBRARY'] = f'{temp_dir}/query-engine'
        os.environ['PRISMA_SCHEMA_ENGINE_BINARY'] = f'{temp_dir}/schema-engine'
        print(f"📁 Using temporary cache directory: {temp_dir}")


def run_command(command, description):
    """Run a command and handle errors with proper Python interpreter"""
    print(f"🔄 {description}...")
    
    # Replace 'python' with the correct Python command
    python_cmd = get_python_command()
    if command.startswith('python '):
        command = command.replace('python ', f'{python_cmd} ', 1)
    
    try:
        result = subprocess.run(
            command, 
            shell=True, 
            check=True, 
            capture_output=True, 
            text=True,
            env=os.environ.copy()
        )
        print(f"✅ {description} completed successfully")
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed")
        print(f"Command: {command}")
        if e.stderr:
            print("STDERR:", e.stderr)
        if e.stdout:
            print("STDOUT:", e.stdout)
        return False


def check_prisma_setup():
    """Check if Prisma is properly set up"""
    print("🔍 Checking Prisma setup...")
    
    try:
        # Try to import prisma
        result = subprocess.run(
            [get_python_command(), '-c', 'import prisma; print("Prisma import: OK")'],
            check=True,
            capture_output=True,
            text=True
        )
        print("✅ Prisma Python client is available")
        return True
    except subprocess.CalledProcessError as e:
        print("❌ Prisma Python client not available")
        print("Installing Prisma...")
        
        # Try to install prisma
        install_result = subprocess.run(
            [get_python_command(), '-m', 'pip', 'install', 'prisma'],
            capture_output=True,
            text=True
        )
        
        if install_result.returncode == 0:
            print("✅ Prisma installed successfully")
            # Generate Prisma client
            generate_result = subprocess.run(
                ['prisma', 'generate'],
                capture_output=True,
                text=True,
                cwd='/app'
            )
            
            if generate_result.returncode == 0:
                print("✅ Prisma client generated successfully")
                return True
            else:
                print("❌ Failed to generate Prisma client")
                print(generate_result.stderr)
        
        return False


def seed_database():
    """Run complete database seeding"""
    print("🌱 Starting complete database seeding...")

    # Setup Prisma environment
    setup_prisma_environment()
    
    # Check Prisma setup
    if not check_prisma_setup():
        print("❌ Prisma setup failed. Please run as root to fix permissions.")
        return False

    # Check database seeding requirements
    print("🔍 Checking database seeding requirements...")
    
    # Run smart seed first (for all tables except subjects)
    if not run_command("python scripts/smart_seed.py", "Running smart seed"):
        print("❌ Smart seed failed. Trying alternative approach...")
        
        # Try with explicit python3
        python_cmd = get_python_command()
        if not run_command(f"{python_cmd} scripts/smart_seed.py", "Running smart seed with explicit Python"):
            return False

    # Run subject sync
    if not run_command("python scripts/sync_subjects.py", "Syncing subjects"):
        # Try with explicit python3
        python_cmd = get_python_command()
        if not run_command(f"{python_cmd} scripts/sync_subjects.py", "Syncing subjects with explicit Python"):
            return False

    print("✅ Complete database seeding finished!")
    return True


def reset_database():
    """Reset the database"""
    print("🔄 Resetting database...")
    setup_prisma_environment()
    return run_command("python scripts/reset_database.py", "Database reset")


def sync_subjects_only():
    """Sync only subjects"""
    print("📚 Syncing subjects only...")
    setup_prisma_environment()
    return run_command("python scripts/sync_subjects.py", "Subject sync")


def reset_and_seed():
    """Reset database and run complete seeding"""
    print("🔄 Reset and complete seeding...")
    if reset_database():
        return seed_database()
    return False


def main():
    parser = argparse.ArgumentParser(description="SOPA Backend Database Management (Production)")
    parser.add_argument(
        "command",
        choices=["seed", "reset", "subjects", "reset-seed", "check"],
        help="Command to execute",
    )

    args = parser.parse_args()

    # Change to script directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(script_dir)
    os.chdir(parent_dir)

    # Print environment info
    print(f"🐍 Using Python: {get_python_command()}")
    print(f"📁 Working directory: {os.getcwd()}")

    if args.command == "seed":
        success = seed_database()
    elif args.command == "reset":
        success = reset_database()
    elif args.command == "subjects":
        success = sync_subjects_only()
    elif args.command == "reset-seed":
        success = reset_and_seed()
    elif args.command == "check":
        success = check_prisma_setup()
    else:
        print("❌ Unknown command")
        success = False

    if success:
        print("\n🎉 Operation completed successfully!")
    else:
        print("\n💡 If you're getting permission errors, try running as root:")
        print("   docker exec -it --user root sopa_api_prod python scripts/fix_prisma_permissions.py")

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
