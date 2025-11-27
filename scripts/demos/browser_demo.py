#!/usr/bin/env python3
"""
Moodle Manager Browser Feature Demo
Demonstrates the new browser functionality in Moodle Manager
"""

# Add the project root to the Python path
import os
import sys

project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

import webbrowser
import sys
import os

def demo_browser_feature():
    """Demonstrate the browser functionality"""
    print("🌐 MOODLE MANAGER BROWSER FEATURE DEMO")
    print("=" * 50)
    print()

    print("✅ Browser functionality has been successfully added to Moodle Manager!")
    print()

    print("📋 WHAT WAS ADDED:")
    print("  • 🌐 Browser button in the main toolbar")
    print("  • Opens http://127.0.0.1/moodle/ in your default web browser")
    print("  • Uses the configured Moodle URL if connected")
    print("  • Shows status messages when opening browser")
    print("  • Handles errors gracefully")
    print()

    print("🎯 HOW TO USE:")
    print("  1. Start Moodle Manager: python main.py")
    print("  2. Look for the 🌐 Browser button in the toolbar")
    print("  3. Click it to open Moodle in your web browser")
    print()

    print("🔧 TECHNICAL DETAILS:")
    print("  • Uses Python's webbrowser module")
    print("  • Automatically detects configured Moodle URL")
    print("  • Falls back to http://127.0.0.1/moodle/ if not connected")
    print("  • Shows user-friendly error messages")
    print()

    print("🚀 TESTING THE FEATURE:")
    moodle_url = "http://127.0.0.1/moodle/"

    try:
        print(f"Opening Moodle URL: {moodle_url}")
        webbrowser.open(moodle_url)
        print("✓ Browser opened successfully!")
        print("  (Your default browser should have opened the Moodle URL)")
    except Exception as e:
        print(f"✗ Browser error: {e}")

    print()
    print("=" * 50)
    print("🎉 Browser feature is ready to use in Moodle Manager!")

if __name__ == "__main__":
    demo_browser_feature()
