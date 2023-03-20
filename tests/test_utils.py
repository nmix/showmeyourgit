import pytest
from freezegun import freeze_time
from datetime import datetime

from smyg import utils


@freeze_time('2023-02-13')
@pytest.mark.parametrize(
        'past, past_date',
        [
            ('13d', datetime(2023, 1, 31)),
            ('12d', datetime(2023, 2, 1)),
            ('3m', datetime(2022, 11, 13)),
            ('1y', datetime(2022, 2, 13)),
            ]
        )
def test_date_from_relative(past, past_date):
    assert utils.date_from_relative(past) == past_date


def test_convert_to_edge_one(one_file_modifications):
    edge_files = utils.convert_to_edge(one_file_modifications)
    assert len(edge_files) == 1


def test_convert_to_edge_multiple(multiple_files_modifications):
    edge_files = utils.convert_to_edge(multiple_files_modifications)
    assert len(edge_files) == 3
