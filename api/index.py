import os
import sys

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dps_ravi.settings')

# Import Django and initialize
from django.core.wsgi import get_wsgi_application
from django.contrib.staticfiles.handlers import StaticFilesHandler

# Get the WSGI application
application = StaticFilesHandler(get_wsgi_application())

# For Vercel serverless functions
if __name__ == "__main__":
    application()
