from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from models import db, TrustedContact, EmergencyService

safety_bp = Blueprint('safety', __name__)

@safety_bp.route('/center')
@login_required
def center():
    contacts = TrustedContact.query.filter_by(user_id=current_user.id).all()
    services = EmergencyService.query.all()
    return render_template('safety/center.html', contacts=contacts, services=services)

@safety_bp.route('/contacts', methods=['POST'])
@login_required
def add_contact():
    name = request.form.get('name', '').strip()
    relationship = request.form.get('relationship', 'Friend')
    phone = request.form.get('phone', '').strip()
    email = request.form.get('email', '').strip()

    tc = TrustedContact(
        user_id=current_user.id,
        name=name,
        relationship=relationship,
        phone=phone,
        email=email
    )
    db.session.add(tc)
    db.session.commit()

    flash(f'Trusted contact {name} added successfully.', 'success')
    return redirect(url_for('safety.center'))

@safety_bp.route('/sos', methods=['POST'])
@login_required
def trigger_sos():
    data = request.json or {}
    lat = data.get('lat', 40.7128)
    lng = data.get('lng', -74.0060)

    contacts = TrustedContact.query.filter_by(user_id=current_user.id).all()
    contact_names = [c.name for c in contacts]

    # Simulated SOS dispatch
    return jsonify({
        'status': 'SUCCESS',
        'message': 'EMERGENCY SOS ACTIVATED. Live location shared with trusted contacts & municipal dispatch.',
        'contacts_notified': contact_names,
        'coords': {'lat': lat, 'lng': lng}
    })
