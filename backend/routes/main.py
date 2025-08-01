from flask import Blueprint, render_template, make_response, url_for, current_app,request
from weasyprint import HTML,CSS
from backend.models import Chanda, GuestPayment, Expense ,Member,Guest,Event,BankTransaction
from sqlalchemy import func
from backend import db  # adjust import if needed
import os
from constants import CATEGORIES
from datetime import date
from flask_login import login_required, current_user
from pypdf import PdfReader, PdfWriter

bp = Blueprint('main', __name__, url_prefix='/report')  # no url_prefix = root "/"

@login_required
def get_event_context(event_id):
    event = db.session.get(Event, event_id)
    if not event:
        return None

    bank_summary = event.bank_summary

    context = {
        'event': event,
        'event_name' : event.name,
        'member_collection': event.member_collection,
        'guest_collection': event.guest_collection,
        'book_collection': event.book_collection,
        'total_collection': event.total_collection,
        'total_expenses': event.total_expenses,
        'balance': event.balance,
        'expense_totals_by_category': event.expense_totals_by_category,
        'bank_summary': bank_summary,
        'bank_withdrawal': bank_summary['withdrawal'],
        'bank_balance': bank_summary['balance'],
        'bank_interest': bank_summary['interest'],
        'today_date': date.today().strftime("%d %B %Y"),
    }

    return context

@bp.route('/update-member-order')
@login_required
def update_member_order():
    members = Member.query.order_by(Member.joining_date.asc()).all()
    for idx, member in enumerate(members, start=1):
        member.order = idx
    db.session.commit()
    return "✅ Member order updated by joining date."

@bp.route('/summary')
@login_required
def summary_report():
    event_id = request.args.get('event_id') 
    context = get_event_context(event_id)
    if not context:
        return "Event not found", 404
  
    #event = db.session.get(Event, event_id)
    chart_labels = list(context['expense_totals_by_category'].keys())
    chart_values = list(context['expense_totals_by_category'].values())
    collection_labels = ["Member", "Guest & Other", "Book"]
    collection_values = [context['member_collection'],context['guest_collection'],context['book_collection']]

    return render_template(
        'report/summary.html',
        categories=CATEGORIES,chart_labels=chart_labels,chart_values=chart_values,
        collection_values=collection_values,collection_labels=collection_labels,
        event_id=event_id,**context
    )



    
@bp.route('/report.pdf')
@login_required
def generate_pdf():
    
    event_id = request.args.get('event_id') 
    context = get_event_context(event_id)
    
    if not context:
        return "Event not found", 404
    
    # Logo for PDF
    logo_path = os.path.join(current_app.static_folder, 'images/logo.png')
    logo_url = f"file://{logo_path}"
    
    statement_img =url_for('static', filename='images/statment.jpeg', _external=True)
    # Render PDF HTML
    rendered_html = render_template(
        'report/summary.html',
        logo_url=logo_url,statement_img=statement_img,is_pdf=True,event_id=event_id,**context
    )
    css_path = os.path.join(current_app.root_path, 'static/css/bootstrap.min.css')
    pdf = HTML(string=rendered_html).write_pdf(stylesheets=[CSS(css_path)])
    
    finame = context['event_name'] +'summary_report.pdf'
    response = make_response(pdf)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'inline ; filename='+finame
    # Usage
    return response

@bp.route('/summary-report.pdf')
@login_required
def generate_full_summary_pdf():
    event_id = request.args.get('event_id') 
    context = get_event_context(event_id)
    if not context:
        return "Event not found", 404
    expenses = db.session.query(Expense).join(Event).filter(Expense.event_id == event_id).all()
  
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
        event_id=event_id,
        # additional
        chandas=chandas,total_chanda=total_chanda,total_collected_amount=total_collected_amount,total_own_payment=total_own_payment,
        guests=guests,categories=CATEGORIES,expenses=expenses,statement_img=statement_img,**context
    )

    css_path = os.path.join(current_app.root_path, 'static/css/bootstrap.min.css')
    pdf = HTML(string=html).write_pdf(stylesheets=[CSS(css_path)])
    #pdf = HTML(string=rendered_html, base_url=current_app.root_path).write_pdf()
    finame = context['event_name'] +'details.pdf'
    response = make_response(pdf)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'inline; filename='+finame
    return response

@bp.route('/view')
def view_full_report():
    event_id = request.args.get('event_id') 
    context = get_event_context(event_id)
    if not context:
        return "Event not found", 404
    expenses = db.session.query(Expense).join(Event).filter(Expense.event_id == event_id).all()
    
    # Charts
    chart_labels = list(context['expense_totals_by_category'].keys())
    chart_values = list(context['expense_totals_by_category'].values())
    collection_labels = ["Member", "Guest & Other", "Book"]
    collection_values = [context['member_collection'],context['guest_collection'],context['book_collection']]

    # Filtered records
    chandas = Chanda.query.filter_by(event_id=event_id).all()
    guest_payments = GuestPayment.query.filter_by(event_id=event_id).all()
    expenses = Expense.query.filter_by(event_id=event_id).all()

    return render_template(
        'report/full_report.html',
        categories=CATEGORIES,chart_labels=chart_labels,
        chart_values=chart_values,collection_labels=collection_labels,
        collection_values=collection_values,chandas=chandas,guest_payments=guest_payments,expenses=expenses,is_pdf=False,event_id=event_id,**context
    )