import scrapy
from scrapy.linkextractors.lxmlhtml import LxmlLinkExtractor
import re
import pandas as pd
from bs4 import BeautifulSoup
from admission_scraper.utils import remove_trailing_slash
from db.session import get_db
from db.data import get_all_institutes


def get_sites() -> list[str]:
    all_institutes = get_all_institutes(next(get_db()))
    if all_institutes is not None:
        return [str(institute.website) for institute in all_institutes]
    return []


class UniSpider(scrapy.Spider):
    name = "uni"
    link_extractor = LxmlLinkExtractor()

    def start_requests(self):
        urls = get_sites()
        for url in urls:
            yield scrapy.Request(
                url=url, callback=self.parse, meta={"original_url": url}
            )

    def parse(self, response):
        admission_terms = [
            "admission",
            "announcement",
            "update",
            "notification",
            # "program",
            # "course",
            # "degree",
            "enrollment",
        ]
        word_pattern = r"\b(?:" + "|".join(admission_terms) + r")s?\b"

        # Use original URL from the CSV instead of response.url
        original_url = response.meta.get("original_url")

        # TODO: Actually update the initial url with the response.url in csv

        res = {
            "site": remove_trailing_slash(response.url),
            "original_url": remove_trailing_slash(original_url),
            "matched_links": [],
        }

        for link in self.link_extractor.extract_links(response):
            text_matches = re.findall(word_pattern, link.text, re.IGNORECASE)
            url_matches = re.findall(word_pattern, link.url, re.IGNORECASE)
            word_matches = [*text_matches, *url_matches]
            if (
                word_matches
                and remove_trailing_slash(link.url) not in res["matched_links"]
            ):
                res["matched_links"].append(remove_trailing_slash(link.url))
                print(f"Found matches {response.url} - {word_matches} in '{link.url}'")

        if not res["matched_links"]:
            links = response.css("a").getall()
            for link in links:
                soup = BeautifulSoup(link, "html.parser")
                link_href = soup.a.get("href") if soup.a else ""
                text = soup.a.get_text() if soup.a else ""
                if not link_href:
                    continue
                text_matches = re.findall(word_pattern, text, re.IGNORECASE)
                url_matches = re.findall(word_pattern, str(link_href), re.IGNORECASE)
                word_matches = [*text_matches, *url_matches]
                if word_matches:
                    if (
                        word_matches
                        and remove_trailing_slash(link_href) not in res["matched_links"]
                    ):
                        res["matched_links"].append(remove_trailing_slash(link_href))
                        print(
                            f"Found matches {response.url} - {word_matches} in '{link_href}'"
                        )

        yield res
