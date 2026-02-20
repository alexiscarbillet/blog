import os
import json
import re
from google import genai
from datetime import datetime

# --- Setup ---
api_key = os.environ.get("GEMINI_API_KEY")
client = genai.Client(api_key=api_key, http_options={'api_version': 'v1'})
HISTORY_FILE = "topic_history.json"

# --- Load History ---
history = []
if os.path.exists(HISTORY_FILE):
    try:
        with open(HISTORY_FILE, "r") as f:
            history = json.load(f)
    except: pass

# --- AI Prompt ---
today = datetime.now().strftime('%Y-%m-%d')
prompt = f"""
Write a technical blog post. 
Start with this EXACT frontmatter:
---
date: {today}
authors: [gemini]
categories: [Tech]
---

Rules:
1. Do NOT include a # Title in the text.
2. The very first line after the frontmatter must be a catchy title but WITHOUT the '#' symbol.
3. Write one intro paragraph, then insert the exact tag: 4. Continue with ## and ### headers for the body.
Previous topics: {", ".join(history[-5:])}
"""

print("Generating content...")
response = client.models.generate_content(model="gemini-1.5-flash", contents=prompt)
raw_text = response.text.strip()

# --- Post-Processing / Sanitization ---

# 1. Ensure frontmatter is at the top and clean
if not raw_text.startswith("---"):
    raw_text = re.sub(r'^.*?(?=---)', '', raw_text, flags=re.DOTALL)

# 2. Extract the first non-empty line as the Title for the slug
lines = [l for l in raw_text.split('\n') if l.strip() and '---' not in l]
title_suggestion = lines[0].replace('#', '').strip() if lines else f"post_{today}"

# 3. Final Content Cleaning: Remove any # Headers that match the title
# This prevents the "Double Title" on the website
clean_content = re.sub(r'^#\s+.*?\n', '', raw_text, count=1, flags=re.MULTILINE)

# 4. Generate filename
slug = re.sub(r'[^\w\s]', '', title_suggestion).lower().replace(' ', '_')
filename = f"docs/posts/{slug}.md"

# --- Save ---
os.makedirs("docs/posts", exist_ok=True)
with open(filename, "w", encoding="utf-8") as f:
    f.write(clean_content)

history.append(slug)
with open(HISTORY_FILE, "w") as f:
    json.dump(history, f, indent=4)

print(f"Successfully created: {filename}")