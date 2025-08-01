from flask import Blueprint, render_template, request, redirect, url_for
from ..models import db, BankTransaction,Event
from datetime import date
from flask_login import login_required, current_user


bp = Blueprint('bank', __name__, url_prefix='/bank')

@bp.route('/')
@login_required
def list_bank():
    bank = BankTransaction.query.order_by(BankTransaction.id).all()
    return render_template('bank/list.html', bank=bank)

@bp.route('/add', methods=['GET', 'POST'])
@login_required
def add_bank():
    if request.method == 'POST':
        bank = BankTransaction(
            event_id=request.form['event_id'],
            transaction_date=date.today(),
            withdrawal_amount=request.form['withdrawal_amount'],
            interest_amount=request.form['interest_amount'],
            balance_amount=request.form['balance_amount'],
            remark=request.form['remark']
        )
        db.session.add(bank)
        db.session.commit()
        return redirect(url_for('bank.list_bank'))
    events = Event.query.all()
    return render_template('bank/add.html', events=events)

@bp.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_bank(id):
    bank = BankTransaction.query.get_or_404(id)
    if request.method == 'POST':
        bank.event_id=request.form['event_id'],
        bank.transaction_date=date.today(),
        bank.withdrawal_amount=request.form['withdrawal_amount'],
        bank.interest_amount=request.form['interest_amount'],
        bank.balance_amount=request.form['balance_amount'],
        bank.remark=request.form['remark']
        db.session.commit()
        return redirect(url_for('bank.list_bank'))
    events = Event.query.all()
    return render_template('bank/edit.html', bank=bank,events=events)

@bp.route('/delete/<int:id>', methods=['GET'])
@login_required
def delete_bank(id):
    bank = BankTransaction.query.get_or_404(id)
    db.session.delete(bank)
    db.session.commit()
    return redirect(url_for('bank.list_bank'))
