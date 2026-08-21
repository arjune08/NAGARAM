# NAGARAM

NAGARAM is a Flask-based civic platform for connecting citizens, volunteers, NGOs, and administrators around community issues and local services.

## Features

- Citizen-facing issue and service workflows
- Role-based areas for citizens, volunteers, NGOs, and administrators
- Authentication with Flask-Login
- Database access through Flask-SQLAlchemy and Supabase PostgreSQL
- Form handling with Flask-WTF
- Image/file support with Pillow
- Environment-based configuration for local development and deployment

## Tech stack

- Python
- Flask
- SQLAlchemy
- Supabase PostgreSQL
- Flask-Login
- Flask-WTF
- Jinja templates

## Project structure

The project currently keeps several application modules and templates at the repository root. The main entry point is `app.py` and the application is assembled through Flask blueprints such as:

- `main.py`
- `auth.py`
- `citizen.py`
- `volunteer.py`
- `ngo.py`
- `admin.py`
- `safety.py`
- `api.py`

Configuration and data models are handled by `config.py` and `models.py`. Supabase database notes are in `supabase/README.md`.

## Getting started

### 1. Clone the repository

```bash
git clone https://github.com/arjune08/NAGARAM.git
cd NAGARAM
```

### 2. Create a virtual environment

```bash
python -m venv .venv
```

Activate it:

```bash
# macOS / Linux
source .venv/bin/activate

# Windows PowerShell
.venv\\Scripts\\Activate.ps1
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Supabase

Copy the example file and set `SUPABASE_DB_URL` to the PostgreSQL connection string for your Supabase project:

```bash
cp .env.example .env
```

Use the PostgreSQL connection string from Supabase, not the REST/API URL. Keep database credentials server-side and never commit them to Git.

### 5. Run the application

```bash
python app.py
```

If your local configuration uses a different entry command, follow the settings in `config.py`.

## Development checks

This repository includes a GitHub Actions workflow that installs dependencies and performs a Python syntax compilation check on every push and pull request.

Run the same basic check locally with:

```bash
python -m compileall -q .
```

## Contributing

1. Create a branch for your change.
2. Keep secrets out of Git.
3. Run the available checks before opening a pull request.
4. Keep commits focused and descriptive.

## Security note

If a real `.env` file has ever been committed, rotate any secrets it contained and remove it from the repository history when practical. `.env.example` should contain placeholders only.
