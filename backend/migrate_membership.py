"""
Migration script to add membership card fields to existing database.
Run this script once to update the database schema.

Usage:
    python migrate_membership.py
"""

import uuid
from datetime import date, timedelta

from sqlalchemy import text

from app.database import SessionLocal, engine
from app.models import Base, User


def migrate_database():
    """Add new columns for membership card functionality"""
    db = SessionLocal()
    
    try:
        print("Starting database migration for membership card feature...")
        
        # Check if columns already exist
        with engine.connect() as conn:
            # Try to query the columns to see if they exist
            try:
                result = conn.execute(text("""
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name='users' 
                    AND column_name IN (
                        'verification_token', 
                        'nomor_anggota', 
                        'golongan', 
                        'kwartir', 
                        'membership_status', 
                        'valid_until', 
                        'foto_url'
                    )
                """))
                existing_columns = [row[0] for row in result]
                print(f"Existing columns: {existing_columns}")
                
            except Exception as e:
                print(f"Error checking columns: {e}")
                existing_columns = []
            
            # Add columns if they don't exist
            columns_to_add = {
                'verification_token': 'UUID UNIQUE',
                'nomor_anggota': 'VARCHAR UNIQUE',
                'golongan': 'VARCHAR',
                'kwartir': 'VARCHAR',
                'membership_status': 'VARCHAR DEFAULT \'active\' NOT NULL',
                'valid_until': 'DATE',
                'foto_url': 'VARCHAR'
            }
            
            for column_name, column_type in columns_to_add.items():
                if column_name not in existing_columns:
                    try:
                        sql = f"ALTER TABLE users ADD COLUMN {column_name} {column_type}"
                        print(f"Adding column: {column_name}")
                        conn.execute(text(sql))
                        conn.commit()
                        print(f"✓ Added column: {column_name}")
                    except Exception as e:
                        print(f"✗ Error adding column {column_name}: {e}")
                else:
                    print(f"✓ Column {column_name} already exists")
        
        print("\n" + "="*50)
        print("Updating existing users with default values...")
        print("="*50 + "\n")
        
        # Update existing users
        users = db.query(User).all()
        updated_count = 0
        
        for user in users:
            needs_update = False
            
            if not user.verification_token:
                user.verification_token = uuid.uuid4()
                needs_update = True
            
            if not user.membership_status:
                user.membership_status = "active"
                needs_update = True
            
            if not user.valid_until:
                user.valid_until = date.today() + timedelta(days=365)
                needs_update = True
            
            if needs_update:
                updated_count += 1
                print(f"✓ Updated user: {user.username} ({user.nama_lengkap})")
        
        if updated_count > 0:
            db.commit()
            print(f"\n✓ Successfully updated {updated_count} users")
        else:
            print("\n✓ No users needed updating")
        
        print("\n" + "="*50)
        print("Migration completed successfully!")
        print("="*50)
        
    except Exception as e:
        print(f"\n✗ Migration failed: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    migrate_database()
