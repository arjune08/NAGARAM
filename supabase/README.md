# NAGARAM Supabase database

The NAGARAM production database is hosted on Supabase PostgreSQL. The Flask application continues to use SQLAlchemy, so the existing models remain the application's database contract.

## Connection

Set this environment variable in Vercel and local development:

```text
SUPABASE_DB_URL=postgresql://...
```

`DATABASE_URL` is also supported for deployment-platform compatibility. Do not use the Supabase REST URL as a SQLAlchemy database URL; use the PostgreSQL connection string from the Supabase database connection settings.

## Current schema

The Supabase project contains the 26 tables represented by `models.py`, including users, complaints, categories, zones, infrastructure assets, maintenance, emergency, NGO, volunteer, sustainability, scenario, notification, audit, and resource data.

## Security

Row Level Security is enabled on the public application tables. The current Flask app accesses PostgreSQL server-side through its database connection rather than directly from browser clients. Do not expose a privileged database password, service key, or direct database connection string to frontend JavaScript.

If the application is later changed to use Supabase's browser Data API directly, add table-specific RLS policies before granting client access.
