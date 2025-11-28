from flask import Flask, request, jsonify
import requests
import os
from datetime import datetime, timedelta

app = Flask(__name__)

DATE_FORMAT = '%Y-%m-%d'

@app.route('/app/send_rappel', methods=['POST'])
@app.route('/api/send_rappel', methods=['POST'])
def send_rappel():
    TOKEN = os.getenv("TOKEN_DISCORD")
    ID_GROUPE = os.getenv("TARGET_GROUP_ID")

    if not all([TOKEN, ID_GROUPE]):
        error_message = "missing env var (TOKEN_DISCORD or TARGET_GROUP_ID)"
        print(f"[ERROR]: {error_message}")
        return jsonify({"error": error_message}), 500
    
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "invalid JSON body"}), 400
            
        CONTENT = data.get('message')
        TARGET_DATE_STR = data.get('target_date') or data.get('date')
    except Exception as e:
        error_message = f"error parsing body: {str(e)}"
        print(f"[ERROR]: {error_message}")
        return jsonify({"error": error_message}), 400

    if not CONTENT:
        error_message = "message is required in body"
        print(f"[ERROR]: {error_message}")
        return jsonify({"error": error_message}), 400
    
    if not TARGET_DATE_STR:
        error_message = "target_date is required in body"
        print(f"[ERROR]: {error_message}")
        return jsonify({"error": error_message}), 400
    
    try:
        target_date_obj = datetime.strptime(TARGET_DATE_STR, DATE_FORMAT).date()
        send_date_obj = target_date_obj - timedelta(days=1)
        send_date_str = send_date_obj.strftime(DATE_FORMAT)
    except ValueError:
        error_message = f"invalid date format - {DATE_FORMAT} (ex: 2026-01-01)"
        print(f"[ERROR]: {error_message}")
        return jsonify({"error": error_message}), 400

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
            return jsonify({
                "success": True,
                "message": log_message,
                "target_date": TARGET_DATE_STR,
                "send_date": send_date_str
            }), 200
        else:
            error_message = f"Discord API error: {res.status_code} - {res.text}"
            print(f"[ERROR]: {error_message}")
            return jsonify({"error": error_message}), 500
    except requests.exceptions.RequestException as e:
        error_message = f"Request failed: {str(e)}"
        print(f"[ERROR]: {error_message}")
        return jsonify({"error": error_message}), 500

@app.route('/', methods=['GET'])
def index():
    return '''
    <!DOCTYPE html>
    <html lang="fr">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Rappels Discord</title>
        <style>
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
                margin: 0;
                padding: 0;
                display: flex;
                justify-content: center;
                align-items: center;
                min-height: 100vh;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
            }
            .container {
                text-align: center;
                padding: 2rem;
            }
            h1 {
                margin: 0 0 1rem 0;
                font-size: 2.5rem;
            }
            p {
                margin: 0.5rem 0;
                opacity: 0.9;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Rappels Discord</h1>
            <p>API de rappels pour Discord</p>
            <p style="margin-top: 2rem; font-size: 0.9rem; opacity: 0.7;">Endpoint: /app/send_rappel</p>
        </div>
    </body>
    </html>
    '''

if __name__ == '__main__':
    app.run(debug=True)

