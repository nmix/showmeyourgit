'''CLI smyg module'''

import datetime as dt
import os
import typer
from typing import Optional

from smyg import __app_name__, __version__
from smyg import binding
from smyg import formatter
from smyg import prom
from smyg import utils
from smyg.metrics import code_churn as cc
from smyg.metrics import code_changes as cch

app = typer.Typer()


@app.command()
def branch_commits(
        sha: str =
        typer.Argument(
            None,
            help='beginning commit SHA'),
        repo_path: str =
        typer.Option(
            '.',
            '--repo-path',
            help='path to git repo'),
        branch: str =
        typer.Option(
            None,
            help='show commits for specified branch'
            ),
        format: str =
        typer.Option(
            'text',
            help='output format [text/json]'),
        push_metrics: bool =
        typer.Option(
            False,
            help='push metrics to gateway'),
        ):
    '''Show changes for bundle of commits

    Assumed that will be used in CI on push event job.
    If we have previous SHA then using just commits with --from-commit.
    If we don't have SHA or '000...' as SHA value then we use only commits
    in single branch
    '''
    path = os.path.abspath(repo_path)
    # --- In Gitlab CI beginning sha contains '000.' (see CI_COMMIT_BEFORE_SHA)
    if sha == '0000000000000000000000000000000000000000':
        sha = None
    # --- get commits bundle
    try:
        commits = binding.branch_commits(path, sha=sha, branch=branch)
    except binding.BindingError as e:
        raise typer.Exit(e)

    typer.echo(
            formatter.format(
                [commit.as_seriable_dict() for commit in commits],
                format,
                'commits'
                ))

    if push_metrics:
        try:
            prom.push_commits([commit.as_dict() for commit in commits])
        except prom.PushGatewayError as e:
            raise typer.Exit(e)


@app.command()
def commit(
        hash: str =
        typer.Argument(
            None,
            help='hash of the commit'),
        repo_path: str =
        typer.Option(
            '.',
            '--repo-path',
            help='path to git repo'),
        branch: str =
        typer.Option(
            None,
            help='show commit info in last commit in branch'
            ),
        format: str =
        typer.Option(
            'text',
            help='output format [text/json]'),
        push_metrics: bool =
        typer.Option(
            False,
            help='push metrics to gateway'),
        ):
    '''Show commit info'''
    path = os.path.abspath(repo_path)
    try:
        commit = binding.commit(path, hash=hash, branch=branch)
    except binding.BindingError as e:
        raise typer.Exit(e)
    typer.echo(formatter.format(commit.as_seriable_dict(), format, 'commit'))
    if push_metrics:
        try:
            prom.push_commits(commit.as_seriable_dict())
        except prom.PushGatewayError as e:
            raise typer.Exit(e)


@app.command()
def codechanges(
        repo_path: str =
        typer.Option(
            '.',
            '--repo-path',
            help='path to git repo'),
        since: dt.datetime =
        typer.Option(
            None,
            help='only commits after this date will be analyzed',
            rich_help_panel='FROM'),
        from_commit: str =
        typer.Option(
            None,
            '--from-commit',
            help='only commits after this commit hash '
            'will be analyzed',
            rich_help_panel='FROM'),
        from_tag: str =
        typer.Option(
            None,
            '--from-tag',
            help='only commits after this commit tag will be analyzed',
            rich_help_panel='FROM'),
        to: dt.datetime =
        typer.Option(
            None,
            help='only commits up to this date will be analyzed',
            rich_help_panel='TO'),
        to_commit: str =
        typer.Option(
            None,
            '--to-commit',
            help='only commits up to this commit hash will be analyzed',
            rich_help_panel='TO'),
        to_tag: str =
        typer.Option(
            None,
            '--to-tag',
            help='only commits up to this commit tag will be analyzed',
            rich_help_panel='TO'),
        branch: str =
        typer.Option(
            None,
            help='only analyses commits that belong to this branch'
            ),
        detail: bool =
        typer.Option(
            False,
            help='show detail code churn per each file'),
        format: str =
        typer.Option(
            'text',
            help='output format [text/json]'),
        for_past: str =
        typer.Option(
            None,
            help='metric for relative period, e.g. 5d, 3m, 1y'),
        push_metrics: bool =
        typer.Option(
            False,
            help='push metrics to prometheus gateway'),
            ):
    '''This metric measures the code changes of each files.'''
    path = os.path.abspath(repo_path)
    if for_past:
        try:
            since = utils.date_from_relative(for_past)
        except ValueError as e:
            raise typer.Exit(e)
    try:
        modified_files = binding.modified_files(path,
                                                since=since,
                                                from_commit=from_commit,
                                                from_tag=from_tag,
                                                to=to,
                                                to_commit=to_commit,
                                                to_tag=to_tag,
                                                only_in_branch=branch)
    except binding.BindingError as e:
        raise typer.Exit(e)
    metrics = cch.CodeChanges(modified_files).calculate(detail=detail)
    typer.echo(formatter.format(metrics, format, 'code_changes'))
    if push_metrics:
        try:
            prom.push_codechanges(metrics,
                                  suffix=for_past)
        except prom.PushGatewayError as e:
            raise typer.Exit(e)


