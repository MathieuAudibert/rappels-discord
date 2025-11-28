import requests
import os
import json
from datetime import datetime, timedelta

DATE_FORMAT = '%Y-%m-%d'

def handler(request, context):
    method = request.get('httpMethod') or request.get('method', 'GET')
    
    if method != 'POST':
        return {"statusCode": 405,"body": json.dumps({"error": "method not allowed, only POST"})}

    TOKEN = os.getenv("TOKEN_DISCORD")
    ID_GROUPE = os.getenv("TARGET_GROUP_ID")

    if not all([TOKEN, ID_GROUPE]):
        error_message = "missing env var (TOKEN_DISCORD or TARGET_GROUP_ID)"
        print(f"[ERROR]: {error_message}") 
        return {"statusCode": 500,"body": json.dumps({"error": error_message})}
    
    try:
        raw_body = request.get('body', '{}')
        if isinstance(raw_body, str):
            data = json.loads(raw_body)
        else:
            data = raw_body
            
        CONTENT = data.get('message')
        TARGET_DATE_STR = data.get('target_date')
    except Exception as e:
        error_message = f"invalid JSON body: {str(e)}"
        print(f"[ERROR]: {error_message}")
        return {"statusCode": 400,"body": json.dumps({"error": error_message})}

    if not CONTENT:
        error_message = "message is required in body"
        print(f"[ERROR]: {error_message}")
        return {"statusCode": 400,"body": json.dumps({"error": error_message})}
    
    if not TARGET_DATE_STR:
        error_message = "target_date is required in body"
        print(f"[ERROR]: {error_message}")
        return {"statusCode": 400,"body": json.dumps({"error": error_message})}
    
    try:
        target_date_obj = datetime.strptime(TARGET_DATE_STR, DATE_FORMAT).date()
        send_date_obj = target_date_obj - timedelta(days=1)
        send_date_str = send_date_obj.strftime(DATE_FORMAT)
    except ValueError:
        error_message = f"invalid date format - {DATE_FORMAT} (ex: 2026-01-01)"
        print(f"[ERROR]: {error_message}")
        return {"statusCode": 400,"body": json.dumps({"error": error_message})}

    url = f"https://discord.com/api/v9/channels/{ID_GROUPE}/messages"
    headers = {
        "Authorization": TOKEN,
        "Content-Type": "application/json"
    }
    
    days_fr = ['lundi', 'mardi', 'mercredi', 'jeudi', 'vendredi', 'samedi', 'dimanche']
    months_fr = ['janvier', 'février', 'mars', 'avril', 'mai', 'juin', 'juillet', 'août', 'septembre', 'octobre', 'novembre', 'décembre']
    
    day_name = days_fr[target_date_obj.weekday()]
    month_name = months_fr[target_date_obj.month - 1]
    formatted_date = f"{day_name.capitalize()}, {target_date_obj.day} {month_name} {target_date_obj.year}"
    
    prefix = f"@here **RAPPEL {formatted_date}** : "
    data_payload = {"content": prefix + CONTENT}

    try:
        res = requests.post(url, headers=headers, json=data_payload, timeout=10)
        
        if res.status_code == 200:
            log_message = f"msg for {formatted_date} sent successfully (scheduled for {send_date_str})"
            print(f"[INFO]: {log_message}")
            return {
                "statusCode": 200,
                "body": json.dumps({
                    "success": True,
                    "message": log_message,
                    "target_date": TARGET_DATE_STR,
                    "send_date": send_date_str
                })
            }
        else:
            error_message = f"Discord API error: {res.status_code} - {res.text}"
            print(f"[ERROR]: {error_message}")
            return {
                "statusCode": 500,
                "body": json.dumps({"error": error_message})
            }
    except requests.exceptions.RequestException as e:
        error_message = f"Request failed: {str(e)}"
        print(f"[ERROR]: {error_message}")
        return {
            "statusCode": 500,
            "body": json.dumps({"error": error_message})
        }