from flask import Blueprint
from flask import render_template
from utils.routes import login_required

blueprint = Blueprint('home', __name__, template_folder='templates',
                      static_folder='static', static_url_path='/static/home')


@login_required
def get_home():
    return render_template('home/home.html', static_url_path=blueprint.static_url_path)


blueprint.add_url_rule('/', view_func=get_home, methods=['GET'])


def register_plugin(app):
    app.register_blueprint(blueprint)
