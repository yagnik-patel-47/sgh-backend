import scrapy
import pandas as pd
from db.session import get_db
from db.models import Institute
from db.data import get_institute_from_website
from admission_scraper.utils import remove_trailing_slash


def get_sites():
    df = pd.read_csv("data/central_universities.csv")
    return df["url"].tolist()


class FixUrlSpider(scrapy.Spider):
    name = "fix_url"
    db = next(get_db())

    def start_requests(self):
        urls = get_sites()
        for url in urls:
            yield scrapy.Request(
                url=url, callback=self.parse, meta={"original_url": url}
            )

    def parse(self, response):
        original_url = response.meta.get("original_url")

        ins = get_institute_from_website(self.db, remove_trailing_slash(original_url))
        # if (ins is not None) and (ins.website != response.url):
        #     print(f"Updating URL for {ins.name} from {ins.website} to {response.url}")
        #     ins.website = response.url
        #     self.db.commit()
        yield {
            "name": ins.name,
            "original_url": original_url,
            "updated_url": response.url,
        }
