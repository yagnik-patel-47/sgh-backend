from bs4 import BeautifulSoup
import re


def extract_context(text, regex_pattern, before=50, after=50):
    # Find all matches of the regex in the text
    matches = list(re.finditer(regex_pattern, text))
    if not matches:
        return []

    results = []
    for match in matches:
        # Get the start and end positions of the match
        start_pos = match.start()
        end_pos = match.end()
        matched_text = match.group()

        # Split the text into tokens (words)
        tokens = text.split()

        # Convert character positions to token positions
        char_count = 0
        token_start = 0
        token_end = 0
        token_positions = []

        for i, token in enumerate(tokens):
            token_positions.append(char_count)
            char_count += len(token) + 1  # +1 for the space

        # Find the token indices corresponding to start_pos and end_pos
        for i, pos in enumerate(token_positions):
            if pos <= start_pos:
                token_start = i
            if pos <= end_pos:
                token_end = i

        # Calculate the range for extraction
        extract_start = max(0, token_start - before)  # Ensure we don't go below 0
        extract_end = min(
            len(tokens), token_end + after
        )  # Ensure we don't exceed text length

        # Extract the tokens and join them back into a string
        context_tokens = tokens[extract_start:extract_end]
        context_text = " ".join(context_tokens)

        results.append(
            {
                "match": matched_text,
                "context": context_text,
                "start_token": extract_start,
                "end_token": extract_end,
            }
        )

    # Combine results with the same matched text
    combined_results = {}
    for result in results:
        match_text = result["match"]
        if match_text in combined_results:
            # Merge contexts
            existing = combined_results[match_text]
            new_context = existing["context"] + "\n\n" + result["context"]

            # Update token ranges
            start_token = min(existing["start_token"], result["start_token"])
            end_token = max(existing["end_token"], result["end_token"])

            combined_results[match_text] = {
                "match": match_text,
                "context": new_context,
                "start_token": start_token,
                "end_token": end_token,
            }
        else:
            combined_results[match_text] = result

    results = list(combined_results.values())

    return results


def clean_body_content(body_content):
    soup = BeautifulSoup(body_content, "html.parser")

    for script_or_style in soup(["script", "style"]):
        script_or_style.extract()

    # Get text or further process the content
    cleaned_content = soup.get_text(separator="\n")
    cleaned_content = "\n".join(
        line.strip() for line in cleaned_content.splitlines() if line.strip()
    )

    return cleaned_content
