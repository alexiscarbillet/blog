import os
import json
from google import genai
from datetime import datetime
import re

# 1. Setup
api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    print("Error: GEMINI_API_KEY not found.")
    exit(1)

client = genai.Client(api_key=api_key)
MODEL_ID = "gemini-1.5-flash"

# 2. History Check (Fixed for your Unicode error)
HISTORY_FILE = "topic_history.json"
history = []

if os.path.exists(HISTORY_FILE):
    try:
        with open(HISTORY_FILE, "r", encoding="utf-8-sig") as f:
            history = json.load(f)
    except Exception as e:
        print(f"Warning: History file issue ({e}). Starting fresh.")
        history = []

# 3. AI Prompt
history_str = ", ".join(history) if history else "None"
today = datetime.now().strftime('%Y-%m-%d')

prompt = f"""
Generate a professional technical IT blog post. 
Previous topics to avoid: {history_str}.

IMPORTANT: Start the response with this exact YAML frontmatter:
---
date: {today}
authors: [gemini]
categories: [Tech, Automation]
description: <A 1-sentence SEO-friendly summary>
---
# <Title Here>
<Content Here>
"""

# 4. Generate Content
print("Consulting Gemini via New SDK...")
response = client.models.generate_content(
    model=MODEL_ID, 
    contents=prompt
)
content = response.text

# Extract Title for filename
try:
    title_line = [l for l in content.split('\n') if l.startswith('# ')][0]
    clean_title = re.sub(r'[^\w\s]', '', title_line.replace('# ', '').strip()).lower().replace(' ', '_')
except Exception:
    clean_title = f"post_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

# Save the post - Ensure path is docs/posts/
os.makedirs("docs/posts", exist_ok=True)
filename = f"docs/posts/{clean_title}.md"

with open(filename, "w", encoding="utf-8") as f:
    f.write(content)

# 5. Update History
history.append(clean_title)
with open(HISTORY_FILE, "w", encoding="utf-8") as f:
    json.dump(history, f, indent=4)

print(f"Successfully generated: {filename}")