from llm.gemini import extract_with_gemini
import pandas as pd
from db.session import get_db
from db.data import (
    get_institute_from_website,
    get_all_tags,
    get_all_programs,
    get_all_scraped_pages,
)
from db.models import Announcement, AnnouncementProgram, ScrapedPage, AnnouncementTags
import hashlib
from datetime import datetime
from zoneinfo import ZoneInfo


db = next(get_db())
db_tags = get_all_tags(db) or []
db_programs = get_all_programs(db) or []
scraped_pages = get_all_scraped_pages(db)
scraped_urls = [page.url for page in scraped_pages] if scraped_pages is not None else []


def content_changed(url, content):
    record = db.query(ScrapedPage).filter(ScrapedPage.url == url).first()

    if not record:
        return True

    new_hash = hashlib.sha256(content.encode()).hexdigest()
    return new_hash != record.content_hash


def process_page(url: str, site: str, items: list[dict[str, str]]):
    for item in items:
        try:
            extracted_data = extract_with_gemini(item["context"], url)
            if "announcements" in extracted_data:
                for announcement in extracted_data["announcements"]:
                    print("\nannouncement:", announcement, "\n")
                    institute = get_institute_from_website(db, item["site"])
                    if institute:
                        try:
                            programs = announcement.get("programs_courses", [])
                            tags = announcement.get("tags", [])

                            announcement_data = {
                                key: value
                                for key, value in announcement.items()
                                if key != "programs_courses" and key != "tags"
                            }
                            ann = Announcement(
                                institution_id=institute.institution_id,
                                state_id=institute.state_id,
                                url=url,
                                **announcement_data,
                            )
                            db.add(ann)
                            db.flush()
                            announcement_id = ann.announcement_id

                            for program in programs:
                                program_instance = next(
                                    (x for x in db_programs if x.name == program), None
                                )
                                if program_instance:
                                    announcement_program = AnnouncementProgram(
                                        announcement_id=announcement_id,
                                        program_id=program_instance.program_id,
                                    )
                                    db.add(announcement_program)

                            for tag in tags:
                                tag_instance = next(
                                    (x for x in db_tags if x.name == tag), None
                                )
                                if tag_instance:
                                    announcement_tags = AnnouncementTags(
                                        announcement_id=announcement_id,
                                        tag_id=tag_instance.tag_id,
                                    )
                                    db.add(announcement_tags)

                            # db.commit()
                        except Exception as e:
                            print(f"Error saving announcement: {e}")
                            db.rollback()
                    else:
                        print(f"No matching institute found for URL: {item['site']}")

        except Exception as e:
            db.rollback()
            print(f"Error processing row - {url}: {e}")

    merged_content = " ".join(
        [item["context"] for item in items if item["context"] is not None]
    )
    content_hash = hashlib.sha256(merged_content.encode()).hexdigest()
    db.add(
        ScrapedPage(
            url=url,
            site=site,
            last_scraped=datetime.now(ZoneInfo("Asia/Kolkata")),
            content_hash=content_hash,
        )
    )
    # db.rollback()
    db.commit()


# df = pd.read_json("pages.jsonl", lines=True)

# grouped_df = (
#     df.groupby("url")
#     .apply(
#         lambda x: pd.Series(
#             {
#                 "site": x["site"].iloc[0],
#                 "items": x.to_dict("records"),
#             }
#         ),
#         include_groups=False,
#     )
#     .reset_index()
# )
# df = grouped_df

# for i, (index, row) in enumerate(df.sample(20).iterrows()):
# print("Processing group", i + 1, "of", len(df))
# if row["url"] in scraped_urls:
#     print(f"Skipping {row['url']}")
#     continue

# merged_content = " ".join(
#     [item["context"] for item in row["items"] if item["context"] is not None]
# )
# if not content_changed(row["url"], merged_content):
#     print(f"Skipping unchanged content for {row['url']}")
#     continue
# process_page(row["url"], row["items"])
# print(f"Processed group {i + 1} - {row['url']}")
