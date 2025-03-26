import scrapy
import re
from admission_scraper.utils import clean_body_content


class UniSpider(scrapy.Spider):
    name = "uni"
    allowed_domains = ["www.unigoa.ac.in", "cuo.ac.in"]
    start_urls = [
        # "https://www.unigoa.ac.in/systems/c/admissions/announcementsnotices.html",
        "https://cuo.ac.in/admission_2025_UG.asp",
    ]

    def parse(self, response):
        body = response.css("body").get()

        if body:
            cleaned_content = clean_body_content(body)
            print(cleaned_content)
        # for el in response.css("body"):
        #     item = AdmissionScraperItem()
        #     item["url"] = response.url
        #     html = el.extract()
        #     page_content = md(html)

        #     admission_terms = r"(?:admission|apply|application|deadline|enroll|registration|announcement|update|notification)"
        #     context_terms = r"(?:requirements|process|spring|fall|semester|term|student|undergraduate|graduate)"
        #     word_pattern = rf"\b{admission_terms}\b|\b{context_terms}\b"
        #     date_pattern = r"(?:(?:\d{1,2}[-./]\d{1,2}[-./]\d{2,4})|(?:\d{1,2}[- ]?(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)[ -]?\d{2,4})|(?:\d{4}[-./]\d{1,2}[-./]\d{1,2}))"

        #     line_number = 0
        #     found_matches = []
        #     lines = page_content.strip().split("\n")

        #     for line in lines:
        #         line_number += 1
        #         clean_line = self.clean_text_edges(line)

        #         print(f"Checking line {line_number}: {clean_line}")
        #         date_matches = re.findall(date_pattern, line)

        #         if date_matches:
        #             word_matches = re.findall(word_pattern, line, re.IGNORECASE)
        #             if word_matches:
        #                 print(
        #                     f"Found matches {word_matches} with dates {date_matches} in '{clean_line}'"
        #                 )
        #                 found_matches.append(
        #                     {
        #                         "line": line_number,
        #                         "text": clean_line,
        #                         "word_matches": word_matches,
        #                         "date_matches": date_matches,
        #                     }
        #                 )

        #     if found_matches:
        #         print("Found admission-related information:")
        #         item["matches"] = found_matches
        #         for match in found_matches:
        #             match_info = (
        #                 f"Line {match['line']}: Matches {match['word_matches']}"
        #             )
        #             if match.get("date_matches"):
        #                 match_info += f" with dates {match['date_matches']}"
        #             match_info += f" in '{match['text']}'"
        #             print(match_info)
        #     else:
        #         item["matches"] = []
        #         print("No admission or announcement information found.")
        #     yield item

    def clean_text_edges(self, text):
        """Clean up the text by removing pipe characters and spaces at the beginning and end only."""
        # Trim leading and trailing whitespace
        text = text.strip()

        # Remove pipe character and whitespace from beginning
        text = re.sub(r"^[\s|]+", "", text)
        text = re.sub(r"[\s|]+$", "", text)
        return text
