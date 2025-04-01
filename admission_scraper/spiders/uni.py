import scrapy
from scrapy.linkextractors import LinkExtractor
import re
import pandas as pd
from bs4 import BeautifulSoup


def get_sites():
    df = pd.read_csv("sites.csv")
    return df["url"].tolist()[:50]


def remove_trailing_slash(url):
    if url.endswith("/"):
        return url[:-1]
    return url


class UniSpider(scrapy.Spider):
    name = "uni"
    start_urls = get_sites()
    link_extractor = LinkExtractor()

    def parse(self, response):
        admission_terms = r"(?:admission|apply|enroll|registration|announcement|update|notification|programs|courses|degree|application|intake|enrollment|entry|admit|acceptance|accepting)"
        word_pattern = rf"\b{admission_terms}\b"

        res = {
            "site": response.url,
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

        # links = response.css("a").getall()
        # for link in links:
        #     soup = BeautifulSoup(link, "html.parser")
        #     link = soup.a.get("href")
        #     text = soup.a.get_text()
        #     if not link:
        #         continue
        #     text_matches = re.findall(word_pattern, text, re.IGNORECASE)
        #     url_matches = re.findall(word_pattern, link, re.IGNORECASE)
        #     word_matches = [*text_matches, *url_matches]
        #     if word_matches:
        #         print(f"Found matches {word_matches} in '{link}'")

        yield res
