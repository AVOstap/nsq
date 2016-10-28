import django
import os
import sys

path = os.path.normpath(os.path.join(os.path.dirname(__file__), '../../'))
sys.path.insert(0, path)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "tick.settings")
django.setup()
