import requests
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta
from http.server import BaseHTTPRequestHandler

load_dotenv()
def handler(request: BaseHTTPRequestHandler, response):
    TOKEN = os.getenv("TOKEN_DISCORD")
    ID_GROUPE = os.getenv("TARGET_GROUP_ID")
    CONTENT = os.getenv("MESSAGE_CONTENT")

    date_for_rappel = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
    
    if not all([TOKEN, ID_GROUPE, CONTENT]):
        error_message = "[ERROR]: missing env variables (TOKEN_DISCORD, TARGET_GROUP_ID, or MESSAGE_CONTENT)"
        print(error_message)
        response.status = 500
        response.body = error_message
        return

    url = f"https://discord.com/api/v9/channels/{ID_GROUPE}/messages"
    headers = {"Authorization": f"{TOKEN}"}
    prefix = f"@here **RAPPEL {date_for_rappel}** : "
    data = {"content": prefix + CONTENT}

    res = requests.post(url, headers=headers, json=data)

    if res.status_code == 200:
        log_message = f"[INFO]: msg sent successfully date - {date_for_rappel}"
        print(log_message)
        response.status = 200
        response.body = log_message
    else:
        error_message = f"[ERROR]: failed to send msg - {res.text}"
        print(error_message)
        response.status = 500
        response.body = error_message
