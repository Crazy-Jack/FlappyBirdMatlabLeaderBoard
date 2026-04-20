import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'flappy.settings')

_application = get_wsgi_application()

SCRIPT_NAME = '/flappybird'

def application(environ, start_response):
    environ['SCRIPT_NAME'] = SCRIPT_NAME
    path_info = environ.get('PATH_INFO', '')
    if path_info.startswith(SCRIPT_NAME):
        environ['PATH_INFO'] = path_info[len(SCRIPT_NAME):]
    return _application(environ, start_response)
