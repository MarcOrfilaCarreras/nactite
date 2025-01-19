from datetime import datetime

from config import INTECAT_CLIENT_SESSIONS
from flask import Blueprint
from flask import flash
from flask import redirect
from flask import render_template
from flask import request
from flask import session
from nactite.reviews.client import Client
from utils.routes import login_required

blueprint = Blueprint('tools-reviews', __name__, template_folder='templates',
                      static_folder='static', static_url_path='/static/tools/reviews')


@login_required
def get_reviews():
    intranet_client = INTECAT_CLIENT_SESSIONS[session['user']]['intranet']
    reviews_client = Client()

    area_arg = request.args.get(
        'store', default=intranet_client.area, type=str)

    data = {}

    try:
        store_name = intranet_client.get_areas(all=True)[area_arg]['nombre']

        store = reviews_client.get_store(store_name)[0]
        reviews = reviews_client.get_reviews(
            store.get('business_id'), limit=20)

        if reviews is None or len(reviews) == 0:
            reviews = []

        data['reviews'] = reviews
        data['defaults'] = {'store': area_arg}
    except Exception as e:
        flash(str(e))
        return redirect('/')

    return render_template('tools-reviews/reviews.html', data=data, static_url_path=blueprint.static_url_path)


blueprint.add_url_rule(
    '/tools/reviews', view_func=get_reviews, methods=['GET'])


def register_plugin(app):
    app.register_blueprint(blueprint)
