from flask import Blueprint, render_template, request, redirect, url_for
from ..models import db, Guest, Event, GuestPayment
from sqlalchemy import func
from flask_login import login_required, current_user

bp = Blueprint('guest_payments', __name__, url_prefix='/guest_payments')


@bp.route('/')
@login_required
def list_payments():
    page = request.args.get('page', 1, type=int)
    selected_event_id = request.args.get('event_id', type=int)

    # Base query
    query = GuestPayment.query
    if selected_event_id:
        query = query.filter_by(event_id=selected_event_id)

    # Pagination
    pagination = query.order_by(GuestPayment.id).paginate(page=page, per_page=12)
    payments = pagination.items

    # Totals
    total_page_amount = sum(p.amount or 0 for p in payments)

    # Total for all filtered rows
    total_amount = query.with_entities(func.coalesce(func.sum(GuestPayment.amount), 0)).scalar()

    # For dropdown
    events = Event.query.order_by(Event.name).all()

    return render_template(
        'guest_payments/list.html',
        payments=payments,
        pagination=pagination,
        total_own=total_page_amount,
        total_amount=total_amount,
        events=events,
        selected_event_id=selected_event_id
    )
     
@bp.route('/add', methods=['GET', 'POST'])
@login_required
def add_payment():
    guests = Guest.query.all()
    events = Event.query.all()
    if request.method == 'POST':
        payment = GuestPayment(
            guest_id=request.form['guest_id'],
            event_id=request.form['event_id'],
            amount=request.form['amount']
        )
        db.session.add(payment)
        db.session.commit()
        return redirect(url_for('guest_payments.list_payments'))
    return render_template('guest_payments/add.html', guests=guests, events=events)

@bp.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_payment(id):
    payment = GuestPayment.query.get_or_404(id)
    guests = Guest.query.all()
    events = Event.query.all()
    if request.method == 'POST':
        payment.guest_id = request.form['guest_id']
        payment.event_id = request.form['event_id']
        payment.amount = request.form['amount']
        db.session.commit()
        return redirect(url_for('guest_payments.list_payments'))
    return render_template('guest_payments/edit.html', payment=payment, guests=guests, events=events)

@bp.route('/delete/<int:id>', methods=['POST'])
@login_required
def delete_payment(id):
    payment = GuestPayment.query.get_or_404(id)
    db.session.delete(payment)
    db.session.commit()
    return redirect(url_for('guest_payments.list_payments'))
