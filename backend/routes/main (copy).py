from flask import Blueprint, render_template, make_response, url_for, current_app,request
from weasyprint import HTML,CSS
from backend.models import Chanda, GuestPayment, Expense ,Member,Guest,Event,BankTransaction
from sqlalchemy import func
from backend import db  # adjust import if needed
import os
from constants import CATEGORIES,BANK
from datetime import date

bp = Blueprint('main', __name__, url_prefix='/report')  # no url_prefix = root "/"


bank_withdrawal = BANK['bank_withdrawal']
bank_balance = BANK['bank_balance']
bank_interest = BANK['bank_interest']

def get_bank_summary(event_id):
    banktr = BankTransaction.query.filter_by(event_id=event_id).first()
    if banktr:
        return {
            'withdrawal': banktr.withdrawal_amount or 0,
            'balance': banktr.balance_amount or 0,
            'interest': banktr.interest_amount or 0
        }
    else:
        return {'withdrawal': 0, 'balance': 0, 'interest': 0}


@bp.route('/update-member-order')
def update_member_order():
    members = Member.query.order_by(Member.joining_date.asc()).all()
    for idx, member in enumerate(members, start=1):
        member.order = idx
    db.session.commit()
    return "✅ Member order updated by joining date."

@bp.route('/summary')
def summary_report():
    event_id = request.args.get('event_id') 
    
    bank = get_bank_summary(event_id)
    bank_withdrawal = bank['withdrawal']
    bank_balance = bank['balance']
    bank_interest = bank['interest']
 
    today_date = date.today().strftime("%d %B %Y")

    member_collection = db.session.query(func.sum(Chanda.own_payment))\
        .filter(Chanda.event_id == event_id, Chanda.member_id.isnot(None))\
        .scalar() or 0

    guest_collection = db.session.query(func.sum(GuestPayment.amount))\
        .filter(GuestPayment.event_id == event_id)\
        .scalar() or 0

    book_collection = db.session.query(func.sum(Chanda.collected_amount))\
        .filter(Chanda.event_id == event_id, Chanda.member_id.isnot(None))\
        .scalar() or 0

    total_collection = member_collection + guest_collection + book_collection

    expense_totals = {
        cname: db.session.query(func.sum(Expense.amount))
            .filter(Expense.category_id == cid, Expense.event_id == event_id)
            .scalar() or 0
        for cid, cname in CATEGORIES.items()
    }
    
    total_expenses = sum(expense_totals.values())
    balance = total_collection - total_expenses
    total_balance = balance + bank_balance + bank_withdrawal
    
    event = db.session.get(Event, event_id)
    chart_labels = list(expense_totals.keys())
    chart_values = list(expense_totals.values())
    collection_labels = ["Member", "Guest & Other", "Book"]
    collection_values = [member_collection, guest_collection, book_collection]

    return render_template(
        'report/summary.html',
        categories=CATEGORIES,
        member_collection=member_collection,
        guest_collection=guest_collection,
        book_collection=book_collection,
        total_collection=total_collection,
        expense_totals=expense_totals,
        total_expenses=total_expenses,
        balance=balance,bank_withdrawal=bank_withdrawal,
        bank_balance=bank_balance,bank_interest=bank_interest,
        total_balance=total_balance,event=event,today_date=today_date,
        chart_labels=chart_labels,chart_values=chart_values,
        collection_values=collection_values,collection_labels=collection_labels,event_id=event_id
    )
    
