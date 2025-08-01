from flask import Blueprint, render_template, request, make_response, url_for, current_app
from weasyprint import HTML
from backend.models import Event,Member

bp = Blueprint('skosdoc', __name__, url_prefix='/letters')
from datetime import datetime

current_date = datetime.today().strftime('%d-%m-%Y')

# Police Permission Letter
@bp.route('/police', methods=['GET', 'POST'])
def generate_police_letter():
    events = Event.query.all()
    members = Member.query.all()
    if request.method == 'POST':
        event_id = request.form.get('event_id')
        station_name = request.form.get('station_name')
        venue_name =   request.form.get('venue_name')
        current_subject = request.form.get('current_subject')
        other_name = request.form.get('other_name')
        event = Event.query.get(event_id)
       

        rendered_html = render_template(
            'documents/police_letter.html',
            event=event,
            station_name=station_name,venue_name=venue_name,
            current_date=current_date,current_subject=current_subject,other_name=other_name,
            org_name="ShreeKhetra Odia Samaj",
            logo_url=url_for('static', filename='images/logo.png', _external=True)
        )
        pdf = HTML(string=rendered_html, base_url=current_app.root_path).write_pdf()
        response = make_response(pdf)
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = 'inline; filename=police_letter.pdf'
        return response

    return render_template('documents/form_police_letter.html', events=events,members=members)

# Chief Guest Invitation Letter
@bp.route('/chiefguest', methods=['GET', 'POST'])
def generate_chiefguest_letter():
    events = Event.query.all()

    if request.method == 'POST':
        event_id = request.form.get('event_id')
        guest_name = request.form.get('guest_name')
        event = Event.query.get(event_id)

        rendered_html = render_template(
            'documents/guest_letter.html',
            event=event,
            guest_name=guest_name,
            org_name="ShreeKhetra Odia Samaj",
            logo_url=url_for('static', filename='images/logo.png', _external=True)
        )
        pdf = HTML(string=rendered_html, base_url=current_app.root_path).write_pdf()
        response = make_response(pdf)
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = 'inline; filename=guest_letter.pdf'
        return response

    return render_template('documents/form_guest_letter.html', events=events)

# Electricity Department Letter
@bp.route('/electricity', methods=['GET', 'POST'])
def generate_electricity_letter():
    events = Event.query.all()

    if request.method == 'POST':
        event_id = request.form.get('event_id')
        office_name = request.form.get('office_name')
        event = Event.query.get(event_id)

        rendered_html = render_template(
            'documents/electricity_letter.html',
            event=event,
            office_name=office_name,
            org_name="ShreeKhetra Odia Samaj",
            logo_url=url_for('static', filename='images/logo.png', _external=True)
        )
        pdf = HTML(string=rendered_html, base_url=current_app.root_path).write_pdf()
        response = make_response(pdf)
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = 'inline; filename=electricity_letter.pdf'
        return response

    return render_template('documents/form_electricity_letter.html', events=events)
