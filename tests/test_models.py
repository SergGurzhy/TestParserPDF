import unittest

import pytest

from data_finder import get_data_from_pdf
from helpers.helpers import get_project_root


class CompareTickets(unittest.TestCase):
    root = get_project_root()
    etalon = get_data_from_pdf(f'{root}/test_task.pdf')
    ticket = get_data_from_pdf(f'{root}/tests/tests_data/test_task_1.pdf')

    def test_self(self):
        self.assertEqual(self.etalon, self.etalon)

    def test_sheet_size(self):
        self.assertEqual(
            self.etalon.get('meta_data').get('sheet_size'),
            self.ticket.get('meta_data').get('sheet_size')
        )

    def test_all_positions_on_sheet(self):
        etalon_key = set(self.etalon.get('body').keys())
        ticket_key = set(self.ticket.get('body').keys())

        self.assertEqual(len(etalon_key ^ ticket_key), 0)

    @pytest.mark.parametrize(
        'ticket, etalon',
        [
            (
              ticket['body']["GRIFFON AVIATION SERVICES LLC"]['coordinates'],
              etalon['body']["GRIFFON AVIATION SERVICES LLC"]['coordinates']
            ),
            (
            ticket['body']["PN"]['coordinates'],
            etalon['body']["PN"]['coordinates']
            ),
            (
            ticket['body']["DESCRIPTION"]['coordinates'],
            etalon['body']["DESCRIPTION"]['coordinates']
            )
        ]
    )
    def test_text_position(self, ticket, etalon):
        assert ticket['x0'] == etalon['x0']
        assert ticket['y0'] == etalon['y0']


if __name__ == '__main__':
    unittest.main()
