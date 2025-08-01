from flask import Blueprint, render_template, request, redirect, url_for
from ..models import db, Event
from datetime import date
from flask_login import login_required, current_user


bp = Blueprint('events', __name__, url_prefix='/events')

@bp.route('/')
@login_required
def list_events():
    events = Event.query.all()
    return render_template('events/events.html', events=events)

@bp.route('/add', methods=['GET', 'POST'])
@login_required
def add_event():
    if request.method == 'POST':
        event = Event(
            name=request.form['name'],
            date=request.form['date'],
            location=request.form['location']
        )
        db.session.add(event)
        db.session.commit()
        return redirect(url_for('events.list_events'))
    return render_template('events/add_event.html', current_date=date.today().isoformat())

@bp.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_event(id):
    event = Event.query.get_or_404(id)
    if request.method == 'POST':
        event.name = request.form['name']
        event.date = request.form['date']
        event.location = request.form['location']
        event.description = request.form.get('description')  # if applicable
        db.session.commit()
        return redirect(url_for('events.list_events'))
    return render_template('events/edit_event.html', event=event)

@bp.route('/delete/<int:id>', methods=['GET'])
@login_required
def delete_event(id):
    event = Event.query.get_or_404(id)
    db.session.delete(event)
    db.session.commit()
    return redirect(url_for('events.list_events'))
