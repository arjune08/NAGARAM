from datetime import datetime
from models import db

class FarmerProfile(db.Model):
    __tablename__ = 'farmer_profiles'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True, nullable=False)
    village = db.Column(db.String(120), default='Demo Gram')
    district = db.Column(db.String(120))
    preferred_language = db.Column(db.String(20), default='en')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Farm(db.Model):
    __tablename__ = 'farms'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    name = db.Column(db.String(120), nullable=False)
    location = db.Column(db.String(200))
    area_acres = db.Column(db.Float, default=0)
    soil_type = db.Column(db.String(80))
    irrigation_type = db.Column(db.String(80))
    current_crop = db.Column(db.String(80))
    crop_stage = db.Column(db.String(80))
    water_availability = db.Column(db.String(30), default='Medium')
    risk_score = db.Column(db.Float, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class FarmIssue(db.Model):
    __tablename__ = 'farm_issues'
    id = db.Column(db.Integer, primary_key=True)
    ticket_id = db.Column(db.String(30), unique=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    farm_id = db.Column(db.Integer, db.ForeignKey('farms.id'))
    category = db.Column(db.String(80), nullable=False)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=False)
    priority = db.Column(db.String(20), default='Medium')
    status = db.Column(db.String(30), default='Reported')
    photo_url = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Recommendation(db.Model):
    __tablename__ = 'farm_recommendations'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    farm_id = db.Column(db.Integer, db.ForeignKey('farms.id'))
    action = db.Column(db.String(255), nullable=False)
    priority = db.Column(db.String(20), nullable=False)
    reason = db.Column(db.Text, nullable=False)
    data_sources = db.Column(db.String(255), default='Available farm data')
    suggested_time = db.Column(db.String(80), default='Today')
    confidence = db.Column(db.Float, default=0.5)
    status = db.Column(db.String(30), default='Recommended')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class FarmRecord(db.Model):
    __tablename__ = 'farm_records'
    id = db.Column(db.Integer, primary_key=True)
    farm_id = db.Column(db.Integer, db.ForeignKey('farms.id'), nullable=False)
    record_type = db.Column(db.String(80), nullable=False)
    note = db.Column(db.Text, nullable=False)
    amount = db.Column(db.Float)
    recorded_at = db.Column(db.DateTime, default=datetime.utcnow)
