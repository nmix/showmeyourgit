'''Prometheus client'''
from __future__ import annotations

import os

import prometheus_client


PUSHGATEWAY_URL = os.getenv('PUSHGATEWAY_URL', 'http://localhost:9091')
PUSHGATEWAY_USERNAME = os.getenv('PUSHGATEWAY_USERNAME')
PUSHGATEWAY_PASSWORD = os.getenv('PUSHGATEWAY_PASSWORD')
PROJECT_NAME = os.getenv('PROJECT_NAME')

registry = prometheus_client.CollectorRegistry()

COMMIT_LABELS = ['author_email', 'project_name']

COMMITS = prometheus_client.Counter(
        'commits',
        'Number of commits',
        COMMIT_LABELS,
        registry=registry)
COMMIT_ADDED_LINES = prometheus_client.Counter(
        'commit_added_lines',
        'Number of added lines in commit',
        COMMIT_LABELS,
        registry=registry)
COMMIT_DELETED_LINES = prometheus_client.Counter(
        'commit_deleted_lines',
        'Number of added deleted in commit',
        COMMIT_LABELS,
        registry=registry)
COMMIT_CHANGED_FILES = prometheus_client.Counter(
        'commit_changed_files',
        'Number of changed files in commit',
        COMMIT_LABELS,
        registry=registry)


class PushGatewayError(Exception):
    '''Default exception for prom module'''


def push_commits(values: list | dict):
    '''Push commit values to pushgateway'''
    if not PUSHGATEWAY_URL:
        raise PushGatewayError(
                '\nAn error occurred during the push metrics:\n'
                'PUSHGATEWAY_URL env variable not set')
    if not isinstance(values, list):
        values = [values]
    for value in values:
        labels = (value.get('author_email'),
                  PROJECT_NAME)
        COMMITS.labels(*labels).inc()
        COMMIT_ADDED_LINES.labels(*labels).inc(value.get('added'))
        COMMIT_DELETED_LINES.labels(*labels).inc(value.get('deleted'))
        COMMIT_CHANGED_FILES.labels(*labels).inc(value.get('changed_files'))
    prometheus_client.push_to_gateway(
            PUSHGATEWAY_URL,
            job='showmeyourgit',
            registry=registry,
            handler=push_gateway_handler)


def push_codechanges(value: dict,
                     metric_name: str = 'codechanges',
                     suffix: str = ''):
    '''Push codechurn values to pushgateway

    Args:
        value - metrics value
        metric_name - metric name: codechanges, codechurn. Uses in metrics
            with equal value format
        suffix - metrics name suffix with relative interval,
            e.g. '5d', '3m'
    '''
    if suffix:
        suffix = '_' + suffix
    added_lines = prometheus_client.Gauge(
            f'{metric_name}_added_lines{suffix}',
            'Number of added lines for period',
            ['project_name'],
            registry=registry)
    added_lines.labels(PROJECT_NAME).set(value.get('added'))
    deleted_lines = prometheus_client.Gauge(
            f'{metric_name}_deleted_lines{suffix}',
            'Number of deleted lines from those that were added for period',
            ['project_name'],
            registry=registry)
    deleted_lines.labels(PROJECT_NAME).set(value.get('deleted'))
    ratio = prometheus_client.Gauge(
            f'{metric_name}_ratio{suffix}',
            'Relative churn value for all files',
            ['project_name'],
            registry=registry)
    ratio.labels(PROJECT_NAME).set(value.get('ratio'))
    prometheus_client.push_to_gateway(
            PUSHGATEWAY_URL,
            job=f'showmeyourgit-{PROJECT_NAME}-{metric_name}{suffix}',
            registry=registry,
            handler=push_gateway_handler)


def push_gateway_handler(url, method, timeout, headers, data):
    return prometheus_client.exposition.basic_auth_handler(
            url,
            method,
            timeout,
            headers,
            data,
            PUSHGATEWAY_USERNAME,
            PUSHGATEWAY_PASSWORD)
