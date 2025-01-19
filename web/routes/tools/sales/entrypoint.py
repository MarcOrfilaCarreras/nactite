import datetime

from config import INTECAT_CLIENT_SESSIONS
from flask import Blueprint
from flask import flash
from flask import redirect
from flask import render_template
from flask import request
from flask import session
from utils.dates import get_months_in_year
from utils.routes import login_required

blueprint = Blueprint('tools-sales', __name__, template_folder='templates',
                      static_folder='static', static_url_path='/static/tools/sales')


@login_required
def get_sales():
    client = INTECAT_CLIENT_SESSIONS[session['user']]['intranet']

    year = request.args.get(
        'year', default=datetime.datetime.today().year, type=int)
    store = request.args.get(
        'store', default=client.area, type=str)

    first_date = datetime.datetime(year, 1, 1)
    last_date = datetime.datetime.today() if year == datetime.datetime.now(
    ).year else datetime.datetime(year, 12, 31)

    data = {'sales': {}, 'vendors': {}, 'areas': {}}

    while first_date <= last_date:
        try:
            sales = client.get_areas(date_from=first_date.strftime(
                '%Y-%m-%d'), date_to=first_date.strftime('%Y-%m-%d'), all=True)[store]
        except Exception as e:
            flash(str(e))
            return redirect('/')

        if (sales is None):
            flash('There was a problem getting the data ...')
            return redirect('/')

        data['sales'][first_date.strftime('%Y-%m-%d')] = sales

        first_date += datetime.timedelta(days=1)

    if len(months := get_months_in_year(year)) > 0:
        for month in months:
            try:
                vendors = client.get_vendors(
                    date_from=month['first_day'], date_to=month['last_day'], all=True)

                if (vendors is None):
                    flash('There was a problem getting the data ...')
                    return redirect('/')

                data['vendors'][month['name']] = vendors

                areas = client.get_areas(
                    date_from=month['first_day'], date_to=month['last_day'], all=True)

                if (areas is None):
                    flash('There was a problem getting the data ...')
                    return redirect('/')

                data['areas'][month['name']] = areas
            except Exception as e:
                flash(str(e))
                return redirect('/')

    data['defaults'] = {'store': store, 'year': year}

    return render_template('tools-sales/sales.html', data=data, static_url_path=blueprint.static_url_path)


blueprint.add_url_rule('/tools/sales', view_func=get_sales, methods=['GET'])


def register_plugin(app):
    app.register_blueprint(blueprint)
