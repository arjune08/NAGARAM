import os
from datetime import datetime, timedelta
import random
from app import create_app
from models import (
    db, User, Category, Zone, MaintenanceTeam, InfrastructureAsset,
    RiskAssessment, Complaint, ComplaintUpdate, MaintenanceRecord,
    MaintenanceTask, TrafficData, EmergencyEvent, EmergencyService,
    BloodDonationRequest, NGOOrganization, Initiative, InitiativeTask,
    VolunteerProfile, VolunteerApplication, SustainabilityIndicator,
    Scenario, ScenarioEffect, TrustedContact, Notification, AuditLog, Resource
)

def seed_database():
    app = create_app()
    with app.app_context():
        db.create_all()

        print("--- Seeding Users ---")
        admin = User(
            full_name="Dr. Elena Vance (City Administrator)",
            email="admin@urbanpulse.ai",
            role="admin",
            phone="+1 (555) 019-2831"
        )
        admin.set_password("admin123")

        citizen = User(
            full_name="Marcus Aurelius Sterling",
            email="citizen@urbanpulse.ai",
            role="citizen",
            phone="+1 (555) 014-9982"
        )
        citizen.set_password("citizen123")

        ngo_user = User(
            full_name="Amara Okafor (CleanCity Alliance)",
            email="ngo@urbanpulse.ai",
            role="ngo",
            phone="+1 (555) 018-3341"
        )
        ngo_user.set_password("ngo123")

        volunteer_user = User(
            full_name="David Chen",
            email="volunteer@urbanpulse.ai",
            role="volunteer",
            phone="+1 (555) 012-7743"
        )
        volunteer_user.set_password("volunteer123")

        db.session.add_all([admin, citizen, ngo_user, volunteer_user])
        db.session.commit()

        print("--- Seeding Categories ---")
        categories_data = [
            ("Pothole & Road Damage", "disc", "#ef4444", "Potholes, cracks, surface erosion, or road structural issues."),
            ("Drainage & Flooding", "droplets", "#3b82f6", "Clogged drains, storm water overflow, or drainage blockage."),
            ("Broken Streetlight", "zap", "#f59e0b", "Faulty lamps, exposed wiring, dark street corridors."),
            ("Waste & Sanitation", "trash-2", "#10b981", "Uncollected garbage, illegal dumping, damaged public bins."),
            ("Accessibility Barriers", "user-check", "#8b5cf6", "Damaged ramps, blocked walkways, broken tactile pavement."),
            ("Public Infrastructure", "building-2", "#6366f1", "Damaged public benches, bus stops, signals, bridges, or walls.")
        ]
        categories = []
        for name, icon, color, desc in categories_data:
            cat = Category(name=name, icon=icon, color=color, description=desc)
            db.session.add(cat)
            categories.append(cat)
        db.session.commit()

        print("--- Seeding Zones ---")
        zones_data = [
            ("Zone 1 - North Metro", "Z-101", 40.7580, -73.9855, 85000, 78.4),
            ("Zone 2 - Central Downtown", "Z-102", 40.7128, -74.0060, 120000, 82.1),
            ("Zone 3 - South Waterfront", "Z-103", 40.7020, -74.0120, 65000, 91.0),
            ("Zone 4 - East Industrial Hub", "Z-104", 40.7300, -73.9500, 45000, 64.8),
            ("Zone 5 - West Residential Heights", "Z-105", 40.7800, -73.9700, 95000, 88.5),
        ]
        zones = []
        for name, code, lat, lng, pop, health in zones_data:
            z = Zone(name=name, code=code, lat=lat, lng=lng, population=pop, health_score=health)
            db.session.add(z)
            zones.append(z)
        db.session.commit()

        print("--- Seeding Maintenance Teams ---")
        teams_data = [
            ("Alpha Asphalt Repair Crew", "Road Work & Paving", "+1 (555) 300-01", "Available", zones[0].id, 6),
            ("Beta Hydro Drainage Squad", "Storm Drainage & Sewers", "+1 (555) 300-02", "On Duty", zones[1].id, 8),
            ("Gamma Grid Electrical Techs", "Lighting & Signals", "+1 (555) 300-03", "Available", zones[2].id, 5),
            ("Delta Rapid Waste Response", "Sanitation & Clearance", "+1 (555) 300-04", "On Duty", zones[3].id, 7),
            ("Epsilon Structural Inspection", "Bridges & Overpasses", "+1 (555) 300-05", "Available", zones[4].id, 4),
        ]
        teams = []
        for name, spec, phone, status, zid, members in teams_data:
            t = MaintenanceTeam(name=name, specialty=spec, contact_phone=phone, status=status, current_zone_id=zid, members_count=members)
            db.session.add(t)
            teams.append(t)
        db.session.commit()

        print("--- Seeding Infrastructure Assets & Risk Engine Data ---")
        asset_types = ["Road", "Bridge", "Drainage", "Streetlight", "Public Building"]
        risk_levels = ["Low", "Moderate", "High", "Critical"]

        assets = []
        for i in range(1, 45):
            z = random.choice(zones)
            atype = random.choice(asset_types)
            year = random.randint(1995, 2022)
            cond = round(random.uniform(40.0, 98.0), 1)
            risk_pct = round(100.0 - cond + random.uniform(-5.0, 10.0), 1)
            risk_pct = max(2.0, min(98.0, risk_pct))

            if risk_pct > 75:
                r_level = "Critical"
            elif risk_pct > 50:
                r_level = "High"
            elif risk_pct > 25:
                r_level = "Moderate"
            else:
                r_level = "Low"

            # Offset coordinates around zone
            alat = z.lat + random.uniform(-0.02, 0.02)
            alng = z.lng + random.uniform(-0.02, 0.02)

            asset = InfrastructureAsset(
                asset_code=f"AST-{atype[:3].upper()}-{1000+i}",
                name=f"{z.name.split('-')[1].strip()} {atype} Section #{i}",
                asset_type=atype,
                zone_id=z.id,
                lat=alat,
                lng=alng,
                installation_year=year,
                condition_score=cond,
                failure_risk_pct=risk_pct,
                risk_level=r_level,
                last_inspected=datetime.utcnow() - timedelta(days=random.randint(1, 120)),
                next_recommended_service=datetime.utcnow() + timedelta(days=random.randint(5, 60))
            )
            db.session.add(asset)
            assets.append(asset)
        db.session.commit()

        # Add Risk Assessments for Assets
        for ast in assets:
            if ast.risk_level in ["High", "Critical"]:
                risk_rec = RiskAssessment(
                    asset_id=ast.id,
                    risk_score=ast.failure_risk_pct,
                    risk_level=ast.risk_level,
                    primary_factors="High traffic density, Heavy monsoon rainfall, Age > 15 years, Micro-fracture detected",
                    recommended_action="Deploy immediate reinforcement crew, seal surface cracks, and inspect load points.",
                    urgency="Immediate" if ast.risk_level == "Critical" else "High"
                )
                db.session.add(risk_rec)
        db.session.commit()

        print("--- Seeding Citizen Complaints ---")
        statuses = ["Submitted", "Verified", "Prioritized", "Assigned", "In Progress", "Resolved", "Confirmed"]
        sample_complaints = [
            ("Severe Pothole on 5th Avenue", "Massive 2-foot wide pothole causing vehicle tire damage near main school crossing.", categories[0], zones[1], "Critical"),
            ("Clogged Storm Drain Flooding Main St", "Heavy rain caused water backup up to knee level. Pedestrians unable to cross.", categories[1], zones[0], "Critical"),
            ("Unlit Alley Behind Metro Station", "Four consecutive streetlights out. Major public safety and security risk at night.", categories[2], zones[3], "High"),
            ("Overflowing Garbage Dumpster near Park", "Trash spilling into sidewalk attracting pests for over 3 days.", categories[3], zones[4], "Medium"),
            ("Broken Wheelchair Ramp at Civic Center", "Concrete ramp cracked and unsafe for disabled citizens.", categories[4], zones[1], "High"),
            ("Damaged Bus Shelter Glass", "Shattered glass pane at Stop #42 posing danger to commuters.", categories[5], zones[2], "Low"),
            ("Deep Asphalt Crevice on Bridge Approach", "Structural crack opening up along expansion joint.", categories[0], zones[3], "High"),
            ("Stormwater Culvert Blockage", "Plastic debris choking the main outflow into the river.", categories[1], zones[4], "High"),
            ("Flickering LED Pole #109", "Intermittent lighting causing glare and visibility hazards.", categories[2], zones[0], "Low"),
            ("Hazardous E-Waste Dumped in Alley", "Chemical containers illegally dumped behind industrial lot.", categories[3], zones[3], "Critical")
        ]

        for idx, (title, desc, cat, zn, prio) in enumerate(sample_complaints):
            c_status = statuses[idx % len(statuses)]
            t_id = f"TKT-2026-{1000+idx}"
            ast = random.choice([a for a in assets if a.zone_id == zn.id]) if assets else None

            c = Complaint(
                ticket_id=t_id,
                user_id=citizen.id,
                category_id=cat.id,
                zone_id=zn.id,
                asset_id=ast.id if ast else None,
                title=title,
                description=desc,
                location_address=f"{zn.name}, Near Marker #{idx+1}",
                lat=zn.lat + random.uniform(-0.01, 0.01),
                lng=zn.lng + random.uniform(-0.01, 0.01),
                status=c_status,
                priority=prio,
                assigned_team_id=teams[idx % len(teams)].id if c_status in ["Assigned", "In Progress", "Resolved", "Confirmed"] else None,
                submitted_at=datetime.utcnow() - timedelta(days=random.randint(1, 14)),
                ai_risk_weight=round(random.uniform(1.2, 4.8), 2)
            )
            if c_status in ["Resolved", "Confirmed"]:
                c.resolved_at = datetime.utcnow() - timedelta(days=random.randint(0, 3))
                c.citizen_feedback = "Issue was promptly resolved by the municipal team. Great work!"

            db.session.add(c)
            db.session.commit()

            # Add Complaint Updates history
            up1 = ComplaintUpdate(complaint_id=c.id, status_from="", status_to="Submitted", notes="Complaint received via UrbanPulse Citizen Portal", updated_by="Citizen")
            db.session.add(up1)
            if c_status != "Submitted":
                up2 = ComplaintUpdate(complaint_id=c.id, status_from="Submitted", status_to="Verified", notes="AI verified image & location validity", updated_by="UrbanPulse AI Core")
                db.session.add(up2)
            if c_status in ["Prioritized", "Assigned", "In Progress", "Resolved", "Confirmed"]:
                up3 = ComplaintUpdate(complaint_id=c.id, status_from="Verified", status_to="Assigned", notes=f"Assigned to {teams[idx % len(teams)].name}", updated_by="City Command Center")
                db.session.add(up3)
            if c_status in ["Resolved", "Confirmed"]:
                up4 = ComplaintUpdate(complaint_id=c.id, status_from="In Progress", status_to="Resolved", notes="Field repair complete. Verification photo uploaded.", updated_by="Crew Supervisor")
                db.session.add(up4)

        db.session.commit()

        print("--- Seeding Traffic & Sustainability Indicators ---")
        for zn in zones:
            t = TrafficData(
                zone_id=zn.id,
                congestion_index=round(random.uniform(25.0, 85.0), 1),
                avg_speed_kmh=round(random.uniform(22.0, 55.0), 1),
                incident_count=random.randint(0, 4)
            )
            db.session.add(t)

        sustainability_metrics = [
            ("SUST-AIR-01", "Air Quality Index (AQI)", "Air Quality", 42.0, 35.0, "AQI", 88.0),
            ("SUST-REN-02", "Renewable Energy Share", "Energy", 38.5, 50.0, "%", 77.0),
            ("SUST-WST-03", "Waste Recycled Rate", "Waste", 64.2, 75.0, "%", 85.0),
            ("SUST-WAT-04", "Water Consumption Efficiency", "Water", 145.0, 120.0, "L/cap/day", 81.0),
            ("SUST-MOB-05", "Public Transit Adoption", "Mobility", 54.0, 65.0, "%", 83.0),
            ("SUST-GRN-06", "Urban Green Canopy Cover", "Green Cover", 28.4, 35.0, "%", 81.0),
            ("SUST-EV-07", "EV Charging Density", "Mobility", 14.2, 20.0, "chargers/km²", 71.0),
            ("SUST-CAR-08", "Carbon Intensity Reduction", "Energy", 22.1, 30.0, "% vs 2020", 74.0)
        ]
        for code, name, cat, val, target, unit, score in sustainability_metrics:
            ind = SustainabilityIndicator(code=code, name=name, category=cat, value=val, target=target, unit=unit, score=score)
            db.session.add(ind)

        db.session.commit()

        print("--- Seeding Emergency Services & Health Data ---")
        emergencies = [
            ("Flash Flood Warning - Zone 1 Lowlands", "Public Health & Safety", "Critical", "Zone 1 Metro Corridor", "High rainfall expected to exceed drainage intake by 140%."),
            ("Major Water Main Burst on 8th Street", "Infrastructure Failure", "High", "Zone 2 Downtown", "Main 24-inch water trunk ruptured causing pressure drop and street submergence.")
        ]
        for title, etype, sev, loc, desc in emergencies:
            ev = EmergencyEvent(title=title, event_type=etype, severity=sev, location=loc, description=desc)
            db.session.add(ev)

        services = [
            ("Metropolitan General Hospital", "Hospital", "100 Hospital Way, Zone 2", "+1 (555) 911-01", 40.7150, -74.0040, 42),
            ("St. Jude Trauma Center", "Hospital", "45 Healthcare Ave, Zone 1", "+1 (555) 911-02", 40.7600, -73.9800, 18),
            ("Central Fire & Rescue Station #4", "Fire Station", "12 Rescue Blvd, Zone 2", "+1 (555) 911-03", 40.7110, -74.0080, 0),
            ("Westside Emergency Shelter", "Emergency Shelter", "88 Haven Road, Zone 5", "+1 (555) 911-04", 40.7820, -73.9680, 120)
        ]
        for name, stype, addr, ph, lat, lng, beds in services:
            srv = EmergencyService(name=name, service_type=stype, address=addr, phone=ph, lat=lat, lng=lng, available_beds=beds)
            db.session.add(srv)

        bloods = [
            ("Metropolitan General Hospital", "O-Negative", 4, "Dr. Robert Vance", "+1 (555) 911-01", "Critical"),
            ("St. Jude Trauma Center", "AB-Positive", 2, "Nurse Sarah Jenkins", "+1 (555) 911-02", "High")
        ]
        for hosp, bg, units, cpers, cph, urg in bloods:
            b = BloodDonationRequest(hospital_name=hosp, blood_group=bg, units_needed=units, contact_person=cpers, contact_phone=cph, urgency=urg)
            db.session.add(b)

        db.session.commit()

        print("--- Seeding NGO & Volunteer Data ---")
        ngo = NGOOrganization(
            user_id=ngo_user.id,
            name="CleanCity Alliance & Resilient Urban Alliance",
            registration_number="NGO-USA-2024-8891",
            category="Environment & Resilience",
            verification_status="Verified",
            website="https://cleancityalliance.org",
            description="Empowering communities through grassroots sustainability, storm response, and infrastructure maintenance."
        )
        db.session.add(ngo)
        db.session.commit()

        init1 = Initiative(
            ngo_id=ngo.id,
            title="Urban Canopy Restoration & Drainage Clearing Drive",
            description="Planting 200 native trees and clearing storm debris from Zone 1 and Zone 4 drainage channels.",
            target_volunteers=25,
            current_volunteers=14,
            location="Zone 1 & Zone 4 Corridors",
            start_date=datetime.utcnow() + timedelta(days=5),
            status="Active"
        )
        db.session.add(init1)
        db.session.commit()

        task1 = InitiativeTask(
            initiative_id=init1.id,
            title="Drainage Debris Clearing Specialist",
            required_skill="Manual Labor & Safety Protocol",
            location="Zone 1 Outflow Gate #3",
            needed_volunteers=10,
            status="Open"
        )
        task2 = InitiativeTask(
            initiative_id=init1.id,
            title="Tree Sapling Planter & Soil Lead",
            required_skill="Botany & Gardening",
            location="Zone 4 Riverside Park",
            needed_volunteers=15,
            status="Open"
        )
        db.session.add_all([task1, task2])
        db.session.commit()

        vol_prof = VolunteerProfile(
            user_id=volunteer_user.id,
            skills="Manual Labor & Safety Protocol, Emergency First Aid, GIS Mapping",
            interests="Disaster Relief, Environmental Sustainability, Community Care",
            availability="Weekends & Evening Hours",
            preferred_location="Zone 1 & Zone 2",
            completed_hours=18
        )
        db.session.add(vol_prof)
        db.session.commit()

        v_app = VolunteerApplication(
            task_id=task1.id,
            volunteer_id=vol_prof.id,
            status="Accepted"
        )
        db.session.add(v_app)

        print("--- Seeding Digital Twin Scenarios ---")
        scen1 = Scenario(
            title="Close Main Downtown Arterial (30 Days)",
            scenario_type="Road Closure",
            description="Simulating full closure of 5th Avenue Corridor for structural bridge girder replacement.",
            parameters='{"closure_road": "5th Avenue", "duration_days": 30, "detour_route": "4th Ave & 7th St"}'
        )
        db.session.add(scen1)
        db.session.commit()

        effects_data = [
            (scen1.id, "Traffic Congestion Index", "+42.5%", "High Increase", 42.5, "Severe"),
            (scen1.id, "Average Commute Delay", "+14.2 mins", "Delay", 14.2, "Moderate"),
            (scen1.id, "Emergency Response Latency", "+3.8 mins", "Delay", 3.8, "Severe"),
            (scen1.id, "Alternative Corridor Load (4th Ave)", "+68.0%", "Overload Risk", 68.0, "Severe"),
            (scen1.id, "Citizen Impact Index", "74/100", "High Disruption", 74.0, "Moderate")
        ]
        for sid, mname, base, pred, chg, imp in effects_data:
            eff = ScenarioEffect(scenario_id=sid, metric_name=mname, baseline_value=base, predicted_value=pred, change_pct=chg, impact_level=imp)
            db.session.add(eff)

        print("--- Seeding Safety, Notifications & Resources ---")
        contact1 = TrustedContact(
            user_id=citizen.id,
            name="Elena Sterling (Mother)",
            relationship="Parent",
            phone="+1 (555) 998-1122",
            email="elena.sterling@example.com"
        )
        db.session.add(contact1)

        notif1 = Notification(
            user_id=citizen.id,
            title="Ticket #TKT-2026-1000 Verified",
            message="Your report regarding 'Severe Pothole on 5th Avenue' has been verified and prioritized by UrbanPulse AI.",
            is_read=False
        )
        db.session.add(notif1)

        log1 = AuditLog(
            admin_name="Dr. Elena Vance",
            action="RESOURCE_REALLOCATION",
            details="Reallocated Maintenance Team Alpha to Zone 1 due to high risk assessment score."
        )
        db.session.add(log1)

        resources_data = [
            ("Asphalt Paving Machine AP-500", "Vehicle", 6, 4, "Zone 1 Depot", "Excellent"),
            ("Heavy-Duty Hydro Jetter Drain Cleaner", "Equipment", 10, 7, "Zone 2 Central Hub", "Good"),
            ("Emergency Mobile Flood Pumps", "Equipment", 15, 12, "Zone 4 Warehouse", "Good"),
            ("Municipal Bucket Trucks (Lighting)", "Vehicle", 8, 5, "Zone 3 Garage", "Fair")
        ]
        for rname, rtype, tot, avail, loc, cond in resources_data:
            res = Resource(name=rname, resource_type=rtype, total_quantity=tot, available_quantity=avail, location_zone=loc, condition=cond)
            db.session.add(res)

        db.session.commit()
        print("Successfully seeded all synthetic city data for UrbanPulse AI!")

if __name__ == '__main__':
    seed_database()
