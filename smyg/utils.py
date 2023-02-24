'''Useful functions

    date_from_relative - convert relative period like '1m' to past date

    convert_to_edge - translate list of vcs.ModifiedFile to vsc.EdgeFile
'''
from __future__ import annotations

from datetime import datetime
import re

from dateutil import relativedelta

from smyg import vcs


def date_from_relative(past: str) -> datetime:
    '''convert relative period like '1m' to past date

    date_from_relative('1m') => TODAY - 1 month
    date_from_relative('21d') => TODAY - 28 days
    etc
    '''
    if not re.match(r'^\d+[ymd]$', past):
        raise ValueError('Relative argument does not match pattern')
    period_types = {'y': 'years', 'm': 'months', 'd': 'days'}
    period = {period_types[past[-1]]: int(past[:-1])}
    return datetime.now() - relativedelta.relativedelta(**period)


def convert_to_edge(modified_files: list[vcs.ModifiedFile]
                    ) -> list[vcs.EdgeFile]:
    '''convert modified files to edge files'''
    edge_files = []
    for modified_file in modified_files:
        for edge_file in edge_files:
            if edge_file.path == modified_file.prev_path:
                edge_file.update(modified_file)
                break
        else:
            edge_files.append(vcs.EdgeFile(modified_file))
    return edge_files
