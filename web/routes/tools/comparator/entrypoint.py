import datetime

from config import INTECAT_CLIENT_SESSIONS
from flask import Blueprint
from flask import flash
from flask import redirect
from flask import render_template
from flask import request
from flask import session
from utils.routes import login_required

blueprint = Blueprint('tools-comparator', __name__, template_folder='templates',
                      static_folder='static', static_url_path='/static/tools/comparator')


@login_required
def get_comparator():
    start_date = request.args.get(
        'start_date', default=datetime.datetime.now().strftime('%Y-%m-%d'), type=str)
    end_date = request.args.get(
        'end_date', default=datetime.datetime.now().strftime('%Y-%m-%d'), type=str)
    option = request.args.get(
        'option', default='apple-care', type=str)

    custom_params = {}

    if option is not None and option == 'apple-care':
        custom_params = {'custom[tipo]': 'catalogo', 'custom[dpto]': '4', 'custom[seccion]': '6',
                         'custom[familia]': '', '&custom[subfamilia]': '', 'custom[marca]': '', 'custom[articulos]': ''}

    if option is not None and option == 'rockglass':
        custom_params = {'custom[tipo]': 'catalogo', 'custom[dpto]': '3', 'custom[seccion]': '43',
                         'custom[familia]': '', '&custom[subfamilia]': '', 'custom[marca]': '787', 'custom[articulos]': ''}

    client = INTECAT_CLIENT_SESSIONS[session['user']]['intranet']

    data = {}

    try:
        data['vendors'] = client.get_vendors(
            date_from=start_date, date_to=end_date, all=True, custom_params=custom_params)
        data['stores'] = client.get_areas(
            date_from=start_date, date_to=end_date, all=True, custom_params=custom_params)

        data['defaults'] = {'vendor': client.id, 'store': client.area}
    except Exception as e:
        flash(str(e))
        return redirect('/')

    return render_template('tools-comparator/comparator.html', data=data, static_url_path=blueprint.static_url_path)


blueprint.add_url_rule('/tools/comparator',
                       view_func=get_comparator, methods=['GET'])


def register_plugin(app):
    app.register_blueprint(blueprint)
