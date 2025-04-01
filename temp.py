from openai import OpenAI

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

client = OpenAI(base_url="http://127.0.0.1:1234/v1", api_key="lm-studio")
MODEL = "llama-3.2-1b-instruct"

response = client.chat.completions.create(
    model=MODEL,
    messages=prompt,
    response_format={
        "type": "json_schema",
        "json_schema": {
            "name": "admission_dates",
            "schema": {
                "type": "object",
                "properties": {
                    "dates": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "required": ["date", "context"],
                            "properties": {
                                "date": {
                                    "type": "string",
                                },
                                "context": {
                                    "type": "string",
                                },
                                "possible_context": {
                                    "type": "string",
                                },
                            },
                        },
                    },
                },
                "required": ["dates"],
                "additionalProperties": False,
            },
        },
    },
)


print(response.choices[0].message.content)


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
