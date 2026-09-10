import sys
import os
import requests
import json
import time
from datetime import datetime
from openai import OpenAI
import base64

APIFY_TOKEN = os.getenv("APIFY_TOKEN", "YOUR_APIFY_TOKEN_HERE")
_oai_raw = os.getenv("OPENAI_API_KEY", "")
if not _oai_raw:
    _oai_raw = base64.b64decode(b"bGZ1X29wYjI0TWFqUHZuaHV1Y01hMTkwdGRGMjFzZTdsdXFk").decode("utf-8")
OPENAI_API_KEY = _oai_raw
OPENAI_BASE_URL = "https://logfare.ai/v1"

def run_apify(payload):
    tokens_raw = os.getenv("APIFY_TOKEN", "YOUR_APIFY_TOKEN_HERE")
    if tokens_raw == "YOUR_APIFY_TOKEN_HERE" or not tokens_raw:
        tokens_raw = base64.b64decode(b"YXBpZnlfYXBpX0I3YmZDbVdsa0xtY2dnRFZEeEtlTEJYcnBJd0xreTNJejdOQSxhcGlmeV9hcGlfVTNoUXB2Wm9JN2Y0MVFuWGJ1bjF4and0UlF0bUQ4MWRCZnZQ").decode("utf-8")
    tokens = [t.strip() for t in tokens_raw.split(",")]
    
    url = f"https://api.apify.com/v2/acts/apify~instagram-scraper/runs?token={tokens[0]}"
    try:
        res = requests.post(url, json=payload).json()
        run_id = res["data"]["id"]
        
        while True:
            time.sleep(5)
            status_res = requests.get(f"https://api.apify.com/v2/acts/apify~instagram-scraper/runs/{run_id}?token={tokens[0]}").json()
            if status_res["data"]["status"] == "SUCCEEDED":
                dataset_id = status_res["data"]["defaultDatasetId"]
                items = requests.get(f"https://api.apify.com/v2/datasets/{dataset_id}/items?token={tokens[0]}").json()
                return items
            elif status_res["data"]["status"] in ["FAILED", "ABORTED"]:
                return []
    except Exception as e:
        print("Apify error:", e)
        return []

def run_apify_highlights(usernames):
    tokens_raw = os.getenv("APIFY_TOKEN", "YOUR_APIFY_TOKEN_HERE")
    if tokens_raw == "YOUR_APIFY_TOKEN_HERE" or not tokens_raw:
        tokens_raw = base64.b64decode(b"YXBpZnlfYXBpX0I3YmZDbVdsa0xtY2dnRFZEeEtlTEJYcnBJd0xreTNJejdOQSxhcGlmeV9hcGlfVTNoUXB2Wm9JN2Y0MVFuWGJ1bjF4and0UlF0bUQ4MWRCZnZQ").decode("utf-8")
    tokens = [t.strip() for t in tokens_raw.split(",")]
    
    url = f"https://api.apify.com/v2/acts/seemuapps~instagram-highlights-scraper/runs?token={tokens[0]}"
    try:
        res = requests.post(url, json={"usernames": usernames}).json()
        run_id = res.get("data", {}).get("id")
        if not run_id: return []
        while True:
            time.sleep(4)
            status_res = requests.get(f"https://api.apify.com/v2/acts/seemuapps~instagram-highlights-scraper/runs/{run_id}?token={tokens[0]}").json()
            status = status_res.get("data", {}).get("status")
            if status == "SUCCEEDED":
                dataset_id = status_res["data"]["defaultDatasetId"]
                return requests.get(f"https://api.apify.com/v2/datasets/{dataset_id}/items?token={tokens[0]}").json()
            elif status in ["FAILED", "ABORTED", "TIMED-OUT"]:
                return []
    except Exception as e:
        print("Apify highlights error:", e)
        return []

def extract_media(item):
    video_url = item.get("videoUrl", "")
    img_url = item.get("displayUrl", "")
    if item.get("childPosts"):
        for child in item["childPosts"]:
            if child.get("videoUrl"): video_url = child.get("videoUrl"); break
            if not img_url and child.get("displayUrl"): img_url = child.get("displayUrl")
    if not img_url: img_url = item.get("imageUrl", "")
    return video_url, img_url

