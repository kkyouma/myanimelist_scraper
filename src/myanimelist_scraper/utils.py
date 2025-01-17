import re
from datetime import UTC, datetime


def name_formatter(input_string: str) -> str:
    """Convert string to arbitrary name convention."""
    # Convert the string to lowercase
    lower_case_string = input_string.lower()

    # Replace spaces and special characters with underscores
    snake_case_string = re.sub(r"[^a-z0-9]+", "_", lower_case_string).strip("_")

    # Get the current date
    current_date = datetime.now(tz=UTC).strftime("%Y-%m-%d")

    # Combine the snake_case string with the date
    return f"{snake_case_string}_{current_date}"
