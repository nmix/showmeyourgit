from smyg import vcs


def test_source_lines_equal():
    line1 = vcs.SourceLine(1, 'hello world')
    line2 = vcs.SourceLine(2, 'hello world')
    assert line1 == line2
