import pytest
from data_finder import get_data_from_pdf
from helpers.helpers import get_project_root

root = get_project_root()
etalon = get_data_from_pdf(f'{root}/test_task.pdf')
ticket = get_data_from_pdf(f'{root}/tests/tests_data/test_task_1.pdf')


def get_test_data():
    pairs = []
    etalon_body = etalon['body']
    ticket_body = ticket['body']
    for el in etalon_body.keys():
        pairs.append((etalon_body[el]['coordinates'], ticket_body[el]['coordinates']))

    return pairs


@pytest.mark.parametrize('ticket, etalon', get_test_data())
def test_text_position(ticket, etalon):
    assert ticket['x0'] == etalon['x0']
    assert ticket['y0'] == etalon['y0']
