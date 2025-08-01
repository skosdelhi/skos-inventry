from flask import Blueprint, render_template, request, redirect, url_for,flash
from ..models import db, Guest, Event
from io import TextIOWrapper
import csv
from flask_login import login_required, current_user

bp = Blueprint('guests', __name__, url_prefix='/guests')

@bp.route('/')
@login_required
def list_guests():
    guests = Guest.query.all()
    return render_template('guests/list.html', guests=guests)

@bp.route('/add', methods=['GET', 'POST'])
@login_required
def add_guest():
    events = Event.query.all()
    if request.method == 'POST':
        guest = Guest(
            name=request.form['name'],
            phone=request.form.get('phone'),
            address=request.form.get('address'),
            
        )
        db.session.add(guest)
        db.session.commit()
        return redirect(url_for('guests.list_guests'))
    return render_template('guests/add.html', events=events)

@bp.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_guest(id):
    guest = Guest.query.get_or_404(id)
    events = Event.query.all()
    if request.method == 'POST':
        guest.name = request.form['name']
        guest.phone = request.form.get('phone')
        guest.address = request.form.get('address')
        db.session.commit()
        return redirect(url_for('guests.list_guests'))
    return render_template('guests/edit.html', guest=guest, events=events)

@bp.route('/delete/<int:id>', methods=['POST'])
@login_required
def delete_guest(id):
    guest = Guest.query.get_or_404(id)
    db.session.delete(guest)
    db.session.commit()
    return redirect(url_for('guests.list_guests'))

@bp.route('/upload', methods=['GET', 'POST'])
@login_required
def upload_guests():
    if request.method == 'POST':
        file = request.files['csv_file']
        if not file.filename.endswith('.csv'):
            flash('Please upload a valid CSV file.', 'danger')
            return redirect(request.url)

        stream = TextIOWrapper(file.stream, encoding='utf-8')
        csv_reader = csv.DictReader(stream)

        count = 0
        for row in csv_reader:
            guest = Guest(
                name=row['name'],
                phone=row.get('phone'),
                address=row.get('address')
                
            )
            db.session.add(guest)
            count += 1

        db.session.commit()
        flash(f'{count} Guests uploaded successfully!', 'success')
        return redirect(url_for('guests.list_guests'))

    return render_template('guests/upload.html')
