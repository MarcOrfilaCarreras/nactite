import datetime
import importlib
import os
import subprocess
from functools import wraps

from bs4 import BeautifulSoup
from config import INTECAT_CLIENT_SESSIONS
from flask import g
from flask import redirect
from flask import request
from flask import session


def register_blueprints(app, path):
    if app is None:
        return False

    if path is None:
        return False

    for root, dirs, files in os.walk(path):
        for file in files:
            if file == 'entrypoint.py':
                module_name = f"{root.replace(os.sep, '.')}.{file[:-3]}"
                module_blueprint = importlib.import_module(module_name)

                if hasattr(module_blueprint, 'register_plugin'):
                    module_blueprint.register_plugin(app)

    return True


inject_global_variables_cache = None


def inject_global_variables(app):
    @app.context_processor
    def inject():
        global inject_global_variables_cache

        if inject_global_variables_cache is not None:
            return inject_global_variables_cache

        user = None

        if ('user' in session and session['user']) and (session['user'] in INTECAT_CLIENT_SESSIONS.keys()):
            user = INTECAT_CLIENT_SESSIONS[session['user']]

        if user is None:
            return {}

        inject_global_variables_cache = {
            'defaults': {
                'dropdowns': {
                    'years': [{'id': year + 1, 'label': f'{year + 1}'} for year in range(2006, datetime.datetime.now().year)],
                    'vendors': [{'id': f'{key}', 'label': f'{vendor["nombre"]}'} for key, vendor in user['intranet'].get_vendors(all=True).items()] if user is not None else [],
                    'stores': [{'id': f'{key}', 'label': f'{store["nombre"]}'} for key, store in user['intranet'].get_areas(all=True).items()] if user is not None else [],
                    'products': [{'id': 'apple-care', 'label': 'AppleCare +'}, {'id': 'rockglass', 'label': 'Rockglass'}]
                }
            }
        }

        return inject_global_variables_cache


def logging(app):
    @app.before_request
    def before_request():
        if not (request.path.startswith('/static/') or request.path.startswith('/favicon')):
            g.start_time = datetime.datetime.now()

            log_data = {
                'timestamp': datetime.datetime.now(),
                'ip': request.headers.getlist('X-Forwarded-For')[0] if request.headers.getlist('X-Forwarded-For') else request.remote_addr,
                'path': request.path,
                'method': request.method,
                'headers': dict(request.headers)
            }

            g.log_data = log_data

    @app.after_request
    def after_request(response):
        if 'log_data' in g:
            execution_time = (datetime.datetime.now() -
                              g.start_time).total_seconds()

            g.log_data['status_code'] = response.status_code
            g.log_data['execution_time'] = execution_time

            with open('requests.log', 'a') as f:
                f.write(
                    f"{g.log_data['timestamp']}, {g.log_data['ip']}, {g.log_data['path']}, {g.log_data['method']}, {g.log_data['status_code']}, {g.log_data['execution_time']} seconds, {session['user'] if 'user' in session else 'null'}\n")

        return response


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not ('user' in session and session['user']):
            return redirect('/auth/login')

        if not (session['user'] in INTECAT_CLIENT_SESSIONS.keys()):
            session.pop('user', None)
            return redirect('/auth/login')

        user = INTECAT_CLIENT_SESSIONS[session['user']]

        if user is None:
            INTECAT_CLIENT_SESSIONS[session['user']] = None

            session.pop('user', None)
            return redirect('/auth/login')

        if user['intranet'] is None or user['sat'] is None:
            INTECAT_CLIENT_SESSIONS[session['user']] = None

            session.pop('user', None)
            return redirect('/auth/login')

        if not user['intranet']._is_logged_in():
            INTECAT_CLIENT_SESSIONS[session['user']] = None

            session.pop('user', None)
            return redirect('/auth/login')

        if not user['sat']._is_logged_in():
            INTECAT_CLIENT_SESSIONS[session['user']] = None

            session.pop('user', None)
            return redirect('/auth/login')

        return f(*args, **kwargs)
    return decorated_function
