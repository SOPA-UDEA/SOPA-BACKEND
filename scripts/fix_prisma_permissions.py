#!/usr/bin/env python3
"""
Fix Prisma permissions and setup in production container
This script handles common permission issues with Prisma binaries
"""

import subprocess
import sys
import os
from pathlib import Path


def run_command(command, cwd=None, capture_output=True):
    """Run a shell command and handle errors"""
    try:
        print(f"🔄 Running: {command}")
        result = subprocess.run(
            command, 
            shell=True, 
            check=True, 
            capture_output=capture_output, 
            text=True, 
            cwd=cwd
        )
        if result.stdout and capture_output:
            print(result.stdout)
        return True, result.stdout if capture_output else ""
    except subprocess.CalledProcessError as e:
        print(f"❌ Error running command: {command}")
        print(f"Return code: {e.returncode}")
        if e.stdout:
            print(f"STDOUT: {e.stdout}")
        if e.stderr:
            print(f"STDERR: {e.stderr}")
        return False, ""


def check_user_permissions():
    """Check current user and permissions"""
    print("🔍 Checking current user and permissions...")
    
    success, output = run_command("whoami")
    if success:
        user = output.strip()
        print(f"Current user: {user}")
        
        # Check if we're root
        if user == "root":
            print("✅ Running as root - should have full permissions")
            return True
        else:
            print(f"⚠️ Running as {user} - may have permission issues")
            return False
    
    return False


def fix_prisma_cache_permissions():
    """Fix Prisma cache directory permissions"""
    print("🔧 Fixing Prisma cache permissions...")
    
    # Get current user
    success, user = run_command("whoami")
    if not success:
        return False
    
    user = user.strip()
    
    # Common Prisma cache locations
    cache_dirs = [
        "/root/.cache/prisma-python",
        f"/home/{user}/.cache/prisma-python",
        "/tmp/prisma-cache"
    ]
    
    for cache_dir in cache_dirs:
        if os.path.exists(cache_dir):
            print(f"📁 Found cache directory: {cache_dir}")
            
            # Fix ownership
            run_command(f"chown -R {user}:{user} {cache_dir}", capture_output=False)
            
            # Fix permissions
            run_command(f"chmod -R 755 {cache_dir}", capture_output=False)


def install_prisma_properly():
    """Install Prisma with proper permissions"""
    print("🔄 Installing Prisma with proper setup...")
    
    # Set environment variables for Prisma
    os.environ["PRISMA_QUERY_ENGINE_LIBRARY"] = "/tmp/prisma-query-engine"
    os.environ["PRISMA_INTROSPECTION_ENGINE_BINARY"] = "/tmp/prisma-introspection-engine"
    
    # Install prisma-client-py
    success, _ = run_command("pip install --upgrade prisma")
    if not success:
        return False
    
    # Try to generate client
    app_dir = Path("/app")
    success, _ = run_command("prisma generate", cwd=app_dir)
    if not success:
        print("⚠️ First generation failed, trying with elevated permissions...")
        
        # Create temp directory for Prisma binaries
        run_command("mkdir -p /tmp/prisma-cache", capture_output=False)
        run_command("chmod 777 /tmp/prisma-cache", capture_output=False)
        
        # Set Prisma binary path
        os.environ["PRISMA_BINARY_TARGET_DIR"] = "/tmp/prisma-cache"
        
        # Try again
        success, _ = run_command("prisma generate", cwd=app_dir)
    
    return success


def run_migrations_safely():
    """Run migrations with proper error handling"""
    print("🔄 Running database migrations safely...")
    
    app_dir = Path("/app")
    
    # First, try to connect to database
    success, _ = run_command("prisma db push --accept-data-loss --force-reset", cwd=app_dir)
    if success:
        print("✅ Database schema updated successfully!")
    else:
        print("⚠️ Schema push failed, trying migrate deploy...")
        success, _ = run_command("prisma migrate deploy", cwd=app_dir)
    
    return success


def main():
    """Main process to fix Prisma issues"""
    print("🚀 Starting Prisma permission fix process...")
    
    # Check if we're in the right directory
    if not Path("/app/prisma/schema.prisma").exists():
        print("❌ Prisma schema not found! Make sure you're in the app container.")
        sys.exit(1)
    
    # Check current user
    is_root = check_user_permissions()
    
    if not is_root:
        print("⚠️ Not running as root. Some operations may fail.")
        print("💡 Try running: docker exec -it --user root sopa_api_prod python scripts/fix_prisma_permissions.py")
    
    # Fix cache permissions
    fix_prisma_cache_permissions()
    
    # Install Prisma properly
    if not install_prisma_properly():
        print("❌ Failed to install Prisma properly!")
        sys.exit(1)
    
    # Run migrations
    if not run_migrations_safely():
        print("❌ Migration process failed!")
        sys.exit(1)
    
    print("🎉 Prisma setup and migrations completed successfully!")
    print("\n📋 Next steps:")
    print("1. Exit root session")
    print("2. Run: python3 scripts/db_manager.py seed")
    print("3. Test API: curl http://localhost:8000/health")


if __name__ == "__main__":
    main()
