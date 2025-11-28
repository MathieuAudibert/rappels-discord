# this file is basically the script you can run. check /api/send-rappel for the clean/accessible vercel api

import requests
import os
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("TOKEN_DISCORD")
BASE_GROUP=os.getenv("BASE_GROUP")

def send_rappel(content, date, ID_GROUPE):
    url=f"https://discord.com/api/v9/channels/{ID_GROUPE}/messages"
    headers={"Authorization": f"{TOKEN}"}
    prefix=f"@here **RAPPEL {date}** : "
    data={"content": prefix+content}

    res = requests.post(url, headers=headers, json=data)
    if res.status_code == 200:
        print("[INFO]: msg sent successfully")
    else:
        print(f"[ERROR]: {res.text}")


if __name__ == "__main__":
    content = input("[INFO]: message - ")
    date= input("[INFO]: date - ")
    ID_GROUPE=input("[INFO]: groupd id - ")
   
    if ID_GROUPE == "":
        ID_GROUPE=BASE_GROUP
    send_rappel(content, date, ID_GROUPE)