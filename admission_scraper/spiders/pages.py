import scrapy
import pandas as pd
import re
from admission_scraper.utils import (
    clean_body_content,
    extract_context,
    remove_trailing_slash,
)
import random
from db.session import get_db
from db.models import ScrapedPage
from db.data import get_all_scraped_pages
from datetime import datetime
from zoneinfo import ZoneInfo
import os
import io


def getUrls() -> list[str]:
    try:
        # Check if file exists first
        if not os.path.exists("uni.jsonl"):
            print("Warning: uni.jsonl file not found")
            return []

        # Open the file and use StringIO to avoid FutureWarning
        with open("uni.jsonl", "r", encoding="utf-8") as f:
            content = f.read()

        # Process only if file has content
        if content.strip():
            df = pd.read_json(io.StringIO(content), lines=True)
            urls = df["matched_links"].tolist()
            urls = [url for sublist in urls for url in sublist]
            urls = list(set(urls))
            random.shuffle(urls)
            return urls
        else:
            print("uni.jsonl file is empty")
            return []
    except Exception as e:
        # More detailed error handling
        print(f"Error reading uni.jsonl: {e}")
        return []


def get_site_from_link(link):
    """
    Extract the site value from uni.json that contains the given link in its matched_links.

    Args:
        link (str): A URL that might be in matched_links of a site

    Returns:
        str: The site value if found, None otherwise
    """
    try:
        # Check if file exists first
        if not os.path.exists("uni.jsonl"):
            print("Warning: uni.jsonl file not found in get_site_from_link")
            return None

        # Open the file and use StringIO to avoid FutureWarning
        with open("uni.jsonl", "r", encoding="utf-8") as f:
            content = f.read()

        if not content.strip():
            print("uni.jsonl file is empty in get_site_from_link")
            return None

        data = pd.read_json(io.StringIO(content), lines=True)

        for _, row in data.iterrows():
            if link in row["matched_links"]:
                return row["original_url"]

        return None
    except Exception as e:
        print(f"Error finding site for link {link}: {e}")
        return None


class PagesSpider(scrapy.Spider):
    name = "pages"
    refresh_days = 2
    counter = 0

    def start_requests(self):
        self.urls = getUrls()
        # diff_urls = []
        # db = next(get_db())
        # scraped_pages = get_all_scraped_pages(db) or []
        # scraped_urls = (
        #     [page.url for page in scraped_pages] if scraped_pages is not None else []
        # )

        # for url in self.urls:
        #     existing = url in scraped_urls
        #     if existing:
        #         existing = next((x for x in scraped_pages if x.url == url), None)

        #     if (
        #         not existing
        #         or (datetime.now(ZoneInfo("Asia/Kolkata")) - existing.last_scraped).days
        #         >= self.refresh_days
        #     ):
        #         # New URL or needs refresh
        #         diff_urls.append(url)
        #         yield scrapy.Request(
        #             url=url, callback=self.parse, meta={"original_url": url}
        #         )
        # self.urls = diff_urls

        for url in self.urls:
            yield scrapy.Request(
                url=url, callback=self.parse, meta={"original_url": url}
            )

    def parse(self, response):
        self.counter += 1

        admission_terms = (
            r"(?:admission|apply|application|deadline|enroll|registration)"
        )
        date_pattern = (
            r"(?:\b(?:\d{1,2}[-./]\d{1,2}[-./](?:\d{4}|\d{2}))\b|"
            + r"\b(?:\d{1,2}[- ]?(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)[- ]?\d{2,4})\b|"
            + r"\b(?:\d{4}[-./]\d{1,2}[-./]\d{1,2})\b)"
        )
        word_pattern = rf"\b{admission_terms}s?\b"

        body_content = response.css("body").get()
        if not body_content:
            return

        cleaned_body_content = clean_body_content(body_content)

        date_matches = extract_context(cleaned_body_content, date_pattern)

        # print(f"\n\nFound {len(date_matches)} date matches in {response.url}\n\n")

        if len(date_matches) != 0:
            for date_match in date_matches:
                if not is_likely_phone_number(date_match["match"]):
                    word_matches = re.findall(
                        word_pattern, date_match["context"], re.IGNORECASE
                    )
                    if word_matches:
                        site = get_site_from_link(response.meta.get("original_url"))
                        yield {
                            "url": remove_trailing_slash(response.url),
                            "site": site,
                            "date": date_match["match"],
                            "context": date_match["context"],
                            "related_dates": date_match.get("related_dates", []),
                        }

        print("processed ", self.counter, "from ", len(self.urls), " urls")


def is_likely_phone_number(text):
    # Phone number patterns to reject
    phone_patterns = [
        r"\d+/\d+/\d+/\d+",  # Pattern like 8200/1/2/3
        r"\d+-\d+-\d+",  # Pattern like 91-72-820
        r"\d{4}-\d{2,3}-\d{2,4}",  # Common phone format with hyphens
        r"\d{10,}",  # Any sequence of 10+ digits (most dates won't have this many)
    ]

    # Date-specific validation
    month_names = r"Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec"
    looks_like_date = bool(
        re.search(rf"\b({month_names})\b", text, re.IGNORECASE)
        or re.search(r"\b\d{4}\b", text)
    )  # Has a 4-digit year

    # Check against phone patterns
    for pattern in phone_patterns:
        if re.search(pattern, text):
            return True

    return not looks_like_date
