import re
with open('build_html.py', 'r', encoding='utf-8') as f:
    code = f.read()

code = re.sub(r'<footer>.*?</footer>', '''<footer>
    <h1 class="footer-title">WHS 1964</h1>
    <div class="footer-poetic">"True elegance belongs to the sincere student, never to the masks of two faces."</div>
    <div class="footer-quotes" style="font-size: 1.2rem; font-style: italic; margin-bottom: 20px;">"Maybe all this scolding was worth the memories"</div>
    <div class="footer-quotes">CRAFTED BY A STUDENT OF WOODLAND HOUSE SCHOOL, CLASS 10TH.</div>
</footer>''', code, flags=re.DOTALL)

with open('build_html.py', 'w', encoding='utf-8') as f:
    f.write(code)
