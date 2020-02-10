from typing import Union
from urllib.parse import urlparse

import magic
from flask import Request


ALLOWED_HTTP_EXTENSIONS = ['html', 'htm', 'xhtml']
ALLOWED_MIME_TYPES = ['text/html', 'application/xhtml+xml']


def validate_url(url: str) -> bool:
    if not url:
        return False

    try:
        parsed_url = urlparse(url)
        return parsed_url.scheme in ['http', 'https'] and parsed_url.netloc
    except ValueError:
        return False


def validate_url_or_html(request: Request) -> Union[str, None]:
    """Check if valid URL or HTML page was passed. Return error msg if so."""
    if request.is_json:
        if not request.json.get('url'):
            return 'Please provide `url` argument.'
        if not validate_url(request.json.get('url')):
            return 'Invalid `url` argument.'
        return
    
    file = request.files.get('file')

    if not (
        file and
        file.filename.split('.')[-1] in ALLOWED_HTTP_EXTENSIONS and
        magic.from_buffer(file.read(2048), mime=True) in ALLOWED_MIME_TYPES
    ):
        return 'Please provide valid HTML file in `file` argument.'

    file.seek(0)
