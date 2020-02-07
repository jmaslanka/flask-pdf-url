import os
import uuid
from werkzeug import FileStorage

import boto3
import pdfkit

S3_BUCKET = os.environ.get('S3_BUCKET')
S3_BUCKET_REGION = os.environ.get('S3_BUCKET_REGION')
IS_OFFLINE = os.environ.get('IS_OFFLINE')
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WKHTMLTOPDF_PATH = os.path.join(BASE_DIR, 'binaries', 'wkhtmltopdf')

s3 = boto3.client('s3')


def convert_html_to_pdf(url: str = '', file: FileStorage = None) -> bytes:
    config = pdfkit.configuration(
        wkhtmltopdf='' if IS_OFFLINE else WKHTMLTOPDF_PATH
    )

    if url:
        return pdfkit.from_url(url, False, configuration=config)
    elif file:
        return pdfkit.from_string(file.read().decode('utf-8'), False, configuration=config)
    
    raise ValueError


def s3_save_file(file: bytes) -> str:
    filename = f'pdfs/{uuid.uuid4().hex}.pdf'
    s3.put_object(
        ACL='public-read', Bucket=S3_BUCKET,
        Body=file, ContentType='application/pdf', Key=filename,
    )
    return f'https://{S3_BUCKET}.s3.{S3_BUCKET_REGION}.amazonaws.com/{filename}'
