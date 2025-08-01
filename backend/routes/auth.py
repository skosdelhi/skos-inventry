from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from ..models import db, Users

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        print("Form submitted")
        username = request.form['username']
        password = request.form['password']
        print(f"Username: {username}, Password: {password}")

        user = Users.query.filter_by(username=username).first()
        if user:
            print("User found in DB")
            if check_password_hash(user.password, password):
                print("Password matched")
                login_user(user)
                # Redirect based on role
                if user.role == 'admin':
                    return redirect(url_for('dashboard.dashboard'))
                elif user.role == 'client':
                    return redirect(url_for('main.client_dashboard'))
                else:
                    flash('Unknown role', 'danger')
            else:
                print("Password did not match")
        else:
            print("User not found")

        flash('Invalid credentialssss', 'danger')
    return render_template('auth/login.html')



@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash("Logged out", "info")
    return redirect(url_for('auth.login'))