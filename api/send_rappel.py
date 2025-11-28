import requests
import os
import json
from datetime import datetime, timedelta

DATE_FORMAT = '%Y-%m-%d'

def handler(request):
    if request.get('method') != 'POST':
        return {"statusCode": 405,"body": "method not allowed, only POST"}

    TOKEN = os.getenv("TOKEN_DISCORD")
    ID_GROUPE = os.getenv("TARGET_GROUP_ID")

    if not all([TOKEN, ID_GROUPE]):
        error_message = "[ERROR]: missing env var (TOKEN_DISCORD or TARGET_GROUP_ID)"
        print(error_message) 
        return {"statusCode": 500,"body": error_message}
    
    try:
        raw_body = request.get('body', '')   
        data = json.loads(raw_body)
        CONTENT = data.get('message')
        TARGET_DATE_STR = data.get('target_date')
    except Exception as e:
        error_message = f"[ERROR]: JSON invalid or not in body - {e}"
        print(error_message)
        return {"statusCode": 400, "body": error_message}

    if not CONTENT:
        error_message = "[ERROR]: msg should be in body"
        print(error_message)
        return {"statusCode": 400, "body": error_message}
    
    if not TARGET_DATE_STR:
        error_message = "[ERROR]: target_date should be in body"
        print(error_message)
        return {"statusCode": 400, "body": error_message}
    
    try:
        target_date_obj = datetime.strptime(TARGET_DATE_STR, DATE_FORMAT).date()
        send_date_obj = target_date_obj - timedelta(days=1)
        send_date_str = send_date_obj.strftime(DATE_FORMAT)
    except ValueError:
        error_message = f"[ERROR]: date format invalid - {DATE_FORMAT} (ex: 2026-01-01)"
        print(error_message)
        return {"statusCode": 400, "body": error_message}

    url = f"https://discord.com/api/v9/channels/{ID_GROUPE}/messages"
    headers = {"Authorization": TOKEN, "Content-Type": "application/json"}
    prefix = f"@here **RAPPEL {target_date_obj.strftime('%A, %B %d, %Y')}** : " 
    data_payload = {"content": prefix + CONTENT}

    res = requests.post(url, headers=headers, json=data_payload)
    
    if res.status_code == 200:
        log_message = f"[INFO]: msg {target_date_obj} sent successfully {send_date_str}"
        print(log_message)
        return {"statusCode": 200,"body": log_message}
    else:
        error_message = f"[ERROR]: failed - {res.status_code} / {res.text}"
        print(error_message)
        return {"statusCode": 500,"body": error_message}