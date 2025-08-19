#!/usr/bin/env python3
"""
Quick test runner for integration test
"""
import subprocess
import sys

try:
    result = subprocess.run([sys.executable, 'test_integration.py'], 
                          capture_output=True, text=True, cwd='d:/freelancer')
    print(result.stdout)
    if result.stderr:
        print("STDERR:", result.stderr)
    sys.exit(result.returncode)
except Exception as e:
    print(f"Error running test: {e}")
    sys.exit(1)
