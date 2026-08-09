import os
import random
from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from auth import role_required
from models import db, Complaint, ComplaintUpdate, Category, Zone, EmergencyService, BloodDonationRequest, Initiative
from werkzeug.utils import secure_filename

citizen_bp = Blueprint('citizen', __name__)

@citizen_bp.route('/dashboard')
@login_required
@role_required('citizen')
def dashboard():
    user_complaints = Complaint.query.filter_by(user_id=current_user.id).order_by(Complaint.submitted_at.desc()).all()
    active_count = len([c for c in user_complaints if c.status not in ['Resolved', 'Confirmed']])
    resolved_count = len([c for c in user_complaints if c.status in ['Resolved', 'Confirmed']])

    emergency_services = EmergencyService.query.limit(4).all()
    initiatives = Initiative.query.limit(3).all()

    return render_template(
        'citizen/dashboard.html',
        user_complaints=user_complaints,
        active_count=active_count,
        resolved_count=resolved_count,
        emergency_services=emergency_services,
        initiatives=initiatives
    )

@citizen_bp.route('/report', methods=['GET', 'POST'])
@login_required
@role_required('citizen')
def report_issue():
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        category_id = request.form.get('category_id')
        zone_id = request.form.get('zone_id')
        description = request.form.get('description', '').strip()
        address = request.form.get('address', '').strip()
        priority = request.form.get('priority', 'Medium')
        lat = request.form.get('lat', 40.7128)
        lng = request.form.get('lng', -74.0060)

        photo_filename = None
        if 'photo' in request.files:
            file = request.files['photo']
            if file and file.filename != '':
                filename = secure_filename(f"complaint_{current_user.id}_{int(datetime.utcnow().timestamp())}.jpg")
                upload_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
                file.save(upload_path)
                photo_filename = filename

        tkt_id = f"TKT-2026-{random.randint(2000, 9999)}"

        complaint = Complaint(
            ticket_id=tkt_id,
            user_id=current_user.id,
            category_id=int(category_id),
            zone_id=int(zone_id) if zone_id else 1,
            title=title,
            description=description,
            location_address=address,
            priority=priority,
            lat=float(lat),
            lng=float(lng),
            photo_url=photo_filename,
            status='Submitted',
            ai_risk_weight=round(random.uniform(1.1, 4.5), 2)
        )
        db.session.add(complaint)
        db.session.commit()

        update = ComplaintUpdate(
            complaint_id=complaint.id,
            status_from='',
            status_to='Submitted',
            notes='Report submitted by citizen via UrbanPulse AI Portal',
            updated_by=current_user.full_name
        )
        db.session.add(update)
        db.session.commit()

        flash(f'Infrastructure issue reported successfully! Ticket ID: {tkt_id}', 'success')
        return redirect(url_for('citizen.my_complaints'))

    categories = Category.query.all()
    zones = Zone.query.all()
    return render_template('citizen/report_issue.html', categories=categories, zones=zones)

@citizen_bp.route('/my-complaints')
@login_required
@role_required('citizen')
def my_complaints():
    complaints = Complaint.query.filter_by(user_id=current_user.id).order_by(Complaint.submitted_at.desc()).all()
    return render_template('citizen/my_complaints.html', complaints=complaints)

@citizen_bp.route('/complaint/<int:id>')
@login_required
@role_required('citizen')
def complaint_detail(id):
    complaint = Complaint.query.get_or_404(id)
    if complaint.user_id != current_user.id and current_user.role != 'admin':
        flash('Unauthorized access to this complaint ticket.', 'danger')
        return redirect(url_for('citizen.my_complaints'))

    return render_template('citizen/complaint_detail.html', complaint=complaint)

@citizen_bp.route('/complaint/<int:id>/confirm', methods=['POST'])
@login_required
@role_required('citizen')
def confirm_resolution(id):
    complaint = Complaint.query.get_or_404(id)
    if complaint.user_id != current_user.id:
        flash('Unauthorized.', 'danger')
        return redirect(url_for('citizen.my_complaints'))

    feedback = request.form.get('feedback', '')
    complaint.status = 'Confirmed'
    complaint.citizen_feedback = feedback

    update = ComplaintUpdate(
        complaint_id=complaint.id,
        status_from='Resolved',
        status_to='Confirmed',
        notes='Citizen confirmed resolution and provided feedback.',
        updated_by=current_user.full_name
    )
    db.session.add(update)
    db.session.commit()

    flash('Thank you for confirming resolution!', 'success')
    return redirect(url_for('citizen.complaint_detail', id=complaint.id))

@citizen_bp.route('/map')
@login_required
@role_required('citizen')
def city_map():
    complaints = Complaint.query.filter(Complaint.status != 'Confirmed').all()
    emergency_services = EmergencyService.query.all()
    zones = Zone.query.all()
    return render_template('citizen/city_map.html', complaints=complaints, emergency_services=emergency_services, zones=zones)

@citizen_bp.route('/emergency')
@login_required
@role_required('citizen')
def emergency():
    services = EmergencyService.query.all()
    blood_requests = BloodDonationRequest.query.order_by(BloodDonationRequest.created_at.desc()).all()
    return render_template('citizen/emergency.html', services=services, blood_requests=blood_requests)

@citizen_bp.route('/community')
@login_required
@role_required('citizen')
def community():
    initiatives = Initiative.query.all()
    return render_template('citizen/community.html', initiatives=initiatives)
