import scrapy
import pandas as pd
import re
from openai import OpenAI
from admission_scraper.utils import clean_body_content


client = OpenAI(base_url="http://127.0.0.1:1234/v1", api_key="lm-studio")
MODEL = "llama-3.2-1b-instruct"


def getLLMResponse(prompt, model=MODEL):
    """
    Get a response from the LM Studio model.
    """
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {
                "role": "system",
                "content": "You are a helpful assistant that extracts dates related to admission from text.",
            },
            *prompt,
        ],
        response_format={
            "type": "json_schema",
            "json_schema": {
                "type": "array",
                "items": {
                    "type": "object",
                    "required": ["date", "context"],
                    "properties": {
                        "date": {
                            "type": "string",
                            "description": "The extracted date in YYYY-MM-DD format, or 'error' if parsing failed",
                            "pattern": "^(\\d{4}-\\d{2}-\\d{2}|error)$",
                        },
                        "context": {
                            "type": "string",
                            "description": "Description of the date's relevance or error message if date parsing failed",
                        },
                        "possible_context": {
                            "type": "string",
                            "description": "Alternative interpretation when context is ambiguous (optional)",
                        },
                    },
                    "additionalProperties": False,
                },
            },
        },
    )
    return response.choices[0].message["content"]


def getUrls():
    df = pd.read_json("uni.json")
    urls = df["matched_links"].tolist()
    urls = [url for sublist in urls for url in sublist]
    urls = list(set(urls))  # Remove duplicates
    return urls[:20]  # Limit to 50 URLs


class PagesSpider(scrapy.Spider):
    name = "pages"
    start_urls = getUrls()

    def parse(self, response):
        admission_terms = (
            r"(?:admission|apply|application|deadline|enroll|registration)"
        )
        date_pattern = r"(?:(?:\d{1,2}[-./]\d{1,2}[-./]\d{2,4})|(?:\d{1,2}[- ]?(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)[ -]?\d{2,4})|(?:\d{4}[-./]\d{1,2}[-./]\d{1,2}))"
        word_pattern = rf"\b{admission_terms}\b"

        body_content = response.css("body").get()
        if not body_content:
            return

        cleaned_body_content = clean_body_content(body_content)

        date_matches = re.findall(date_pattern, cleaned_body_content)
        word_matches = re.findall(word_pattern, cleaned_body_content, re.IGNORECASE)
        if date_matches and word_matches:
            print(cleaned_body_content)
            # resp = getLLMResponse(
            #     [
            #         {
            #             "role": "user",
            #             "content": cleaned_body_content,
            #         }
            #     ]
            # )
            # print(f"Response: {resp}")
