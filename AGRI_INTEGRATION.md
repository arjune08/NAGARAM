# NAGARAM + AGRI-NAGARAM Integration

This branch keeps the existing NAGARAM civic platform and adds an agricultural workspace inside the same application.

## Architecture

- **Citizen**: existing civic reporting and community features
- **Farmer**: dedicated AGRI-NAGARAM workspace
- **Admin / NGO / Volunteer**: existing organization workflows remain available
- **Shared action network**: farm issues generate notifications and use the same platform identity and authentication ecosystem

## New farmer routes

- `/farmer/dashboard`
- `/farmer/farms`
- `/farmer/issue`
- `/farmer/market`
- `/farmer/health`
- `/farmer/scenario` (POST demo decision scenario)

## Prototype decision model

The farmer dashboard uses transparent demo scoring signals and clearly labels outputs as prototype/demo data. It is not a scientific agronomic model.

Inputs currently represented include weather scenario, water implication, crop stage, crop-health/pest risk and market opportunity. The scenario endpoint demonstrates the connected flow:

`Rain probability → weather risk → water action → disease monitoring → updated recommendation state`

## Database additions

- FarmerProfile
- Farm
- FarmIssue
- Recommendation
- FarmRecord

The existing database remains the primary persistence layer. New agricultural tables are registered through SQLAlchemy before `db.create_all()`.

## Important verification checklist

1. Install existing dependencies from `requirements.txt`.
2. Configure the existing database environment variables.
3. Start the Flask application using the repository's existing entrypoint.
4. Register through `/auth/register/farmer`.
5. Confirm redirect to `/farmer/dashboard`.
6. Change the rain scenario and verify the JSON-backed dashboard update.
7. Add a farm and verify it persists after refresh.
8. Submit a farm issue and verify it appears in the farmer dashboard workflow.

## Data labels

Demo values, buyer offers and prototype decision outputs are intentionally labelled **DEMO DATA**, **Estimated** or **Prototype** and must not be presented as live agricultural intelligence.
