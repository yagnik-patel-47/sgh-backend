from openai import OpenAI
from groq import Groq
from dotenv import load_dotenv
import os
import json

load_dotenv()

content = """
Last date to apply for UG & PG programmes for this round of admissions
12 Apr 2025
Jaipur
Campus
Last date to apply for UG & PG programmes for this round of admissions
15 Apr 2025
Amity Universe
"""

prompt = [{"role": "user", "content": f"content:\n\n{content}"}]


try:
    with open("base_prompt.txt", "r") as file:
        base_prompt = file.read().strip()

    # Add base prompt as system message if it exists and isn't empty
    if base_prompt:
        prompt.insert(0, {"role": "system", "content": base_prompt})
except FileNotFoundError:
    # If file doesn't exist, continue with the default system message
    pass

# client = OpenAI(base_url="http://127.0.0.1:1234/v1", api_key="lm-studio")
# MODEL = "llama-3.2-1b-instruct"
client = Groq(
    api_key=os.environ.get("GROQ_API_KEY"),
)

response = client.chat.completions.create(
    model="llama-3.1-8b-instant",
    messages=prompt,
    response_format={
        "type": "json_object",
        # "json_schema": {
        #     "name": "admission_announcements",
        #     "schema": {
        #         "type": "object",
        #         "properties": {
        #             "announcements": {
        #                 "type": "array",
        #                 "items": {
        #                     "type": "object",
        #                     "required": ["title", "content", "announcement_type"],
        #                     "properties": {
        #                         "title": {
        #                             "type": "string",
        #                             "description": "Title of the announcement",
        #                         },
        #                         "content": {
        #                             "type": "string",
        #                             "description": "Main text content of the announcement",
        #                         },
        #                         "published_date": {
        #                             "type": "string",
        #                             "format": "date",
        #                             "description": "Date when the announcement was published (YYYY-MM-DD)",
        #                         },
        #                         "application_open_date": {
        #                             "type": ["string", "null"],
        #                             "format": "date",
        #                             "description": "Date when applications open (YYYY-MM-DD)",
        #                         },
        #                         "application_deadline": {
        #                             "type": ["string", "null"],
        #                             "format": "date",
        #                             "description": "Application deadline date (YYYY-MM-DD)",
        #                         },
        #                         "term": {
        #                             "type": ["string", "null"],
        #                             "description": "Academic term referenced (e.g., 'Fall 2025')",
        #                         },
        #                         "contact_info": {
        #                             "type": ["string", "null"],
        #                             "description": "Contact information provided in the announcement",
        #                         },
        #                         "announcement_type": {
        #                             "type": "string",
        #                             "enum": [
        #                                 "admission_dates",
        #                                 "contact_info",
        #                                 "general",
        #                             ],
        #                             "description": "Type of announcement",
        #                         },
        #                     },
        #                 },
        #             }
        #         },
        #         "required": ["announcements"],
        #         "additionalProperties": False,
        #     },
        # },
    },
)

result_json = json.loads(response.choices[0].message.content)
print(response.choices[0].message.content)
print(result_json)


# "$defs": {
#     "date": {
#         "type": "object",
#         "required": ["date", "context"],
#         "properties": {
#             "date": {
#                 "type": "string",
#                 "description": "The extracted date in YYYY-MM-DD format, or 'error' if parsing failed",
#                 "pattern": "^(\\d{4}-\\d{2}-\\d{2}|error)$",
#             },
#             "context": {
#                 "type": "string",
#                 "description": "Description of the date's relevance or error message if date parsing failed",
#             },
#             "possible_context": {
#                 "type": "string",
#                 "description": "Alternative interpretation when context is ambiguous (optional)",
#             },
#         },
#     }
# },
