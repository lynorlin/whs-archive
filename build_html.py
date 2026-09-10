import json

def build():
    try:
        with open('memories_data.json', 'r', encoding='utf-8') as f:
            memories = f.read()
    except:
        memories = "[]"
        
    try:
        with open('events.json', 'r', encoding='utf-8') as f:
            events = f.read()
    except:
        events = '{"upcoming":[], "past":[]}'

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
        const memoryCards = document.querySelectorAll('.memory-card');
        filterBtns.forEach(btn => {{
            btn.addEventListener('click', () => {{
                filterBtns.forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
                const filter = btn.dataset.filter;
                memoryCards.forEach(card => {{
                    if(filter === 'all' || card.dataset.filter === filter) card.classList.remove('hidden');
                    else card.classList.add('hidden');
                }});
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

footer {{ padding: 80px 40px; background: var(--text); color: var(--bg); text-align: center; display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 20px; }}
footer h1 {{ font-size: clamp(3rem, 8vw, 6rem); margin-bottom: 10px; line-height: 1; }}
.footer-quotes {{ font-size: 0.9rem; max-width: 600px; line-height: 1.6; opacity: 0.8; }}
.footer-poetic {{ font-family: 'Oswald', sans-serif; font-size: 1.5rem; color: var(--accent); text-transform: uppercase; margin-bottom: 15px; letter-spacing: 1px; }}
@media (max-width: 768px) {{ footer {{ padding: 40px 20px; }} }}
</style>
</head>
<body>

<audio id="bg-audio" loop src="https://archive.org/download/lofi-study/lofi-study.mp3"></audio>
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

<footer>
    <h1 class="footer-title">WHS 1964</h1>
    <div class="footer-poetic">"True elegance belongs to the sincere student, never to the masks of two faces."</div>
    <div class="footer-quotes">CRAFTED BY A STUDENT OF WOODLAND HOUSE SCHOOL, CLASS 10TH.</div>
</footer>

<script>
const RAW_MEMORIES = {memories};
const RAW_EVENTS = {events};

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
    const upHtml = (RAW_EVENTS.upcoming || []).map(e => `
        <div class="event-item anim-up">
            <div class="e-date">${{e.date}}</div>
            <div class="e-title">${{e.name}}</div>
            <div class="e-desc">${{e.desc}}</div>
            <button class="notify-btn hover-target" onclick="triggerNotify(this)">+ Notify Me</button>
        </div>
    `).join('') || '<div class="event-item">No upcoming events scheduled.</div>';
    document.getElementById('up-list').innerHTML = upHtml;

    const pastHtml = (RAW_EVENTS.past || []).map(e => `
        <div class="event-item anim-up">
            <div class="e-date">${{e.date}}</div>
            <div class="e-title">${{e.name}}</div>
            <div class="e-desc">${{e.desc}}</div>
        </div>
    `).join('') || '<div class="event-item">Processing...</div>';
    document.getElementById('past-list').innerHTML = pastHtml;

    let galHtml = '';
    let storyHtml = '';
    let hasStories = false;

    RAW_MEMORIES.forEach((m, idx) => {{
        const imgUrl = m.tg_img ? `/api/media?id=${{m.tg_img}}` : m.img;
        const videoUrl = m.tg_video ? `/api/media?id=${{m.tg_video}}` : m.video;
        const hasVideo = videoUrl && videoUrl.trim() !== "";
        let tClass = "type-post";
        let filterType = "post";
        
        if(m.type.toLowerCase().includes("story") || m.title.toLowerCase().includes("story") || m.title.toLowerCase().includes("highlight")) {{
            tClass = "type-story";
            hasStories = true;
            const media = `<img src="${{imgUrl}}" loading="lazy">`;
            storyHtml += `
                <div class="story-item hover-target" data-index="${{idx}}">
                    ${{media}}
                    <div class="story-play-btn">VIEW</div>
                </div>
            `;
            return; 
        }} else if(hasVideo || m.type.toLowerCase().includes("video")) {{
            tClass = "type-video";
            filterType = "video";
        }}

        const media = hasVideo ? 
            `<img src="${{imgUrl}}" loading="lazy" referrerpolicy="no-referrer"><div class="play-btn">PLAY VIDEO</div>` : 
            `<img src="${{imgUrl}}" loading="lazy" referrerpolicy="no-referrer"><div class="play-btn">VIEW POST</div>`;

        galHtml += `
            <div class="memory-card hover-target anim-grid" data-filter="${{filterType}}" data-index="${{idx}}">
                <div class="memory-media">${{media}}</div>
                <div class="memory-info">
                    <div class="m-type ${{tClass}}">${{m.type}}</div>
                    <div class="m-title">${{m.title}}</div>
                    <div class="m-desc">${{m.desc}}</div>
                </div>
            </div>
        `;
    }});
    
    document.getElementById('gallery').innerHTML = galHtml;
    
    if(hasStories) {{
        document.getElementById('story-container').style.display = 'block';
        document.getElementById('story-scroll').innerHTML = storyHtml;
    }}

    document.getElementById('mentors-grid').innerHTML = TEACHERS.map(t => `
        <div class="mentor-card hover-target anim-grid">
            <div class="mentor-name">${{t.name}}</div><div class="mentor-role">${{t.role}}</div>
        </div>
    `).join('');
}}

let isToasting = false;
window.triggerNotify = function(btn) {{
    if(!("Notification" in window)) {{
        alert("This browser does not support desktop notification");
        showToast(btn);
    }} else if(Notification.permission !== "granted") {{
        Notification.requestPermission().then(perm => {{
            if(perm === "granted") {{ showToast(btn); }}
            else {{ alert("Notifications blocked by browser."); }}
        }});
    }} else {{
        showToast(btn);
    }}
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

    document.querySelectorAll('.memory-card, .story-item').forEach(card => {{
        card.addEventListener('click', () => {{
            const idx = card.getAttribute('data-index');
            const data = RAW_MEMORIES[idx];
            const imgUrl = data.tg_img ? `/api/media?id=${{data.tg_img}}` : data.img;
            const videoUrl = data.tg_video ? `/api/media?id=${{data.tg_video}}` : data.video;
            const hasVideo = videoUrl && videoUrl.trim() !== "";
            
            if(hasVideo) {{
                container.innerHTML = `<video id="modal-media" src="${{videoUrl}}" controls autoplay playsinline></video>`;
            }} else {{
                container.innerHTML = `<img id="modal-media" src="${{imgUrl}}">`;
            }}
            caption.innerHTML = `<strong>${{data.title}}</strong><br><br>${{data.desc}}`;

            modal.style.display = 'flex';
            anime({{ targets: modal, opacity: [0, 1], duration: 400, easing: 'easeOutSine' }});
            anime({{ targets: container, scale: [0.8, 1], translateY: [50, 0], duration: 600, easing: 'easeOutExpo' }});
            document.body.style.overflow = 'hidden'; 
        }});
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

window.addEventListener('DOMContentLoaded', () => {{
    build();
    initFilters();
    initAudio();
    initCustomCursor();
    initVideoModal();
    initAnimations();
}});
</script>
</body>
</html>"""

    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(html_content)
    print("Build complete.")

if __name__ == "__main__":
    build()



