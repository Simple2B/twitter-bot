from flask import render_template, Blueprint

from app.controllers import parse_gsheet

main_blueprint = Blueprint('main', __name__)


@main_blueprint.route('/')
def index():
    keywords = parse_gsheet()
    return render_template('index.html', keywords=keywords)
