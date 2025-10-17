#!/usr/bin/env python3
"""
Verification script to check AIM installation and configuration.
"""

import sys
import os
from pathlib import Path


def check_python_version():
    """Check Python version."""
    print("Checking Python version...")
    version = sys.version_info
    if version.major >= 3 and version.minor >= 10:
        print(f"✓ Python {version.major}.{version.minor}.{version.micro}")
        return True
    else:
        print(f"✗ Python {version.major}.{version.minor}.{version.micro} (requires 3.10+)")
        return False


def check_dependencies():
    """Check if required dependencies are installed."""
    print("\nChecking dependencies...")
    required = ["mcp", "anthropic", "pydantic", "yaml"]
    all_ok = True
    
    for package in required:
        try:
            if package == "yaml":
                __import__("yaml")
            else:
                __import__(package)
            print(f"✓ {package}")
        except ImportError:
            print(f"✗ {package} (not installed)")
            all_ok = False
    
    return all_ok


def check_api_key():
    """Check if API key is set."""
    print("\nChecking API key...")
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if api_key:
        print(f"✓ ANTHROPIC_API_KEY is set ({api_key[:10]}...)")
        return True
    else:
        print("✗ ANTHROPIC_API_KEY not set")
        print("  Set it with: export ANTHROPIC_API_KEY='your-key'")
        return False


def check_aim_installation():
    """Check if AIM is properly installed."""
    print("\nChecking AIM installation...")
    try:
        import aim_mcp_server
        print(f"✓ AIM MCP Server {aim_mcp_server.__version__}")
        return True
    except ImportError as e:
        print(f"✗ AIM not installed: {e}")
        print("  Install with: pip install -e .")
        return False


def check_storage_directories():
    """Check if storage directories exist."""
    print("\nChecking storage directories...")
    aim_dir = Path.home() / ".aim"
    tasks_dir = aim_dir / "tasks"
    logs_dir = aim_dir / "logs"
    
    for dir_path, name in [(tasks_dir, "tasks"), (logs_dir, "logs")]:
        if dir_path.exists():
            print(f"✓ {name} directory exists: {dir_path}")
        else:
            print(f"ℹ {name} directory will be created on first run: {dir_path}")
    
    return True


def test_import():
    """Test importing key modules."""
    print("\nTesting imports...")
    try:
        from aim_mcp_server import create_server
        print("✓ Can import create_server")
        
        from aim_mcp_server.task_manager import TaskManager
        print("✓ Can import TaskManager")
        
        from aim_mcp_server.agents.registry import AgentRegistry
        print("✓ Can import AgentRegistry")
        
        return True
    except Exception as e:
        print(f"✗ Import error: {e}")
        return False


def main():
    """Run all checks."""
    print("=" * 60)
    print("AIM MCP Server - Installation Verification")
    print("=" * 60)
    
    checks = [
        ("Python version", check_python_version),
        ("Dependencies", check_dependencies),
        ("API key", check_api_key),
        ("AIM installation", check_aim_installation),
        ("Storage directories", check_storage_directories),
        ("Module imports", test_import),
    ]
    
    results = []
    for name, check_func in checks:
        try:
            result = check_func()
            results.append((name, result))
        except Exception as e:
            print(f"✗ Error during {name} check: {e}")
            results.append((name, False))
    
    print("\n" + "=" * 60)
    print("Summary")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status:8} {name}")
    
    print(f"\nPassed: {passed}/{total}")
    
    if passed == total:
        print("\n🎉 All checks passed! AIM is ready to use.")
        print("\nNext steps:")
        print("1. Configure Claude Desktop (see QUICKSTART.md)")
        print("2. Restart Claude Desktop")
        print("3. Try: python -m aim_mcp_server (to test server)")
        return 0
    else:
        print("\n⚠️  Some checks failed. Please fix the issues above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())

