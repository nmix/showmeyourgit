'''Internal entities of the git vcs, like commits, modified files, tags
and support classes.
'''

from __future__ import annotations

import dataclasses
import datetime
import enum
import hashlib


def ratio(added: int, deleted: int) -> float:
    '''Calculate deleted and added lines ratio'''
    if added == 0:
        return 0.0
    return round(deleted / added * 100, 2)


class ChangeType(enum.Enum):
    '''Type of modified file change'''
    UNDEFINED = 0
    ADDED = 1
    DELETED = 2
    MODIFIED = 3
    RENAMED = 4


class SourceLine:
    '''Line instance of source file with number and text value

    Attributes:
        number: number of line
        value: line text
    '''

    def __init__(self, number: int, value: str) -> None:
        self.number = number
        self.value = value
        self.digest = hashlib.md5(value.encode()).hexdigest()

    def __eq__(self, other) -> bool:
        if self.digest == other.digest:
            return True
        return False

    def __repr__(self) -> str:
        return f'{self.number:5d}: {self.value}'


def parsed_diff_to_source_lines(parsed_diff: list[tuple]) -> list[SourceLine]:
    '''Convert added or deleted lines to list of SourceLine instances

    Args:
        parsed_diff: added or deleted sequence of pairs:
            [(LINE_NUM, LINE_TEXT), ...]
    Returns:
        list of SourceLine instances.
    '''
    lines = []
    for diff in parsed_diff:
        lines.append(SourceLine(number=diff[0], value=diff[1]))
    return lines


class ModifiedFile:
    '''Modified file info with added or deleted lines

    Attributes:
        added: number of added lines
        deleted: number of deleted lines
        changed_lines_total: added and deleted lines sum
        path: actual file path (after rename or delete)
        prev_path: previous file path (before rename or delete)
        path_changed: file path was changed (renamed)
        change_type: file was added, deleted, renamed or just modified
    '''

    def __init__(self,
                 old_path: str | None,
                 new_path: str | None,
                 added_lines: list[tuple] = None,
                 deleted_lines: list[tuple] = None):
        '''Object initalizer

        Args:
            old_path - source file path before changes
            new_path - source file path after changes
            added_lines - added lines to file: [(LINE_NUM, LINE_TEXT), ...]
            deleted_lines - deleted lines from file:
                [(LINE_NUM, LINE_TEXT), ...]
        '''
        self.old_path = old_path
        self.new_path = new_path
        self.added_lines = parsed_diff_to_source_lines(added_lines or [])
        self.deleted_lines = parsed_diff_to_source_lines(deleted_lines or [])

    @property
    def added(self) -> int:
        return len(self.added_lines)

    @property
    def deleted(self) -> int:
        return len(self.deleted_lines)

    @property
    def changed_lines_total(self) -> int:
        return self.added + self.deleted

    @property
    def path(self) -> str:
        if self.change_type == ChangeType.DELETED:
            return self.old_path
        return self.new_path

    @property
    def prev_path(self) -> str:
        if self.path_changed:
            return self.old_path
        return self.path

    @property
    def path_changed(self) -> bool:
        if self.old_path and self.new_path and self.old_path != self.new_path:
            return True
        return False

    @property
    def change_type(self) -> ChangeType:
        if self.old_path is None and self.new_path:
            return ChangeType.ADDED
        if self.old_path and self.new_path is None:
            return ChangeType.DELETED
        if self.old_path and self.new_path and self.changed_lines_total > 0:
            return ChangeType.MODIFIED
        if self.old_path and self.new_path and self.changed_lines_total == 0:
            return ChangeType.RENAMED
        return ChangeType.UNDEFINED

    def __repr__(self) -> str:
        if self.path_changed:
            return f'{self.old_path}->{self.new_path} {self.change_type}'
        return f'{self.path} {self.change_type}'


class EdgeFile:
    '''Edge file state with actual numbers of added lines

    Every modified file instance change state: lines added, lines deleted,
    file path changed.
    Every modification in lines shifts line numbers

    Attributes:
        added: total number of added lines
        deleted: total number of deleted lines from added lines
        ratio: the ratio between deleted and added linese
        churn: number of deleted lines from added lines
        churn_ratio: the ratio between churn and added linese (code churn)
        line_value: get line text by line number
    '''

    def __init__(self, file: ModifiedFile):
        # --- total added lines
        self.added_lines = []
        # --- deleted lines from added lines
        self.deleted_lines = []
        # --- churn lines
        self.churn_lines = []
        # ---
        self.update(file)

    def update(self, file: ModifiedFile):
        '''Update current path and state of lines'''
        self.path = file.path

        # --- process deleted lines
        for line in file.deleted_lines:
            self.deleted_lines.append(line)
            if line in self.added_lines:
                self.churn_lines.append(line)

        # --- process added lines
        for line in file.added_lines:
            self.added_lines.append(line)

    @property
    def added(self) -> int:
        return len(self.added_lines)

    @property
    def deleted(self) -> int:
        return len(self.deleted_lines)

    @property
    def churn(self) -> int:
        return len(self.churn_lines)

    @property
    def ratio(self) -> float:
        return ratio(added=self.added, deleted=self.deleted)

    @property
    def churn_ratio(self) -> float:
        return ratio(added=self.added, deleted=self.churn)

    def __str__(self):
        return self.path

    def __repr__(self):
        return self.path


# pylint: disable=too-many-instance-attributes
@dataclasses.dataclass
class Commit:
    '''A Commit object has all the information of a Git commit'''

    sha: str
    msg: str
    author_name: str
    author_email: str
    author_date: datetime.datetime
    committer_name: str
    committer_email: str
    committer_date: datetime.datetime
    project_name: str
    added: int
    deleted: int
    changed_files: int
    branches: list
    parents: list

    def as_dict(self) -> dict:
        '''Represent instance as dict'''
        return dataclasses.asdict(self)

    def as_seriable_dict(self) -> dict:
        '''Represent instance as seriable dict'''
        seriable = dict(self.as_dict())
        seriable.update(
                {'author_date': str(self.author_date),
                 'committer_date': str(self.committer_date),
                 'branches': list(self.branches),
                 })
        return seriable

    def __repr__(self):
        return f'{self.sha} {self.msg}'
