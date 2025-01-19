from datetime import datetime

from flask import Blueprint
from flask import flash
from flask import redirect
from flask import render_template
from flask import request
from flask import session
from utils.routes import login_required

from config import INTECAT_CLIENT_SESSIONS

blueprint = Blueprint('leaderboards-vendors', __name__, template_folder='templates',
                      static_folder='static', static_url_path='/static/leaderboards/vendors')


@login_required
def get_vendors():
    start_date = request.args.get(
        'start_date', default=datetime.now().strftime('%Y-%m-%d'), type=str)
    end_date = request.args.get(
        'end_date', default=datetime.now().strftime('%Y-%m-%d'), type=str)

    client = INTECAT_CLIENT_SESSIONS[session['user']]['intranet']

    data = {}

    try:
        vendors = client.get_vendors(
            date_from=start_date, date_to=end_date, all=True)
        data['stores'] = client.get_areas(all=True)
    except Exception as e:
        flash(str(e))
        return redirect('/')

    if (vendors is None) or (data['stores'] is None):
        flash('There was a problem getting the data ...')
        return redirect('/')

    data['vendors'] = dict(
        sorted(vendors.items(), key=lambda item: item[1]['ventas'], reverse=True))

    return render_template('leaderboards-vendors/vendors.html', data=data, static_url_path=blueprint.static_url_path)


blueprint.add_url_rule('/leaderboards/vendors',
                       view_func=get_vendors, methods=['GET'])


def register_plugin(app):
    app.register_blueprint(blueprint)
