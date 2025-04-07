from llm.gemini import extract_with_gemini
import pandas as pd
from db.setup import get_db
from db.data import get_institute_from_website, get_program_from_name
from db.models import Announcement, AnnouncementProgram

db = next(get_db())

df = pd.read_json("pages.json")
# Only iterate through the first 10 rows

for index, row in df.sample(10).iterrows():
    try:
        extracted_data = extract_with_gemini(row["context"], row["url"])
        if "announcements" in extracted_data:
            for announcement in extracted_data["announcements"]:
                institute = get_institute_from_website(db, row["site"])
                if institute:
                    try:
                        programs = announcement.get("programs_courses", [])

                        announcement_data = {
                            key: value
                            for key, value in announcement.items()
                            if key != "programs_courses"
                        }
                        ann = Announcement(
                            institution_id=institute.institution_id,
                            state_id=institute.state_id,
                            url=row["url"],
                            **announcement_data,
                        )
                        # print(announcement, programs)
                        db.add(ann)
                        db.flush()  # Flush to get the generated ID without committing
                        announcement_id = (
                            ann.announcement_id
                        )  # Capture the generated announcement ID

                        for program in programs:
                            program_instance = get_program_from_name(db, program)
                            if program_instance:
                                announcement_program = AnnouncementProgram(
                                    announcement_id=announcement_id,
                                    program_id=program_instance.program_id,
                                )
                                db.add(announcement_program)

                        db.commit()
                    except Exception as e:
                        print(f"Error saving announcement: {e}")
                        db.rollback()
                else:
                    print(f"No matching institute found for URL: {row['site']}")
    except Exception as e:
        print(f"Error processing row {index}: {e}")
