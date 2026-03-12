"""
Database initialization script.
Creates all database tables defined in the models.

Usage:
    python init_db.py
"""
import os
from app import create_app, db
from models import User


def init_database():
    """Initialize the database and create all tables"""
    app = create_app()
    
    with app.app_context():
        print("Creating database tables...")
        db.create_all()
        print("✓ Database tables created successfully!")
        print("\nTables created:")
        print("  - users")


def drop_database():
    """Drop all database tables (WARNING: destructive operation)"""
    app = create_app()
    
    with app.app_context():
        response = input("⚠️  WARNING: This will delete all tables and data. Continue? (yes/no): ")
        if response.lower() == 'yes':
            print("Dropping all tables...")
            db.drop_all()
            print("✓ All tables dropped successfully!")
        else:
            print("Operation cancelled.")


if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == 'drop':
            drop_database()
        elif sys.argv[1] == 'init':
            init_database()
        else:
            print("Usage:")
            print("  python init_db.py init    - Create all database tables")
            print("  python init_db.py drop    - Drop all database tables")
    else:
        # Default behavior: initialize database
        init_database()
