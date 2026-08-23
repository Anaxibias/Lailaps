from flask import Blueprint

service_bp = Blueprint('services', __name__)

from app.services import user_services, job_services, external