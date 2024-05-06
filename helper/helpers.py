import os
import re
from datetime import datetime
from dateutil import parser
from helper.patterns import STR_PATTERNS, DATE_FORMATS


def get_project_root() -> str:
    current_file = os.path.abspath(__file__)
    while not os.path.isfile(os.path.join(current_file, 'README.md')):
        current_file = os.path.dirname(current_file)

    return current_file


def detect_txt_format(value: str) -> dict:
    patterns = STR_PATTERNS
    for pattern in patterns:
        if bool(re.match(pattern, value)):
            return {
                "type": "string",
                "pattern": pattern
            }

    return {
        "type": 'string',
        "pattern": ''
    }


def detect_date_format(value: str) -> dict:
    date_formats = DATE_FORMATS
    try:
        _ = parser.parse(value, dayfirst=True)
    except ValueError:
        return {
            "type": '',
            "pattern": ''
        }
    else:
        for fmt in date_formats:
            try:
                datetime.strptime(value, fmt)
                return {"type": "date",
                        "pattern": fmt}
            except ValueError:
                continue
    return {
        "type": 'string',
        "pattern": ''
    }


def determine_value_type(value) -> dict:
    if not value:
        return {
            "type": "string",
            "pattern": ''
        }
    value = value.strip()

    pattern = r"^\d+$"
    has_only_numbers = bool(re.match(pattern, value))
    if has_only_numbers:
        return {
            "type": "number",
            "pattern": pattern
        }

    date = detect_date_format(value)
    if date.get('pattern'):
        return date

    string = detect_txt_format(value)
    if string:
        return string

    return {
        "type": "string",
        "pattern": ''
    }
