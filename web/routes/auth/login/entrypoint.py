from config import INTECAT_CLIENT_SESSIONS
from flask import Blueprint
from flask import flash
from flask import redirect
from flask import render_template
from flask import request
from flask import session
from nactite.intranet.client import Client as IntranetClient
from nactite.sat.client import Client as SatClient

blueprint = Blueprint('auth-login', __name__, template_folder='templates',
                      static_folder='static', static_url_path='/static/auth/login')


def get_login():
    if request.method != 'GET':
        return redirect('/auth/login')

    if 'user' in session.keys() and session['user']:
        return redirect('/')

    return render_template('auth-login/login.html', static_url_path=blueprint.static_url_path)


def post_login():
    if request.method != 'POST':
        return redirect('/auth/login')

    session.pop('user', None)

    intranet_client = IntranetClient()
    sat_client = SatClient()

    try:
        if not intranet_client.login(username=request.form['username'], password=request.form['password']):
            flash('Username or password incorrect')
            return redirect('/auth/login')

        if not sat_client.login(username=request.form['username'], password=request.form['password']):
            flash('Username or password incorrect')
            return redirect('/auth/login')
    except Exception as e:
        flash(str(e))
        return redirect('/auth/login')

    session['user'] = request.form['username']

    INTECAT_CLIENT_SESSIONS[request.form['username']] = {
        'intranet': intranet_client, 'sat': sat_client}

    return redirect('/')


blueprint.add_url_rule('/auth/login', view_func=get_login, methods=['GET'])
blueprint.add_url_rule('/auth/login', view_func=post_login, methods=['POST'])


def register_plugin(app):
    app.register_blueprint(blueprint)
