import scrapy
import pandas as pd
import re
from admission_scraper.utils import clean_body_content, extract_context


def getUrls():
    try:
        df = pd.read_json("uni.json")
        urls = df["matched_links"].tolist()
        urls = [url for sublist in urls for url in sublist]
        urls = list(set(urls))
        return urls[:50]
    except:
        # If the file doesn't exist, return an empty list
        print("File not found")
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
        with open("uni.json", "r") as f:
            data = pd.read_json(f)

        for _, row in data.iterrows():
            if link in row["matched_links"]:
                return row["site"]

        return None
    except Exception as e:
        print(f"Error finding site for link {link}: {e}")
        return None


class PagesSpider(scrapy.Spider):
    name = "pages"
    start_urls = getUrls()

    def parse(self, response):
        admission_terms = (
            r"(?:admission|apply|application|deadline|enroll|registration)"
        )
        date_pattern = (
            r"(?:\b(?:\d{1,2}[-./]\d{1,2}[-./](?:\d{4}|\d{2}))\b|"
            + r"\b(?:\d{1,2}[- ]?(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)[- ]?\d{2,4})\b|"
            + r"\b(?:\d{4}[-./]\d{1,2}[-./]\d{1,2})\b)"
        )
        word_pattern = rf"\b{admission_terms}\b"

        body_content = response.css("body").get()
        if not body_content:
            return

        cleaned_body_content = clean_body_content(body_content)

        date_matches = extract_context(cleaned_body_content, date_pattern)

        print(f"\n\nFound {len(date_matches)} date matches in {response.url}\n\n")

        if len(date_matches) != 0:
            for date_match in date_matches:
                if not is_likely_phone_number(date_match["match"]):
                    word_matches = re.findall(
                        word_pattern, date_match["context"], re.IGNORECASE
                    )
                    if word_matches:
                        site = get_site_from_link(response.url)
                        yield {
                            "url": response.url,
                            "site": site,
                            "date": date_match["match"],
                            "context": date_match["context"],
                        }


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
