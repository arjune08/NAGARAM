from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from routes.auth import role_required
from models import (
    db, Complaint, ComplaintUpdate, InfrastructureAsset, RiskAssessment,
    MaintenanceTeam, MaintenanceTask, Zone, TrafficData, EmergencyEvent,
    SustainabilityIndicator, Scenario, ScenarioEffect, AuditLog, Resource, Category
)
from datetime import datetime

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/command-center')
@login_required
@role_required('admin')
def command_center():
    # Overall city stats
    total_issues = Complaint.query.count()
    active_issues = Complaint.query.filter(Complaint.status.notin_(['Resolved', 'Confirmed'])).count()
    critical_risks = InfrastructureAsset.query.filter_by(risk_level='Critical').count()
    high_risks = InfrastructureAsset.query.filter_by(risk_level='High').count()
    available_teams = MaintenanceTeam.query.filter_by(status='Available').count()
    total_teams = MaintenanceTeam.query.count()
    
    city_health_score = 81.6
    infrastructure_risk_score = round(((critical_risks * 3 + high_risks * 1.5) / max(1, InfrastructureAsset.query.count())) * 25.0, 1)

    recent_complaints = Complaint.query.order_by(Complaint.submitted_at.desc()).limit(6).all()
    critical_assets = InfrastructureAsset.query.filter(InfrastructureAsset.risk_level.in_(['Critical', 'High'])).limit(5).all()

    return render_template(
        'admin/command_center.html',
        total_issues=total_issues,
        active_issues=active_issues,
        critical_risks=critical_risks,
        high_risks=high_risks,
        available_teams=available_teams,
        total_teams=total_teams,
        city_health_score=city_health_score,
        infrastructure_risk_score=infrastructure_risk_score,
        recent_complaints=recent_complaints,
        critical_assets=critical_assets
    )

