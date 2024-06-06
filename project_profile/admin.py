from flask_admin.contrib.sqla import ModelView
from flask import redirect, url_for, request, session
from flask_admin import BaseView, expose
from .models import Customer, Car, Appointment

class AdminModelView(ModelView):
    def is_accessible(self):
        return session.get('admin_logged_in')

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('admin_login', next=request.url))


class CustomerAdminView(BaseView):
    @expose('/')
    def index(self):
        customers = Customer.query.all()
        return self.render('admin/customer_index.html', customers=customers)

    @expose('/view/<int:customer_id>')
    def view(self, customer_id):
        customer = Customer.query.get_or_404(customer_id)
        cars = Car.query.filter_by(customer_id=customer.id).all()
        appointments = Appointment.query.filter_by(customer_id=customer.id).all()
        return self.render('admin/customer_view.html', customer=customer, cars=cars, appointments=appointments)