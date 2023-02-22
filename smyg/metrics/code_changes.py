'''Code changes metric module

   Metrics values:
      * count of added lines
      * count of deleted lines
      * relative changes value for each file
      * relative changes value for all files
'''

from typing import Mapping, List

from smyg import vcs
from smyg import utils


class CodeChanges:
    '''This metric measures the code changes of files and relative values

    Attributes:
        calculate: calculate metric values
    '''

    def __init__(self,
                 modified_files: List[vcs.ModifiedFile] = None):
        '''Object initalizer

        Attributes:
            commits - chronological sequence of commits (modified files groups)
        '''
        self.modified_files = modified_files or []

    def calculate(self, detail: bool = False) -> Mapping:
        '''Calculate code changes metric

        Args:
            detail: detail code changes per each file

        Returns:
            A dict with calculated values.
            For example:

            {'added': 1000,
             'deleted': 200,
             'ratio': '20',
             'files': [('/file/path': 10, 1, 10')]}

            Returned keys:
            added: count of added lines
            deleted: count of deleted lines from those that were added
            ratio: relative value for all files (in percent)
            files: detailed info per each file
        '''

        self.edge_files = utils.convert_to_edge(self.modified_files)

        # --- calculate lines in edge files
        added = deleted = 0
        detail_files = []
        for edge_file in self.edge_files:
            added += edge_file.added
            deleted += edge_file.deleted
            detail_files.append((edge_file.path,
                                 edge_file.added,
                                 edge_file.deleted,
                                 edge_file.ratio))

        values = {'added': added,
                  'deleted': deleted,
                  'ratio': vcs.ratio(added=added, deleted=deleted)}

        if detail:
            values['files'] = sorted(detail_files,
                                     key=lambda x: x[3],
                                     reverse=True)

        return values
