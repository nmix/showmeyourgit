'''Covert metrics or instance dictionaries to specified format'''

from typing import Mapping

import os
import json
import jinja2


class FormatterError(Exception):
    '''Default formatter exception'''


def render(value: Mapping, output: str, template_name: str = None) -> str:
    '''Convert metrics to output format'''
    if output == 'text':
        path = os.path.join(os.path.dirname(__file__), 'templates')
        env = jinja2.Environment(loader=jinja2.FileSystemLoader(
            searchpath=path))
        template = env.get_template(f'{template_name}.j2')
        return template.render({'ctx': value})

    if output == 'json':
        return json.dumps(value)

    raise FormatterError(f'Unknown format {output}')
