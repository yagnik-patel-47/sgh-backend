from sqlalchemy.orm import Session
from models import Institute, State
from setup import get_db
import pandas as pd
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
import logging
import re

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


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


def seed_institutes(db: Session):
    # Load sites data
    df = pd.read_csv("sites.csv")
    data = df.to_dict(orient="records")

    # Load states data and create a mapping of state names to state_ids
    states_df = pd.DataFrame(get_all_states(db))

    # Create both regular and normalized mappings for better matching
    state_name_to_id_map = dict(zip(states_df["name"], states_df["state_id"]))
    normalized_state_map = {
        normalize_state_name(name): id
        for name, id in zip(states_df["name"], states_df["state_id"])
    }

    # Map state names to state_ids for each site
    data_with_state_id = []
    unmatched_states = set()

    for site in data:
        state_name = site["state"]

        # Try direct match first
        state_id = state_name_to_id_map.get(state_name)

        # If direct match fails, try normalized match
        if not state_id:
            normalized_name = normalize_state_name(state_name)
            state_id = normalized_state_map.get(normalized_name)

            # Additional loose matching for common variations
            if not state_id:
                # Try partial matching for longer state names
                for db_state, db_id in normalized_state_map.items():
                    # Check if one is a substring of the other (in either direction)
                    if (
                        normalized_name in db_state or db_state in normalized_name
                    ) and len(db_state) > 3:
                        state_id = db_id
                        logger.info(
                            f"Partial match found: '{state_name}' matched with '{db_state}'"
                        )
                        break

        if state_id:
            site_with_state_id = site.copy()
            site_with_state_id["state_id"] = state_id
            data_with_state_id.append(site_with_state_id)
        else:
            unmatched_states.add(state_name)
            logger.warning(
                f"State '{state_name}' not found in states mapping for site: {site['uni_name']}"
            )

    if unmatched_states:
        logger.warning(f"Unmatched states: {', '.join(sorted(unmatched_states))}")

    logger.info(
        f"Processed {len(data_with_state_id)} out of {len(data)} sites with valid state IDs"
    )

    spiltted_data = split_content(data_with_state_id)

    try:
        for batch in spiltted_data:
            sites = []
            for site in batch:
                website = Institute(
                    name=site["uni_name"],
                    website=site["url"],
                    state_id=site["state_id"],
                )
                sites.append(website)
            db.add_all(sites)
        db.commit()
        logger.info(
            f"Successfully added {len(data_with_state_id)} institutes to the database"
        )

    except IntegrityError as e:
        db.rollback()
        logger.error(f"Integrity error creating site: {str(e)}")
        raise ValueError(f"Value already exists: {str(e)}")

    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error creating site: {str(e)}")
        raise Exception(f"Database error: {str(e)}")


def seed_states(db: Session):
    states = pd.read_json("db\seed_data\states.json")
    states = states.to_dict(orient="records")

    try:
        for state in states:
            state_instance = State(
                name=state["name"],
                abbreviation=state["abbreviation"],
            )
            db.add(state_instance)
        db.commit()
    except IntegrityError as e:
        db.rollback()
        logger.error(f"Integrity error creating state: {str(e)}")
        raise ValueError(f"Value already exists: {str(e)}")
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error creating state: {str(e)}")
        raise Exception(f"Database error: {str(e)}")


if __name__ == "__main__":
    db = next(get_db())
    seed_states(db)
    seed_institutes(db)
