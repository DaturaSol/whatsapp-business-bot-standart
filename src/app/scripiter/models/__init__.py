"""Module responsible for calling and the registery"""

from app.scripiter.models.user import user_bp
from app.scripiter.models.unasus import unasus_bp
from app.scripiter.models.redirecter import redirecter_bp
from app.scripiter.models.welcome import welcome_bp


registery = {}
registery.update(user_bp.get_registery())
registery.update(unasus_bp.get_registery())
registery.update(redirecter_bp.get_registery())
registery.update(welcome_bp.get_registery())
