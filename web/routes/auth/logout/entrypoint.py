from flask import Blueprint
from flask import redirect
from flask import request
from flask import session
from nactite.intranet.client import Client as Client
from utils.routes import login_required

from config import INTECAT_CLIENT_SESSIONS


blueprint = Blueprint('auth-logout', __name__, template_folder='templates',
                      static_folder='static', static_url_path='/static/auth/logout')


@login_required
def post_logout():
    if request.method != 'POST':
        return redirect('auth/login')

    INTECAT_CLIENT_SESSIONS[session['user']] = None

    session.pop('user', None)

    return redirect('/')


blueprint.add_url_rule('/auth/logout', view_func=post_logout, methods=['POST'])


def register_plugin(app):
    app.register_blueprint(blueprint)
