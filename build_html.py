import json

def build():
    try:
        with open('memories_data.json', 'r', encoding='utf-8-sig') as f:
            memories = f.read().strip()
    except:
        memories = "[]"
        
    try:
        with open('events.json', 'r', encoding='utf-8-sig') as f:
            events = f.read().strip()
    except:
        events = '{"upcoming":[], "past":[]}'

    try:
        with open('funders.json', 'r', encoding='utf-8-sig') as f:
            funders = f.read().strip()
    except:
        funders = '[{"name": "Founding Patron", "role": "Legacy Benefactor", "tier": "Diamond Patron", "note": "The primary visionary who funded and made the creation of this permanent archive possible."}]'


    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>WHS | The Vault</title>
<link rel="icon" href="data:;base64,iVBORw0KGgo=">
<link href="https://fonts.googleapis.com/css2?family=Oswald:wght@300;400;500;700&family=JetBrains+Mono:wght@100;400;700&display=swap" rel="stylesheet">
<script src="https://cdnjs.cloudflare.com/ajax/libs/animejs/3.2.1/anime.min.js"></script>

<script>
    function triggerNotify(btn) {{
        btn.innerText = "? Subscribed";
        btn.style.background = "var(--text)";
        btn.style.color = "var(--bg)";
    }}

    function initFilters() {{
        const filterBtns = document.querySelectorAll('.filter-btn');
        filterBtns.forEach(btn => {{
            btn.addEventListener('click', () => {{
                filterBtns.forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
                const filter = btn.dataset.filter;
                if(filter === 'all') {{
                    window._filteredMem = window._allMemories.slice();
                }} else if(filter === 'video') {{
                    window._filteredMem = window._allMemories.filter(m => m._hasVideo);
                }} else {{
                    window._filteredMem = window._allMemories.filter(m => !m._hasVideo);
                }}
                window._renderCount = 0;
                document.getElementById('gallery').innerHTML = '';
                const lb = document.getElementById('load-more-btn');
                if(lb) lb.style.display = 'inline-block';
                window.renderMore();
            }});
        }});
    }}
</script>

<style>
/* EDITORIAL BRUTALISM AESTHETIC */
:root {{
    --bg: #F4F4F0;
    --text: #111111;
    --accent: #D9381E; 
    --border: #111111;
}}
* {{ box-sizing: border-box; margin: 0; padding: 0; cursor: none; }}
body {{
    font-family: 'JetBrains Mono', monospace;
    background-color: var(--bg);
    color: var(--text);
    overflow-x: hidden;
}}
::-webkit-scrollbar {{ width: 8px; }}
::-webkit-scrollbar-track {{ background: var(--bg); border-left: 1px solid var(--border); }}
::-webkit-scrollbar-thumb {{ background: var(--text); }}

.cursor-dot, .cursor-outline {{ position: fixed; top: 0; left: 0; transform: translate(-50%, -50%); border-radius: 50%; z-index: 10000; pointer-events: none; }}
.cursor-dot {{ width: 8px; height: 8px; background: var(--accent); }}
.cursor-outline {{ width: 40px; height: 40px; border: 2px solid var(--text); transition: width 0.2s, height 0.2s, background 0.2s; }}
@media (max-width: 768px) {{ .cursor-dot, .cursor-outline {{ display: none; }} * {{ cursor: auto !important; }} }}

#preloader {{
    position: fixed; top: 0; left: 0; width: 100vw; height: 100vh;
    background: var(--text); color: var(--bg); z-index: 9999;
    display: flex; flex-direction: column; align-items: center; justify-content: center;
    padding: 20px; text-align: center;
}}
#preloader h1 {{ font-size: clamp(2rem, 5vw, 4rem); letter-spacing: 5px; }}
.load-bar-container {{ width: 100%; max-width: 300px; height: 2px; background: rgba(255,255,255,0.2); margin-top: 20px; overflow: hidden; }}
.load-bar {{ width: 0%; height: 100%; background: var(--accent); }}

.grid-overlay {{
    position: fixed; top: 0; left: 0; width: 100vw; height: 100vh;
    background-image: linear-gradient(rgba(17,17,17,0.05) 1px, transparent 1px), linear-gradient(90deg, rgba(17,17,17,0.05) 1px, transparent 1px);
    background-size: 50px 50px; z-index: -1; pointer-events: none;
}}

h1, h2, h3, .display-text {{ font-family: 'Oswald', sans-serif; text-transform: uppercase; }}

nav {{
    position: fixed; top: 0; left: 0; width: 100%; border-bottom: 2px solid var(--border);
    display: flex; justify-content: space-between; padding: 20px 40px;
    background: var(--bg); z-index: 100; text-transform: uppercase; font-weight: 700;
}}
.nav-links a {{ text-decoration: none; color: var(--text); margin-left: 30px; position: relative; }}
@media (max-width: 768px) {{
    nav {{ padding: 15px 20px; flex-direction: column; gap: 10px; text-align: center; }}
    .nav-links a {{ margin: 0 10px; font-size: 0.8rem; }}
}}

.hero {{
    min-height: 100vh; padding: 140px 40px 40px 40px; display: flex; flex-direction: column; justify-content: space-between;
    border-bottom: 2px solid var(--border);
}}
.hero-line-container {{ font-family:'Oswald'; font-size: clamp(3rem, 10vw, 10rem); line-height: 1; margin-bottom: 40px; text-transform:uppercase; }}
.hero-marquee {{ overflow: hidden; white-space: nowrap; border-top: 2px solid var(--border); border-bottom: 2px solid var(--border); padding: 10px 0; margin-bottom: 40px; }}
.marquee-content {{ display: inline-block; font-size: 8vw; font-family: 'Oswald', sans-serif; font-weight: 700; letter-spacing: -2px; }}
@media (max-width: 768px) {{ .hero {{ padding: 120px 20px 20px 20px; }} }}

section {{ border-bottom: 2px solid var(--border); }}
.section-header {{ padding: 40px; border-bottom: 2px solid var(--border); background: var(--text); color: var(--bg); }}
.section-title {{ font-size: clamp(2.5rem, 5vw, 4rem); letter-spacing: 2px; }}
@media (max-width: 768px) {{ .section-header {{ padding: 20px; }} }}

