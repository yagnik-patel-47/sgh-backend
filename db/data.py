from sqlalchemy.orm import Session
from db.models import Institute, Program


def get_institute_from_website(db: Session, website: str):
    """
    Get the institute from the database based on the website URL.

    Args:
        db (Session): SQLAlchemy session object.
        website (str): The website URL of the institute.

    Returns:
        Institute: The Institute object if found, None otherwise.
    """
    try:
        return db.query(Institute).filter(Institute.website == website).first()
    except Exception as e:
        print(f"Error fetching institute for website {website}: {e}")
        return None


def get_program_from_name(db: Session, name: str):
    """
    Get the program from the database based on the program name.

    Args:
        db (Session): SQLAlchemy session object.
        name (str): The name of the program.

    Returns:
        Program: The Program object if found, None otherwise.
    """
    try:
        return db.query(Program).filter(Program.name == name).first()
    except Exception as e:
        print(f"Error fetching program for name {name}: {e}")
        return None
