import re

with open('build_html.py', 'r', encoding='utf-8') as f:
    code = f.read()

# Fix the broken curly braces
# Let's just restore from git and then use replace properly with {{ and }}

