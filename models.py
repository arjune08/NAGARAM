from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='citizen') # citizen, admin, ngo, volunteer
    phone = db.Column(db.String(20))
    avatar = db.Column(db.String(255), default='default-avatar.png')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)

    # Relationships
    complaints = db.relationship('Complaint', backref='reporter', lazy=True)
    notifications = db.relationship('Notification', backref='user', lazy=True)
    trusted_contacts = db.relationship('TrustedContact', backref='user', lazy=True)
    volunteer_profile = db.relationship('VolunteerProfile', backref='user', uselist=False)
    ngo_profile = db.relationship('NGOOrganization', backref='user', uselist=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Category(db.Model):
    __tablename__ = 'categories'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)
    icon = db.Column(db.String(50), default='alert-circle')
    color = db.Column(db.String(20), default='#3b82f6')
    description = db.Column(db.Text)
    complaints = db.relationship('Complaint', backref='category', lazy=True)


class Zone(db.Model):
    __tablename__ = 'zones'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    code = db.Column(db.String(20), unique=True)
    lat = db.Column(db.Float)
    lng = db.Column(db.Float)
    population = db.Column(db.Integer, default=50000)
    health_score = db.Column(db.Float, default=85.0)

    assets = db.relationship('InfrastructureAsset', backref='zone', lazy=True)
    complaints = db.relationship('Complaint', backref='zone', lazy=True)
    traffic_logs = db.relationship('TrafficData', backref='zone', lazy=True)


class MaintenanceTeam(db.Model):
    __tablename__ = 'maintenance_teams'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    specialty = db.Column(db.String(100))
    contact_phone = db.Column(db.String(20))
    status = db.Column(db.String(20), default='Available') # Available, On Duty, Maintenance
    current_zone_id = db.Column(db.Integer, db.ForeignKey('zones.id'))
    members_count = db.Column(db.Integer, default=5)

    complaints = db.relationship('Complaint', backref='assigned_team', lazy=True)
    tasks = db.relationship('MaintenanceTask', backref='team', lazy=True)


class InfrastructureAsset(db.Model):
    __tablename__ = 'infrastructure_assets'
    id = db.Column(db.Integer, primary_key=True)
    asset_code = db.Column(db.String(50), unique=True, nullable=False)
    name = db.Column(db.String(120), nullable=False)
    asset_type = db.Column(db.String(50), nullable=False) # Road, Bridge, Drainage, Streetlight, Building
    zone_id = db.Column(db.Integer, db.ForeignKey('zones.id'))
    lat = db.Column(db.Float, nullable=False)
    lng = db.Column(db.Float, nullable=False)
    installation_year = db.Column(db.Integer, default=2015)
    condition_score = db.Column(db.Float, default=80.0) # 0-100
    failure_risk_pct = db.Column(db.Float, default=15.0)
    risk_level = db.Column(db.String(20), default='Low') # Low, Moderate, High, Critical
    last_inspected = db.Column(db.DateTime, default=datetime.utcnow)
    next_recommended_service = db.Column(db.DateTime)

    risks = db.relationship('RiskAssessment', backref='asset', lazy=True)
    maintenance_records = db.relationship('MaintenanceRecord', backref='asset', lazy=True)
    complaints = db.relationship('Complaint', backref='asset', lazy=True)


class RiskAssessment(db.Model):
    __tablename__ = 'risk_assessments'
    id = db.Column(db.Integer, primary_key=True)
    asset_id = db.Column(db.Integer, db.ForeignKey('infrastructure_assets.id'), nullable=False)
    risk_score = db.Column(db.Float, nullable=False)
    risk_level = db.Column(db.String(20), nullable=False)
    primary_factors = db.Column(db.Text) # JSON/comma list
    recommended_action = db.Column(db.Text)
    urgency = db.Column(db.String(20), default='Medium') # Low, Medium, High, Immediate
    assessed_at = db.Column(db.DateTime, default=datetime.utcnow)