@app.command()
def codechurn(
        repo_path: str =
        typer.Option(
            '.',
            '--repo-path',
            help='path to git repo'),
        since: dt.datetime =
        typer.Option(
            None,
            help='only commits after this date will be analyzed',
            rich_help_panel='FROM'),
        from_commit: str =
        typer.Option(
            None,
            '--from-commit',
            help='only commits after this commit hash '
            'will be analyzed',
            rich_help_panel='FROM'),
        from_tag: str =
        typer.Option(
            None,
            '--from-tag',
            help='only commits after this commit tag will be analyzed',
            rich_help_panel='FROM'),
        to: dt.datetime =
        typer.Option(
            None,
            help='only commits up to this date will be analyzed',
            rich_help_panel='TO'),
        to_commit: str =
        typer.Option(
            None,
            '--to-commit',
            help='only commits up to this commit hash will be analyzed',
            rich_help_panel='TO'),
        to_tag: str =
        typer.Option(
            None,
            '--to-tag',
            help='only commits up to this commit tag will be analyzed',
            rich_help_panel='TO'),
        branch: str =
        typer.Option(
            None,
            help='only analyses commits that belong to this branch'
            ),
        detail: bool =
        typer.Option(
            False,
            help='show detail code churn per each file'),
        format: str =
        typer.Option(
            'text',
            help='output format [text/json]'),
        for_past: str =
        typer.Option(
            '',
            help='metric for relative period, e.g. 5d, 3m, 1y'),
        push_metrics: bool =
        typer.Option(
            False,
            help='push metrics to prometheus gateway'),
        ):
    '''This metric measures the code churns of each file.'''
    path = os.path.abspath(repo_path)
    if for_past:
        try:
            since = utils.date_from_relative(for_past)
        except ValueError as e:
            raise typer.Exit(e)
    try:
        modified_files = binding.modified_files(path,
                                                since=since,
                                                from_commit=from_commit,
                                                from_tag=from_tag,
                                                to=to,
                                                to_commit=to_commit,
                                                to_tag=to_tag,
                                                only_in_branch=branch)
    except binding.BindingError as e:
        raise typer.Exit(e)
    code_churn = cc.CodeChurn(modified_files)
    metrics = code_churn.calculate(detail=detail)
    typer.echo(formatter.format(metrics, format, 'code_changes'))
    if push_metrics:
        try:
            prom.push_codechanges(metrics,
                                  metric_name='codechurn',
                                  suffix=for_past)
        except prom.PushGatewayError as e:
            raise typer.Exit(e)


def _version_callback(value: bool) -> None:
    if value:
        typer.echo(f'{__app_name__} v{__version__}')
        raise typer.Exit()


@app.callback()
def main(
    version: Optional[bool] = typer.Option(
        None,
        '--version',
        '-v',
        help="show the application's version and exit",
        callback=_version_callback,
        is_eager=True,
    )
) -> None:
    # pylint: disable=unused-argument
    return
