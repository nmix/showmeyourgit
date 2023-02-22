from helpers import utils

from smyg import vcs
from smyg.metrics import code_churn as cc


def test_simple_churn():
    lines = [(1, 'print("Hello world")')]
    file = vcs.ModifiedFile(old_path=None,
                            new_path='/main.py',
                            added_lines=lines)
    value = cc.CodeChurn([file]).calculate()
    assert value == {'added': 1, 'deleted': 0, 'ratio': 0.0}


def test_simple_change_history():
    modifications = [
            # --- add 1 line
            (None,
             'main.py',
             [(1, 'print("Hello world")')],
             []),
            # --- add more 2 lines
            ('main.py',
             'main.py',
             [(2, 'print("Hello world 2")'), (3, 'print("Hello world 3")')],
             []),
            # --- delete first line
            ('main.py',
             'main.py',
             [],
             [(1, 'print("Hello world")')]),
            # --- replace third line (line num was shifted)
            ('main.py',
             'main.py',
             [(2, 'print("Hello world 3 new")')],
             [(2, 'print("Hello world 3")')]),
            # --- insert new lines to the beginning
            ('main.py',
             'main.py',
             [
                 (1, 'print("Hello world 1 new")'),
                 (2, 'print("Hello world 2 new")'),
                 (3, 'print("Hello world 3 new")'),
                 (4, 'print("Hello world 4 new")'),
                 ],
             []),
            ]
    modified_files = utils.modified_files_from_raw(modifications)
    val = cc.CodeChurn(modified_files).calculate()
    assert val == {'added': 8, 'deleted': 2, 'ratio': 25.0}


def test_code_churn_with_rename():
    modifications = [
            # --- add 1 line
            (None,
             'main.py',
             [(1, 'print("Hello world")')],
             []),
            # --- add more 2 lines
            ('main.py',
             'main.py',
             [(2, 'print("Hello world 2")'), (3, 'print("Hello world 3")')],
             []),
            # --- rename file and remove first line and othe line
            ('main.py',
             'app.py',
             [],
             [(1, 'print("Hello world")'), (333, 'print("Hello world 4")')]),
            ]
    modified_files = utils.modified_files_from_raw(modifications)
    val = cc.CodeChurn(modified_files).calculate()
    assert val == {'added': 3, 'deleted': 1, 'ratio': 33.33}


def test_code_churn_with_multiple_files():
    modifications = [
            # --- remove old file
            ('utils.py', None,
             [],
             [(1, '    foo'), (2, '    bar'), (3, 'foobar')]),
            # --- add new file
            (None, 'libs.py',
             [(1, '    foo'), (2, '    bar'), (3, 'foobar')],
             []),
            # --- delete second line
            ('libs.py', 'libs.py',
             [],
             [(2, '    bar')]),
            # --- replace "third" line (now it second)
            ('libs.py', 'libs.py',
             [(2, 'barbarbar')],
             [(2, 'foobar')]),
            # --- rename file and insert lines
            ('libs.py', 'mylibs.py',
             [(1, 'one'), (2, 'two'), (3, 'three')],
             []),
            # --- add another file
            (None, 'test.py',
             [(1, 'one'), (2, 'two'), (3, 'three')],
             []),
            # --- ... and delete it
            ('test.py', None,
             [],
             [(1, 'one'), (2, 'two'), (3, 'three')]),
            ]
    modified_files = utils.modified_files_from_raw(modifications)
    val = cc.CodeChurn(modified_files).calculate()
    assert val == {'added': 10, 'deleted': 5, 'ratio': 50}


def test_code_churn_with_detail_option():
    modifications = [
            # --- remove old file
            ('utils.py', None,
             [],
             [(1, '    foo'), (2, '    bar'), (3, 'foobar')]),
            # --- add new file
            (None, 'libs.py',
             [(1, '    foo'), (2, '    bar'), (3, 'foobar')],
             []),
            # --- delete second line
            ('libs.py', 'libs.py',
             [],
             [(2, '    bar')]),
            # --- replace "third" line (now it second)
            ('libs.py', 'libs.py',
             [(2, 'barbarbar')],
             [(2, 'foobar')]),
            # --- rename file and insert lines
            ('libs.py', 'mylibs.py',
             [(1, 'one'), (2, 'two'), (3, 'three')],
             []),
            # --- add another file
            (None, 'test.py',
             [(1, 'one'), (2, 'two'), (3, 'three')],
             []),
            # --- ... and delete it
            ('test.py', None,
             [],
             [(1, 'one'), (2, 'two'), (3, 'three')]),
            ]
    modified_files = utils.modified_files_from_raw(modifications)
    val = cc.CodeChurn(modified_files).calculate(detail=True)
    assert val == {'added': 10,
                   'deleted': 5,
                   'ratio': 50.0,
                   'files': [('test.py', 3, 3, 100.0),
                             ('mylibs.py', 7, 2, 28.57),
                             ('utils.py', 0, 0, 0.0)]}


def test_code_churn_with_sorted_detail():
    modifications = [
            # --- create new file 1
            (None, 'file1.py',
             [(1, 'one'), (2, 'two'), (3, 'three')],
             []),
            # --- delete lines in file 1
            ('file1.py', 'file1.py',
             [],
             [(1, 'one')]),
            # --- create new file 2
            (None, 'file2.py',
             [(1, 'one')],
             []),
            # --- delete lines in file 2
            ('file2.py', 'file2.py',
             [],
             [(1, 'one')]),
            # --- create new file 3
            (None, 'file3.py',
             [(1, 'one'), (2, 'two'), (3, 'three'), (4, 'four')],
             []),
            # --- delete lines in file 3
            ('file3.py', 'file3.py',
             [],
             [(1, 'one'), (2, 'two')]),
            ]
    modified_files = utils.modified_files_from_raw(modifications)
    val = cc.CodeChurn(modified_files).calculate(detail=True)
    assert val == {'added': 8,
                   'deleted': 4,
                   'ratio': 50.0,
                   'files': [('file2.py', 1, 1, 100.0),
                             ('file3.py', 4, 2, 50.0),
                             ('file1.py', 3, 1, 33.33)]}
