from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from babel.numbers import format_currency

login_manager = LoginManager()
login_manager.login_view = 'auth.login'  # This refers to the 'login' route in the 'auth' blueprint



db = SQLAlchemy()
migrate = Migrate()  # <- Define it globally

def create_app():
    app = Flask(__name__, template_folder='templates')
    # Register Jinja2 filter
    def initials_filter(name):
     if not isinstance(name, str):
        name = str(name)
     return ''.join(part[0].upper() for part in name.strip().split() if part)
    def first_name_filter(name):
     return name.strip().split()[0] if name else ''
      
    def inr_filter(value):
      return '{:,.2f}'.format(value or 0) 

    app.add_template_filter(first_name_filter, name='spacefirst_name')
    app.add_template_filter(initials_filter, name='initials')
    app.add_template_filter(inr_filter, name='inr')
    app.config.from_object('config')

    db.init_app(app)
    migrate.init_app(app, db)  # <- Initialize here
    login_manager.init_app(app)
    from .routes import register_blueprints
    from .models import Member, Event, Chanda, Guest, GuestPayment, Expense,Users
    
    @login_manager.user_loader
    def load_user(user_id):
        return Users.query.get(int(user_id))
      
    def inr_filter(value):
      try:
          return format_currency(value, 'INR', locale='en_IN')
      except:
        return value
  
    app.add_template_filter(inr_filter, name='inr')
    
    # Register Blueprints
    #from .routes import register_routes
    
    register_blueprints(app)
    
    @app.context_processor
    def inject_counts():
      def get_counts():
        return {
            'count_members': db.session.query(Member).count(),
            'count_events': db.session.query(Event).count(),
            'count_chanda': db.session.query(Chanda).count(),
            'count_guests': db.session.query(Guest).count(),
            'count_guest_payments': db.session.query(GuestPayment).count(),
            'count_expenses': db.session.query(Expense).count()
         }
      return get_counts()
   
  

    return app