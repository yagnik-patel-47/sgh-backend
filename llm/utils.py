import json
import os


def extract_program_names() -> list[str]:
    try:
        json_path = os.path.join("seed_data", "programs.json")

        with open(json_path, "r") as f:
            programs = json.load(f)

        program_names = [program["name"] for program in programs]

        return program_names

    except Exception as e:
        print(f"Error extracting program names: {e}")
