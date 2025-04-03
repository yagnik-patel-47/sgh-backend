from google import genai
from google.genai import types
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

prompt = f"\ncontent:\n\n{content}"
base_prompt = ""

try:
    with open("base_prompt.txt", "r") as file:
        loaded_prompt = file.read().strip()

    # Add base prompt as system message if it exists and isn't empty
    if loaded_prompt:
        base_prompt = loaded_prompt
except FileNotFoundError:
    # If file doesn't exist, continue with the default system message
    pass

client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

response = client.models.generate_content(
    model="gemini-2.0-flash",
    contents=prompt,
    config={
        "system_instruction": base_prompt,
        "response_mime_type": "application/json",
        "response_schema": {
            "type": "object",
            "properties": {
                "announcements": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "required": ["title", "content", "announcement_type"],
                        "properties": {
                            "title": {
                                "type": "string",
                                "description": "Title of the announcement",
                            },
                            "content": {
                                "type": "string",
                                "description": "Main text content of the announcement",
                            },
                            "published_date": {
                                "type": "string",
                                "format": "date-time",
                                "description": "Date when the announcement was published (YYYY-MM-DD)",
                                "nullable": True,
                            },
                            "application_open_date": {
                                "type": "string",
                                "format": "date-time",
                                "description": "Date when applications open (YYYY-MM-DD)",
                                "nullable": True,
                            },
                            "application_deadline": {
                                "type": "string",
                                "format": "date-time",
                                "description": "Application deadline date (YYYY-MM-DD)",
                                "nullable": True,
                            },
                            "term": {
                                "type": "string",
                                "description": "Academic term referenced (e.g., 'Fall 2025')",
                                "nullable": True,
                            },
                            "contact_info": {
                                "type": "string",
                                "description": "Contact information provided in the announcement",
                                "nullable": True,
                            },
                            "announcement_type": {
                                "type": "string",
                                "enum": [
                                    "admission_dates",
                                    "contact_info",
                                    "general",
                                ],
                                "description": "Type of announcement",
                            },
                        },
                    },
                }
            },
        },
    },
)

response_text = response.candidates[0].content.parts[0].text
result_json = json.loads(response_text)
print(response_text)
print(result_json)
