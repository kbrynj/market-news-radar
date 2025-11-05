#!/usr/bin/env python3
"""
Validation script to check Market News Radar configuration.
Run this before deployment to ensure everything is properly set up.
"""
import os
import sys
from pathlib import Path

def check_file_exists(filepath, required=True):
    """Check if a file exists."""
    exists = Path(filepath).exists()
    status = "✅" if exists else ("❌" if required else "⚠️")
    req_text = "REQUIRED" if required else "OPTIONAL"
    print(f"{status} {filepath} - {req_text}")
    return exists

def check_directory_exists(dirpath, required=True):
    """Check if a directory exists."""
    exists = Path(dirpath).is_dir()
    status = "✅" if exists else ("❌" if required else "⚠️")
    req_text = "REQUIRED" if required else "OPTIONAL"
    print(f"{status} {dirpath}/ - {req_text}")
    return exists

def check_env_var(varname, required=False):
    """Check if an environment variable is set."""
    value = os.environ.get(varname)
    is_set = value is not None and value != ""
    status = "✅" if is_set else ("⚠️" if not required else "❌")
    req_text = "REQUIRED" if required else "OPTIONAL"
    
    if is_set:
        # Mask the value for security
        masked = value[:3] + "*" * (len(value) - 3) if len(value) > 3 else "***"
        print(f"{status} {varname}={masked} - {req_text}")
    else:
        print(f"{status} {varname} (not set) - {req_text}")
    
    return is_set

def main():
    print("=" * 80)
    print("Market News Radar - Configuration Validation")
    print("=" * 80)
    
    all_good = True
    
    # Check required files
    print("\n📄 Required Files:")
    all_good &= check_file_exists("requirements.txt", required=True)
    all_good &= check_file_exists("backend/app.py", required=True)
    all_good &= check_file_exists("backend/db.py", required=True)
    all_good &= check_file_exists("backend/scraper.py", required=True)
    all_good &= check_file_exists("frontend/index.html", required=True)
    all_good &= check_file_exists("frontend/app.js", required=True)
    all_good &= check_file_exists("frontend/styles.css", required=True)
    all_good &= check_file_exists("Dockerfile", required=True)
    all_good &= check_file_exists("docker-compose.yml", required=True)
    
    # Check optional/documentation files
    print("\n📝 Documentation Files:")
    check_file_exists("README.md", required=False)
    check_file_exists(".env.example", required=False)
    check_file_exists(".gitignore", required=False)
    check_file_exists("run_dev.py", required=False)
    check_file_exists("test_company_matching.py", required=False)
    
    # Check directories
    print("\n📁 Directories:")
    check_directory_exists("backend", required=True)
    check_directory_exists("frontend", required=True)
    check_directory_exists("data", required=False)
    
    # Check environment variables
    print("\n🔧 Environment Variables:")
    check_env_var("ADMIN_TOKEN", required=False)
    check_env_var("DB_PATH", required=False)
    
    # Check Python dependencies (if running with venv)
    print("\n🐍 Python Environment:")
    try:
        import fastapi
        import uvicorn
        import aiohttp
        import feedparser
        import aiosqlite
        import vaderSentiment
        print("✅ All Python dependencies installed")
    except ImportError as e:
        print(f"❌ Missing Python dependency: {e.name}")
        all_good = False
    
    # Final result
    print("\n" + "=" * 80)
    if all_good:
        print("✅ ALL CHECKS PASSED - Ready to deploy!")
        print("=" * 80)
        return 0
    else:
        print("❌ SOME CHECKS FAILED - Please fix the issues above")
        print("=" * 80)
        return 1

if __name__ == "__main__":
    sys.exit(main())
