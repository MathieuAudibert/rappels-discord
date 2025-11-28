import requests
import os
import json
from datetime import datetime, timedelta
from http.server import BaseHTTPRequestHandler
# from dotenv import load_dotenv
# load_dotenv()

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
        
    except Exception as e:
        error_message = f"[ERROR]: message invalid - {e}"
        print(error_message)
        response.status = 400 
        response.body = error_message
        return

    if not CONTENT:
        error_message = "[ERROR]: messge should be in body"
        print(error_message)
        response.status = 400
        response.body = error_message
        return
    
    date_for_rappel = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')  
    url = f"https://discord.com/api/v9/channels/{ID_GROUPE}/messages"
    headers = {"Authorization": f"{TOKEN}", "Content-Type": "application/json"}
    
    prefix = f"@here **RAPPEL {date_for_rappel}** : "
    data_payload = {"content": prefix + CONTENT}

    res = requests.post(url, headers=headers, json=data_payload)
    if res.status_code == 200:
        log_message = f"[INFO]: msg sent - {date_for_rappel}"
        print(log_message)
        response.status = 200
        response.body = log_message
    else:
        error_message = f"[ERROR]: failed - {res.text}"
        print(error_message)
        response.status = 500
        response.body = error_message