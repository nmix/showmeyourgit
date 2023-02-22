'''Common functions for test cases'''

from smyg import vcs


def modified_files_from_raw(raw_data):
    '''Create instance or list of instances from raw data

    Attributes:
        raw_data - list of tuples with format:
            (
                old_path,
                new_path,
                [(line_number, 'added line'), ...],
                [(line_number, 'deleted line), ...],
            )
    '''
    modified_files = []
    for item in raw_data:
        modified_files.append(
                vcs.ModifiedFile(old_path=item[0],
                                 new_path=item[1],
                                 added_lines=item[2],
                                 deleted_lines=item[3]))
    return modified_files
