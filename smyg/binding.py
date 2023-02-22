'''Package bindings'''

import sys
import pydriller
import git

from typing import Optional, List

from smyg import vcs


class BindingError(Exception):
    '''Default exception for binding module'''
    pass


def branch_commits(
        path: str,
        sha: Optional[str] = None,
        branch: Optional[str] = None
        ) -> List[vcs.Commit]:
    '''Find bundle of commits for a branch

    Args:
        path: absolute path to repo
        sha: starting commit SHA
            if sha not null then returns all commits from this sha
            if sha null then return all commits only for a branch
        branch: specified branch
    '''

    if sha:
        repo = pydriller.Repository(path,
                                    from_commit=sha,
                                    only_in_branch=branch,
                                    order='reverse')
        commits = [commit for commit in repo.traverse_commits()][:-1]
    else:
        repo = pydriller.Repository(path,
                                    only_in_branch=branch,
                                    order='reverse')
        commits = []
        for commit in repo.traverse_commits():
            if len(commit.branches) == 1:
                commits.append(commit)
            else:
                break
    # ---
    return [_create_vcs_commit(commit) for commit in commits]


def commit(
        path: str,
        hash: Optional[str] = None,
        branch: Optional[str] = None):
    '''Find commit in history'''
    if hash:
        repo = pydriller.Repository(path,
                                    single=hash,
                                    only_in_branch=branch,
                                    order='reverse')
    else:
        repo = pydriller.Repository(path,
                                    only_in_branch=branch,
                                    order='reverse')
    try:
        commit = next(repo.traverse_commits())
    except git.GitCommandError as e:
        raise BindingError(e)
    return _create_vcs_commit(commit)


def modified_files(path: str, **kargs):
    '''Get list of modified files from repo

    Attributes:
        path: repo path
    '''
    files = []
    # --- TODO: try except in for next() iteration instead separate call
    try:
        next(pydriller.Repository(path, **kargs).traverse_commits())
    except git.GitCommandError as e:
        raise BindingError(e)
    except StopIteration:
        pass
    # ---
    for commit in pydriller.Repository(path, **kargs).traverse_commits():
        try:
            commit_files = commit.modified_files
        except ValueError as e:
            print(f'Error occurred while processing the commit '
                  f'{commit.hash}: {e}', file=sys.stderr)
            continue
        for file in commit_files:
            files.append(
                    vcs.ModifiedFile(
                        old_path=file.old_path,
                        new_path=file.new_path,
                        added_lines=file.diff_parsed.get('added'),
                        deleted_lines=file.diff_parsed.get('deleted')))
    return files


def _create_vcs_commit(commit: pydriller.Commit) -> vcs.Commit:
    return vcs.Commit(
            hash=commit.hash,
            msg=commit.msg,
            author_name=commit.author.name,
            author_email=commit.author.email,
            author_date=commit.author_date,
            committer_name=commit.committer.name,
            committer_email=commit.committer.email,
            committer_date=commit.committer_date,
            project_name=commit.project_name,
            added=commit.insertions,
            deleted=commit.deletions,
            changed_files=commit.files,
            branches=commit.branches,
            )
