from datetime import datetime

from flask import Blueprint
from flask import flash
from flask import redirect
from flask import render_template
from flask import request
from flask import session
from utils.routes import login_required

from config import INTECAT_CLIENT_SESSIONS

blueprint = Blueprint('leaderboards-sat', __name__, template_folder='templates',
                      static_folder='static', static_url_path='/static/leaderboards/sat')


@login_required
def get_sats():
    start_date = request.args.get(
        'start_date', default=datetime.now().strftime('%Y-%m-%d'), type=str)
    end_date = request.args.get(
        'end_date', default=datetime.now().strftime('%Y-%m-%d'), type=str)

    client = INTECAT_CLIENT_SESSIONS[session['user']]['sat']

    data = {}

    try:
        service_locations = client.get_service_locations()

        for service in service_locations:
            if 'SAT-' not in service['key']:
                continue

            repairs = client.get_repairs(
                service_location=service['key'], date_from=start_date, date_to=end_date)
            total_cost = sum(float(repair['cost']) for repair in repairs)

            data[service['key']] = {
                'name': service['name'],
                'repairs': len(repairs),
                'total': round(total_cost, 2)
            }

    except Exception as e:
        flash(str(e))
        return redirect('/')

    sorted_data = sorted(data.values(), key=lambda x: x['total'], reverse=True)

    return render_template('leaderboards-sat/sat.html', data=sorted_data, static_url_path=blueprint.static_url_path)


blueprint.add_url_rule('/leaderboards/sat',
                       view_func=get_sats, methods=['GET'])


def register_plugin(app):
    app.register_blueprint(blueprint)
