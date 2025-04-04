from groq import Groq
from dotenv import load_dotenv
import os
import json
from utils import extract_program_names

load_dotenv()

content = """
Admission Notice 2024-25 for Payment Click to view | Notice for NAD Digilocker ABC ID Click to view | Home / PG Diploma Courses PG Diploma Courses PG Diploma Courses Date: 20/06/2023 Letter No. : CNLU/PGDC/2023-06 : List of selected candidates for Post Graduate Diploma Courses at CNLU, Patna Date: 31/03/2023 Notice for PG Diploma Courses Chanakya National Law University, Patna has begin One Year Post Graduate Diploma Course for the Academic Session 2022 – 2023. a) Post Graduate Diploma in Human Rights. b) Post Graduate Diploma in Cyber Law. c) Post Graduate Diploma in Intellectual Property Law. d) Post Graduate
"""
url = "https://cnlu.ac.in/pg-diploma-courses/"
prompt = [{"role": "user", "content": f"Text Chunk:\n{content}\nSource URL: {url}"}]

try:
    with open("base_prompt.txt", "r") as file:
        base_prompt = file.read().strip()

    # Add base prompt as system message if it exists and isn't empty
    if base_prompt:
        prompt.insert(0, {"role": "system", "content": base_prompt})
except FileNotFoundError:
    # If file doesn't exist, continue with the default system message
    pass

client = Groq(
    api_key=os.environ.get("GROQ_API_KEY"),
)
programs = extract_program_names()

response = client.chat.completions.create(
    model="llama-3.1-8b-instant",
    messages=prompt,
    stream=False,
    response_format={
        "type": "json_object",
        "json_schema": {
            "name": "admission_announcements",
            "schema": {
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
                                    "format": "date",
                                    "description": "Date when the announcement was published (YYYY-MM-DD)",
                                },
                                "application_open_date": {
                                    "type": ["string", "null"],
                                    "format": "date",
                                    "description": "Date when applications open (YYYY-MM-DD)",
                                },
                                "application_deadline": {
                                    "type": ["string", "null"],
                                    "format": "date",
                                    "description": "Application deadline date (YYYY-MM-DD)",
                                },
                                "term": {
                                    "type": ["string", "null"],
                                    "description": "Academic term referenced (e.g., 'Fall 2025')",
                                },
                                "contact_info": {
                                    "type": ["string", "null"],
                                    "description": "Contact information provided in the announcement",
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
                                "programs_courses": {
                                    "type": "array",
                                    "items": {
                                        "type": "string",
                                        "enum": programs,
                                        "description": "Names of programs or courses related to the announcement",
                                    },
                                },
                            },
                        },
                    }
                },
                "required": ["announcements"],
                "additionalProperties": False,
            },
        },
    },
)

result_json = json.loads(response.choices[0].message.content)
print(response.choices[0].message.content)
print(result_json)
