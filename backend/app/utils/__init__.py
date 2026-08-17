from flask import Blueprint

utils_bp = Blueprint('utils', __name__)

from app.utils import parsers