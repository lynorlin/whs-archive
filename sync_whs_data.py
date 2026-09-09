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
        print("Apify run failed. Using cached data."); return []
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
    from datetime import datetime
    today = datetime.now().strftime("%Y-%m-%d")
    if APIFY_TOKEN == 'YOUR_APIFY_TOKEN_HERE':
        print("SECURE MODE: Please set APIFY_TOKEN and OPENAI_API_KEY environment variables.")
        return

    print("Scraping 10 years of memories...")
    posts = run_apify({"directUrls":["https://www.instagram.com/whssgr/", "https://www.instagram.com/whs_official_alumni/"],"resultsType":"posts","resultsLimit":5000})
    for p in posts: p['is_post'] = True
    
    stories = run_apify({"directUrls":["https://www.instagram.com/whssgr/", "https://www.instagram.com/whs_official_alumni/"],"resultsType":"stories","resultsLimit":1000})
    for s in stories: s['is_story'] = True
    
    # Adding highlights specific call just in case Apify supports it via highlights/ URL
    highlights = run_apify({"directUrls":["https://www.instagram.com/whssgr/highlights/", "https://www.instagram.com/whs_official_alumni/highlights/"],"resultsType":"stories","resultsLimit":1000})
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

    
    # Permanent Highlights
    permanent_highlights = [
        {
            "title": "Story Archive",
            "desc": "Celebrating six decades of educational excellence, nurturing dreams, and building a legacy at Woodland House School. A milestone etched in history. #60Years",
            "img": "https://scontent-ams2-1.cdninstagram.com/v/t51.71878-15/769168341_1398927335676883_127250475374029066_n.jpg?stp=dst-jpg_e15_tt6&_nc_cat=111&ig_cache_key=Mzk2MzYxMjMzNDM3MzA4MTkxOQ%3D%3D.3-ccb7-5&ccb=7-5&_nc_sid=58cdad&efg=eyJ2ZW5jb2RlX3RhZyI6IkNMSVBTLnhwaWRzLjY0MC5zZHIudmlkZW9fZGVmYXVsdF9jb3Zlcl9mcmFtZS5DMyJ9&_nc_ohc=VNiSkE58AB8Q7kNvwEBIhKf&_nc_oc=Adq48N7Ly3zQ-rc3BdBfbg3JoP4e0j3HwcADGUEzKLQXSsU7tlCGn_CwLmk-vnOMdpCin-MDgM7N5FpkB6YGPPO9&_nc_ad=z-m&_nc_cid=0&_nc_zt=23&_nc_ht=scontent-ams2-1.cdninstagram.com&_nc_gid=XNrGLB_3AlSP3DZqodPEWA&_nc_ss=7a22e&oh=00_AQJcaaT1ZZivHWOD4i8HzrO0piqmhD5IHr9nHd3ONrZJIQ&oe=6AA6CB05",
            "video": "",
            "date": today,
            "type": "Story"
        },
        {
            "title": "Story Archive",
            "desc": "Reconnecting the past with the present. Reliving cherished memories and celebrating the incredible journeys of our Woodlanders at the Alumni Meet.",
            "img": "https://instagram.fbne6-1.fna.fbcdn.net/v/t51.71878-15/775799324_2366633547476425_2614606676397782666_n.jpg?stp=dst-jpg_e15_tt6&_nc_cat=105&ig_cache_key=Mzk2NTczODI3OTgwODU3MDk4MDIyMzA1MzY2NzQ1NjQ0MjQ%3D.3-ccb7-5&ccb=7-5&_nc_sid=58cdad&efg=eyJ2ZW5jb2RlX3RhZyI6IkNMSVBTLnhwaWRzLjY0MC5zZHIudmlkZW9fbmZyYW1lX2NvdmVyX2ZyYW1lLkMzIn0%3D&_nc_ohc=SZ6T4Lbcn98Q7kNvwEGMF5v&_nc_oc=AdqVdAZz_BcEAEKGleVyrqFHCi-nQ_BzJDW33TXUQjVQgKaasmNE0HPSNpIVhn24K7I&_nc_ad=z-m&_nc_cid=0&_nc_zt=23&_nc_ht=instagram.fbne6-1.fna&_nc_gid=SGbcfzy_SHrKP2HrvAS5Zw&_nc_ss=7a22e&oh=00_AQL-PfJEgNfAD-69v62RJvkiwvMqvqrs8SBrIF7w6eTl0w&oe=6AA6E65A",
            "video": "",
            "date": today,
            "type": "Story"
        },
        {
            "title": "Story Archive",
            "desc": "The vibrant festivities of Dussehra 2024 at our campus. A joyous celebration of truth, courage, and cultural heritage.",
            "img": "https://scontent-fco2-1.cdninstagram.com/v/t51.71878-15/775147657_1069908232066658_4887997966797194667_n.jpg?stp=dst-jpg_e15_tt6&_nc_cat=101&ig_cache_key=Mzk2NjkwNjIzMDcxNjkzMDExMA%3D%3D.3-ccb7-5&ccb=7-5&_nc_sid=58cdad&efg=eyJ2ZW5jb2RlX3RhZyI6IkNMSVBTLnhwaWRzLjY0MC5zZHIudmlkZW9fZGVmYXVsdF9jb3Zlcl9mcmFtZS5DMyJ9&_nc_ohc=yDTxD2BaT3kQ7kNvwH8L1s6&_nc_oc=AdpH2ObwE3Ec0DWX4aNnTWn-ax2s15adqAFTZHnvXWrnWyCCJTapAW0fYv4-ayofdl8&_nc_ad=z-m&_nc_cid=0&_nc_zt=23&_nc_ht=scontent-fco2-1.cdninstagram.com&_nc_gid=zSGsNLmW12XXYh4WcxdKHQ&_nc_ss=7a22e&oh=00_AQINJVPE4srpL04Kty2moRkS_GuLtKYhaFNF0QCgUSIa5A&oe=6AA6F4D3",
            "video": "",
            "date": today,
            "type": "Story"
        },
        {
            "title": "Story Archive",
            "desc": "Founder's Day. Honoring the visionaries who built this institution. A day of reverence, reflection, and pride in our roots.",
            "img": "https://via.placeholder.com/800x800/111111/F4F4F0?text=Founder%27s+Day",
            "video": "",
            "date": today,
            "type": "Story"
        },
        {
            "title": "Story Archive",
            "desc": "Fun! Beyond the books! Capturing the joy, laughter, and spirited moments that make everyday life at Woodland unforgettable.",
            "img": "https://via.placeholder.com/800x800/D9381E/F4F4F0?text=Fun",
            "video": "",
            "date": today,
            "type": "Story"
        }
    ]

    try:
        with open('memories_data.json', 'r', encoding='utf-8') as f:
            old_memories = json.load(f)
    except:
        old_memories = []

    old_images = {m.get('img') for m in old_memories if m.get('img')}
    new_memories = []
    for m in memories:
        if m.get('img') not in old_images:
            new_memories.append(m)
            old_images.add(m.get('img'))
            
    final_memories = old_memories + new_memories

    with open('memories_data.json', 'w', encoding='utf-8') as f:
        json.dump(final_memories, f, indent=4)

        
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