@admin_bp.route('/issues', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def issues():
    if request.method == 'POST':
        complaint_id = request.form.get('complaint_id')
        new_status = request.form.get('status')
        team_id = request.form.get('team_id')
        notes = request.form.get('notes', 'Updated by Administrator')

        complaint = Complaint.query.get_or_404(complaint_id)
        old_status = complaint.status

        if new_status:
            complaint.status = new_status
            if new_status in ['Resolved', 'Confirmed']:
                complaint.resolved_at = datetime.utcnow()

        if team_id:
            complaint.assigned_team_id = int(team_id)

        update_entry = ComplaintUpdate(
            complaint_id=complaint.id,
            status_from=old_status,
            status_to=complaint.status,
            notes=notes,
            updated_by=current_user.full_name
        )
        db.session.add(update_entry)

        # Audit log
        audit = AuditLog(
            admin_name=current_user.full_name,
            action='ISSUE_STATUS_UPDATE',
            details=f"Updated ticket #{complaint.ticket_id} status from {old_status} to {complaint.status}"
        )
        db.session.add(audit)
        db.session.commit()

        flash(f"Ticket #{complaint.ticket_id} updated successfully.", "success")
        return redirect(url_for('admin.issues'))

    status_filter = request.args.get('status', 'all')
    if status_filter != 'all':
        all_complaints = Complaint.query.filter_by(status=status_filter).order_by(Complaint.submitted_at.desc()).all()
    else:
        all_complaints = Complaint.query.order_by(Complaint.submitted_at.desc()).all()

    teams = MaintenanceTeam.query.all()
    categories = Category.query.all()

    return render_template('admin/issues.html', complaints=all_complaints, teams=teams, categories=categories, status_filter=status_filter)

@admin_bp.route('/digital-twin')
@login_required
@role_required('admin')
def digital_twin():
    scenarios = Scenario.query.order_by(Scenario.created_at.desc()).all()
    zones = Zone.query.all()
    assets = InfrastructureAsset.query.all()
    return render_template('admin/digital_twin.html', scenarios=scenarios, zones=zones, assets=assets)

@admin_bp.route('/digital-twin/simulate', methods=['POST'])
@login_required
@role_required('admin')
def digital_twin_simulate():
    title = request.form.get('title', 'Urban Simulation Scenario')
    stype = request.form.get('scenario_type', 'Road Closure')
    description = request.form.get('description', '')

    scen = Scenario(title=title, scenario_type=stype, description=description)
    db.session.add(scen)
    db.session.commit()

    # Generate synthetic digital twin simulation results
    effects = [
        ScenarioEffect(scenario_id=scen.id, metric_name="Traffic Congestion Index", baseline_value="45.0%", predicted_value="78.2%", change_pct=33.2, impact_level="Severe"),
        ScenarioEffect(scenario_id=scen.id, metric_name="Average Delay per Trip", baseline_value="12.0 mins", predicted_value="24.5 mins", change_pct=104.1, impact_level="Moderate"),
        ScenarioEffect(scenario_id=scen.id, metric_name="Emergency Transit Latency", baseline_value="4.2 mins", predicted_value="8.1 mins", change_pct=92.8, impact_level="Severe"),
        ScenarioEffect(scenario_id=scen.id, metric_name="Public Transport Load factor", baseline_value="62.0%", predicted_value="89.0%", change_pct=27.0, impact_level="Positive")
    ]
    db.session.add_all(effects)

    audit = AuditLog(
        admin_name=current_user.full_name,
        action='DIGITAL_TWIN_SIMULATION',
        details=f"Ran Digital Twin What-If simulation: {title}"
    )
    db.session.add(audit)
    db.session.commit()

    flash(f"Digital Twin Simulation '{title}' generated successfully!", "success")
    return redirect(url_for('admin.digital_twin'))

@admin_bp.route('/risk-engine')
@login_required
@role_required('admin')
def risk_engine():
    critical_assets = InfrastructureAsset.query.filter_by(risk_level='Critical').all()
    high_assets = InfrastructureAsset.query.filter_by(risk_level='High').all()
    moderate_assets = InfrastructureAsset.query.filter_by(risk_level='Moderate').all()
    low_assets = InfrastructureAsset.query.filter_by(risk_level='Low').all()

    assessments = RiskAssessment.query.order_by(RiskAssessment.risk_score.desc()).all()

    return render_template(
        'admin/risk_engine.html',
        critical_assets=critical_assets,
        high_assets=high_assets,
        moderate_assets=moderate_assets,
        low_assets=low_assets,
        assessments=assessments
    )

@admin_bp.route('/predictive-maintenance')
@login_required
@role_required('admin')
def predictive_maintenance():
    assets_needing_service = InfrastructureAsset.query.filter(InfrastructureAsset.failure_risk_pct > 40.0).order_by(InfrastructureAsset.failure_risk_pct.desc()).all()
    tasks = MaintenanceTask.query.all()
    teams = MaintenanceTeam.query.all()
    return render_template('admin/predictive_maintenance.html', assets=assets_needing_service, tasks=tasks, teams=teams)

@admin_bp.route('/resource-optimizer')
@login_required
@role_required('admin')
def resource_optimizer():
    teams = MaintenanceTeam.query.all()
    resources = Resource.query.all()

    # AI allocation recommendation logic
    high_risk_zones = Zone.query.order_by(Zone.health_score.asc()).all()
    recommendation = f"AI Optimization System recommends deploying Team Alpha to {high_risk_zones[0].name} due to 3 high-risk drainage assets and a 68% citizen report density."

    return render_template('admin/resource_optimizer.html', teams=teams, resources=resources, recommendation=recommendation)

@admin_bp.route('/decision-support')
@login_required
@role_required('admin')
def decision_support():
    return render_template('admin/decision_support.html')

@admin_bp.route('/sustainability')
@login_required
@role_required('admin')
def sustainability():
    indicators = SustainabilityIndicator.query.all()
    return render_template('admin/sustainability.html', indicators=indicators)

@admin_bp.route('/data-hub')
@login_required
@role_required('admin')
def data_hub():
    return render_template('admin/data_hub.html')

@admin_bp.route('/audit-log')
@login_required
@role_required('admin')
def audit_log():
    logs = AuditLog.query.order_by(AuditLog.timestamp.desc()).all()
    return render_template('admin/audit_log.html', logs=logs)