class Complaint(db.Model):
    __tablename__ = 'complaints'
    id = db.Column(db.Integer, primary_key=True)
    ticket_id = db.Column(db.String(30), unique=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)
    zone_id = db.Column(db.Integer, db.ForeignKey('zones.id'))
    asset_id = db.Column(db.Integer, db.ForeignKey('infrastructure_assets.id'), nullable=True)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=False)
    location_address = db.Column(db.String(255))
    lat = db.Column(db.Float)
    lng = db.Column(db.Float)
    photo_url = db.Column(db.String(255))
    status = db.Column(db.String(30), default='Submitted') # Submitted, Verified, Prioritized, Assigned, In Progress, Resolved, Confirmed
    priority = db.Column(db.String(20), default='Medium') # Low, Medium, High, Critical
    assigned_team_id = db.Column(db.Integer, db.ForeignKey('maintenance_teams.id'), nullable=True)
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)
    resolved_at = db.Column(db.DateTime)
    ai_risk_weight = db.Column(db.Float, default=1.0)
    citizen_feedback = db.Column(db.Text)

    updates = db.relationship('ComplaintUpdate', backref='complaint', lazy=True, cascade='all, delete-orphan')


class ComplaintUpdate(db.Model):
    __tablename__ = 'complaint_updates'
    id = db.Column(db.Integer, primary_key=True)
    complaint_id = db.Column(db.Integer, db.ForeignKey('complaints.id'), nullable=False)
    status_from = db.Column(db.String(30))
    status_to = db.Column(db.String(30), nullable=False)
    notes = db.Column(db.Text)
    updated_by = db.Column(db.String(100), default='System')
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)


class MaintenanceRecord(db.Model):
    __tablename__ = 'maintenance_records'
    id = db.Column(db.Integer, primary_key=True)
    asset_id = db.Column(db.Integer, db.ForeignKey('infrastructure_assets.id'), nullable=False)
    performed_by = db.Column(db.String(100))
    work_done = db.Column(db.Text)
    cost = db.Column(db.Float)
    date_completed = db.Column(db.DateTime, default=datetime.utcnow)


class MaintenanceTask(db.Model):
    __tablename__ = 'maintenance_tasks'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    asset_type = db.Column(db.String(50))
    location = db.Column(db.String(200))
    team_id = db.Column(db.Integer, db.ForeignKey('maintenance_teams.id'))
    priority = db.Column(db.String(20), default='Medium')
    status = db.Column(db.String(30), default='Scheduled') # Scheduled, In Progress, Completed
    scheduled_date = db.Column(db.DateTime, default=datetime.utcnow)
    estimated_hours = db.Column(db.Float, default=4.0)


class TrafficData(db.Model):
    __tablename__ = 'traffic_data'
    id = db.Column(db.Integer, primary_key=True)
    zone_id = db.Column(db.Integer, db.ForeignKey('zones.id'), nullable=False)
    congestion_index = db.Column(db.Float, default=45.0) # 0-100
    avg_speed_kmh = db.Column(db.Float, default=35.0)
    incident_count = db.Column(db.Integer, default=0)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)


class EmergencyEvent(db.Model):
    __tablename__ = 'emergency_events'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    event_type = db.Column(db.String(50)) # Severe Weather, Infrastructure Failure, Public Health, Safety
    severity = db.Column(db.String(20), default='High') # Moderate, High, Critical
    location = db.Column(db.String(200))
    description = db.Column(db.Text)
    status = db.Column(db.String(20), default='Active') # Active, Resolved
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class EmergencyService(db.Model):
    __tablename__ = 'emergency_services'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    service_type = db.Column(db.String(50)) # Hospital, Fire Station, Police, Emergency Shelter
    address = db.Column(db.String(200))
    phone = db.Column(db.String(30))
    lat = db.Column(db.Float, nullable=False)
    lng = db.Column(db.Float, nullable=False)
    available_beds = db.Column(db.Integer, default=25)


class BloodDonationRequest(db.Model):
    __tablename__ = 'blood_donation_requests'
    id = db.Column(db.Integer, primary_key=True)
    hospital_name = db.Column(db.String(120), nullable=False)
    blood_group = db.Column(db.String(10), nullable=False) # A+, O-, etc.
    units_needed = db.Column(db.Integer, default=2)
    contact_person = db.Column(db.String(100))
    contact_phone = db.Column(db.String(30))
    urgency = db.Column(db.String(20), default='High')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class NGOOrganization(db.Model):
    __tablename__ = 'ngo_organizations'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(150), nullable=False)
    registration_number = db.Column(db.String(50))
    category = db.Column(db.String(50)) # Disaster Relief, Sanitation, Environment, Health
    verification_status = db.Column(db.String(20), default='Verified') # Pending, Verified
    website = db.Column(db.String(150))
    description = db.Column(db.Text)

    initiatives = db.relationship('Initiative', backref='organization', lazy=True)


