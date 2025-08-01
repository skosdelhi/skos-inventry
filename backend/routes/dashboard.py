from flask import Blueprint, render_template, request, redirect, url_for
from ..models import db, Event, Chanda, Expense, Guest,GuestPayment,BankTransaction,Users
#from sqlalchemy import func
from constants import BANK
from datetime import date
from flask_login import login_required
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_required, current_user


#bp = Blueprint('chanda', __name__, url_prefix='/dashboard')

bp = Blueprint('dashboard', __name__, url_prefix='/')

# Create a new bank transaction
@bp.route('/update-bank')
def update_bank_detail():
    # Create a new bank transaction
    new_tx = BankTransaction(
        event_id=3,  # Replace with actual event_id as needed
        transaction_date=date.today(),
        withdrawal_amount=0,
        interest_amount=0,
        balance_amount=0,
        remark="Post puja balance update"
       
    )

    db.session.add(new_tx)
    db.session.commit()

    return "Bank transaction 3 added successfully!"


# Create a new bank transaction
@bp.route('/update-user')
def update_user_detail():
    # Create a new user transaction
    hashed_pw = generate_password_hash('admin123')
    new_tx = Users(username="admin", email="admin@example.com", password=hashed_pw,role="admin")
    db.session.add(new_tx)
    db.session.commit()

    return "Basernk transaction 3 added successfully!"

@bp.route('/', methods=['GET', 'POST'])
@login_required
def dashboard():
    from sqlalchemy import func
    from datetime import date
       
    current_date =date.today()
    all_events = Event.query.order_by(Event.date.asc()).all()
    selected_ids = request.args.getlist('event_ids', type=int)

    # Default: last 3 events
    if not selected_ids:
        selected_events = all_events[:3]
    else:
        selected_events = Event.query.filter(Event.id.in_(selected_ids)).all()

    event_summaries = []
    latest_past_event = None

    # Step 1: Identify latest event before today
    past_events = [e for e in selected_events if e.date < date.today()]
    if past_events:
        latest_past_event = max(past_events, key=lambda e: e.date)
        
    for event in selected_events:
        
        banktr = BankTransaction.query.filter_by(event_id=event.id).first()
        if banktr:
            bank_withdrawal = banktr.withdrawal_amount or 0
            bank_balance = banktr.balance_amount or 0
            bank_interest = banktr.interest_amount or 0
        else:
            bank_withdrawal = bank_balance = bank_interest = 0
            
        # 👉 Add bank_amount only for latest past event
        if latest_past_event and event.id == latest_past_event.id:
            balance = event.total_collection - event.total_expenses + bank_balance + bank_withdrawal 
            applied_bank = bank_balance + bank_withdrawal
            currentbalance = balance
            bank_inlatest_interest = bank_interest
        else:
            balance = event.total_collection - event.total_expenses
            applied_bank = 0
       
        #balance = total_collection - total_expenses

        event_summaries.append({
            'id': event.id,
            'name': event.name,
            'member_chanda': event.member_collection,
            'book_chanda': event.book_collection,
            'guest_payment': event.guest_collection,
            'total_collection': event.total_collection,
            'total_expenses': event.total_expenses,
            'balance': event.balance,
            'bank_amount': applied_bank  # Pass it to the template
             
        })

    # Chart data
    chart_labels = [e['name'] for e in event_summaries]
    chart_income = [e['total_collection'] for e in event_summaries]
    chart_expense = [e['total_expenses'] for e in event_summaries]

    return render_template(
        'dashboard.html',
        all_events=all_events,
        selected_ids=selected_ids,
        event_summaries=event_summaries,
        chart_labels=chart_labels,
        chart_income=chart_income,
        chart_expense=chart_expense,currentbalance=currentbalance,
        current_date=current_date,bank_interest=bank_inlatest_interest
    )