@bp.route('/report.pdf')
def generate_pdf():
    event_id = request.args.get('event_id') 
    #event_id = 1  # or pass as query param: request.args.get('event_id', type=int)
    
    today_date = date.today().strftime("%d %B %Y")
    
    bank = get_bank_summary(event_id)
    bank_withdrawal = bank['withdrawal']
    bank_balance = bank['balance']
    bank_interest = bank['interest']

    # Filtered Collections
    member_collection = db.session.query(func.sum(Chanda.own_payment))\
        .filter(Chanda.member_id.isnot(None), Chanda.event_id == event_id)\
        .scalar() or 0

    guest_collection = db.session.query(func.sum(GuestPayment.amount))\
        .filter(GuestPayment.event_id == event_id)\
        .scalar() or 0

    book_collection = db.session.query(func.sum(Chanda.collected_amount))\
        .filter(Chanda.member_id.isnot(None), Chanda.event_id == event_id)\
        .scalar() or 0

    total_collection = member_collection + guest_collection + book_collection

    # Filtered Expenses by Category
    expense_totals = {
        cname: db.session.query(func.sum(Expense.amount))\
            .filter(Expense.category_id == cid, Expense.event_id == event_id)\
            .scalar() or 0
        for cid, cname in CATEGORIES.items()
    }

    total_expenses = sum(expense_totals.values())
    balance = total_collection - total_expenses
    total_balance = balance + bank_balance + bank_withdrawal
    event = db.session.get(Event, event_id)
    # Logo for PDF
    logo_path = os.path.join(current_app.static_folder, 'images/logo.png')
    logo_url = f"file://{logo_path}"
    
    statement_img =url_for('static', filename='images/statment.jpeg', _external=True)
    # Render PDF HTML
    rendered_html = render_template(
        'report/summary.html',
        categories=CATEGORIES,
        member_collection=member_collection,
        guest_collection=guest_collection,
        book_collection=book_collection,
        total_collection=total_collection,
        expense_totals=expense_totals,
        total_expenses=total_expenses,
        logo_url=logo_url,
        balance=balance,
        bank_balance=bank_balance,
        bank_withdrawal=bank_withdrawal,
        bank_interest=bank_interest,
        total_balance=total_balance,today_date = today_date,event=event,statement_img=statement_img,
        is_pdf=True,event_id=event_id
    )

    css_path = os.path.join(current_app.root_path, 'static/css/bootstrap.min.css')
    pdf = HTML(string=rendered_html).write_pdf(stylesheets=[CSS(css_path)])

    response = make_response(pdf)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'inline; filename=Saraswatipuja2025summary_report.pdf'
    return response

@bp.route('/summary-report.pdf')
def generate_full_summary_pdf():
    
    #event_id = request.args.get('event_id', type=int, default=1)
    #event_id = 1;
    event_id = request.args.get('event_id') 
    
    bank = get_bank_summary(event_id)
    bank_withdrawal = bank['withdrawal']
    bank_balance = bank['balance']
    bank_interest = bank['interest']
    
    """ event = db.session.get(Event, event_id)

    event.guests
    event.chandas
    event.expenses
    event.guest_payments
    event.bank_transactions

    event.total_collection
    event.total_expenses
    event.balance
     """
    
    expenses = db.session.query(Expense).join(Event).filter(Expense.event_id == event_id).all()
    event = db.session.get(Event, event_id)
    event_name = event.name
    member_collection = db.session.query(func.sum(Chanda.own_payment))\
        .filter(Chanda.member_id.isnot(None), Chanda.event_id == event_id)\
        .scalar() or 0

    guest_collection = db.session.query(func.sum(GuestPayment.amount))\
        .filter(GuestPayment.event_id == event_id)\
        .scalar() or 0

    book_collection = db.session.query(func.sum(Chanda.collected_amount))\
        .filter(Chanda.member_id.isnot(None), Chanda.event_id == event_id)\
        .scalar() or 0

    total_collection = member_collection + guest_collection + book_collection

    expense_totals = {
        cname: db.session.query(func.sum(Expense.amount)).filter(Expense.category_id == cid,Expense.event_id == event_id).scalar() or 0
        for cid, cname in CATEGORIES.items()
    }
    total_expenses = sum(expense_totals.values())
    balance = total_collection - total_expenses
    total_balance = balance + bank_balance + bank_withdrawal + bank_interest

    # Chanda Details
    chandas = db.session.query(Chanda).join(Member).filter(Chanda.event_id == event_id).all()

    total_own_payment = sum(c.own_payment or 0 for c in chandas)
    total_collected_amount = sum(c.collected_amount or 0 for c in chandas)
    total_chanda = total_own_payment + total_collected_amount
   
    guests = db.session.query(GuestPayment).join(Guest).join(Event).filter(GuestPayment.event_id ==event_id).all()
    logo_path = os.path.join(current_app.root_path, 'static/images/logo.png')
    logo_url=url_for('static', filename='images/logo.png', _external=True)
    
    statement_img =url_for('static', filename='images/statment.jpeg', _external=True)
    html = render_template(
        'report/full_summary_pdf.html',
        logo_path=logo_path,logo_url=logo_url,
        member_collection=member_collection,
        guest_collection=guest_collection,
        book_collection=book_collection,
        total_collection=total_collection,
        expense_totals=expense_totals,
        total_expenses=total_expenses,
        balance=balance,
        bank_withdrawal=bank_withdrawal,
        bank_balance=bank_balance,bank_interest=bank_interest,
        total_balance=total_balance,event_id=event_id,event=event,
        # additional
        chandas=chandas,total_chanda=total_chanda,total_collected_amount=total_collected_amount,total_own_payment=total_own_payment,
        guests=guests,categories=CATEGORIES,expenses=expenses,statement_img=statement_img
    )

    css_path = os.path.join(current_app.root_path, 'static/css/bootstrap.min.css')
    pdf = HTML(string=html).write_pdf(stylesheets=[CSS(css_path)])
    #pdf = HTML(string=rendered_html, base_url=current_app.root_path).write_pdf()
    finame = event_name +'details.pdf'
    response = make_response(pdf)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'inline; filename='+finame
    return response


