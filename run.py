import os
from app import create_app
from models import db, User

# Vercel imports this module and uses the Flask WSGI app.
# Keep initialization side-effect-light: schema creation happens in create_app().
app = create_app()

if __name__ == '__main__':
    # Local development only. Never run the development server on Vercel.
    with app.app_context():
        db.create_all()
        if not User.query.first():
            try:
                from seed_data import seed_database
                seed_database()
            except Exception as e:
                print(f"Error seeding database: {e}")

    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)), debug=False)
