import os.path

import pytest
from _pytest.mark import ParameterSet
from pdf_parser import get_data_from_pdf
from helper.helpers import get_project_root
from enum import StrEnum


class Parameter(StrEnum):
    COORDINATES = 'coordinates'
    TYPE_KEY = 'type_key'
    TYPE_VALUE = 'type_value'
    KEY_FONT_INFO = 'key_font_info'
    VALUE_FONT_INFO = 'val_font_info'
    VALUE = 'value'


root = get_project_root()
etalon: dict = get_data_from_pdf(os.path.join(root, 'test_task.pdf'))
# ticket: dict = get_data_from_pdf(os.path.join(root, 'data_for_tests/test_task_1.pdf'))
ticket: dict = get_data_from_pdf(os.path.join(root, 'tests', 'data_for_tests/test_task_wrong_value_location.pdf'))


def get_test_data(param: Parameter) -> list[ParameterSet]:
    pairs = []
    etalon_body = etalon['body']
    ticket_body = ticket['body']

    for key in etalon_body.keys():
        if key not in ticket_body:
            continue
        pairs.append(
            pytest.param(etalon_body[key][param.value], ticket_body[key][param.value], id=f"Key: {key}")
        )

    return pairs


class TestTicket:

    def test_sheet_size(self):
        assert etalon['meta_data']['sheet_size'] == ticket['meta_data']['sheet_size']

    def test_all_positions_on_sheet(self):
        etalon_key = set(etalon.get('body').keys())
        ticket_key = set(ticket.get('body').keys())
        assert etalon_key ^ ticket_key == set()

    @pytest.mark.parametrize('ticket, etalon', get_test_data(param=Parameter.COORDINATES))
    def test_text_position(self, ticket, etalon):
        assert ticket['x0'] == etalon['x0']
        assert ticket['y0'] == etalon['y0']

    @pytest.mark.parametrize('ticket, etalon', get_test_data(param=Parameter.TYPE_KEY))
    def test_type_key(self, ticket, etalon):
        assert ticket['pattern'] == etalon['pattern']
        assert ticket['type'] == etalon['type']

    @pytest.mark.parametrize('ticket, etalon', get_test_data(param=Parameter.TYPE_VALUE))
    def test_type_value(self, ticket, etalon):
        assert ticket['pattern'] == etalon['pattern']
        assert ticket['type'] == etalon['type']

    @pytest.mark.parametrize('ticket, etalon', get_test_data(param=Parameter.KEY_FONT_INFO))
    def test_key_font_info(self, ticket, etalon):
        assert ticket['font_name'] == etalon['font_name']
        assert ticket['font_size'] == etalon['font_size']

    @pytest.mark.parametrize('ticket, etalon', get_test_data(param=Parameter.VALUE_FONT_INFO))
    def test_value_font_info(self, ticket, etalon):
        assert ticket['font_name'] == etalon['font_name']
        assert ticket['font_size'] == etalon['font_size']