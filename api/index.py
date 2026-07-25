import os
import sys

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dps_ravi.settings')

# Import Django and initialize
import django
django.setup()

from django.core.wsgi import get_wsgi_application
from django.contrib.staticfiles.handlers import StaticFilesHandler

# Run migrations on cold start
def run_migrations():
    """Run migrations and load fixtures on cold start"""
    from django.core.management import call_command
    
    try:
        print("Running migrations...")
        call_command('migrate', '--run-syncdb', verbosity=0)
        print("Migrations completed.")
    except Exception as e:
        print(f"Migration error: {e}")

# Run migrations on import (cold start)
run_migrations()

# Get the WSGI application
application = StaticFilesHandler(get_wsgi_application())

# For Vercel serverless functions
if __name__ == "__main__":
    application()
