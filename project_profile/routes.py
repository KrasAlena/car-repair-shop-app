from flask import render_template, request, redirect, url_for, session, flash
from flask_bcrypt import generate_password_hash, check_password_hash
from flask import current_app as app
from flask_login import login_user, login_required, logout_user, current_user
from . import db
from .models import Customer, Car, Service, Appointment
from .forms import CustomerForm, LoginForm, CarForm, BookingForm


@app.route('/')
def landing_page():
    return render_template('landing.html')


@app.route('/about')
def about_page():
    return render_template('about.html')


@app.route('/become_customer', methods=['GET', 'POST'])
def become_customer():
    form = CustomerForm()
    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data)
        new_customer = Customer(name=form.name.data, email=form.email.data, phone_number=form.phone_number.data, password=hashed_password)
        db.session.add(new_customer)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('become_customer.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        customer = Customer.query.filter_by(email=email).first()
        if customer and check_password_hash(customer.password, password):
            login_user(customer)
            return redirect(url_for('user_profile'))
    return render_template('login.html', form=form)


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('landing_page'))


@app.route('/profile')
@login_required
def user_profile():
    cars = current_user.cars
    appointments = current_user.appointments
    print(f"User {current_user.name} has the following appointments: {appointments}")
    return render_template('user_profile.html', name=current_user.name, cars=cars, appointments=appointments)


@app.route('/admin_login',  methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        password = request.form.get('password')
        if password == app.config['ADMIN_PASSWORD']:
            session['admin_logged_in'] = True
            return redirect('/admin')
        else:
            flash('Invalid password')
    return render_template('admin_login.html')


@app.route('/admin')
def admin():
    if not session.get('admin_logged_in'):
        return render_template(url_for('admin_login'))
    return redirect('/admin/')


@app.route('/add_car', methods=['GET', 'POST'])
@login_required
def add_car():
    form = CarForm()
    if form.validate_on_submit():
        new_car = Car(make=form.make.data, model=form.model.data, year=form.year.data, customer_id=current_user.id)
        db.session.add(new_car)
        db.session.commit()
        return redirect(url_for('user_profile'))
    return render_template('car_form.html', form=form)


@app.route('/edit_car/<int:car_id>', methods=['GET', 'POST'])
@login_required
def edit_car(car_id):
    car = Car.query.get_or_404(car_id)
    if car.customer_id != current_user.id:
        return redirect(url_for('user_profile'))
    form = CarForm(obj=car)
    if form.validate_on_submit():
        car.make = form.make.data
        car.model = form.model.data
        car.year = form.year.data
        db.session.commit()
        return redirect(url_for('user_profile'))
    return render_template('car_form.html', form=form)


@app.route('/delete_car/<int:car_id>', methods=['POST'])
@login_required
def delete_car(car_id):
    car = Car.query.get_or_404(car_id)
    if car.customer_id != current_user.id:
        return redirect(url_for('user_profile'))
    db.session.delete(car)
    db.session.commit()
    return redirect(url_for('user_profile'))


@app.route('/services')
@login_required
def view_services():
    services = Service.query.all()
    return render_template('services.html', services=services)


@app.route('/book_appointment', methods=['GET', 'POST'])
@login_required
def book_appointment():
    form = BookingForm()
    form.car_id.choices = [(car.id, f"{car.make} {car.model}") for car in current_user.cars]
    form.service_id.choices = [(service.id, service.name) for service in Service.query.all()]
    if form.validate_on_submit():
        print("Form validated successfully")
        print(f"Date and Time: {form.date_time.data}")
        print(f"Car ID: {form.car_id.data}")
        print(f"Service ID: {form.service_id.data}")

        new_appointment = Appointment(
            date_time=form.date_time.data,
            customer_id=current_user.id,
            car_id=form.car_id.data,
            service_id=form.service_id.data
        )
        db.session.add(new_appointment)
        db.session.commit()
        print("New appointment created successfully")
        return redirect(url_for('user_profile'))
    else:
        if request.method == 'POST':
            print("Form validation failed")
            print(form.errors)
    return render_template('booking_form.html', form=form)


@app.route('/cancel_appointment/<int:appointment_id>', methods=['POST'])
@login_required
def cancel_appointment(appointment_id):
    appointment = Appointment.query.get_or_404(appointment_id)
    if appointment.customer_id != current_user.id:
        return redirect(url_for('user_profile'))
    db.session.delete(appointment)
    db.session.commit()
    return redirect(url_for('user_profile'))