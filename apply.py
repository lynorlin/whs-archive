import re

with open('build_html.py', 'r', encoding='utf-8') as f:
    code = f.read()

# 1. Update quote
code = code.replace(
    '<div class="footer-poetic">"True elegance belongs to the sincere student, never to the masks of two faces."</div>',
    '<div class="footer-poetic">"True elegance belongs to the sincere student, never to the masks of two faces."</div>\n    <div class="footer-quotes" style="font-size: 1.2rem; font-style: italic; margin-bottom: 20px;">"Maybe all this scolding was worth the memories"</div>'
)

# 2. Update Audio
code = code.replace(
    'src="https://archive.org/download/lofi-study/lofi-study.mp3"',
    'src="assets/billie.mp3"'
)

# 3. Update build() function for lazy loading.
build_js = '''
    const upHtml = (RAW_EVENTS.upcoming || []).map(e => `
        <div class="event-item anim-up">
            <div class="e-date">${e.date}</div>
            <div class="e-title">${e.name}</div>
            <div class="e-desc">${e.desc}</div>
            <button class="notify-btn hover-target" onclick="triggerNotify(this)">+ Notify Me</button>
        </div>
    `).join('') || '<div class="event-item">No upcoming events scheduled.</div>';
    document.getElementById('up-list').innerHTML = upHtml;

    const pastHtml = (RAW_EVENTS.past || []).map(e => `
        <div class="event-item anim-up">
            <div class="e-date">${e.date}</div>
            <div class="e-title">${e.name}</div>
            <div class="e-desc">${e.desc}</div>
        </div>
    `).join('') || '<div class="event-item">Processing...</div>';
    document.getElementById('past-list').innerHTML = pastHtml;

    window.filteredMemories = [];
    window.currentRenderCount = 0;
    let storyHtml = '';
    let hasStories = false;

    RAW_MEMORIES.forEach((m, idx) => {
        m.original_index = idx;
        if(m.type.toLowerCase().includes("story") || m.title.toLowerCase().includes("story") || m.title.toLowerCase().includes("highlight")) {
            hasStories = true;
            const imgUrl = m.tg_img ? `/api/media?id=${m.tg_img}` : m.img;
            const media = `<img src="${imgUrl}" loading="lazy">`;
            storyHtml += `
                <div class="story-item hover-target" data-index="${idx}">
                    ${media}
                    <div class="story-play-btn">VIEW</div>
                </div>
            `;
            m.is_story_card = true;
        } else {
            m.is_story_card = false;
            m.hasVideo = (m.video && m.video.trim() !== "") || m.type.toLowerCase().includes("video");
            window.filteredMemories.push(m);
        }
    });

    if(hasStories) {
        document.getElementById('story-container').style.display = 'block';
        document.getElementById('story-scroll').innerHTML = storyHtml;
    }

    document.getElementById('gallery').innerHTML = '';
    window.renderMore = function() {
        let html = '';
        const limit = Math.min(window.currentRenderCount + 30, window.filteredMemories.length);
        for(let i = window.currentRenderCount; i < limit; i++) {
            const m = window.filteredMemories[i];
            const imgUrl = m.tg_img ? `/api/media?id=${m.tg_img}` : m.img;
            let tClass = m.hasVideo ? "type-video" : "type-post";
            let filterType = m.hasVideo ? "video" : "post";
            const media = m.hasVideo ? 
                `<img src="${imgUrl}" loading="lazy" referrerpolicy="no-referrer"><div class="play-btn">PLAY VIDEO</div>` : 
                `<img src="${imgUrl}" loading="lazy" referrerpolicy="no-referrer"><div class="play-btn">VIEW POST</div>`;

            html += `
                <div class="memory-card hover-target anim-grid" data-filter="${filterType}" data-index="${m.original_index}">
                    <div class="memory-media">${media}</div>
                    <div class="memory-info">
                        <div class="m-type ${tClass}">${m.type}</div>
                        <div class="m-title">${m.title}</div>
                        <div class="m-desc">${m.desc}</div>
                    </div>
                </div>
            `;
        }
        window.currentRenderCount = limit;
        document.getElementById('gallery').insertAdjacentHTML('beforeend', html);

        const loadBtn = document.getElementById('load-more-btn');
        if(window.currentRenderCount >= window.filteredMemories.length) {
            if(loadBtn) loadBtn.style.display = 'none';
        } else {
            if(!loadBtn) {
                const btnHtml = `<div style="text-align:center; padding: 40px; grid-column: 1 / -1;"><button id="load-more-btn" class="notify-btn hover-target" onclick="window.renderMore()">LOAD MORE MEMORIES</button></div>`;
                document.getElementById('gallery').insertAdjacentHTML('afterend', btnHtml);
            } else {
                loadBtn.style.display = 'inline-block';
            }
        }
    };

    window.renderMore();

    document.getElementById('mentors-grid').innerHTML = TEACHERS.map(t => `
        <div class="mentor-card hover-target anim-grid">
            <div class="mentor-name">${t.name}</div><div class="mentor-role">${t.role}</div>
        </div>
    `).join('');
'''

build_js_escaped = build_js.replace('{', '{{').replace('}', '}}')

code = re.sub(
    r'    const upHtml = \(RAW_EVENTS\.upcoming \|\| \[\]\)\.map.*?</div>\n    `\)\.join\(\'\'\);',
    build_js_escaped,
    code,
    flags=re.DOTALL
)

# 4. Fix filters
filter_logic = '''
    function initFilters() {
        const filterBtns = document.querySelectorAll('.filter-btn');
        filterBtns.forEach(btn => {
            btn.addEventListener('click', () => {
                filterBtns.forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
                const filter = btn.dataset.filter;
                
                window.filteredMemories = RAW_MEMORIES.filter(m => {
                    if(m.is_story_card) return false;
                    if(filter === 'all') return true;
                    if(filter === 'video') return m.hasVideo;
                    if(filter === 'post') return !m.hasVideo;
                });
                
                window.currentRenderCount = 0;
                document.getElementById('gallery').innerHTML = '';
                const loadBtn = document.getElementById('load-more-btn');
                if(loadBtn) loadBtn.style.display = 'inline-block';
                window.renderMore();
            });
        });
    }
'''
filter_logic_escaped = filter_logic.replace('{', '{{').replace('}', '}}')
code = re.sub(r'    function initFilters\(\) \{.*?\n    \}', filter_logic_escaped, code, flags=re.DOTALL)

# 5. Fix Notify
notify_logic = '''
window.triggerNotify = function(btn) {
    window.open("https://t.me/whs1966_bot?start=subscribe", "_blank");
}
'''
notify_logic_escaped = notify_logic.replace('{', '{{').replace('}', '}}')
code = re.sub(r'window\.triggerNotify = function\(btn\) \{.*?\n\}', notify_logic_escaped, code, flags=re.DOTALL)

with open('build_html.py', 'w', encoding='utf-8') as f:
    f.write(code)

print("Updates applied to build_html.py")
