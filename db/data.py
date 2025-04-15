from sqlalchemy.orm import Session
from db.models import Institute, Program, Tag, ScrapedPage


def get_institute_from_website(db: Session, website: str):
    try:
        return db.query(Institute).filter(Institute.website == website).first()
    except Exception as e:
        print(f"Error fetching institute for website {website}: {e}")
        return None


def get_all_institutes(db: Session):
    try:
        return db.query(Institute).all()
    except Exception as e:
        print(f"Error fetching all institutes: {e}")
        return None


def get_all_programs(db: Session):
    try:
        return db.query(Program).all()
    except Exception as e:
        print(f"Error fetching all programs: {e}")
        return None


def get_all_tags(db: Session):
    try:
        return db.query(Tag).all()
    except Exception as e:
        print(f"Error fetching all tags: {e}")
        return None


def get_all_scraped_pages(db: Session):
    try:
        return db.query(ScrapedPage).all()
    except Exception as e:
        print(f"Error fetching all scraped pages: {e}")
        return None
