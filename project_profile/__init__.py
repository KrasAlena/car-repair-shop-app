from flask import Flask
from flask_login import LoginManager
from flask_admin import Admin
from .models import db, Customer, Car, Service, Appointment
from .admin import AdminModelView, CustomerAdminView
import os
from dotenv import load_dotenv

def create_app():
    app = Flask(__name__)

    load_dotenv()

    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///car_repair_shop.db'
    app.config['SECRET_KEY'] = os.urandom(24)
    app.config['ADMIN_PASSWORD'] = os.getenv('ADMIN_PASSWORD')

    db.init_app(app)

    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'login'

    @login_manager.user_loader
    def load_user(user_id):
        return Customer.query.get(int(user_id))

    from .admin import AdminModelView
    admin = Admin(app, name='AdminDashboard', template_mode='bootstrap3')
    admin.add_view(AdminModelView(Customer, db.session))
    admin.add_view(AdminModelView(Car, db.session))
    admin.add_view(AdminModelView(Service, db.session))
    admin.add_view(AdminModelView(Appointment, db.session))
    admin.add_view(CustomerAdminView(name='Customer details', endpoint='customeradminview'))

    with app.app_context():
        db.create_all()
        initialize_services()
        from . import routes

    return app


def initialize_services():
    services = [
        {'name': 'Oil change', 'description': 'Change the engine oil and replace the oil filter', 'estimated_cost': 50.0},
        {'name': 'Tire replacement', 'description': 'Replace old tires with new ones', 'estimated_cost': 100.0},
        {'name': 'Brake inspection', 'description': 'Inspect brake pads and rotors', 'estimated_cost': 40.0},
        {'name': 'Engine diagnostic', 'description': 'Perform a diagnostic test on the engine', 'estimated_cost': 60.0},
    ]
    for service_data in services:
        if not Service.query.filter_by(name=service_data['name']).first():
            new_service = Service(**service_data)
            db.session.add(new_service)
    db.session.commit()

