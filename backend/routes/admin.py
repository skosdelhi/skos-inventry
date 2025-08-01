# app/routes/admin.py
from flask import Blueprint, render_template, request, redirect, url_for, flash
from werkzeug.security import generate_password_hash
from flask_login import login_required
from ..models import db, Users

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.route('/users')
@login_required
def list_users():
    users = Users.query.all()
    return render_template('admin/list.html', users=users)

@admin_bp.route('/users/create', methods=['GET', 'POST'])
@login_required
def create_user():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = generate_password_hash(request.form['password'])
        role = request.form['role']

        new_user = Users(username=username, email=email, password=password, role=role)
        db.session.add(new_user)
        db.session.flush()

        

        db.session.commit()
        flash("User created successfully", "success")
        return redirect(url_for('admin.list_users'))

    return render_template('admin/create.html')

# app/routes/admin.py (continued)

@admin_bp.route('/users/edit/<int:user_id>', methods=['GET', 'POST'])
@login_required
def edit_user(user_id):
    user = Users.query.get_or_404(user_id)

    if request.method == 'POST':
        user.username = request.form['username']
        user.email = request.form['email']
        user.role = request.form['role']

        if request.form.get('password'):
            user.password = generate_password_hash(request.form['password'])

        if user.role == 'client':
            if user.client:
                client = user.client
            
        else:
            if user.client:
                db.session.delete(user.client)

        db.session.commit()
        flash("User updated successfully", "success")
        return redirect(url_for('admin.list_users'))

    return render_template('admin/edit.html', user=user)


@admin_bp.route('/users/delete/<int:user_id>', methods=['POST'])
@login_required
def delete_user(user_id):
    user = Users.query.get_or_404(user_id)

    if user.client:
        db.session.delete(user.client)

    db.session.delete(user)
    db.session.commit()
    flash("User deleted successfully", "success")
    return redirect(url_for('admin.list_users'))