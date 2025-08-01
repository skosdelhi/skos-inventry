from flask import Blueprint, render_template, request, redirect, url_for
from ..models import db, Expense, Event ,Member
from sqlalchemy import func
from constants import CATEGORIES
from flask_login import login_required, current_user

bp = Blueprint('expenses', __name__, url_prefix='/expenses')
   
@bp.route('/')
@login_required
def list_expenses():
    page = request.args.get('page', 1, type=int)
    selected_event_id = request.args.get('event_id', type=int)
    selected_category_id = request.args.get('category_id', type=int)


    # Base query
    query = Expense.query
    if selected_event_id:
        query = query.filter_by(event_id=selected_event_id)
    
    if selected_category_id:
        query = query.filter_by(category_id=selected_category_id)   

    # Pagination
    pagination = query.order_by(Expense.id).paginate(page=page, per_page=60)
    paginated_expenses = pagination.items

    # Totals
    total_expenses_pg = sum(e.amount or 0 for e in paginated_expenses)
    total_expenses = query.with_entities(func.coalesce(func.sum(Expense.amount), 0)).scalar()

    # Dropdown data
    events = Event.query.order_by(Event.name).all()
    #categories = ExpenseCategory.query.all()  # if you're using categories

    return render_template(
        'expenses/list.html',
        expenses=paginated_expenses,
        pagination=pagination,
        total_expenses=total_expenses,
        total_expenses_pg=total_expenses_pg,
        categories=CATEGORIES,selected_category_id=selected_category_id,
        events=events,
        selected_event_id=selected_event_id
    )    

@bp.route('/add', methods=['GET', 'POST'])
@login_required
def add_expense():
    events = Event.query.all()
    members = Member.query.all()
     
    #headings = ["Murti", "Bhoji", "Decoration", "Tent", "Music", "Flower", "Cook", "Ration", "Music"]
    if request.method == 'POST':
        selected_member_ids = request.form.getlist('bought_by')
        selected_members = Member.query.filter(Member.id.in_(selected_member_ids)).all()
        
        expense = Expense(
            event_id=request.form['event_id'],
            category_id=request.form['category_id'],
            heading=request.form['heading'],
            amount=request.form['amount'],
            notes=request.form.get('notes'),
            bought_by =selected_members
            #bought_by_id=int(request.form['bought_by']) if request.form['bought_by'] else None
        ) 
        db.session.add(expense)
        db.session.commit()
        return redirect(url_for('expenses.list_expenses'))
    return render_template('expenses/add.html', events=events, categories=CATEGORIES, members=members, expense=None)

@bp.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_expense(id):
    expense = Expense.query.get_or_404(id)
    events = Event.query.all()
    members = Member.query.all()
    
    if request.method == 'POST':
        expense.event_id = request.form['event_id']
        expense.category_id = request.form['category_id']
        expense.heading = request.form['heading']
        expense.amount = request.form['amount']
        expense.notes = request.form.get('notes')

        selected_member_ids = request.form.getlist('bought_by')  # ✅ Fixed
        selected_members = Member.query.filter(Member.id.in_(selected_member_ids)).all()
        expense.bought_by = selected_members

        db.session.commit()
        return redirect(url_for('expenses.list_expenses'))

    return render_template(
        'expenses/add.html',
        events=events,
        members=members,
        categories=CATEGORIES,
        expense=expense
    )

@bp.route('/delete/<int:id>', methods=['POST'])
@login_required
def delete_expense(id):
    expense = Expense.query.get_or_404(id)
    db.session.delete(expense)
    db.session.commit()
    return redirect(url_for('expenses.list_expenses'))
