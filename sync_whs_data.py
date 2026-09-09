import os
import requests
import json
import time
from datetime import datetime
from openai import OpenAI

# SECURITY FIX: Using environment variables to hide exposed API keys
APIFY_TOKEN = os.getenv('APIFY_TOKEN', 'YOUR_APIFY_TOKEN_HERE')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', 'YOUR_OPENAI_API_KEY_HERE')
OPENAI_BASE_URL = 'https://logfare.ai/v1'

def run_apify(payload):
    url = f"https://api.apify.com/v2/acts/apify~instagram-scraper/runs?token={APIFY_TOKEN}"
    r = requests.post(url, json=payload)
    if r.status_code not in [200, 201]:
        print("Apify run failed. Check API key.")
        return []
    run_data = r.json()['data']
    run_id = run_data['id']
    dataset_id = run_data['defaultDatasetId']
    
    while True:
        status_r = requests.get(f"https://api.apify.com/v2/actor-runs/{run_id}?token={APIFY_TOKEN}").json()['data']
        if status_r['status'] in ['SUCCEEDED', 'FAILED', 'ABORTED']: break
        time.sleep(4)
        
    ds_r = requests.get(f"https://api.apify.com/v2/datasets/{dataset_id}/items?token={APIFY_TOKEN}").json()
    return ds_r

def extract_media(item):
    video_url = item.get('videoUrl', '')
    img_url = item.get('displayUrl', '')
    if not video_url and item.get('children'):
        for child in item.get('children'):
            if child.get('videoUrl'): video_url = child.get('videoUrl'); break
            if not img_url and child.get('displayUrl'): img_url = child.get('displayUrl')
    if not img_url: img_url = item.get('url', 'https://via.placeholder.com/800')
    return video_url, img_url

def main():
    if APIFY_TOKEN == 'YOUR_APIFY_TOKEN_HERE':
        print("SECURE MODE: Please set APIFY_TOKEN and OPENAI_API_KEY environment variables.")
        return

    print("Scraping 10 years of memories...")
    posts = run_apify({"directUrls":["https://www.instagram.com/whssgr/"],"resultsType":"posts","resultsLimit":5000})
    for p in posts: p['is_post'] = True
    
    stories = run_apify({"directUrls":["https://www.instagram.com/whssgr/"],"resultsType":"stories","resultsLimit":1000})
    for s in stories: s['is_story'] = True
    
    # Adding highlights specific call just in case Apify supports it via highlights/ URL
    highlights = run_apify({"directUrls":["https://www.instagram.com/whssgr/highlights/"],"resultsType":"stories","resultsLimit":1000})
    for h in highlights: h['is_story'] = True

    all_items = posts + stories + highlights
    if not all_items: return
    
    openai_client = OpenAI(api_key=OPENAI_API_KEY, base_url=OPENAI_BASE_URL)
    
    memories = []
    seen = set()
    all_captions = []
    
    for item in all_items:
        video_url, img_url = extract_media(item)
        if img_url in seen: continue
        seen.add(img_url)
        
        caption = item.get('caption', item.get('text', 'Woodland House School.'))
        date_str = item.get('timestamp', '')[:10] if item.get('timestamp') else "2024-01-01"
        type_str = "Story" if item.get('is_story') else ("Video" if video_url else "Post")
        
        all_captions.append(f"[{date_str}] {caption}")
        
        memories.append({
            "title": f"{type_str} Archive",
            "desc": caption,
            "img": img_url,
            "video": video_url,
            "date": date_str,
            "type": type_str
        })

    with open('memories_data.json', 'w', encoding='utf-8') as f:
        json.dump(memories, f, indent=4)
        
    print("Extracting chronological events...")
    combined_captions = "\n".join(all_captions[:40])
    today = datetime.now().strftime("%Y-%m-%d")
    
    prompt = f"""
    Read the following Instagram captions from Woodland House School.
    TODAY'S EXACT DATE IS: {today}
    
    You must classify events strictly based on today's date ({today}).
    - If the event date is strictly AFTER {today}, it goes in "upcoming".
    - If the event date is strictly BEFORE OR ON {today}, it goes in "past".
    
    DO NOT PUT PAST EVENTS IN THE UPCOMING LIST. For example, September 4th 2026 is BEFORE September 9th 2026, so it is a PAST event.
    
    Return ONLY valid JSON in this format:
    {{
      "upcoming": [ {{"name": "Event Name", "date": "Estimated Date", "desc": "Details"}} ],
      "past": [ {{"name": "Event Name", "date": "Date", "desc": "Details"}} ]
    }}
    Captions:
    {combined_captions}
    """
    
    try:
        resp = openai_client.chat.completions.create(model="auto", messages=[{"role":"user","content":prompt}])
        raw = resp.choices[0].message.content.strip()
        if raw.startswith("```json"): raw = raw[7:]
        if raw.startswith("```"): raw = raw[3:]
        if raw.endswith("```"): raw = raw[:-3]
        events_data = json.loads(raw.strip())
        with open('events.json', 'w', encoding='utf-8') as f:
            json.dump(events_data, f, indent=4)
        print("Events accurately mapped using today's date.")
    except Exception as e:
        print("Failed to map events:", e)

if __name__ == "__main__":
    main()
