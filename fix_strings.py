import os

html_path = 'c:/Users/nagun/.gemini/antigravity/brain/base_ai_agent/static/index.html'
js_path = 'c:/Users/nagun/.gemini/antigravity/brain/base_ai_agent/static/script.js'

with open(html_path, 'r', encoding='utf-8') as f:
    html_text = f.read()

# Replace the overly verbose line in the HTML
old_html = "Hello! I am the SGBC AI Agent. I have access to Wikipedia, Math calculation, and DuckDuckGo for live internet searches. How can I help you today?"
new_html = "Hello! I am the SGBC AI Agent. How can I help you today?"
html_text = html_text.replace(old_html, new_html)

with open(html_path, 'w', encoding='utf-8') as f:
    f.write(html_text)


with open(js_path, 'r', encoding='utf-8') as f:
    js_text = f.read()

# Replace the overly verbose line in the JavaScript reset function
old_js = "<div class='message-content'>Hello! I am the SGBC AI Agent. I have a completely fresh memory. How can I help you?</div></div>"
new_js = "<div class='message-content'>Hello! I am the SGBC AI Agent. How can I help you?</div></div>"
js_text = js_text.replace(old_js, new_js)

with open(js_path, 'w', encoding='utf-8') as f:
    f.write(js_text)

print('Successfully removed the hardcoded sentences.')
