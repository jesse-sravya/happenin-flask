import json
import os
import requests

import cachecontrol
import google.auth.transport.requests

from flask import Flask, jsonify, request
from flask_cors import CORS

from google.oauth2 import id_token

from helpers import calendar_helper


app = Flask(__name__)
CORS(app, supports_credentials=True)

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")



@app.route('/api/login', methods=['POST'])
def login():
    request_payload = request.data.decode("utf-8")
    if request_payload:
        request_json = json.loads(request_payload)
        token = request_json.get("token")
        accessToken = request_json.get("accessToken")

        session = requests.session()
        cached_session = cachecontrol.CacheControl(session)
        oauth_request = google.auth.transport.requests.Request(session=cached_session)
        id_info = id_token.verify_oauth2_token(token, oauth_request, GOOGLE_CLIENT_ID)
        
        user_id = id_info['sub']
        
        return jsonify({ 'token': token, 'accessToken': accessToken, 'google_user_id': user_id }), 200
    return jsonify({}), 400


@app.route('/api/events/create', methods=['POST'])
def create_event():
    request_payload = request.data.decode("utf-8")
    auth_header = request.headers.get('Authorization')
    
    if request_payload:
        request_json = json.loads(request_payload)

        event = request_json.get("event", {})
        
        success, event = calendar_helper.create_event(event, auth_header)
        if success:
            return jsonify({'event': event}), 200

    return jsonify({}), 400


@app.route('/api/events/public', methods=['GET'])
def get_public_events():
    success, events = calendar_helper.get_public_events()
    if success:
        return jsonify({'public_events': events}), 200
    return jsonify({}), 400


@app.route('/api/events/private', methods=['GET'])
def get_private_events():
    auth_header = request.headers.get('Authorization')
    success, events = calendar_helper.get_private_events(auth_header)
    if success:
        return jsonify({'private_events': events}), 200
    return jsonify({}), 400


@app.route('/api/events/attend', methods=['PATCH'])
def attend_event():
    auth_header = request.headers.get('Authorization')
    request_payload = request.data.decode("utf-8")
    
    if request_payload:
        request_json = json.loads(request_payload)
        event_id = request_json.get("event_id")
        success = calendar_helper.attend_event(auth_header, event_id)
        
        if success:
            return jsonify({}), 200
    return jsonify({}), 400

