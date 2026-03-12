"""
This module initializes Django environment
to allow using Django ORM inside standalone scripts.
"""
import os
import sys
import django

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'braincomua_playwright_project')))

os.environ['DJANGO_SETTINGS_MODULE'] = 'braincomua_playwright_project.settings'

django.setup()