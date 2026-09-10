import os
import json
import requests
from openai import OpenAI
from datetime import datetime

BOT_TOKEN = "8781356380:AAGc1w9SBiV6AOMtpNO_JpypaeXdW54WwMw"
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "YOUR_OPENAI_API_KEY_HERE")
OPENAI_BASE_URL = "https://logfare.ai/v1"
SUBSCRIBERS_FILE = "subscribers.json"
EVENTS_FILE = "events.json"
MEMORIES_FILE = "memories_data.json"

def get_subscribers():
    if os.path.exists(SUBSCRIBERS_FILE):
        with open(SUBSCRIBERS_FILE, 'r') as f:
            subs = json.load(f)
    else:
        subs = []
        
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates"
    try:
        res = requests.get(url, timeout=10).json()
        if res.get("ok"):
            for result in res.get("result", []):
                msg = result.get("message", {})
                chat_id = msg.get("chat", {}).get("id")
                if chat_id and chat_id not in subs:
                    subs.append(chat_id)
                    send_msg(chat_id, "Welcome to Woodland House School Notifications! You will receive updates about upcoming events.")
    except Exception as e:
        print("Error fetching Telegram updates:", e)
        
    with open(SUBSCRIBERS_FILE, 'w') as f:
        json.dump(subs, f)
    return subs

def send_msg(chat_id, text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": chat_id, "text": text}
    requests.post(url, json=payload)

def extract_events():
    if not os.path.exists(MEMORIES_FILE): return
    with open(MEMORIES_FILE, 'r', encoding='utf-8') as f:
        memories = json.load(f)[:15]
        
    captions = "\n---\n".join([f"Date: {m['date']}\nCaption: {m['desc']}" for m in memories])
    
    if os.path.exists(EVENTS_FILE):
        with open(EVENTS_FILE, 'r', encoding='utf-8') as f:
            old_events_data = json.load(f)
    else:
        old_events_data = {"upcoming": [], "past": []}
        
    prompt = f'''
    Extract school events from these recent Instagram posts. 
    Separate them into "upcoming" and "past" events.
    Output JSON format ONLY:
    {{
        "upcoming": [{{"date": "YYYY-MM-DD or specific date mentioned", "name": "Event Name", "desc": "Short description"}}],
        "past": [{{"date": "YYYY-MM-DD", "name": "Event Name", "desc": "Short description"}}]
    }}
    
    Recent posts:
    {captions}
    '''
    
    try:
        client = OpenAI(api_key=OPENAI_API_KEY, base_url=OPENAI_BASE_URL)
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            response_format={ "type": "json_object" }
        )
        new_events_data = json.loads(response.choices[0].message.content)
    except Exception as e:
        print("Error extracting events via AI:", e)
        return
        
    old_upcoming_names = [e["name"] for e in old_events_data.get("upcoming", [])]
    new_upcoming = [e for e in new_events_data.get("upcoming", []) if e["name"] not in old_upcoming_names]
    
    with open(EVENTS_FILE, 'w', encoding='utf-8') as f:
        json.dump(new_events_data, f, indent=4)
        
    if new_upcoming:
        subs = get_subscribers()
        for ev in new_upcoming:
            msg = f"🔔 *NEW UPCOMING EVENT*\n\n*Name:* {ev['name']}\n*Date:* {ev['date']}\n*Details:* {ev['desc']}"
            for sub in subs:
                send_msg(sub, msg)
                
if __name__ == "__main__":
    get_subscribers()
    extract_events()
