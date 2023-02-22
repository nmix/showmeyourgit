import pytest
from helpers import utils as test_utils

from smyg import utils


@pytest.fixture
def one_file_modifications():
    modifications = [
            # --- create new file 1
            (None, 'file1',
             [(1, 'one'), (2, 'two'), (3, 'three')],
             []),
            # --- delete lines in file 1
            ('file1', 'file1',
             [],
             [(1, 'one')]),
            # --- rename and add line
            ('file1', 'file2',
             [(101, 'one')],
             []),
            # --- delete lines
            ('file2', 'file2',
             [],
             [(101, 'one')]),
            # --- rename and insert lines
            ('file2', 'file3',
             [(1, 'one'), (2, 'two'), (3, 'three'), (4, 'four')],
             []),
            # --- delete lines
            ('file3', 'file3',
             [],
             [(1, 'one'), (2, 'two')]),
            ]
    return test_utils.modified_files_from_raw(modifications)


@pytest.fixture
def one_file_modifications_converted(one_file_modifications):
    return utils.convert_to_edge(one_file_modifications)


@pytest.fixture
def multiple_files_modifications():
    modifications = [
            # --- edit existing file 1
            ('file1', 'file1',
             [(101, '100 one'), (102, '100 two'), (103, '100 three')],
             []),
            # --- delete lines in file 1
            ('file1', 'file1',
             [],
             [(1, 'one')]),
            # --- create file 2
            (None, 'file2',
             [(1, 'one')],
             []),
            # --- delete line
            ('file2', 'file2',
             [],
             [(1, 'one')]),
            # --- create file 3
            (None, 'file3',
             [(1, 'one'), (2, 'two'), (3, 'three'), (4, 'four')],
             []),
            # --- rename and delete lines from 3
            ('file3', 'file4',
             [],
             [(1, 'one'), (2, 'two')]),
            ]
    return test_utils.modified_files_from_raw(modifications)


@pytest.fixture
def multiple_files_modifications_converted(multiple_files_modifications):
    return utils.convert_to_edge(multiple_files_modifications)
