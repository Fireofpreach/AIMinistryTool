from app import app, db
import models

def update_database():
    """Update database schema to match current models"""
    with app.app_context():
        print("Starting database update...")
        db.create_all()
        print("Database schema updated successfully!")

if __name__ == "__main__":
    update_database()