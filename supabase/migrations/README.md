# Applied migrations

The connected Supabase project has two applied migrations:

1. `create_nagaram_schema` — creates the 26 PostgreSQL tables represented by the current SQLAlchemy models and adds core indexes.
2. `enable_rls_on_nagaram_tables` — enables Row Level Security on those public tables.

The current Flask application uses a server-side PostgreSQL connection through SQLAlchemy. Before exposing any table directly through Supabase's client Data API, define and test table-specific RLS policies for the intended user roles.