class Initiative(db.Model):
    __tablename__ = 'initiatives'
    id = db.Column(db.Integer, primary_key=True)
    ngo_id = db.Column(db.Integer, db.ForeignKey('ngo_organizations.id'), nullable=False)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text)
    target_volunteers = db.Column(db.Integer, default=10)
    current_volunteers = db.Column(db.Integer, default=0)
    location = db.Column(db.String(200))
    start_date = db.Column(db.DateTime)
    status = db.Column(db.String(20), default='Active') # Active, Completed

    tasks = db.relationship('InitiativeTask', backref='initiative', lazy=True)


class InitiativeTask(db.Model):
    __tablename__ = 'initiative_tasks'
    id = db.Column(db.Integer, primary_key=True)
    initiative_id = db.Column(db.Integer, db.ForeignKey('initiatives.id'), nullable=False)
    title = db.Column(db.String(150), nullable=False)
    required_skill = db.Column(db.String(100))
    location = db.Column(db.String(200))
    needed_volunteers = db.Column(db.Integer, default=5)
    status = db.Column(db.String(20), default='Open') # Open, Filled, Completed

    applications = db.relationship('VolunteerApplication', backref='task', lazy=True)


class VolunteerProfile(db.Model):
    __tablename__ = 'volunteer_profiles'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    skills = db.Column(db.Text) # Comma-separated
    interests = db.Column(db.Text)
    availability = db.Column(db.String(100), default='Weekends')
    preferred_location = db.Column(db.String(100))
    completed_hours = db.Column(db.Integer, default=12)

    applications = db.relationship('VolunteerApplication', backref='volunteer', lazy=True)


class VolunteerApplication(db.Model):
    __tablename__ = 'volunteer_applications'
    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.Integer, db.ForeignKey('initiative_tasks.id'), nullable=False)
    volunteer_id = db.Column(db.Integer, db.ForeignKey('volunteer_profiles.id'), nullable=False)
    status = db.Column(db.String(20), default='Pending') # Pending, Accepted, Completed
    applied_at = db.Column(db.DateTime, default=datetime.utcnow)


class SustainabilityIndicator(db.Model):
    __tablename__ = 'sustainability_indicators'
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(50), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50), nullable=False) # Energy, Water, Waste, Mobility, Air Quality, Green Cover
    value = db.Column(db.Float, nullable=False)
    target = db.Column(db.Float, nullable=False)
    unit = db.Column(db.String(20))
    score = db.Column(db.Float, default=80.0) # Normalized score out of 100


class Scenario(db.Model):
    __tablename__ = 'scenarios'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    scenario_type = db.Column(db.String(50)) # Road Closure, Infrastructure Mod, Traffic Reroute, Emergency
    description = db.Column(db.Text)
    parameters = db.Column(db.Text) # JSON string
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    effects = db.relationship('ScenarioEffect', backref='scenario', lazy=True)


class ScenarioEffect(db.Model):
    __tablename__ = 'scenario_effects'
    id = db.Column(db.Integer, primary_key=True)
    scenario_id = db.Column(db.Integer, db.ForeignKey('scenarios.id'), nullable=False)
    metric_name = db.Column(db.String(100), nullable=False)
    baseline_value = db.Column(db.String(50))
    predicted_value = db.Column(db.String(50))
    change_pct = db.Column(db.Float)
    impact_level = db.Column(db.String(20), default='Moderate') # Positive, Low, Moderate, Severe


class TrustedContact(db.Model):
    __tablename__ = 'trusted_contacts'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    relationship = db.Column(db.String(50))
    phone = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(120))


class Notification(db.Model):
    __tablename__ = 'notifications'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(150), nullable=False)
    message = db.Column(db.Text, nullable=False)
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class AuditLog(db.Model):
    __tablename__ = 'audit_logs'
    id = db.Column(db.Integer, primary_key=True)
    admin_name = db.Column(db.String(100), nullable=False)
    action = db.Column(db.String(100), nullable=False)
    details = db.Column(db.Text)
    ip_address = db.Column(db.String(50), default='127.0.0.1')
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)


class Resource(db.Model):
    __tablename__ = 'resources'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    resource_type = db.Column(db.String(50)) # Equipment, Vehicle, Crew Material
    total_quantity = db.Column(db.Integer, default=10)
    available_quantity = db.Column(db.Integer, default=7)
    location_zone = db.Column(db.String(100))
    condition = db.Column(db.String(20), default='Good')
