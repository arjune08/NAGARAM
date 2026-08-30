from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from models import db, Notification
from farmer_models import FarmerProfile, Farm, FarmIssue, Recommendation, FarmRecord

farmer_bp = Blueprint('farmer', __name__)

def farmer_required(view):
    from functools import wraps
    @wraps(view)
    def wrapped(*args, **kwargs):
        if current_user.role not in ('farmer', 'admin'):
            flash('This workspace is available to farmer accounts.', 'warning')
            return redirect(url_for('main.workspace'))
        return view(*args, **kwargs)
    return wrapped

def ensure_demo_farm(user):
    farm = Farm.query.filter_by(user_id=user.id).first()
    if not farm:
        farm = Farm(user_id=user.id, name='Demo Farm', location='Demo Gram', area_acres=2.4, soil_type='Loam', irrigation_type='Drip', current_crop='Tomato', crop_stage='Flowering', water_availability='Medium', risk_score=64)
        db.session.add(farm); db.session.flush()
    if not Recommendation.query.filter_by(user_id=user.id).first():
        rows = [
            ('Inspect tomato plants for possible pest symptoms','High','Regional reports and crop stage indicate a possible increased risk.','Regional reports, Crop stage, Weather conditions','Today',0.78),
            ('Consider delaying irrigation','Medium','Rain probability in the demo scenario is elevated, so immediate irrigation may be unnecessary.','Weather scenario, Water availability, Irrigation history','Within 24 hours',0.72),
            ('Compare nearby buyer offers','Opportunity','Available demo offers may improve estimated net realization after transport costs.','Market prices, Buyer demand','This week',0.68),
        ]
        for action,priority,reason,sources,timing,confidence in rows:
            db.session.add(Recommendation(user_id=user.id,farm_id=farm.id,action=action,priority=priority,reason=reason,data_sources=sources,suggested_time=timing,confidence=confidence))
    db.session.commit()
    return farm

@farmer_bp.route('/dashboard')
@login_required
@farmer_required
def dashboard():
    farm = ensure_demo_farm(current_user)
    recommendations = Recommendation.query.filter_by(user_id=current_user.id).order_by(Recommendation.id).all()
    issues = FarmIssue.query.filter_by(user_id=current_user.id).order_by(FarmIssue.created_at.desc()).limit(5).all()
    return render_template('farmer_dashboard.html', farm=farm, recommendations=recommendations, issues=issues)

@farmer_bp.route('/farms', methods=['GET','POST'])
@login_required
@farmer_required
def farms():
    if request.method == 'POST':
        name = request.form.get('name','').strip()
        if not name:
            flash('Farm name is required.', 'danger')
        else:
            db.session.add(Farm(user_id=current_user.id,name=name,location=request.form.get('location','').strip(),area_acres=float(request.form.get('area_acres') or 0),soil_type=request.form.get('soil_type',''),irrigation_type=request.form.get('irrigation_type',''),current_crop=request.form.get('current_crop',''),crop_stage=request.form.get('crop_stage',''),water_availability=request.form.get('water_availability','Medium')))
            db.session.commit(); flash('Farm added successfully.', 'success')
            return redirect(url_for('farmer.farms'))
    return render_template('farmer_farms.html', farms=Farm.query.filter_by(user_id=current_user.id).all())

@farmer_bp.route('/issue', methods=['GET','POST'])
@login_required
@farmer_required
def report_issue():
    farms = Farm.query.filter_by(user_id=current_user.id).all()
    if request.method == 'POST':
        title=request.form.get('title','').strip(); description=request.form.get('description','').strip()
        if not title or not description:
            flash('Please add both a title and description.', 'danger')
        else:
            issue=FarmIssue(ticket_id=f'AG-{datetime.utcnow().strftime("%y%m%d%H%M%S")}',user_id=current_user.id,farm_id=request.form.get('farm_id') or None,category=request.form.get('category','Other'),title=title,description=description,priority=request.form.get('priority','Medium'))
            db.session.add(issue); db.session.add(Notification(user_id=current_user.id,title='Farm issue reported',message=f'{title} has entered the shared action workflow.'))
            db.session.commit(); flash('Agricultural issue reported and added to the action workflow.', 'success')
            return redirect(url_for('farmer.dashboard'))
    return render_template('farmer_issue.html', farms=farms)

@farmer_bp.route('/market')
@login_required
@farmer_required
def market():
    offers=[{'buyer':'Demo Fresh Produce Co.','price':26,'distance':8,'pickup':'Yes','quantity':'1,000 kg'},{'buyer':'Regional FPO Hub','price':25,'distance':3,'pickup':'Collection point','quantity':'800 kg'},{'buyer':'Metro Wholesale','price':28,'distance':31,'pickup':'No','quantity':'1,500 kg'}]
    return render_template('farmer_market.html', offers=offers)

@farmer_bp.route('/health')
@login_required
@farmer_required
def health():
    return render_template('farmer_health.html')

@farmer_bp.route('/scenario', methods=['POST'])
@login_required
@farmer_required
def scenario():
    data=request.get_json(silent=True) or {}
    rain=max(0,min(100,float(data.get('rain_probability',20))))
    weather_risk=round(20+rain*0.65)
    disease_risk=round(18+rain*0.55)
    water_action='Consider delaying irrigation' if rain>=55 else 'Continue planned irrigation and monitor soil moisture'
    recs=Recommendation.query.filter_by(user_id=current_user.id).all()
    for rec in recs:
        if 'irrigation' in rec.action.lower(): rec.reason=f'Rain probability is now {rain:.0f}% in this DEMO scenario; {"delaying irrigation may reduce unnecessary water use" if rain>=55 else "rainfall is less likely, so follow the planned schedule while monitoring moisture"}.'
    db.session.add(Notification(user_id=current_user.id,title='Farm scenario updated',message=f'DEMO scenario updated: rain probability {rain:.0f}%. Recommendations were recalculated.'))
    db.session.commit()
    return jsonify({'rain_probability':rain,'weather_risk':weather_risk,'disease_risk':disease_risk,'water_action':water_action,'note':'DEMO DATA — prototype connected decision model'})

@farmer_bp.route('/recommendations/<int:recommendation_id>/done', methods=['POST'])
@login_required
@farmer_required
def mark_done(recommendation_id):
    rec=Recommendation.query.filter_by(id=recommendation_id,user_id=current_user.id).first_or_404()
    rec.status='Done'; db.session.commit()
    return jsonify({'ok':True,'status':'Done'})
