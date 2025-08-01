from flask import Blueprint, render_template, request, redirect, url_for,flash,Response,make_response,jsonify
from ..models import db, Member
from datetime import date
from io import TextIOWrapper
from io import StringIO,BytesIO
import csv
from weasyprint import HTML
from flask_login import login_required, current_user

bp = Blueprint('members', __name__, url_prefix='/members')

@bp.route('/')
@login_required
def list_members():
    page = request.args.get('page', 1, type=int)
    pagination = Member.query.order_by(Member.order).paginate(page=page, per_page=60)
    members = pagination.items
    return render_template('members/list.html', members=members, pagination=pagination)


@bp.route('/update-order', methods=['POST'])
@login_required
def update_order():
    data = request.get_json()
    for item in data:
        member = Member.query.get(int(item['id']))
        if member:
            member.order = item['order']
    db.session.commit()
    return jsonify({'status': 'success'})


@bp.route('/download')
@login_required
def download_members():
    members = Member.query.order_by(Member.id).all()

    si = StringIO()
    writer = csv.writer(si)
    
    # Header row
    writer.writerow(['ID', 'Name', 'Phone', 'Address'])
    
    # Data rows
    for m in members:
        writer.writerow([
            m.id,
            m.name,
            m.phone
            
        ])
    
    output = si.getvalue()
    si.close()
    
    return Response(
        output,
        mimetype='text/csv',
        headers={"Content-Disposition": "attachment;filename=members.csv"}
    )
@login_required
@bp.route('/download-pdf')
def download_members_pdf():
    members = Member.query.order_by(Member.id).all()
    rendered_html = render_template('members/pdf.html', members=members)

    pdf_io = BytesIO()
    HTML(string=rendered_html).write_pdf(pdf_io)
    pdf_io.seek(0)

    response = make_response(pdf_io.read())
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'attachment; filename=members.pdf'
    return response

@bp.route('/add', methods=['GET', 'POST'])
@login_required
def add_member():
    if request.method == 'POST':
        member = Member(
            name=request.form['name'],
            phone=request.form['phone'],
            address=request.form['address'],
            status=request.form['status'],
            joining_date=request.form['joining_date']
        )
        db.session.add(member)
        db.session.commit()
        return redirect(url_for('members.list_members'))
    return render_template('members/add.html', current_date=date.today().isoformat())

@bp.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_member(id):
    member = Member.query.get_or_404(id)
    if request.method == 'POST':
        member.name = request.form['name']
        member.phone = request.form['phone']
        member.address = request.form['address']
        member.status = request.form['status']
        member.joining_date = request.form['joining_date']
        db.session.commit()
        return redirect(url_for('members.list_members'))
    return render_template('members/edit.html', member=member)

@bp.route('/delete/<int:id>')
@login_required
def delete_member(id):
    member = Member.query.get_or_404(id)
    db.session.delete(member)
    db.session.commit()
    return redirect(url_for('members.list_members'))

@bp.route('/upload', methods=['GET', 'POST'])
@login_required
def upload_members():
    if request.method == 'POST':
        file = request.files['csv_file']
        if not file.filename.endswith('.csv'):
            flash('Please upload a valid CSV file.', 'danger')
            return redirect(request.url)

        stream = TextIOWrapper(file.stream, encoding='utf-8')
        csv_reader = csv.DictReader(stream)

        count = 0
        for row in csv_reader:
            member = Member(
                name=row['name'],
                phone=row.get('phone'),
                address=row.get('address'),
                status=row.get('status', 'Active')
            )
            db.session.add(member)
            count += 1

        db.session.commit()
        flash(f'{count} members uploaded successfully!', 'success')
        return redirect(url_for('members.list_members'))

    return render_template('members/upload.html')