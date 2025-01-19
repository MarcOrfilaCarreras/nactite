from datetime import datetime

from flask import Blueprint
from flask import flash
from flask import redirect
from flask import render_template
from flask import request
from flask import session
from utils.routes import login_required

from config import INTECAT_CLIENT_SESSIONS

blueprint = Blueprint('leaderboards-stores', __name__, template_folder='templates',
                      static_folder='static', static_url_path='/static/leaderboards/stores')


@login_required
def get_stores():
    start_date = request.args.get(
        'start_date', default=datetime.now().strftime('%Y-%m-%d'), type=str)
    end_date = request.args.get(
        'end_date', default=datetime.now().strftime('%Y-%m-%d'), type=str)

    client = INTECAT_CLIENT_SESSIONS[session['user']]['intranet']

    data = {}

    try:
        stores = client.get_areas(
            date_from=start_date, date_to=end_date, all=True)
        data['vendors'] = client.get_vendors(all=True)
    except Exception as e:
        flash(str(e))
        return redirect('/')

    if (stores is None) or (data['vendors'] is None):
        flash('There was a problem getting the data ...')
        return redirect('/')

    data['stores'] = dict(
        sorted(stores.items(), key=lambda item: item[1]['ventas'], reverse=True))

    return render_template('leaderboards-stores/stores.html', data=data, static_url_path=blueprint.static_url_path)


blueprint.add_url_rule('/leaderboards/stores',
                       view_func=get_stores, methods=['GET'])


def register_plugin(app):
    app.register_blueprint(blueprint)
