#!/usr/bin/env python3
"""
Setup verification script for MCP Toolbox.

Checks that all dependencies are installed and components can be imported.
Run this after installation to verify everything is set up correctly.

Usage:
    python verify_setup.py
"""

import sys
import importlib.util


def check_python_version():
    """Verify Python version is 3.10 or higher."""
    print("Checking Python version...")
    version = sys.version_info
    if version >= (3, 10):
        print(f"  ✓ Python {version.major}.{version.minor}.{version.micro}")
        return True
    else:
        print(f"  ✗ Python {version.major}.{version.minor}.{version.micro} (need 3.10+)")
        return False


def check_package(package_name, import_name=None):
    """Check if a package is installed."""
    if import_name is None:
        import_name = package_name

    spec = importlib.util.find_spec(import_name)
    if spec is not None:
        print(f"  ✓ {package_name}")
        return True
    else:
        print(f"  ✗ {package_name} - Install with: pip install {package_name}")
        return False


def check_optional_package(package_name, import_name=None):
    """Check optional package."""
    if import_name is None:
        import_name = package_name

    spec = importlib.util.find_spec(import_name)
    if spec is not None:
        print(f"  ✓ {package_name} (optional)")
        return True
    else:
        print(f"  ○ {package_name} (optional) - Not installed")
        return False


def check_modules():
    """Check if project modules can be imported."""
    print("\nChecking project modules...")

    # Add server directory to path
    sys.path.insert(0, 'server')

    modules = [
        ('tools.format_tools', 'Format tools'),
        ('tools.text_tools', 'Text tools'),
        ('tools.network_tools', 'Network tools'),
        ('registry', 'Tool registry'),
    ]

    all_ok = True
    for module_name, description in modules:
        try:
            importlib.import_module(module_name)
            print(f"  ✓ {description} ({module_name})")
        except Exception as e:
            print(f"  ✗ {description} ({module_name}) - Error: {e}")
            all_ok = False

    return all_ok


def check_ollama():
    """Check if Ollama is available."""
    print("\nChecking Ollama (optional)...")
    try:
        import ollama
        ollama.list()
        print("  ✓ Ollama is installed and running")
        return True
    except ImportError:
        print("  ○ Ollama package not installed")
        print("    Install with: pip install ollama")
        return False
    except Exception as e:
        print("  ○ Ollama not running")
        print("    Start with: ollama serve")
        return False


def main():
    """Run all checks."""
    print("=" * 60)
    print(" MCP Toolbox - Setup Verification")
    print("=" * 60 + "\n")

    checks = []

    # Python version
    checks.append(("Python version", check_python_version()))

    # Required packages
    print("\nChecking required packages...")
    required_packages = [
        ('mcp', 'mcp'),
        ('pydantic', 'pydantic'),
        ('pyyaml', 'yaml'),
        ('fastapi', 'fastapi'),
        ('uvicorn', 'uvicorn'),
        ('ollama', 'ollama'),
        ('pytest', 'pytest'),
        ('python-dotenv', 'dotenv'),
    ]

    for package, import_name in required_packages:
        checks.append((package, check_package(package, import_name)))

    # Optional packages
    print("\nChecking optional packages...")
    check_optional_package('aiohttp')
    check_optional_package('black')
    check_optional_package('ruff')

    # Project modules
    checks.append(("Project modules", check_modules()))

    # Ollama
    check_ollama()

    # Summary
    print("\n" + "=" * 60)
    print(" Summary")
    print("=" * 60)

    required_checks = [check for check in checks if check[0] != "Ollama"]
    passed = sum(1 for _, result in required_checks if result)
    total = len(required_checks)

    print(f"\nRequired components: {passed}/{total} passed")

    if passed == total:
        print("\n✓ All required components are installed!")
        print("\nYou can now:")
        print("  1. Test with Inspector: npx @modelcontextprotocol/inspector python server/stdio_server.py")
        print("  2. Run example client: python client/example_usage.py")
        print("  3. Run tests: pytest tests/")
        print("  4. Start Ollama host: python host/run_ollama.py")
        return 0
    else:
        print("\n✗ Some required components are missing.")
        print("\nInstall missing packages with:")
        print("  pip install -r requirements.txt")
        return 1


if __name__ == "__main__":
    sys.exit(main())