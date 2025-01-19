from datetime import datetime
from datetime import timedelta

from config import INTECAT_CLIENT_SESSIONS
from flask import Blueprint
from flask import flash
from flask import redirect
from flask import render_template
from flask import request
from flask import session
from utils.routes import login_required

blueprint = Blueprint('commissions', __name__, template_folder='templates',
                      static_folder='static', static_url_path='/static/commissions')


def calculate_commissions_2024(start_date, end_date, client):
    hours_params = {'custom[tipo]': 'articulo', 'custom[dpto]': '4', 'custom[seccion]': '', 'custom[familia]': '',
                    '&custom[subfamilia]': '', 'custom[marca]': '', 'custom[articulos]': '9654,9537,9441'}

    area_sales = client.get_areas(
        date_from=start_date, date_to=end_date, all=False)
    area_sales_with_hours = client.get_areas(
        date_from=start_date, date_to=end_date, all=False, custom_params=hours_params)

    vendor_sales = client.get_vendors(
        date_from=start_date, date_to=end_date, all=False)
    vendor_sales_with_hours = client.get_vendors(
        date_from=start_date, date_to=end_date, all=False, custom_params=hours_params)

    num_devices_sold = area_sales['iphone'] + area_sales['cpu'] + \
        area_sales['ipad'] + area_sales['watch'] + area_sales['airpods']
    area_growth = (((area_sales['ventas'] - area_sales['prev_ventas']) / area_sales['prev_ventas']) * 100) if (
        ((area_sales['ventas'] - area_sales['prev_ventas']) / area_sales['prev_ventas']) * 100) > 0 else 0

    insurances_ratio = ((area_sales['seguros_garante']) /
                        num_devices_sold) * 100 if num_devices_sold != 0 else 0
    insurances_iphone_ratio = ((area_sales['seguros_garante']) /
                               area_sales['iphone']) * 100 if area_sales['iphone'] != 0 else 0
    insurances_vendor_commissions = vendor_sales['seguros_garante'] * 7.5 if insurances_ratio >= 40 else vendor_sales['seguros_garante'] * \
        5 if insurances_ratio >= 30 else vendor_sales['seguros_garante'] * \
        2.5 if insurances_ratio >= 20 else 0

    financing_ratio = (area_sales['financiacion'] / area_sales['num_tickets']
                       ) * 100 if area_sales['num_tickets'] != 0 else 0
    financing_vendor_commissions = vendor_sales['financiacion'] * \
        5 if financing_ratio >= 10 else 0

    hours_ratio = (area_sales_with_hours['personalizado'] / area_sales_with_hours['iphone']
                   ) * 100 if area_sales_with_hours['iphone'] != 0 else 0
    hours_vendor_commissions = (vendor_sales_with_hours['ventas_personalizado'] / 1.21) * 0.15 if hours_ratio >= 25 else (
        vendor_sales_with_hours['ventas_personalizado'] / 1.21) * 0.10 if hours_ratio >= 20 else (vendor_sales_with_hours['ventas_personalizado'] / 1.21) * 0.05 if hours_ratio >= 15 else 0

    third_party_accesories_ratio = (
        area_sales['ventas_accesorios_3pp'] / area_sales['ventas']) * 100 if area_sales['ventas'] != 0 else 0
    third_party_accesories_vendor_commissions = vendor_sales['ventas_accesorios_3pp'] / \
        1.21 if third_party_accesories_ratio >= 10 else 0

    def get_rate(product):
        if area_growth > 10:
            return {'cpu': 15, 'ipad': 7.5, 'watch': 7.5, 'airpods': 2}.get(product, 0)
        elif area_growth > 5:
            return {'cpu': 10, 'ipad': 5, 'watch': 5, 'airpods': 1}.get(product, 0)
        return 0

    adjustment_factor = 1 if insurances_iphone_ratio >= 40 else 0.5 if insurances_iphone_ratio <= 40 else 0.5

    result = {
        'Insurances': {
            'ratio': round(insurances_ratio, 2),
            'total': round(insurances_vendor_commissions, 2)
        },
        'Financing': {
            'ratio': round(financing_ratio, 2),
            'total': round(financing_vendor_commissions, 2)
        },
        'Hours': {
            'ratio': round(hours_ratio, 2),
            'total': round(hours_vendor_commissions, 2)
        },
        'Third Party Accesories': {
            'ratio': round(third_party_accesories_ratio, 2),
            'total': round(third_party_accesories_vendor_commissions, 2)
        },
        'Mac': {
            'ratio': '',
            'total': round((vendor_sales['cpu'] * get_rate('cpu')) * adjustment_factor, 2)
        },
        'iPad': {
            'ratio': '',
            'total': round((vendor_sales['ipad'] * get_rate('ipad')) * adjustment_factor, 2)
        },
        'Watch': {
            'ratio': '',
            'total': round((vendor_sales['watch'] * get_rate('watch')) * adjustment_factor, 2)
        },
        'AirPods': {
            'ratio': '',
            'total': round((vendor_sales['airpods'] * get_rate('airpods')) * adjustment_factor, 2)
        },
        '‎': {
            'ratio': '',
            'total': ''
        }
    }

    result['Total'] = {
        'ratio': '',
        'total': sum(item['total'] for item in result.values() if isinstance(item['total'], (int, float)))
    }

    return result


@login_required
def get_commissions():
    start_date = request.args.get('start_date', default=datetime.today().replace(
        day=1).strftime('%Y-%m-%d'), type=str)
    end_date = request.args.get(
        'end_date', default=(datetime.now().replace(day=28) + timedelta(days=4) - timedelta(days=(datetime.now().replace(day=28) + timedelta(days=4)).day)).strftime('%Y-%m-%d'), type=str)

    client = INTECAT_CLIENT_SESSIONS[session['user']]['intranet']

    data = {}

    try:
        data['commissions'] = calculate_commissions_2024(
            start_date, end_date, client)
    except Exception as e:
        flash(str(e))
        return redirect('/')

    return render_template('commissions/commissions.html', data=data, static_url_path=blueprint.static_url_path)


blueprint.add_url_rule(
    '/commissions', view_func=get_commissions, methods=['GET'])


def register_plugin(app):
    app.register_blueprint(blueprint)
