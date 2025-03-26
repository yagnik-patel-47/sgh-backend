import scrapy
import re
from dateutil.parser import parse
import spacy
from collections import defaultdict


class AdmissionsScraperSpider(scrapy.Spider):
    name = "add"
    allowed_domains = ["www.unigoa.ac.in", "cuo.ac.in"]
    start_urls = [
        # "https://www.unigoa.ac.in/systems/c/admissions/announcementsnotices.html",
        "https://cuo.ac.in/admission_2025_UG.asp",
    ]

    def __init__(self):
        # Load spaCy model for NLP
        self.nlp = spacy.load("en_core_web_sm")
        # Store extracted data: {activity: date}
        self.admission_data = defaultdict(list)
        # Track the current section for context
        self.current_section = "General"

    def parse(self, response):
        # Step 1: Extract all text content with some structural context
        self.extract_text_with_context(response)

        # Step 2: Process the extracted data and yield results
        yield self.process_extracted_data()

    def extract_text_with_context(self, response):
        # Extract all headings to track sections
        headings = response.xpath("//h1 | //h2 | //h3 | //h4")
        for heading in headings:
            heading_text = heading.xpath(".//text()").get()
            if heading_text:
                self.current_section = heading_text.strip()

            # Extract all text elements following this heading until the next heading
            following_elements = heading.xpath("following-sibling::*")
            for element in following_elements:
                # Stop if we hit another heading
                if element.xpath("self::h1 | self::h2 | self::h3 | self::h4"):
                    break

                # Extract text from paragraphs, lists, divs, spans, etc.
                text = " ".join(element.xpath(".//text()").getall()).strip()
                if text:
                    # Process the text to extract dates and activities
                    self.extract_dates_and_activities(text, self.current_section)

    def extract_dates_and_activities(self, text, section):
        # Define a comprehensive regex pattern for dates
        date_pattern = r"\b(\d{1,2}\.\d{1,2}\.\d{4}|\d{1,2}\s*(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)\s*\d{4}|\d{1,2}(?:st|nd|rd|th)?\s*(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)\s*\d{4})\b"
        matches = re.finditer(date_pattern, text, re.IGNORECASE)

        for match in matches:
            date_str = match.group(0)
            date_start, date_end = match.span()

            # Normalize the date
            normalized_date = self.normalize_date(date_str)
            if not normalized_date:
                continue

            # Extract the activity (text before the date)
            activity = text[:date_start].strip()
            if not activity:
                continue

            # Clean up the activity
            activity = self.clean_activity(activity, section)

            # Store the activity and date
            if activity:
                self.admission_data[activity].append(normalized_date)

    def normalize_date(self, date_str):
        # Remove time part if present (e.g., "11:59 P.M.")
        date_str = re.sub(r"\s*\(\d{1,2}:\d{2}\s*(?:A\.M\.|P\.M\.)\)", "", date_str)
        try:
            # Parse the date using dateutil
            parsed_date = parse(date_str, dayfirst=True, fuzzy=True)
            # Convert to a consistent format (DD.MM.YYYY)
            return parsed_date.strftime("%d.%m.%Y")
        except ValueError:
            return None

    def clean_activity(self, activity, section):
        # Remove trailing prepositions or conjunctions
        activity = re.sub(
            r"\b(is|on|by|until|upto|to|for|from)\b.*$",
            "",
            activity,
            flags=re.IGNORECASE,
        ).strip()

        # Use spaCy to extract meaningful phrases
        doc = self.nlp(activity)
        # Look for noun phrases or verb phrases that describe the activity
        for chunk in doc.noun_chunks:
            activity_text = chunk.text.strip()
            if activity_text:
                # Add section context to disambiguate
                return f"{section}: {activity_text}"

        # Fallback: Look for specific keywords
        if "last date" in activity.lower():
            return f"{section}: Last Date to Submit Applications"
        elif "closing date" in activity.lower():
            return f"{section}: Closing Date"
        elif "commencement" in activity.lower():
            return f"{section}: Commencement"
        elif "announcement" in activity.lower():
            return f"{section}: Announcement"

        # If no meaningful activity is found, return None
        return None

    def process_extracted_data(self):
        # Deduplicate and select the most recent date for each activity
        final_data = {}
        for activity, dates in self.admission_data.items():
            if dates:
                # Sort dates and take the most recent one (in case of duplicates)
                sorted_dates = sorted(
                    dates, key=lambda x: parse(x, dayfirst=True), reverse=True
                )
                final_data[activity] = sorted_dates[0]

        return final_data
