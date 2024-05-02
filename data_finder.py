import json
import re
from datetime import datetime
import os
import fitz
from dateutil import parser
from pdfminer.high_level import extract_pages
from pdfminer.pdfparser import PDFParser
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfpage import PDFPage
from pdfminer.layout import LTTextBoxHorizontal

"""
Каждый из приведенных выше типов имеет .bboxсвойство, которое содержит кортеж ( x0 , y0 , x1 , y1 ), 
содержащий координаты левой, нижней, правой и верхней части объекта соответственно. 
Координаты Y даны как расстояние от нижнего края страницы. Если вам удобнее работать с осью Y,
 идущей сверху вниз, вы можете вычесть их из высоты страницы .mediabox:
"""


def detect_txt_format(value: str) -> dict:
    patterns = [
        r'^[A-Z]+$',
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


def get_pdf_page_size(pdf_path):
    with open(pdf_path, 'rb') as fp:
        parser = PDFParser(fp)
        document = PDFDocument(parser)
        page = next(PDFPage.create_pages(document), None)

        if page:
            mediabox = page.mediabox
            if mediabox:
                width = mediabox[2] - mediabox[0]
                height = mediabox[3] - mediabox[1]
                return (width, height)

    return None


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
    text_blocks = extract_data(pdf_path)
    # for k in text_blocks:
    #     print(k)

    for k, v in text_blocks.items():
        print(f"{k}: {v}")

    with open('result.json', 'w') as fp:
        json.dump(text_blocks, fp)
