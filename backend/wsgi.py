import os
import sys
from pathlib import Path
from dotenv import load_dotenv
env_path = '{}/.env'.format(Path(__file__).resolve().parent.parent)
load_dotenv(dotenv_path=env_path)
sys.path.append('/home/zhenyu/apps/backend')
os.environ.setdefault("PYTHON_EGG_CACHE", "/home/zhenyu/apps/backend/egg_cache")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.settings")
os.environ['HTTPS'] = "on"
os.environ['wsgi.url_scheme'] = 'https'
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
