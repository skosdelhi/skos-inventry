# backend/routes/chanda.py

from flask import Blueprint, render_template, request, redirect, url_for,flash
from ..models import db, Chanda, Member, Event
from sqlalchemy import func
from io import TextIOWrapper
from flask_login import login_required, current_user
import csv

bp = Blueprint('chanda', __name__, url_prefix='/chanda')


@bp.route('/')
@login_required
def list_chanda():
    page = request.args.get('page', 1, type=int)
    selected_event_id = request.args.get('event_id', type=int)

    # Filter conditionally
    query = Chanda.query
    if selected_event_id:
        query = query.filter_by(event_id=selected_event_id)

    pagination = query.order_by(Chanda.id).paginate(page=page, per_page=50)
    chandas = pagination.items

    # Totals for current filtered page
    total_own = sum(c.own_payment or 0 for c in chandas)
    total_collected = sum(c.collected_amount or 0 for c in chandas)

    # For dropdown
    events = Event.query.all()

    return render_template(
        'chanda/list.html',
        chandas=chandas,
        pagination=pagination,
        total_own=total_own,
        total_collected=total_collected,
        events=events,
        selected_event_id=selected_event_id
    )


@bp.route('/add', methods=['GET', 'POST'])
@login_required
def add_chanda():
    members = Member.query.all()
    events = Event.query.all()

    if request.method == 'POST':
        collected = request.form.get('collected_amount')
        collected_amount = float(collected) if collected else None
        own_payment = request.form.get('own_payment')
        own_payment = float(own_payment) if own_payment else None
        
        chanda = Chanda(
            member_id=request.form['member_id'],
            event_id=request.form['event_id'],
            #own_payment=request.form['own_payment'],
            #collected_amount=request.form['collected_amount']
            own_payment=own_payment,
            collected_amount=collected_amount
        )
        db.session.add(chanda)
        db.session.commit()
        return redirect(url_for('chanda.list_chanda'))

    return render_template('chanda/add.html', members=members, events=events)

# Edit Chanda
@bp.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_chanda(id):
    chanda = Chanda.query.get_or_404(id)
    members = Member.query.all()
    events = Event.query.all()

    if request.method == 'POST':
        collected = request.form.get('collected_amount')
        collected_amount = float(collected) if collected else None
        own_payment = request.form.get('own_payment')
        own_payment = float(own_payment) if own_payment else None
        
        chanda.member_id = request.form['member_id']
        chanda.event_id = request.form['event_id']
        chanda.own_payment = own_payment
        chanda.collected_amount = collected_amount
        
        db.session.commit()
        return redirect(url_for('chanda.list_chanda'))

    return render_template('chanda/edit.html', chanda=chanda, members=members, events=events)

# Delete Chanda
@bp.route('/delete/<int:id>', methods=['GET'])
@login_required
def delete_chanda(id):
    chanda = Chanda.query.get_or_404(id)
    db.session.delete(chanda)
    db.session.commit()
    return redirect(url_for('chanda.list_chanda'))

@bp.route('/summary')
@login_required
def chanda_summary():
    # Summary by Event
    event_summary = (
        db.session.query(
            Event.name,
            func.sum(Chanda.own_payment),
            func.sum(Chanda.collected_amount)
        )
        .join(Chanda.event)
        .group_by(Event.id)
        .all()
    )

    # Summary by Member
    member_summary = (
        db.session.query(
            Member.name,
            func.sum(Chanda.own_payment),
            func.sum(Chanda.collected_amount)
        )
        .join(Chanda.member)
        .group_by(Member.id)
        .all()
    )

    return render_template(
        'chanda/summary.html',
        event_summary=event_summary,
        member_summary=member_summary
    )
@bp.route('/upload', methods=['GET', 'POST'])
@login_required
def upload_chandas():
    if request.method == 'POST':
        file = request.files['csv_file']
        if not file.filename.endswith('.csv'):
            flash('Please upload a valid CSV file.', 'danger')
            return redirect(request.url)

        stream = TextIOWrapper(file.stream, encoding='utf-8')
        csv_reader = csv.DictReader(stream)



        count = 0
        for row in csv_reader:
            chanda = Chanda(
                member_id=row['member_id'],
                event_id=row.get('event_id'),
                own_payment=row.get('own_payment'),
                collected_amount=row.get('collected_amount')
            )
            db.session.add(chanda)
            count += 1

        db.session.commit()
        flash(f'{count} chanda uploaded successfully!', 'success')
        return redirect(url_for('chanda.list_chanda'))

    return render_template('chanda/upload.html')    