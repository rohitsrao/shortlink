import re

from flask import jsonify, make_response, request
from url_shortener import app
from url_shortener.utils import *
from url_shortener.models import Link

@app.route('/', methods=['GET'])
def root_route():
    return jsonify()

@app.route('/decode', methods=['POST'])
def decode():
    
    if request.content_type != 'application/json':
        return jsonify({'error_message': 'Request content type is not application/json'}), 400
    
    req = request.get_json()
    
    if 'short_url' not in req: return jsonify({'error_message': 'Request json body missing short_url key'}), 400
    if req['short_url'] == '': return jsonify({'error_message': 'short_url in request json body cannot by empty string'}), 400
    if req['short_url'] == None: return jsonify({'error_message': 'short_url in request json body cannot be None / null'}), 400
    
    base_url_regex = r'http:\/\/short.est\/[a-zA-Z0-9]+'
    if re.fullmatch(base_url_regex, req['short_url']) == None:
        error_message = 'short_url is invalid. Valid format - http://short.est/unique-string - Unique string can contain only a-z, A-Z and 0-9'
        return jsonify({'error_message': error_message}), 400
    
    short = req['short_url'].split('/')[-1]
    
    link = Link.query.get(short)
    if link == None: return jsonify({'error_message': 'URL does not exist in database'}), 400
    else: return jsonify({'long_url': link.url}), 200

@app.route('/encode', methods=['POST'])
def encode():
    
    if request.content_type != 'application/json':
        return jsonify({'error_message': 'Request content type is not application/json'}), 400
    
    req = request.get_json()
    
    if 'long_url' not in req: return jsonify({'error_message': 'Request json body missing long_url key'}), 400
    if req['long_url'] == '': return jsonify({'error_message': 'long_url in request json body cannot by empty string'}), 400
    if req['long_url'] == None: return jsonify({'error_message': 'long_url in request json body cannot be None / null'}), 400

    standard_url_regex = r'https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)'
    if re.fullmatch(standard_url_regex, req['long_url']) == None:
        return jsonify({'error_message': 'Provided URL is not a valid URL'}), 400

    base_url = 'http://short.est/'
    short_url_string = generate_short_url_string()
    op_result = add_link_to_database(short_url_string, req['long_url'])
    if op_result['status'] == 'failed':
        error_dict = {
            'error_message': 'URL has already been shortened before',
            'short_url': base_url + op_result['existing_short']
        }
        return jsonify(error_dict), 400
    shortened_url = base_url + short_url_string
    return jsonify({'short_url': shortened_url}), 201

