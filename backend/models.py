from . import db
from datetime import date
from sqlalchemy import func
from flask_login import UserMixin

class Users(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # 'admin' or 'staff'

# Association Table for Many-to-Many relation between Expense and Member
expense_members = db.Table('expense_members',
    db.Column('expense_id', db.Integer, db.ForeignKey('expense.id'), primary_key=True),
    db.Column('member_id', db.Integer, db.ForeignKey('member.id'), primary_key=True)
)

class Member(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20))
    address = db.Column(db.String(200))
    status = db.Column(db.String(20), default='Active')
    joining_date = db.Column(db.Date, default=date.today)
    order = db.Column(db.Integer, default=0)


class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    date = db.Column(db.Date, nullable=False)
    location = db.Column(db.String(200))
    description = db.Column(db.Text)
    
    # Relationships
    chandas = db.relationship('Chanda', backref='event', lazy='dynamic')
    expenses = db.relationship('Expense', backref='event', lazy='dynamic')
    guest_payments = db.relationship('GuestPayment', backref='event', lazy='dynamic')
    bank_transactions = db.relationship('BankTransaction', backref='event', lazy='dynamic')

    # Computed Properties
    @property
    def member_collection(self):
        return db.session.query(func.sum(Chanda.own_payment))\
            .filter(Chanda.event_id == self.id, Chanda.member_id.isnot(None)).scalar() or 0

    @property
    def guest_collection(self):
        return db.session.query(func.sum(GuestPayment.amount))\
            .filter(GuestPayment.event_id == self.id).scalar() or 0

    @property
    def book_collection(self):
        return db.session.query(func.sum(Chanda.collected_amount))\
            .filter(Chanda.event_id == self.id, Chanda.member_id.isnot(None)).scalar() or 0

    @property
    def total_collection(self):
        return self.member_collection + self.guest_collection + self.book_collection

    @property
    def total_expenses(self):
        return sum(e.amount for e in self.expenses)

    @property
    def balance(self):
        return self.total_collection - self.total_expenses
    
    @property
    def expense_totals_by_category(self):
        from constants import CATEGORIES

        return {
            cname: db.session.query(func.sum(Expense.amount))
                .filter(Expense.category_id == cid, Expense.event_id == self.id)
                .scalar() or 0
            for cid, cname in CATEGORIES.items()
        }
        
    @property
    def bank_summary(self):
        banktr = BankTransaction.query.filter_by(event_id=self.id).first()
        if banktr:
            return {
                'withdrawal': banktr.withdrawal_amount or 0,
                'balance': banktr.balance_amount or 0,
                'interest': banktr.interest_amount or 0
            }
        else:
            return {
                'withdrawal': 0,
                'balance': 0,
                'interest': 0
            }

class Chanda(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'), nullable=False)
    member_id = db.Column(db.Integer, db.ForeignKey('member.id'), nullable=False)
    own_payment = db.Column(db.Float, default=0.0)
    collected_amount = db.Column(db.Float, default=0.0)

    member = db.relationship('Member', backref=db.backref('chandas', lazy='dynamic'))
    

class Guest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(15))
    address = db.Column(db.String(200))
    
    payments = db.relationship('GuestPayment', back_populates='guest')


class GuestPayment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    guest_id = db.Column(db.Integer, db.ForeignKey('guest.id'), nullable=False)
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    
    guest = db.relationship('Guest', back_populates='payments')


class Expense(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'), nullable=False)
    category_id = db.Column(db.Integer, nullable=False)
    heading = db.Column(db.String(100), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    notes = db.Column(db.String(200))

    bought_by = db.relationship('Member', secondary=expense_members, backref=db.backref('expenses_bought', lazy='select'))


class BankTransaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'), nullable=False)
    transaction_date = db.Column(db.Date, default=date.today)
    withdrawal_amount = db.Column(db.Float, default=0.0)
    interest_amount = db.Column(db.Float, default=0.0)
    balance_amount = db.Column(db.Float, default=0.0)
    remark = db.Column(db.String(200))
