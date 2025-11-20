#!/usr/bin/env python
"""
Test Runner Script for Study Companion API
Provides easy commands to run different types of tests
"""

import os
import sys
import subprocess
from pathlib import Path

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"\n{'='*60}")
    print(f"Running: {description}")
    print(f"Command: {command}")
    print(f"{'='*60}")
    
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    
    if result.returncode == 0:
        print("✅ SUCCESS")
        if result.stdout:
            print(result.stdout)
    else:
        print("❌ FAILED")
        if result.stderr:
            print("Error:", result.stderr)
        if result.stdout:
            print("Output:", result.stdout)
    
    return result.returncode == 0

def main():
    """Main test runner function"""
    if len(sys.argv) < 2:
        print("""
Study Companion API Test Runner

Usage: python test_runner.py <command>

Available commands:
  all          - Run all tests
  models       - Run model tests only
  views        - Run view tests only
  serializers  - Run serializer tests only
  integration  - Run integration tests only
  coverage     - Run tests with coverage report
  fast         - Run tests without migrations
  verbose      - Run tests with verbose output
  help         - Show this help message

Examples:
  python test_runner.py all
  python test_runner.py models
  python test_runner.py coverage
        """)
        return

    command = sys.argv[1].lower()
    
    # Base Django test command
    base_cmd = "python manage.py test"
    
    if command == "help":
        main()
        return
    
    elif command == "all":
        success = run_command(
            f"{base_cmd} base --verbosity=2",
            "All Tests"
        )
    
    elif command == "models":
        success = run_command(
            f"{base_cmd} base.test_models --verbosity=2",
            "Model Tests"
        )
    
    elif command == "views":
        success = run_command(
            f"{base_cmd} base.test_views --verbosity=2",
            "View Tests"
        )
    
    elif command == "serializers":
        success = run_command(
            f"{base_cmd} base.test_serializers --verbosity=2",
            "Serializer Tests"
        )
    
    elif command == "integration":
        success = run_command(
            f"{base_cmd} base.test_integration --verbosity=2",
            "Integration Tests"
        )
    
    elif command == "coverage":
        # Install coverage if not available
        subprocess.run("pip install coverage", shell=True, capture_output=True)
        
        commands = [
            ("coverage erase", "Clear previous coverage data"),
            ("coverage run --source='.' manage.py test base", "Run tests with coverage"),
            ("coverage report", "Generate coverage report"),
            ("coverage html", "Generate HTML coverage report")
        ]
        
        success = True
        for cmd, desc in commands:
            if not run_command(cmd, desc):
                success = False
                break
        
        if success:
            print("\n📊 Coverage report generated!")
            print("📁 HTML report available in: htmlcov/index.html")
    
    elif command == "fast":
        success = run_command(
            f"{base_cmd} base --keepdb --verbosity=2",
            "Fast Tests (Keep Database)"
        )
    
    elif command == "verbose":
        success = run_command(
            f"{base_cmd} base --verbosity=3 --debug-mode",
            "Verbose Tests"
        )
    
    else:
        print(f"❌ Unknown command: {command}")
        print("Run 'python test_runner.py help' for available commands")
        return
    
    # Final status
    if success:
        print(f"\n🎉 {command.upper()} TESTS COMPLETED SUCCESSFULLY!")
    else:
        print(f"\n💥 {command.upper()} TESTS FAILED!")
        sys.exit(1)

if __name__ == "__main__":
    main()