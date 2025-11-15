"""
Database migration script to add location fields to Conversation and Message tables
Run this script to update your existing database schema
"""

from sqlalchemy import create_engine, text
from database import DATABASE_URL
import os

def migrate_database():
    """Add location columns to existing tables"""

    # Configure engine based on database type
    if DATABASE_URL.startswith("sqlite"):
        engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
    else:
        engine = create_engine(DATABASE_URL)

    with engine.connect() as conn:
        print("Starting database migration...")

        try:
            # Add latitude and longitude to conversations table
            print("Adding latitude and longitude columns to conversations table...")
            conn.execute(text("""
                ALTER TABLE conversations
                ADD COLUMN IF NOT EXISTS latitude FLOAT,
                ADD COLUMN IF NOT EXISTS longitude FLOAT
            """))
            conn.commit()
            print("✓ Conversations table updated")

        except Exception as e:
            print(f"Conversations table migration (may already exist): {e}")

        try:
            # Add latitude and longitude to messages table
            print("Adding latitude and longitude columns to messages table...")
            conn.execute(text("""
                ALTER TABLE messages
                ADD COLUMN IF NOT EXISTS latitude FLOAT,
                ADD COLUMN IF NOT EXISTS longitude FLOAT
            """))
            conn.commit()
            print("✓ Messages table updated")

        except Exception as e:
            print(f"Messages table migration (may already exist): {e}")

        print("\n✓ Database migration completed successfully!")
        print("You can now use location-based features.")

if __name__ == "__main__":
    migrate_database()
