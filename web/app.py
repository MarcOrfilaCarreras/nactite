from config import Configuration
from flask import Flask
from utils.routes import inject_global_variables
from utils.routes import logging
from utils.routes import register_blueprints

app = Flask(__name__)
app.config.from_object(Configuration)

register_blueprints(app=app, path='routes')
inject_global_variables(app=app)
logging(app=app)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
