from google import genai
from google.genai import types
from dotenv import load_dotenv
import os
import json
from utils import extract_program_names

load_dotenv()

content = """
Admission Notice 2024-25 for Payment Click to view | Notice for NAD Digilocker ABC ID Click to view | Home / PG Diploma Courses PG Diploma Courses PG Diploma Courses Date: 20/06/2023 Letter No. : CNLU/PGDC/2023-06 : List of selected candidates for Post Graduate Diploma Courses at CNLU, Patna Date: 31/03/2023 Notice for PG Diploma Courses Chanakya National Law University, Patna has begin One Year Post Graduate Diploma Course for the Academic Session 2022 – 2023. a) Post Graduate Diploma in Human Rights. b) Post Graduate Diploma in Cyber Law. c) Post Graduate Diploma in Intellectual Property Law. d) Post Graduate
"""
url = "https://cnlu.ac.in/pg-diploma-courses/"

prompt = f"Text Chunk:\n{content}\nSource URL: {url}"
base_prompt = ""
programs = extract_program_names()

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
        },
    },
)

response_text = response.candidates[0].content.parts[0].text
result_json = json.loads(response_text)
print(response_text)
print(result_json)
