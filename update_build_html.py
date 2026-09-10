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
    'src="https://archive.org/download/TheWayOfTheTearsExclusiveNasheedMuhammadAlMuqit_201501/The%20Way%20of%20The%20Tears%20-%20Exclusive%20Nasheed%20-%20Muhammad%20al%20Muqit.mp3"'
)

# 3. Optimize Gallery Rendering (Lazy loading DOM)
js_replace = '''
    let galHtml = '';
    let storyHtml = '';
    let hasStories = false;
    
    window.filteredMemories = [];
    window.currentRenderCount = 0;

    // Filter once initially
    RAW_MEMORIES.forEach((m, idx) => {
        m.original_index = idx;
        if(m.type.toLowerCase().includes("story") || m.title.toLowerCase().includes("story") || m.title.toLowerCase().includes("highlight")) {
            hasStories = true;
            const imgUrl = m.tg_img ? /api/media?id= : m.img;
            const media = <img src="" loading="lazy">;
            storyHtml += 
                <div class="story-item hover-target" data-index="">
                    
                    <div class="story-play-btn">VIEW</div>
                </div>
            ;
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
    
    window.renderMore = function() {
        let html = '';
        const limit = Math.min(window.currentRenderCount + 30, window.filteredMemories.length);
        for(let i = window.currentRenderCount; i < limit; i++) {
            const m = window.filteredMemories[i];
            const imgUrl = m.tg_img ? /api/media?id= : m.img;
            let tClass = m.hasVideo ? "type-video" : "type-post";
            let filterType = m.hasVideo ? "video" : "post";
            const media = m.hasVideo ? 
                <img src="" loading="lazy" referrerpolicy="no-referrer"><div class="play-btn">PLAY VIDEO</div> : 
                <img src="" loading="lazy" referrerpolicy="no-referrer"><div class="play-btn">VIEW POST</div>;

            html += 
                <div class="memory-card hover-target anim-grid" data-filter="" data-index="">
                    <div class="memory-media"></div>
                    <div class="memory-info">
                        <div class="m-type "></div>
                        <div class="m-title"></div>
                        <div class="m-desc"></div>
                    </div>
                </div>
            ;
        }
        window.currentRenderCount = limit;
        document.getElementById('gallery').insertAdjacentHTML('beforeend', html);
        
        if(window.currentRenderCount >= window.filteredMemories.length) {
            const loadBtn = document.getElementById('load-more-btn');
            if(loadBtn) loadBtn.style.display = 'none';
        }
    };

    document.getElementById('gallery').innerHTML = '';
    window.renderMore();
    
    // Add load more button if not exists
    if(!document.getElementById('load-more-btn')) {
        const btnHtml = <div style="text-align:center; padding: 40px;"><button id="load-more-btn" class="notify-btn hover-target" onclick="window.renderMore()">LOAD MORE MEMORIES</button></div>;
        document.getElementById('gallery').insertAdjacentHTML('afterend', btnHtml);
    }
'''

# We need to replace the old gallery loop.
import re
code = re.sub(r'let galHtml = \'\';.*?document\.getElementById\(\'story-scroll\'\)\.innerHTML = storyHtml;\s*\}', js_replace.replace('\\', '\\\\'), code, flags=re.DOTALL)

# Fix filter logic
filter_logic = '''
    function initFilters() {
        const filterBtns = document.querySelectorAll('.filter-btn');
        filterBtns.forEach(btn => {
            btn.addEventListener('click', () => {
                filterBtns.forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
                const filter = btn.dataset.filter;
                
                // Re-filter memory array
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
code = re.sub(r'function initFilters\(\) \{.*?\n    \}', filter_logic.strip(), code, flags=re.DOTALL)

# Fix notify
notify_logic = '''
window.triggerNotify = function(btn) {
    window.open("https://t.me/whs1966_bot?start=subscribe", "_blank");
}
'''
code = re.sub(r'window\.triggerNotify = function\(btn\) \{.*?\}\n\}', notify_logic.strip(), code, flags=re.DOTALL)

with open('build_html.py', 'w', encoding='utf-8') as f:
    f.write(code)

print("Updated build_html.py successfully!")