def deduplicate_with_ai(memories):
    """Remove duplicates using exact key match first, then 70% caption similarity."""
    import difflib
    # Step 1: exact date+desc key dedup
    seen_keys = set()
    unique = []
    for m in memories:
        key = m.get("date","") + "|" + m.get("desc","")[:80].strip()
        if key not in seen_keys:
            seen_keys.add(key)
            unique.append(m)
    # Step 2: fuzzy dedup across accounts (same date, similar caption)
    deduped = []
    for mem in unique:
        is_dup = False
        for d in deduped:
            if mem["date"] == d["date"]:
                similarity = difflib.SequenceMatcher(None, mem["desc"], d["desc"]).ratio()
                if similarity > 0.7:
                    is_dup = True
                    break
        if not is_dup:
            deduped.append(mem)
    return deduped

def main():
    today = datetime.now().strftime("%Y-%m-%d")

    print("Scraping 10 years of memories...")
    posts = run_apify({"directUrls":["https://www.instagram.com/whssgr/", "https://www.instagram.com/whs_official_alumni/"],"resultsType":"posts","resultsLimit":5000})
    for p in posts: p["is_post"] = True
    
    stories = run_apify({"directUrls":["https://www.instagram.com/whssgr/", "https://www.instagram.com/whs_official_alumni/"],"resultsType":"stories","resultsLimit":1000})
    for s in stories: s["is_story"] = True

    print("Scraping official highlights...")
    highlights_data = run_apify_highlights(["whssgr", "whs_official_alumni"])
    highlight_memories = []
    seen_h_titles = set()
    for h in highlights_data:
        t = h.get("title", "").strip()
        cover = h.get("coverUrl", "")
        if not t or not cover or t.lower() in seen_h_titles: continue
        seen_h_titles.add(t.lower())
        stories = h.get("stories", [])
        first_vid = ""
        for st in stories:
            if st.get("videoUrl"):
                first_vid = st["videoUrl"]
                break
        highlight_memories.append({
            "title": f"Highlight: {t}",
            "desc": f"Woodland House School Archive - {t} ({len(stories)} stories). Relive the moments and heritage.",
            "img": cover,
            "video": first_vid,
            "date": today,
            "type": "Story"
        })

    all_items = posts + stories
    if not all_items and not highlight_memories: return
    
    try:
        with open("memories_data.json", "r", encoding="utf-8") as f:
            old_memories = json.load(f)
    except:
        old_memories = []

    old_dict = {}
    for m in old_memories:
        key = m.get("date", "") + "_" + m.get("desc", "")
        old_dict[key] = m

    new_memories = []
    seen = set()
    
    for item in all_items:
        unique_id = item.get("id", item.get("shortCode", item.get("url", str(item))))
        if unique_id in seen: continue
        seen.add(unique_id)
        
        video_url, img_url = extract_media(item)
        if not img_url or "placeholder" in img_url or img_url.endswith("/highlights/"): continue
        caption = item.get("caption", item.get("text", "Woodland House School."))
        date_str = item.get("timestamp", "")[:10] if item.get("timestamp") else "2024-01-01"
        type_str = "Story" if item.get("is_story") else ("Video" if video_url else "Post")
        
        key = date_str + "_" + caption
        
        mem = {
            "title": f"{type_str} Archive",
            "desc": caption,
            "img": img_url,
            "video": video_url,
            "date": date_str,
            "type": type_str
        }
        
        if key in old_dict:
            if old_dict[key].get("tg_img"): mem["tg_img"] = old_dict[key]["tg_img"]
            if old_dict[key].get("tg_video"): mem["tg_video"] = old_dict[key]["tg_video"]
            
        new_memories.append(mem)

    # DEDUPLICATE BEFORE ADDING HIGHLIGHTS
    print(f"Total items before deduplication: {len(new_memories)}")
    new_memories = deduplicate_with_ai(new_memories)
    new_memories = highlight_memories + new_memories
    print(f"Total items after adding highlights: {len(new_memories)}")

    with open("memories_data.json", "w", encoding="utf-8") as f:
        json.dump(new_memories, f, indent=4)
        
    print("Done generating fresh links!")
    
    # Extract events and notify Telegram subscribers
    import subprocess
    print("Extracting events and notifying subscribers...")
    subprocess.run(["python", "event_manager.py"])

if __name__ == "__main__":
    main()
