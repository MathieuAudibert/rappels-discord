import requests
import os
import json
from datetime import datetime, timedelta
from http.server import BaseHTTPRequestHandler

DATE_FORMAT = '%Y-%m-%d'

def handler(request: BaseHTTPRequestHandler, response):
    TOKEN = os.getenv("TOKEN_DISCORD")
    ID_GROUPE = os.getenv("TARGET_GROUP_ID")

    if not all([TOKEN, ID_GROUPE]):
        error_message = "[ERROR]: missing env var (TOKEN_DISCORD or TARGET_GROUP_ID)"
        print(error_message) 
        response.status = 500
        response.body = error_message
        return
    
    try:
        body_length = int(request.headers.get('content-length', 0))
        body = request.rfile.read(body_length)
        data = json.loads(body)
        
        CONTENT = data.get('message')
        TARGET_DATE_STR = data.get('target_date')
        
    except Exception as e:
        error_message = f"[ERROR]: JSON invalid or not in body - {e}"
        print(error_message)
        response.status = 400 
        response.body = error_message
        return

    if not CONTENT:
        error_message = "[ERROR]: 'message' should be in body"
        print(error_message)
        response.status = 400
        response.body = error_message
        return
    
    if not TARGET_DATE_STR:
        error_message = "[ERROR]: 'target_date' should be in body"
        print(error_message)
        response.status = 400
        response.body = error_message
        return
    
    try:
        target_date_obj = datetime.strptime(TARGET_DATE_STR, DATE_FORMAT).date()
        send_date_obj = target_date_obj - timedelta(days=1)
        send_date_str = send_date_obj.strftime(DATE_FORMAT)
        
    except ValueError:
        error_message = f"[ERROR]: date format invalid - {DATE_FORMAT} (ex: 2026-01-01)"
        print(error_message)
        response.status = 400
        response.body = error_message
        return

    url = f"https://discord.com/api/v9/channels/{ID_GROUPE}/messages"
    headers = {"Authorization": f"{TOKEN}", "Content-Type": "application/json"}
    prefix = f"@here **RAPPEL {target_date_obj.strftime('%A, %B %d, %Y')}** (Sending {send_date_str}): " 
    data_payload = {"content": prefix + CONTENT}

    res = requests.post(url, headers=headers, json=data_payload)
    
    if res.status_code == 200:
        log_message = f"[INFO]: msg {target_date_obj} sent successfully {send_date_str}"
        print(log_message)
        response.status = 200
        response.body = log_message
    else:
        error_message = f"[ERROR]: failed - {res.text}"
        print(error_message)
        response.status = 500
        response.body = error_message