/* Timeline */
.events-wrapper {{ display: flex; flex-wrap: wrap; }}
.event-col {{ flex: 1; min-width: 100%; border-right: none; border-bottom: 2px solid var(--border); }}
@media (min-width: 768px) {{
    .event-col {{ min-width: 300px; border-right: 2px solid var(--border); border-bottom: none; }}
    .event-col:last-child {{ border-right: none; }}
}}
.event-col-title {{ padding: 20px 40px; border-bottom: 2px solid var(--border); font-size: 1.5rem; background: var(--bg); color: var(--text); font-weight:bold; }}
.event-item {{ padding: 30px 40px; border-bottom: 2px solid var(--border); transition: background 0.3s; position: relative; }}
.event-item:last-child {{ border-bottom: none; }}
.event-item:hover {{ background: #e5e5df; }}
.e-date {{ font-size: 0.8rem; color: var(--accent); margin-bottom: 10px; font-weight: 700; }}
.e-title {{ font-size: 2rem; font-family: 'Oswald'; margin-bottom: 10px; line-height: 1.2; }}
@media (max-width: 768px) {{ .event-col-title, .event-item {{ padding: 20px; }} .e-title {{ font-size: 1.5rem; }} }}

.notify-btn {{
    margin-top: 15px; padding: 10px 20px; border: 2px solid var(--text); background: transparent;
    font-family: 'Oswald'; text-transform: uppercase; font-weight: 700; transition: all 0.3s;
}}
.notify-btn:hover {{ background: var(--text); color: var(--bg); }}

/* Story Playlist UI */
.story-playlist-container {{
    border-bottom: 2px solid var(--border); padding: 40px; background: var(--bg);
}}
.story-playlist-title {{ font-size: 1.5rem; font-family: 'Oswald'; text-transform: uppercase; margin-bottom: 20px; }}
.story-scroll {{ display: flex; gap: 20px; overflow-x: auto; padding-bottom: 20px; }}
.story-scroll::-webkit-scrollbar {{ height: 6px; }}
.story-scroll::-webkit-scrollbar-track {{ background: transparent; }}
.story-scroll::-webkit-scrollbar-thumb {{ background: var(--text); }}
.story-item {{ min-width: 200px; width: 200px; border: 2px solid var(--border); background: #000; position: relative; cursor: pointer; aspect-ratio: 9/16; flex-shrink: 0; overflow: hidden; }}
.story-item img {{ width: 100%; height: 100%; object-fit: cover; opacity: 0.7; transition: 0.3s; filter: grayscale(100%); }}
.story-item:hover img {{ opacity: 1; filter: grayscale(0%); transform: scale(1.05); }}
.story-play-btn {{ position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); border: 2px solid #fff; color: #fff; background: rgba(0,0,0,0.5); padding: 10px; font-family: 'Oswald'; text-transform: uppercase; font-size: 0.8rem; pointer-events: none; opacity: 0; transition: 0.3s; }}
.story-item:hover .story-play-btn {{ opacity: 1; }}

/* Filter Bar */
.filter-bar {{ padding: 20px 40px; border-bottom: 2px solid var(--border); display: flex; gap: 15px; background: var(--bg); overflow-x: auto; }}
.filter-btn {{ padding: 8px 20px; border: 2px solid var(--text); background: transparent; font-family: 'Oswald'; font-weight: bold; text-transform: uppercase; transition: 0.3s; white-space: nowrap; }}
.filter-btn:hover, .filter-btn.active {{ background: var(--text); color: var(--bg); }}

/* Archives Grid */
.archive-grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); }}
.memory-card {{ border-right: 2px solid var(--border); border-bottom: 2px solid var(--border); position: relative; overflow: hidden; background: var(--bg); transition: 0.3s; display: block; }}
.memory-card.hidden {{ display: none; }}
.memory-media {{ width: 100%; aspect-ratio: 1/1; position: relative; border-bottom: 2px solid var(--border); overflow: hidden; background: #000; }}
.memory-media img, .memory-media video {{ width: 100%; height: 100%; object-fit: cover; opacity: 0.8; transition: 0.5s; filter: grayscale(100%); pointer-events: none; }}
.memory-card:hover .memory-media img, .memory-card:hover .memory-media video {{ opacity: 1; filter: grayscale(0%); transform: scale(1.05); }}
.memory-info {{ padding: 25px; pointer-events: none; }}
.m-type {{ font-size: 0.7rem; background: var(--text); color: var(--bg); padding: 5px 10px; display: inline-block; margin-bottom: 15px; text-transform: uppercase; font-weight: bold; }}
.type-story {{ background: var(--accent); }}
.type-video {{ background: #000; color: #fff; }}
.m-title {{ font-size: 1.5rem; font-family: 'Oswald'; margin-bottom: 10px; line-height: 1.2; }}
.m-desc {{ font-size: 0.85rem; line-height: 1.5; max-height: 80px; overflow: hidden; text-overflow: ellipsis; display: -webkit-box; -webkit-line-clamp: 4; -webkit-box-orient: vertical; }}

.play-btn {{ position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); border: 2px solid #fff; color: #fff; background: rgba(0,0,0,0.5); padding: 15px 30px; font-family: 'Oswald'; text-transform: uppercase; opacity: 0; transition: opacity 0.3s; pointer-events: none; text-align: center; }}
.memory-card:hover .play-btn {{ opacity: 1; }}

@media (max-width: 768px) {{ 
    .play-btn {{ opacity: 1; padding: 10px 20px; font-size: 0.8rem; }} 
    .story-play-btn {{ opacity: 1 !important; }}
    .story-item img {{ opacity: 1 !important; filter: grayscale(0%) !important; }}
    .memory-media img, .memory-media video {{ opacity: 1 !important; filter: grayscale(0%) !important; }}
}}

/* Modal */
#video-modal {{ position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; background: rgba(17,17,17,0.98); z-index: 100000; display: none; flex-direction: column; align-items: center; justify-content: center; opacity: 0; padding: 20px; }}
#modal-close {{ position: absolute; top: 20px; right: 20px; color: #fff; font-size: 1.5rem; font-family: 'Oswald'; font-weight: bold; padding: 10px; z-index: 100001; }}
#modal-content-container {{ width: 100%; max-width: 1000px; max-height: 70vh; position: relative; border: 2px solid var(--accent); background: #000; box-shadow: 0 20px 50px rgba(0,0,0,0.5); display: flex; justify-content: center; align-items: center; }}
#modal-media {{ width: 100%; height: 100%; max-height: 70vh; object-fit: contain; display: block; }}
#modal-caption {{ color: #fff; font-family: 'JetBrains Mono'; margin-top: 20px; text-align: center; max-width: 800px; line-height: 1.5; font-size: 0.9rem; overflow-y: auto; max-height: 15vh; padding: 0 20px; }}

#toast {{ position: fixed; bottom: -100px; left: 50%; transform: translateX(-50%); background: var(--accent); color: #fff; font-family: 'Oswald'; font-size: 1.2rem; padding: 15px 40px; border-radius: 5px; z-index: 999999; box-shadow: 0 10px 30px rgba(217, 56, 30, 0.4); text-transform: uppercase; letter-spacing: 1px; }}

/* Audio Player */
#audio-controls {{
    position: fixed; bottom: 30px; right: 30px; z-index: 9999;
}}
#audio-toggle {{
    padding: 10px 20px; border: 2px solid var(--text); background: var(--bg); color: var(--text);
    font-family: 'Oswald'; font-weight: bold; text-transform: uppercase; box-shadow: 4px 4px 0 var(--text);
    transition: all 0.2s;
}}
#audio-toggle:hover {{ transform: translate(2px, 2px); box-shadow: 2px 2px 0 var(--text); }}
@media (max-width: 768px) {{ #audio-controls {{ bottom: 15px; right: 15px; }} }}

/* Mentors */
.mentors-grid {{ display: flex; flex-wrap: wrap; }}
.mentor-card {{ flex: 1 1 250px; border-right: 2px solid var(--border); border-bottom: 2px solid var(--border); padding: 40px; text-align: center; transition: background 0.3s; }}
.mentor-card:hover {{ background: var(--text); color: var(--bg); }}
.mentor-card:hover .mentor-role {{ color: var(--bg); }}
.mentor-name {{ font-size: 2rem; font-family: 'Oswald'; margin-bottom: 10px; }}
.mentor-role {{ font-size: 0.8rem; color: var(--accent); text-transform: uppercase; font-weight: 700; transition: color 0.3s; }}
@media (max-width: 768px) {{ .mentor-card {{ padding: 30px; }} }}

/* Funders Section — Brutalist palette */
#funders {{ position: relative; border-bottom: 2px solid var(--border); overflow: hidden; background: var(--bg); }}
.funders-money-canvas {{ position: absolute; top: 0; left: 0; width: 100%; height: 100%; pointer-events: none; z-index: 1; opacity: 0.4; }}
.funders-intro-banner {{ padding: 30px 40px; border-bottom: 2px solid var(--border); display: flex; justify-content: space-between; align-items: center; gap: 30px; background: var(--bg); position: relative; z-index: 2; }}
.funders-intro-text {{ max-width: 680px; }}
.funders-intro-text strong {{ display: block; font-family: 'Oswald', sans-serif; font-size: 1.4rem; color: var(--text); letter-spacing: 1px; margin-bottom: 8px; text-transform: uppercase; }}
.funders-intro-text p {{ font-size: 0.88rem; line-height: 1.65; opacity: 0.75; margin: 0; font-family: 'JetBrains Mono', monospace; }}
.funders-cta-wrap {{ flex-shrink: 0; display: flex; flex-direction: column; gap: 10px; align-items: flex-end; }}
.funder-pledge-btn {{ display: inline-flex; align-items: center; gap: 10px; padding: 14px 28px; background: var(--text); color: var(--bg); font-family: 'Oswald', sans-serif; font-weight: 700; font-size: 1rem; letter-spacing: 1.5px; text-transform: uppercase; text-decoration: none; border: 2px solid var(--text); box-shadow: 4px 4px 0 var(--accent); transition: all 0.2s; cursor: pointer; }}
.funder-pledge-btn:hover {{ transform: translate(-3px, -3px); box-shadow: 7px 7px 0 var(--accent); }}
.funder-stars-note {{ font-family: 'JetBrains Mono', monospace; font-size: 0.7rem; color: var(--accent); letter-spacing: 1px; text-transform: uppercase; text-align: right; }}
.funders-grid {{ display: flex; flex-wrap: wrap; position: relative; z-index: 2; }}
.funder-card {{ flex: 1 1 280px; border-right: 2px solid var(--border); border-bottom: 2px solid var(--border); padding: 45px 35px; text-align: center; position: relative; overflow: hidden; background: var(--bg); transition: background 0.3s, color 0.3s; cursor: default; }}
.funder-card:hover {{ background: var(--text); color: var(--bg); }}
.funder-card:hover .funder-role {{ color: var(--bg); opacity: 0.7; }}
.funder-card:hover .funder-badge {{ background: var(--bg); color: var(--text); border-color: var(--bg); }}
.funder-badge {{ display: inline-flex; align-items: center; gap: 6px; font-size: 0.7rem; font-family: 'JetBrains Mono', monospace; font-weight: 700; text-transform: uppercase; background: var(--text); color: var(--bg); border: 1px solid var(--text); padding: 4px 12px; margin-bottom: 18px; letter-spacing: 1px; transition: all 0.3s; }}
.funder-name {{ font-size: 2.2rem; font-family: 'Oswald', sans-serif; margin-bottom: 8px; letter-spacing: 0.5px; line-height: 1.1; }}
.funder-role {{ font-size: 0.8rem; color: var(--accent); text-transform: uppercase; font-weight: 700; letter-spacing: 1.5px; margin-bottom: 14px; transition: color 0.3s; }}
.funder-note {{ font-size: 0.82rem; line-height: 1.6; opacity: 0.75; max-width: 320px; margin: 0 auto; font-family: 'JetBrains Mono', monospace; }}
/* Telegram Stars Modal */
#stars-modal {{ position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; background: rgba(17,17,17,0.97); z-index: 200000; display: none; flex-direction: column; align-items: center; justify-content: center; padding: 20px; opacity: 0; }}
.stars-modal-box {{ background: var(--bg); border: 2px solid var(--border); box-shadow: 8px 8px 0 var(--accent); max-width: 520px; width: 100%; padding: 40px; position: relative; }}
.stars-modal-close {{ position: absolute; top: 15px; right: 20px; font-family: 'Oswald'; font-size: 1.4rem; cursor: pointer; color: var(--text); background: none; border: none; font-weight: 700; padding: 4px 8px; }}
.stars-modal-title {{ font-family: 'Oswald'; font-size: 1.8rem; text-transform: uppercase; margin-bottom: 10px; letter-spacing: 1px; }}
.stars-modal-sub {{ font-family: 'JetBrains Mono'; font-size: 0.78rem; line-height: 1.7; opacity: 0.75; margin-bottom: 24px; }}
.stars-tiers {{ display: flex; flex-direction: column; gap: 12px; margin-bottom: 24px; }}
.stars-tier-btn {{ display: flex; align-items: center; justify-content: space-between; padding: 14px 20px; border: 2px solid var(--border); background: var(--bg); font-family: 'Oswald'; font-size: 1rem; text-transform: uppercase; letter-spacing: 1px; text-decoration: none; color: var(--text); transition: all 0.2s; box-shadow: 3px 3px 0 var(--border); }}
.stars-tier-btn:hover {{ background: var(--text); color: var(--bg); box-shadow: 5px 5px 0 var(--accent); transform: translate(-2px,-2px); }}
.stars-tier-amount {{ font-family: 'JetBrains Mono'; font-size: 0.82rem; opacity: 0.7; }}
.stars-disclaimer {{ font-family: 'JetBrains Mono'; font-size: 0.72rem; line-height: 1.6; opacity: 0.6; border-top: 1px solid var(--border); padding-top: 14px; margin: 0; }}
@media (max-width: 768px) {{ .funders-intro-banner {{ flex-direction: column; align-items: flex-start; padding: 25px 20px; }} .funder-card {{ padding: 30px 20px; }} .funders-cta-wrap {{ align-items: flex-start; }} }}

/* Disclaimer Box in Footer */
.disclaimer-container {{ margin: 25px auto 10px; max-width: 840px; border: 1px dashed rgba(244, 244, 240, 0.35); background: rgba(0, 0, 0, 0.4); padding: 22px 28px; text-align: left; border-radius: 2px; }}
.disclaimer-badge {{ font-family: 'Oswald', sans-serif; font-size: 0.85rem; color: var(--accent); letter-spacing: 1.5px; text-transform: uppercase; font-weight: 700; margin-bottom: 10px; display: flex; align-items: center; gap: 8px; }}
.disclaimer-text {{ font-family: 'JetBrains Mono', monospace; font-size: 0.78rem; line-height: 1.7; color: var(--bg); opacity: 0.88; margin: 0; }}

footer {{ padding: 80px 40px; background: var(--text); color: var(--bg); text-align: center; display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 20px; }}
footer h1 {{ font-size: clamp(3rem, 8vw, 6rem); margin-bottom: 10px; line-height: 1; }}
.footer-quotes {{ font-size: 0.9rem; max-width: 600px; line-height: 1.6; opacity: 0.8; }}
.footer-poetic {{ font-family: 'Oswald', sans-serif; font-size: 1.5rem; color: var(--accent); text-transform: uppercase; margin-bottom: 15px; letter-spacing: 1px; }}
@media (max-width: 768px) {{ footer {{ padding: 40px 20px; }} }}
</style>
</head>
<body>

<audio id="bg-audio" loop src="assets/billie.mp3"></audio>
<div id="audio-controls">
    <button id="audio-toggle" class="hover-target">[ PLAY AUDIO ]</button>
</div>

<div class="cursor-dot" id="cursor-dot"></div>
<div class="cursor-outline" id="cursor-outline"></div>

<div id="toast">NOTIFICATION SET</div>

<div id="preloader">
    <h1>ARCHIVE LOADING</h1>
    <div class="load-bar-container"><div class="load-bar"></div></div>
</div>

<div id="video-modal">
    <div id="modal-close" class="hover-target">CLOSE [X]</div>
    <div id="modal-content-container"></div>
    <div id="modal-caption"></div>
</div>

<div class="grid-overlay"></div>

<nav id="nav">
    <div>Woodland House School</div>
    <div class="nav-links">
        <a href="#events" class="hover-target">Events</a>
        <a href="#archives" class="hover-target">Archives</a>
        <a href="#mentors" class="hover-target">Mentors</a>
        <a href="#funders" class="hover-target">Funders</a>
    </div>
</nav>

<section class="hero">
    <div>
        <p style="font-size: 1.2rem; margin-bottom: 20px; font-weight:bold;">EST. 1964</p>
        <div class="hero-line-container">
            <div class="hero-line">Uncompromising</div>
            <div class="hero-line" style="color: var(--accent);">Legacy</div>
        </div>
    </div>
    <div class="hero-marquee hover-target">
        <div class="marquee-content">
            WHS ARCHIVES 60 YEARS WHS ARCHIVES 60 YEARS WHS ARCHIVES 60 YEARS WHS ARCHIVES 60 YEARS
        </div>
    </div>
</section>

<section id="events">
    <div class="section-header"><h2 class="section-title">Timeline</h2></div>
    <div class="events-wrapper">
        <div class="event-col">
            <div class="event-col-title" style="display:flex; justify-content:space-between; align-items:center;">Upcoming <button class="notify-btn hover-target" onclick="triggerNotify(this)" style="font-size:0.5em; padding:5px 10px;">+ Subscribe to Updates</button></div>
            <div id="up-list"></div>
        </div>
        <div class="event-col">
            <div class="event-col-title">Past</div>
            <div id="past-list"></div>
        </div>
    </div>
</section>

<section id="archives">
    <div class="section-header"><h2 class="section-title">The Vault</h2></div>
    
    <div class="story-playlist-container" id="story-container" style="display:none;">
        <div class="story-playlist-title">Highlights & Stories</div>
        <div class="story-scroll" id="story-scroll"></div>
    </div>

    <div class="filter-bar">
        <button class="filter-btn hover-target active" data-filter="all">ALL</button>
        <button class="filter-btn hover-target" data-filter="video">VIDEOS</button>
        <button class="filter-btn hover-target" data-filter="post">POSTS</button>
    </div>
    
    <div class="archive-grid" id="gallery"></div>
</section>

<section id="mentors">
    <div class="section-header"><h2 class="section-title">Mentors</h2></div>
    <div class="mentors-grid" id="mentors-grid"></div>
</section>

<section id="funders">
    <div class="section-header"><h2 class="section-title">Funders &amp; Benefactors</h2></div>
    <canvas class="funders-money-canvas" id="funders-money-canvas"></canvas>
    <div class="funders-intro-banner">
        <div class="funders-intro-text">
            <strong>OUR GRATITUDE TO THOSE WHO KEEP THIS ALIVE</strong>
            <p>This archive exists because of people who believe memories deserve permanence. All voluntary contributions support website hosting, server costs &amp; digital events run by the website team — not school administrative functions. Free to access. Always.</p>
        </div>
        <div class="funders-cta-wrap">
            <button class="funder-pledge-btn hover-target" onclick="openStarsModal()">⭐ BECOME A FUNDER</button>
            <span class="funder-stars-note">100% anonymous · in-app Stars</span>
        </div>
    </div>
    <div class="funders-grid" id="funders-grid"></div>
</section>

<!-- Telegram Stars & Direct Support Modal -->
<div id="stars-modal" role="dialog" aria-modal="true">
    <div class="stars-modal-box">
        <button class="stars-modal-close hover-target" onclick="closeStarsModal()" aria-label="Close">✕</button>
        <div class="stars-modal-title">⭐ Support WHS Archive</div>
        <p class="stars-modal-sub">
            Your voluntary sponsorship keeps our digital archive servers running. <strong>Your identity and banking details remain completely protected.</strong>
        </p>

        <!-- Stars Tutorial Box -->
        <div style="background: rgba(0,0,0,0.03); border: 1px dashed var(--border); padding: 14px 16px; margin-bottom: 20px; text-align: left; font-family: 'JetBrains Mono', monospace; font-size: 0.78rem; line-height: 1.65;">
            <strong style="color: var(--accent); display: block; margin-bottom: 6px;">💡 HOW TELEGRAM STARS WORK:</strong>
            1. Tap <strong>"Pay with Telegram Stars"</strong> below to open our verified bot.<br>
            2. Choose your tier (25, 50, 100, or 250 Stars). Telegram opens an in-app sheet. Pay via Apple Pay, Google Play, or Card with 1 tap.<br>
            3. Reply to the bot with your Name to be honored in this gallery!
        </div>

        <div class="stars-tiers">
            <a href="https://t.me/whs1966_bot?start=funder" target="_blank" class="stars-tier-btn hover-target">
                <span>⭐ PAY WITH TELEGRAM STARS</span>
                <span class="stars-tier-amount">@whs1966_bot →</span>
            </a>
        </div>
        <p class="stars-disclaimer">
            ⚠️ Contributions strictly fund website hosting, server infrastructure &amp; website-team digital events.<br>
            NOT for school administration or school-run events. Non-profit memory vault.
        </p>
    </div>
</div>

<footer>
    <h1 class="footer-title">WHS 1964</h1>
    <div class="footer-poetic">"True elegance belongs to the sincere student, never to the masks of two faces."</div>
    <div class="footer-quotes" style="font-size: 1.2rem; font-style: italic; margin-bottom: 20px;">"Maybe all this scolding was worth the memories"</div>
    
    <div class="disclaimer-container">
        <div class="disclaimer-badge">⚖️ LEGAL DISCLAIMER & FAIR USE NOTICE</div>
        <p class="disclaimer-text">
            We do not claim or hold ownership over any videos, photographs, or audio tracks used on this website. All copyrights, trademarks, and media assets belong strictly to their original creators, artists, and copyright holders. This website is strictly an independent, non-commercial school community project created by students of Woodland House School solely for storing, preserving, and celebrating our memories for fun.
        </p>
    </div>

    <div class="footer-quotes" style="margin-top: 15px;">CRAFTED BY A STUDENT OF WOODLAND HOUSE SCHOOL, CLASS 10TH.</div>
</footer>

<script>
window.openStarsModal = function() {{
    const m = document.getElementById('stars-modal');
    if(!m) return;
    m.style.display = 'flex';
    if(window.anime) {{
        anime({{ targets: m, opacity: [0, 1], duration: 250, easing: 'easeOutSine' }});
        anime({{ targets: '.stars-modal-box', scale: [0.85, 1], translateY: [30, 0], duration: 350, easing: 'easeOutExpo' }});
    }} else {{
        m.style.opacity = '1';
    }}
    document.body.style.overflow = 'hidden';
}};

window.closeStarsModal = function() {{
    const m = document.getElementById('stars-modal');
    if(!m) return;
    if(window.anime) {{
        anime({{ targets: m, opacity: 0, duration: 200, easing: 'easeInSine', complete: () => {{
            m.style.display = 'none';
            document.body.style.overflow = 'auto';
        }}}});
    }} else {{
        m.style.display = 'none';
        document.body.style.overflow = 'auto';
    }}
}};

document.addEventListener('click', (e) => {{
    const m = document.getElementById('stars-modal');
    if(m && e.target === m) {{ window.closeStarsModal(); }}
}});

const RAW_MEMORIES = {memories};
const RAW_EVENTS = {events};
const RAW_FUNDERS = {funders};

const TEACHERS = [
  {{ name: "Sana Ma'am", role: "Educator" }}, 
  {{ name: "Naveed Sir", role: "Educator" }},
  {{ name: "Farooq Sir", role: "Educator" }}, 
  {{ name: "Shafi Sir", role: "Secretary" }},
  {{ name: "Sharifa Ma'am", role: "Supervisor" }}, 
  {{ name: "Shaista Shah", role: "Administrator" }},
  {{ name: "Riki Singh", role: "Director" }}, 
  {{ name: "Shaista Rishi", role: "Educator" }},
  {{ name: "Ifra", role: "Staff" }}, 
  {{ name: "Insha", role: "Staff" }},
  {{ name: "Ruhi", role: "Staff" }}, 
  {{ name: "Fiza", role: "Staff" }},
  {{ name: "Younis Sir", role: "Sports" }}
];

function build() {{
    const todayStr = new Date().toISOString().slice(0, 10);
    const allEvents = [...(RAW_EVENTS.upcoming || []), ...(RAW_EVENTS.past || [])];
    const seen = new Set();
    const dedupedEvents = [];
    allEvents.forEach(e => {{
        if(e.name && !seen.has(e.name)) {{
            seen.add(e.name);
            dedupedEvents.push(e);
        }}
    }});
    dedupedEvents.sort((a, b) => (b.date || "").localeCompare(a.date || ""));

    const upcomingList = dedupedEvents.filter(e => e.date && e.date > todayStr);
    const pastList = dedupedEvents.filter(e => !e.date || e.date <= todayStr);

    const upHtml = upcomingList.map(e => `
        <div class="event-item anim-up">
            <div class="e-date">${{e.date}}</div>
            <div class="e-title">${{e.name}}</div>
            <div class="e-desc">${{e.desc}}</div>
            <button class="notify-btn hover-target" onclick="triggerNotify(this)">+ Notify Me</button>
        </div>
    `).join('') || `
        <div class="event-item anim-up" style="border-left-color: var(--accent);">
            <div class="e-date">LATEST UPDATE</div>
            <div class="e-title">No upcoming events scheduled currently.</div>
            <div class="e-desc">Stay tuned! Click below to subscribe on Telegram and receive instant notifications when WHS announces upcoming events.</div>
            <button class="notify-btn hover-target" onclick="triggerNotify(this)">+ Subscribe on Telegram</button>
        </div>
    `;
    document.getElementById('up-list').innerHTML = upHtml;

    const pastHtml = pastList.map(e => `
        <div class="event-item anim-up">
            <div class="e-date">${{e.date}}</div>
            <div class="e-title">${{e.name}}</div>
            <div class="e-desc">${{e.desc}}</div>
        </div>
    `).join('') || '<div class="event-item">No past events recorded.</div>';
    document.getElementById('past-list').innerHTML = pastHtml;

    window._allMemories = [];
    window._filteredMem = [];
    window._renderCount = 0;
    let storyHtml = '';
    let hasStories = false;

    RAW_MEMORIES.forEach((m, idx) => {{
        m._idx = idx;
        const imgUrl = m.tg_img ? `/api/media?id=${{m.tg_img}}` : m.img;
        if(!imgUrl || imgUrl.includes('placeholder') || imgUrl.endsWith('/highlights/')) return;

        if(m.type.toLowerCase().includes("story") || m.title.toLowerCase().includes("story") || m.title.toLowerCase().includes("highlight")) {{
            hasStories = true;
            const cleanTitle = m.title.replace(/^Highlight:\\s*/i, '').replace(/^Story:\\s*/i, '');
            const hasVid = !!(m.video && m.video.trim());
            storyHtml += `
                <div class="story-item hover-target" data-index="${{idx}}">
                    <img src="${{imgUrl}}" data-fallback="${{m.img}}" loading="lazy" referrerpolicy="no-referrer" onerror="if(this.dataset.fallback && this.src !== this.dataset.fallback) {{ this.src = this.dataset.fallback; }} else {{ this.closest('.story-item')?.remove(); }}">
                    <div class="story-play-btn">${{hasVid ? '▶ WATCH' : 'VIEW'}}</div>
                    <div style="position:absolute; bottom:0; left:0; right:0; background:linear-gradient(transparent, rgba(0,0,0,0.85)); color:#fff; padding:10px 8px 6px; font-family:'Oswald',sans-serif; font-size:0.85rem; text-transform:uppercase; letter-spacing:0.5px; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; text-align:center; pointer-events:none;">${{cleanTitle}}</div>
                </div>
            `;
            m._isStory = true;
        }} else {{
            const videoUrl = m.tg_video ? `/api/media?id=${{m.tg_video}}` : m.video;
            m._hasVideo = !!(videoUrl && videoUrl.trim());
            m._isStory = false;
            window._allMemories.push(m);
        }}
    }});

    if(hasStories) {{
        document.getElementById('story-container').style.display = 'block';
        document.getElementById('story-scroll').innerHTML = storyHtml;
    }}

    window._filteredMem = window._allMemories.slice();

    window.renderMore = function() {{
        const start = window._renderCount;
        const end = Math.min(start + 30, window._filteredMem.length);
        let html = '';
        for(let i = start; i < end; i++) {{
            const m = window._filteredMem[i];
            const imgUrl = m.tg_img ? `/api/media?id=${{m.tg_img}}` : m.img;
            const videoUrl = m.tg_video ? `/api/media?id=${{m.tg_video}}` : m.video;
            const tClass = m._hasVideo ? "type-video" : "type-post";
            const filterType = m._hasVideo ? "video" : "post";
            const media = m._hasVideo
                ? `<img src="${{imgUrl}}" data-fallback="${{m.img}}" loading="lazy" referrerpolicy="no-referrer" onerror="if(this.dataset.fallback && this.src !== this.dataset.fallback) {{ this.src = this.dataset.fallback; }} else {{ this.closest('.memory-card')?.remove(); }}"><div class="play-btn">PLAY VIDEO</div>`
                : `<img src="${{imgUrl}}" data-fallback="${{m.img}}" loading="lazy" referrerpolicy="no-referrer" onerror="if(this.dataset.fallback && this.src !== this.dataset.fallback) {{ this.src = this.dataset.fallback; }} else {{ this.closest('.memory-card')?.remove(); }}"><div class="play-btn">VIEW POST</div>`;
            html += `
                <div class="memory-card hover-target anim-grid" data-filter="${{filterType}}" data-index="${{m._idx}}">
                    <div class="memory-media">${{media}}</div>
                    <div class="memory-info">
                        <div class="m-type ${{tClass}}">${{m.type}}</div>
                        <div class="m-title">${{m.title}}</div>
                        <div class="m-desc">${{m.desc}}</div>
                    </div>
                </div>`;
        }}
        window._renderCount = end;
        document.getElementById('gallery').insertAdjacentHTML('beforeend', html);
        let btn = document.getElementById('load-more-btn');
        if(window._renderCount >= window._filteredMem.length) {{
            if(btn) btn.style.display = 'none';
        }} else {{
            if(!btn) {{
                document.getElementById('gallery').insertAdjacentHTML('afterend',
                    `<div style="text-align:center;padding:40px;"><button id="load-more-btn" class="notify-btn hover-target" onclick="window.renderMore()">LOAD MORE MEMORIES</button></div>`);
            }} else {{ btn.style.display = 'inline-block'; }}
        }}
    }};

    document.getElementById('gallery').innerHTML = '';
    window.renderMore();

    document.getElementById('mentors-grid').innerHTML = TEACHERS.map(t => `
        <div class="mentor-card hover-target anim-grid">
            <div class="mentor-name">${{t.name}}</div><div class="mentor-role">${{t.role}}</div>
        </div>
    `).join('');

    document.getElementById('funders-grid').innerHTML = (RAW_FUNDERS || []).map(f => `
        <div class="funder-card hover-target anim-grid">
            <div class="funder-badge">🪙 ${{f.tier || 'HONORARY PATRON'}}</div>
            <div class="funder-name">${{f.name}}</div>
            <div class="funder-role">${{f.role || 'Contributor'}}</div>
            <div class="funder-note">${{f.note || 'Generously supported the Woodland House School Archive.'}}</div>
        </div>
    `).join('');
}}

let isToasting = false;
window.triggerNotify = function(btn) {{
    window.open("https://t.me/whs1966_bot?start=subscribe", "_blank");
}}

function showToast(btn) {{
    btn.innerText = "Subscribed";
    btn.style.background = "var(--accent)";
    btn.style.color = "#fff";
    btn.style.borderColor = "var(--accent)";
    
    if(typeof isToasting !== 'undefined' && !isToasting) {{
        isToasting = true;
        const toast = document.getElementById("toast");
        if(toast && typeof anime !== 'undefined') {{
            anime.timeline({{ easing: "easeOutElastic(1, .8)" }})
                 .add({{ targets: toast, bottom: "40px", duration: 800 }})
                 .add({{ targets: toast, bottom: "-100px", duration: 600, delay: 3000, easing: "easeInBack", complete: () => isToasting = false }});
        }}
    }}
}}
function initAudio() {{
    let bgAudio = null;
    const btn = document.getElementById('audio-toggle');
    let isPlaying = false;
    
        btn.addEventListener('click', () => {{
        if(!bgAudio) {{
            bgAudio = document.getElementById('bg-audio');
            bgAudio.volume = 0.5;
        }}
        
        if(isPlaying) {{
            bgAudio.pause();
            btn.innerText = "[ PLAY AUDIO ]";
            btn.style.background = "var(--bg)";
            btn.style.color = "var(--text)";
        }} else {{
            let playPromise = bgAudio.play();
            if (playPromise !== undefined) {{
                playPromise.then(_ => {{
                    btn.innerText = "[ PAUSE AUDIO ]";
                    btn.style.background = "var(--text)";
                    btn.style.color = "var(--bg)";
                }}).catch(error => {{
                    console.log("Audio play blocked:", error);
                    btn.innerText = "[ TAP AGAIN TO PLAY ]";
                }});
            }}
        }}
        isPlaying = !isPlaying;
    }});
}}

function initCustomCursor() {{
    if(window.innerWidth <= 768) return; 
    const dot = document.getElementById('cursor-dot');
    const outline = document.getElementById('cursor-outline');
    let mouseX = 0, mouseY = 0;
    let outlineX = 0, outlineY = 0;

    window.addEventListener('mousemove', (e) => {{
        mouseX = e.clientX; mouseY = e.clientY;
        dot.style.left = mouseX + 'px'; dot.style.top = mouseY + 'px';
    }});

    function animateCursor() {{
        outlineX += (mouseX - outlineX) * 0.15;
        outlineY += (mouseY - outlineY) * 0.15;
        outline.style.left = outlineX + 'px';
        outline.style.top = outlineY + 'px';
        requestAnimationFrame(animateCursor);
    }}
    animateCursor();

    document.body.addEventListener('mouseover', (e) => {{
        if(e.target.closest('.hover-target') || e.target.closest('#modal-close') || e.target.closest('.notify-btn')) {{
            outline.style.width = '60px'; outline.style.height = '60px';
            outline.style.background = 'rgba(217, 56, 30, 0.2)';
            outline.style.borderColor = 'transparent';
        }}
    }});
    document.body.addEventListener('mouseout', (e) => {{
        if(e.target.closest('.hover-target') || e.target.closest('#modal-close') || e.target.closest('.notify-btn')) {{
            outline.style.width = '40px'; outline.style.height = '40px';
            outline.style.background = 'transparent';
            outline.style.borderColor = 'var(--text)';
        }}
    }});
}}

function initVideoModal() {{
    const modal = document.getElementById('video-modal');
    const container = document.getElementById('modal-content-container');
    const caption = document.getElementById('modal-caption');
    const closeBtn = document.getElementById('modal-close');

    // Event delegation — works on dynamically added cards
    document.addEventListener('click', (e) => {{
        const card = e.target.closest('.memory-card, .story-item');
        if(!card) return;
        const idx = card.getAttribute('data-index');
        const data = RAW_MEMORIES[idx];
        if(!data) return;
        const imgUrl = data.tg_img ? `/api/media?id=${{data.tg_img}}` : data.img;
        const videoUrl = data.tg_video ? `/api/media?id=${{data.tg_video}}` : data.video;
        const hasVideo = videoUrl && videoUrl.trim() !== "";
        
        if(hasVideo) {{
            container.innerHTML = `<video id="modal-media" src="${{videoUrl}}" data-fallback="${{data.video}}" controls autoplay playsinline onerror="if(this.dataset.fallback && this.src !== this.dataset.fallback) {{ this.src = this.dataset.fallback; }}"></video>`;
        }} else {{
            container.innerHTML = `<img id="modal-media" src="${{imgUrl}}" data-fallback="${{data.img}}" onerror="if(this.dataset.fallback && this.src !== this.dataset.fallback) {{ this.src = this.dataset.fallback; }}">`;
        }}
        caption.innerHTML = `<strong>${{data.title}}</strong><br><br>${{data.desc}}`;

        modal.style.display = 'flex';
        anime({{ targets: modal, opacity: [0, 1], duration: 400, easing: 'easeOutSine' }});
        anime({{ targets: container, scale: [0.8, 1], translateY: [50, 0], duration: 600, easing: 'easeOutExpo' }});
        document.body.style.overflow = 'hidden'; 
    }});

    closeBtn.addEventListener('click', closeModal);
    modal.addEventListener('click', (e) => {{ if(e.target === modal) closeModal(); }});
    closeBtn.addEventListener('mouseenter', () => {{ if(window.innerWidth > 768) anime({{ targets: closeBtn, scale: 1.2, duration: 200 }}); }});
    closeBtn.addEventListener('mouseleave', () => {{ if(window.innerWidth > 768) anime({{ targets: closeBtn, scale: 1, duration: 200 }}); }});

    function closeModal() {{
        anime({{
            targets: modal, opacity: 0, duration: 300, easing: 'easeInSine',
            complete: () => {{
                modal.style.display = 'none';
                container.innerHTML = ''; 
                document.body.style.overflow = 'auto'; 
            }}
        }});
    }}
}}

function initAnimations() {{
    const tl = anime.timeline({{ easing: 'easeOutExpo' }});
    tl.add({{ targets: '.load-bar', width: ['0%', '100%'], duration: 1500, easing: 'easeInOutQuart' }})
      .add({{ targets: '#preloader h1', translateY: -50, opacity: 0, duration: 600 }}, '-=200')
      .add({{ targets: '.load-bar-container', opacity: 0, duration: 400 }}, '-=600')
      .add({{ targets: '#preloader', translateY: '-100%', duration: 800, easing: 'easeInOutQuint' }});

    tl.add({{ targets: '#nav', translateY: [-100, 0], duration: 800 }}, '-=400')
      .add({{ targets: '.hero p', opacity: [0,1], translateX: [-20, 0], duration: 800 }}, '-=600')
      .add({{ targets: '.hero-line', translateY: [100, 0], opacity: [0,1], duration: 1000, delay: anime.stagger(200) }}, '-=800');

    anime({{ targets: '.marquee-content', translateX: ['0%', '-50%'], duration: 15000, easing: 'linear', loop: true }});

    const observer = new IntersectionObserver((entries) => {{
        entries.forEach(entry => {{
            if(entry.isIntersecting) {{
                const el = entry.target;
                if(el.classList.contains('section-header')) {{
                    anime({{ targets: el, background: ['#F4F4F0', '#111111'], color: ['#111111', '#F4F4F0'], duration: 800, easing: 'easeOutSine' }});
                    anime({{ targets: el.querySelector('.section-title'), translateX: [-50, 0], opacity: [0, 1], duration: 800, delay: 200 }});
                }}
                else if(el.classList.contains('anim-up')) {{
                    anime({{ targets: el, translateY: [50, 0], opacity: [0, 1], duration: 800, easing: 'easeOutQuart' }});
                }}
                else if(el.classList.contains('anim-grid')) {{
                    anime({{ targets: el, scale: [0.95, 1], opacity: [0, 1], duration: 800, easing: 'easeOutBack' }});
                }}
                observer.unobserve(el);
            }}
        }});
    }}, {{ threshold: 0.1 }});

    document.querySelectorAll('.section-header, .anim-up, .anim-grid').forEach(el => {{
        if(el.classList.contains('anim-up') || el.classList.contains('anim-grid')) el.style.opacity = '0';
        observer.observe(el);
    }});
}}

function initFundersAnimation() {{
    const canvas = document.getElementById('funders-money-canvas');
    if (!canvas) return;
    const ctx = canvas.getContext('2d');

    function resize() {{
        canvas.width  = canvas.offsetWidth;
        canvas.height = canvas.offsetHeight;
    }}
    resize();
    window.addEventListener('resize', resize);

    const NOTES = [];
    const COUNT = 18;
    const NW = 64, NH = 28;

    function rand(a, b) {{ return a + Math.random() * (b - a); }}

    for (let k = 0; k < COUNT; k++) {{
        NOTES.push({{
            x:  rand(0, canvas.width),
            y:  rand(-canvas.height, 0),
            vx: rand(-0.3, 0.3),
            vy: rand(0.5, 1.4),
            angle: rand(0, Math.PI * 2),
            va:    rand(-0.01, 0.01),
            ft:    rand(0, Math.PI * 2),
            fs:    rand(0.014, 0.028),
        }});
    }}

    function drawNote(n) {{
        ctx.save();
        ctx.translate(n.x, n.y);
        ctx.rotate(n.angle);
        const sy = Math.cos(n.ft);
        ctx.scale(1, sy === 0 ? 0.01 : sy);
        ctx.globalAlpha = 0.5;

        ctx.fillStyle   = '#232320';
        ctx.strokeStyle = '#4a4a46';
        ctx.lineWidth   = 1;
        ctx.beginPath(); ctx.rect(-NW/2, -NH/2, NW, NH); ctx.fill(); ctx.stroke();

        ctx.strokeStyle = '#393936';
        ctx.lineWidth   = 0.6;
        ctx.beginPath(); ctx.rect(-NW/2+3, -NH/2+3, NW-6, NH-6); ctx.stroke();

        ctx.fillStyle    = '#6b6b65';
        ctx.font         = 'bold 9px monospace';
        ctx.textAlign    = 'center';
        ctx.textBaseline = 'middle';
        ctx.fillText('\u20b9', -NW/2+10, 0);
        ctx.fillText('\u20b9',  NW/2-10, 0);

        ctx.strokeStyle = '#2f2f2c';
        ctx.lineWidth   = 0.4;
        for (let r = -8; r < NH; r += 5) {{
            ctx.beginPath();
            ctx.moveTo(-NW/2+4, -NH/2+r);
            ctx.lineTo( NW/2-4, -NH/2+r+2);
            ctx.stroke();
        }}
        ctx.restore();
    }}

    function tick() {{
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        const W = canvas.width, H = canvas.height;
        NOTES.forEach(n => {{
            n.x += n.vx; n.y += n.vy;
            n.angle += n.va; n.ft += n.fs;
            if (n.y > H + NH)   {{ n.y = -NH; n.x = rand(0, W); }}
            if (n.x < -NW - 10)   n.x = W + NW;
            if (n.x >  W + NW)    n.x = -NW;
            drawNote(n);
        }});
        requestAnimationFrame(tick);
    }}
    tick();
}}

window.addEventListener('DOMContentLoaded', () => {{
    build();
    initFilters();
    initAudio();
    initCustomCursor();
    initVideoModal();
    initAnimations();
    initFundersAnimation();
}});
</script>
</body>
</html>"""

    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(html_content)
    print("Build complete.")

if __name__ == "__main__":
    build()



