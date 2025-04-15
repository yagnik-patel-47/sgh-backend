import re
from sqlalchemy.orm import Session
from db.models import State


def split_content(content, max_length=100):
    return [content[i : i + max_length] for i in range(0, len(content), max_length)]


def normalize_state_name(state_name):
    """Normalize state name for better matching"""
    if not state_name:
        return ""

    # Convert to lowercase
    normalized = state_name.lower().strip()

    # Remove special characters and extra spaces
    normalized = re.sub(r"[^\w\s]", "", normalized)
    normalized = re.sub(r"\s+", " ", normalized)

    # Common abbreviation mappings
    abbreviations = {
        "ap": "andhra pradesh",
        "ts": "telangana",
        "tn": "tamil nadu",
        "wb": "west bengal",
        "up": "uttar pradesh",
        "mp": "madhya pradesh",
        "jk": "jammu and kashmir",
        "hp": "himachal pradesh",
        "nct": "delhi",
    }

    if normalized in abbreviations:
        normalized = abbreviations[normalized]

    return normalized


def get_all_states(db: Session):
    states = db.query(State).all()
    states_list = []
    for state in states:
        states_list.append(
            {
                "state_id": state.state_id,
                "name": state.name,
                "abbreviation": state.abbreviation,
            }
        )
    return states_list
