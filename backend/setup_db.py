import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from app.config import DATABASE_URL
from app.database import Base, engine
from app.seed import seed_default_admin, seed_lms_dummy_data

print("Checking if database 'db_epelatihan' exists...")
try:
    # Try connecting directly to db_epelatihan
    conn = psycopg2.connect(
        dbname='db_epelatihan',
        user='postgres',
        password='syamstedc',
        host='localhost',
        port='5432'
    )
    conn.close()
    print("Database 'db_epelatihan' already exists.")
except psycopg2.OperationalError:
    print("Database does not exist. Creating...")
    try:
        # Connect to default 'postgres' database to create the new one
        conn = psycopg2.connect(
            dbname='postgres',
            user='postgres',
            password='syamstedc',
            host='localhost',
            port='5432'
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        cursor.execute('CREATE DATABASE db_epelatihan')
        cursor.close()
        conn.close()
        print("Database 'db_epelatihan' created successfully.")
    except Exception as e:
        print(f"Error creating database: {e}")

print("Migrating tables...")
Base.metadata.create_all(bind=engine)
print("Tables migrated.")

print("Seeding dummy data...")
seed_default_admin()
seed_lms_dummy_data()
print("Dummy data seeded successfully. Dummy user 'peserta1' with password 'peserta123' has been created.")
