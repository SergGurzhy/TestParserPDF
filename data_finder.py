import json
import re
from datetime import datetime
import os
from typing import Iterable

import fitz
from dateutil import parser
from pdfminer.high_level import extract_pages
from pdfminer.pdfparser import PDFParser
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfpage import PDFPage
from pdfminer.layout import LTTextBoxHorizontal, LTTextContainer, LTChar

"""
Каждый из приведенных выше типов имеет .bboxсвойство, которое содержит кортеж ( x0 , y0 , x1 , y1 ), 
содержащий координаты левой, нижней, правой и верхней части объекта соответственно. 
Координаты Y даны как расстояние от нижнего края страницы. Если вам удобнее работать с осью Y,
 идущей сверху вниз, вы можете вычесть их из высоты страницы .mediabox:
"""


def detect_txt_format(value: str) -> dict:
    patterns = [
        r'^[A-Z]+$',
        r'^[A-Z ]+$',
        r'^[a-z]+$',
        r'^[A-Z0-9]+$',
        r'^[a-z0-9]+$',
        r'^[a-zA-Z0-9]+$'
    ]
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
    date_formats = [
        '%d.%m.%Y',
        '%m.%d.%Y',
        '%Y.%m.%d',
        '%Y.%d.%m',
    ]
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


def clear_word(word: str) -> str:
    word = word.strip()
    index = word.find(':')
    if len(word) > 1 and index > -1:
        return word[:index]
    return word


def extract_words_details(pdf_path):
    text_details = {}

    pdf_document = fitz.open(pdf_path)
    page = pdf_document[0]
    text_details['fonts'] = page.get_fonts()

    text_blocks = page.get_text("dict")["blocks"]

    for block in text_blocks:
        if "lines" in block:
            for line in block["lines"]:
                for span in line["spans"]:
                    text_details[clear_word(span['text'])] = {
                        'font_name': span['font'],
                        'font_size': round(span['size'], 3),
                        'font_color': span['color'],
                    }

    pdf_document.close()

    for key in list(text_details.keys()):
        if key == "":
            del text_details[key]

    return text_details


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


def extract_text_with_font_details(pdf_path):
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


def extract_data(pdf_path):
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

    page_details = extract_words_details(pdf_path)

    for page_layout in extract_pages(pdf_path):
        for element in page_layout:
            if isinstance(element, LTTextBoxHorizontal):
                text = element.get_text().strip()
                x0, y0, _, _, = element.bbox
                key, val, sep = get_key_value(text)

                data['body'][key] = {
                    'value': val,
                    'type_value': determine_value_type(val),
                    'type_key': determine_value_type(key),
                    'separator': sep,
                    'key_font': page_details.get(key),
                    'val_font': page_details.get(val),
                    'coordinates': {
                        'x0': round(x0, 3),
                        'y0': round(y0, 3),
                    }
                }

    return data


def get_key_value(text: str) -> tuple[str, str, str]:
    sep_index = text.find(':')
    key = text[:sep_index].strip() if sep_index > -1 else text.strip()
    val = text[sep_index + 1:].strip() if sep_index > -1 else ''

    # line_break_index = val.find('\n')
    # if line_break_index > -1:
    #     val = val[:line_break_index].strip()

    separator = ':' if sep_index > -1 else ''
    return key, val, separator


def get_project_root() -> str:
    current_file = os.path.abspath(__file__)
    while not os.path.isfile(os.path.join(current_file, 'test_task.pdf')):
        current_file = os.path.dirname(current_file)

    return current_file


if __name__ == '__main__':
    # Пример использования
    pdf_path = 'test_task.pdf'
    data = extract_text_with_font_details(pdf_path)

    text_blocks = extract_data(pdf_path)

    # for k, v in text_blocks.items():
    #     print(f"{k}: {v}")
    #
    with open('result_1.json', 'w') as fp:
        json.dump(data, fp)

    # with open('result_1.json', 'w') as fp:
    #     json.dump(text_blocks, fp)
