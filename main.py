from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from admission_scraper.spiders.pages import PagesSpider
from admission_scraper.spiders.uni import UniSpider
from llm.process import content_changed, process_page
from db.session import get_db
from db.data import get_all_scraped_pages
import pandas as pd

settings = get_project_settings()


def main():
    process = CrawlerProcess(settings)

    deferred = process.crawl(UniSpider)
    deferred.addCallback(lambda _: process.crawl(PagesSpider))
    process.start()

    try:
        df = pd.read_json("pages.jsonl", lines=True)

        grouped_df = (
            df.groupby("url")
            .apply(
                lambda x: pd.Series(
                    {
                        "site": x["site"].iloc[0],
                        "items": x.to_dict("records"),
                    }
                ),
                include_groups=False,
            )
            .reset_index()
        )
        df = grouped_df

        db = next(get_db())
        scraped_pages = get_all_scraped_pages(db)
        scraped_urls = (
            [page.url for page in scraped_pages] if scraped_pages is not None else []
        )

        for i, (_, row) in enumerate(df.iterrows()):
            print("Processing group", i + 1, "of", len(df))
            if row["url"] in scraped_urls:
                print(f"Skipping {row['url']}")
                continue

            merged_content = " ".join(
                [
                    item["context"]
                    for item in row["items"]
                    if item["context"] is not None
                ]
            )
            if not content_changed(row["url"], merged_content):
                print(f"Skipping unchanged content for {row['url']}")
                continue
            process_page(row["url"], row["site"], row["items"])
            print(f"Processed group {i + 1} - {row['url']}")
    except Exception as e:
        print(f"Error processing group: {e}")


if __name__ == "__main__":
    main()
