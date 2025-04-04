from sqlalchemy.orm import Session
from models import Institute, State, Program
from setup import get_db
import pandas as pd
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
import logging
from utils import split_content, normalize_state_name, get_all_states

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


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
    states = pd.read_json("seed_data\states.json")
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


def seed_programs(db: Session):
    programs = pd.read_json("seed_data\programs.json")
    programs = programs.to_dict(orient="records")

    try:
        for program in programs:
            program_instance = Program(
                name=program["name"],
                description=program["description"],
                degree_level=program["degree_level"],
                duration_months=program["duration_months"],
            )
            db.add(program_instance)
        db.commit()
    except IntegrityError as e:
        db.rollback()
        logger.error(f"Integrity error creating program: {str(e)}")
        raise ValueError(f"Value already exists: {str(e)}")
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error creating program: {str(e)}")
        raise Exception(f"Database error: {str(e)}")


if __name__ == "__main__":
    # db = next(get_db())
    # seed_states(db)
    # seed_institutes(db)
    # seed_programs(db)
    pass
