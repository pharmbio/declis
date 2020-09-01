from flask import Blueprint

bp = Blueprint('reg', __name__, template_folder='templates')

from app.reg import routes
