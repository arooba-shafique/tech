#!/usr/bin/env python
"""Build script for Vercel deployment - runs migrations and loads fixtures."""
import os
import sys
import django

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dps_ravi.settings')

# Setup Django
django.setup()

from django.core.management import call_command

def build():
    """Run migrations and load fixtures."""
    print("Starting build process...")
    
    # Run migrations
    print("Running migrations...")
    call_command('migrate', '--run-syncdb', verbosity=1)
    print("Migrations completed.")
    
    # Load fixtures
    print("Loading fixtures...")
    try:
        call_command('loaddata', 'initial_admin', verbosity=1)
        print("Fixtures loaded.")
    except Exception as e:
        print(f"Fixture loading skipped: {e}")
    
    print("Build process completed.")

if __name__ == '__main__':
    build()