@bp.route('/view')
def view_full_report():
    event_id = request.args.get('event_id') 
    event = db.session.get(Event, event_id)
    expenses = db.session.query(Expense).join(Event).filter(Expense.event_id == event_id).all()
    bank = get_bank_summary(event_id)
    bank_withdrawal = bank['withdrawal']
    bank_balance = bank['balance']
    bank_interest = bank['interest']

    # Collections
    member_collection = db.session.query(func.sum(Chanda.own_payment))\
        .filter(Chanda.member_id.isnot(None), Chanda.event_id == event_id)\
        .scalar() or 0

    guest_collection = db.session.query(func.sum(GuestPayment.amount))\
        .filter(GuestPayment.event_id == event_id)\
        .scalar() or 0

    book_collection = db.session.query(func.sum(Chanda.collected_amount))\
        .filter(Chanda.member_id.isnot(None), Chanda.event_id == event_id)\
        .scalar() or 0

    total_collection = member_collection + guest_collection + book_collection

    # Expenses by category
    expense_totals = {
        cname: db.session.query(func.sum(Expense.amount))\
            .filter(Expense.category_id == cid, Expense.event_id == event_id)\
            .scalar() or 0
        for cid, cname in CATEGORIES.items()
    }

    total_expenses = sum(expense_totals.values())

    balance = total_collection - total_expenses
    total_balance = balance + bank_balance + bank_withdrawal

    # Charts
    chart_labels = list(expense_totals.keys())
    chart_values = list(expense_totals.values())
    collection_labels = ["Member", "Guest & Other", "Book"]
    collection_values = [member_collection, guest_collection, book_collection]

    # Filtered records
    chandas = Chanda.query.filter_by(event_id=event_id).all()
    guest_payments = GuestPayment.query.filter_by(event_id=event_id).all()

    return render_template(
        'report/full_report.html',
        categories=CATEGORIES,
        member_collection=member_collection,
        guest_collection=guest_collection,
        book_collection=book_collection,
        total_collection=total_collection,
        expense_totals=expense_totals,
        total_expenses=total_expenses,
        balance=balance,
        bank_balance=bank_balance,
        bank_withdrawal=bank_withdrawal,
        total_balance=total_balance,
        chart_labels=chart_labels,
        chart_values=chart_values,
        collection_labels=collection_labels,
        collection_values=collection_values,
        chandas=chandas,
        guest_payments=guest_payments,
        bank_interest=bank_interest,expenses=expenses,event=event,
        is_pdf=False,event_id=event_id
    )
