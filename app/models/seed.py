from sqlalchemy import text
from app.core.database import SessionLocal

def seed_roles():
    db = SessionLocal()
    try:
        # Insert roles if they don't exist
        db.execute(text("""
            INSERT INTO sys_roles (code) 
            VALUES ('admin'), ('recruiter'), ('candidate')
            ON CONFLICT (code) DO NOTHING
        """))
        db.commit()
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()