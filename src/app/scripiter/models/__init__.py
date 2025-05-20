"""Module responsible for calling and the registery"""

from app.scripiter.models.user import user_bp


registery = {}
registery.update(user_bp.get_registery())

