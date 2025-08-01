from .members import bp as members_bp
from .events import bp as events_bp
from .expenses import bp as expenses_bp
from .chanda import bp as chanda_bp
from .guests import bp as guests_bp
from .guest_payments import bp as guest_payments_bp
from .main import bp as main_bp
from .skosdoc import bp as skosdoc_bp
from .dashboard import bp as dashboard_bp 
from .auth import auth
from .admin import admin_bp
from .bank import bp as  bank_bp


def register_blueprints(app):
    app.register_blueprint(members_bp)
    app.register_blueprint(events_bp)
    app.register_blueprint(expenses_bp)
    app.register_blueprint(chanda_bp)
    app.register_blueprint(guests_bp)
    app.register_blueprint(guest_payments_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(skosdoc_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(auth)
    app.register_blueprint(bank_bp)
    
   