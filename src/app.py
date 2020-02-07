import os
import random
import string
from datetime import datetime

import boto3
import pdfkit
from flask import Flask, jsonify, request, url_for, redirect

from .utils import convert_html_to_pdf, s3_save_file
from .validators import validate_url, validate_url_or_html


app = Flask(__name__)

URLS_TABLE = os.environ['URLS_TABLE']
IS_OFFLINE = os.environ.get('IS_OFFLINE')

if IS_OFFLINE:
    dynamodb = boto3.client(
        'dynamodb',
        region_name='localhost',
        endpoint_url='http://localhost:8000',
    )
else:
    dynamodb = boto3.client('dynamodb')


@app.route('/newUrl/', methods=['POST'])
def create_url():
    url = request.json.get('url')
    if not validate_url(url):
        return jsonify({'error': 'Please provide valid `url` argument.'}), 400

    new_id = ''.join(random.choices(string.ascii_letters + string.digits, k=6))

    dynamodb.put_item(
        TableName=URLS_TABLE,
        Item={
            'id': {'S': new_id},
            'url': {'S': url},
            'creator_ip': {'S': str(request.remote_addr)},
            'creator_user_agent': {'S': str(request.user_agent)},
            'created_at': {'S': datetime.now().isoformat()},
        }
    )

    return jsonify({'url': url_for('.get_url', url_id=new_id, _external=True)}), 201


@app.route('/r/<string:url_id>', methods=['GET'])
def get_url(url_id):
    resp = dynamodb.get_item(
        TableName=URLS_TABLE,
        Key={'id': {'S': url_id}},
    )
    item = resp.get('Item')
    if not item:
        return jsonify({'error': 'URL does not exist.'}), 404

    return redirect(item.get('url').get('S'), code=301)


@app.route('/htmlToPdf/', methods=['POST'])
def html_to_pdf():
    if msg := validate_url_or_html(request):
        return jsonify({'error': msg}), 400

    if request.is_json:
        file = convert_html_to_pdf(url=request.json['url'])
    else:
        file = convert_html_to_pdf(file=request.files['file'])

    return jsonify({'url': s3_save_file(file)}), 200
