import os
from app import create_app
from models import db, User

app = create_app()

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        # Auto-seed if database has no users
        if not User.query.first():
            print("Database empty. Auto-seeding synthetic city data...")
            try:
                from seed_data import seed_database
                seed_database()
            except Exception as e:
                print(f"Error seeding database: {e}")
    
    app.run(host='0.0.0.0', port=5000, debug=True)
