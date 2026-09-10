import os
import json
import base64
import requests
from openai import OpenAI
from datetime import datetime

BOT_TOKEN = "8781356380:AAGc1w9SBiV6AOMtpNO_JpypaeXdW54WwMw"
_oai_raw = os.getenv("OPENAI_API_KEY", "")
if not _oai_raw:
    _oai_raw = base64.b64decode(b"bGZ1X29wYjI0TWFqUHZuaHV1Y01hMTkwdGRGMjFzZTdsdXFk").decode("utf-8")
OPENAI_API_KEY = _oai_raw
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
        
    today_str = datetime.now().strftime("%Y-%m-%d")
    prompt = f'''
    Today's date is {today_str}.
    Extract school events from these recent Instagram posts. 
    CRITICAL: Any event that occurred on or before {today_str} MUST be placed in "past".
    ONLY events occurring strictly in the future (after {today_str}) can be placed in "upcoming".
    
    Output JSON format ONLY:
    {{
        "upcoming": [{{"date": "YYYY-MM-DD", "name": "Event Name", "desc": "Short description"}}],
        "past": [{{"date": "YYYY-MM-DD", "name": "Event Name", "desc": "Short description"}}]
    }}
    
    Recent posts:
    {captions}
    '''
    
    try:
        client = OpenAI(api_key=OPENAI_API_KEY, base_url=OPENAI_BASE_URL)
        response = client.chat.completions.create(
            model="logfare/auto",
            messages=[{"role": "user", "content": prompt}],
            response_format={ "type": "json_object" }
        )
        raw_data = json.loads(response.choices[0].message.content)
        
        # Enforce strict date logic in code
        all_events = raw_data.get("upcoming", []) + raw_data.get("past", [])
        clean_upcoming = []
        clean_past = []
        for ev in all_events:
            d = ev.get("date", "")
            if d and d > today_str:
                clean_upcoming.append(ev)
            else:
                clean_past.append(ev)
        new_events_data = {"upcoming": clean_upcoming, "past": clean_past}
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
