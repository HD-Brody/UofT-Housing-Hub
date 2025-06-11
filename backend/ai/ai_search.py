import os
import json
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def get_filters_from_query(user_query):
    system_prompt = (
        "You are a helpful assistant that extracts numeric housing search filters from vague or specific natural language queries. "
        "You must respond with ONLY a JSON object, with no explanation or markdown. "
        "The JSON must include exactly these keys: budget, bedrooms, bathrooms, max_walk_time. "
        "Each value must be an integer or float. Never return null. "
        "If the user is vague or omits a filter, infer a reasonable numeric value using common sense. "
        "Do not include any non-numeric or string values. Use your best judgment, and always return clean numbers. "

        "Guidelines:\n"
        "- 'reasonably priced' means $800–$1000 per person\n"
        "- Budget should be the total for all people (e.g., 3 people = $2400–$3000)\n"
        "- 'super close to campus' = 5 minutes walk\n"
        "- 'close to campus' = 15–20 minutes walk\n"
        "- 'not too far' = 25 minutes\n"
        "- If bathrooms are not mentioned, assume 1\n"
        "- If number of people is mentioned, assume same number of bedrooms\n"
        "- Round to clean numbers like 900, 1500, 2200, etc"
    )

    user_prompt = f"Extract filters from this message: '{user_query}'"

    response = client.chat.completions.create(
        model="gpt-4-1106-preview",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.2
    )

    content = response.choices[0].message.content.strip()

    # Clean up optional ```json blocks
    if content.startswith("```json"):
        content = content[7:-3].strip()
    elif content.startswith("```"):
        content = content[3:-3].strip()

    try:
        return json.loads(content)
    except json.JSONDecodeError:
        print("Failed to parse JSON:")
        print(content)
        return None


if __name__ == "__main__":
    test_query = "Find me a reasonably priced place for me and my two friends thats within walking distance to campus"
    filters = get_filters_from_query(test_query)
    print(filters)