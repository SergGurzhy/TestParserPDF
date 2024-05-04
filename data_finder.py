import json
import re
from datetime import datetime
from typing import Iterable
from dateutil import parser
from pdfminer.high_level import extract_pages
from pdfminer.pdfparser import PDFParser
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfpage import PDFPage
from pdfminer.layout import LTTextContainer, LTChar
from helpers.patterns import STR_PATTERNS, DATE_FORMATS


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


def get_pdf_page_size(pdf_path) -> tuple:
    with open(pdf_path, 'rb') as fp:
        parser = PDFParser(fp)
        document = PDFDocument(parser)
        page = next(PDFPage.create_pages(document), None)

        if page:
            mediabox = page.mediabox
            if mediabox:
                width = mediabox[2] - mediabox[0]
                height = mediabox[3] - mediabox[1]
                return width, height

    return None


def get_data_from_pdf(pdf_path):
    data = {
        'meta_data': {},
        'body': {}
    }

    page_size = get_pdf_page_size(pdf_path)

    if page_size is None:
        return None

    width, height = page_size
    data['meta_data']['sheet_size'] = {
        'width': width,
        'height': height
    }

    for page_layout in extract_pages(pdf_path):
        for element in page_layout:
            if isinstance(element, LTTextContainer):
                for text_line in element:
                    if isinstance(text_line, Iterable):
                        key_done = False
                        key = ''
                        value = ''
                        coordinates = {}
                        separator = ''
                        key_font_info = {
                            'font_name': set(),
                            'font_size': set(),
                        }
                        val_font_info = {
                            'font_name': set(),
                            'font_size': set(),
                        }
                        index = 0
                        for character in text_line:
                            if isinstance(character, LTChar):
                                if index == 0:
                                    x0, y0, _, _ = character.bbox
                                    coordinates['x0'] = str(round(x0, 3))
                                    coordinates['y0'] = str(round(y0, 3))

                                char = character.get_text()
                                if char != ':' and not key_done:
                                    key += char
                                    key_font_info['font_name'].add(character.fontname)
                                    key_font_info['font_size'].add(character.size)

                                if char == ':' and not key_done:
                                    separator += char
                                    key_done = True

                                if char != ':' and key_done:
                                    value += char
                                    val_font_info['font_name'].add(character.fontname)
                                    val_font_info['font_size'].add(character.size)

                                index += 1

                        key_done = False

                        key_font_info['font_name'] = key_font_info['font_name'].pop()
                        key_font_info['font_size'] = str(round(key_font_info['font_size'].pop(), 3))

                        if value:
                            val_font_info['font_name'] = str(next(iter(val_font_info['font_name'])))
                            val_font_info['font_size'] = str(round(next(iter(val_font_info['font_size'])), 3))
                        else:
                            val_font_info['font_name'] = ''
                            val_font_info['font_size'] = ''

                        data['body'][key] = {
                            'value': value,
                            'type_value': determine_value_type(value),
                            'type_key': determine_value_type(key),
                            'key_font_info': key_font_info,

                            'val_font_info': val_font_info,
                            'separator': separator,
                            'coordinates': coordinates,
                        }

    return data


if __name__ == '__main__':
    # Пример использования
    pdf_path = 'test_task.pdf'
    data = get_data_from_pdf(pdf_path)

    with open('result_1.json', 'w') as fp:
        json.dump(data, fp)
