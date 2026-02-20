import os
import json
import re
from google import genai
from datetime import datetime

# --- 1. Setup ---
# Ensure you have 'pip install google-genai' in your workflow
api_key = os.environ.get("GEMINI_API_KEY")
client = genai.Client(api_key=api_key)
HISTORY_FILE = "topic_history.json"

# --- 2. Load History ---
history = []
if os.path.exists(HISTORY_FILE):
    try:
        with open(HISTORY_FILE, "r") as f:
            history = json.load(f)
    except: pass

# --- 3. Gemini 2.0 Prompt ---
today = datetime.now().strftime('%Y-%m-%d')
prompt = f"""
Write a technical blog post for a high-end engineering blog.
Start with this EXACT frontmatter:
---
date: {today}
authors: [gemini]
categories: [Tech]
---

Rules:
1. Do NOT include a Markdown title (no # Title). 
2. The first line after the frontmatter should be the title in plain text.
3. Write one engaging intro paragraph, then insert the exact tag: 4. Use ## and ### for sections.
5. Provide high-quality code examples if relevant.
Recent topics to avoid repeating: {", ".join(history[-5:])}
"""

print("Consulting Gemini 2.0 Flash...")
response = client.models.generate_content(
    model="gemini-2.0-flash", 
    contents=prompt
)
raw_text = response.text.strip()

# --- 4. Sanitization ---

# Ensure frontmatter is at the absolute top
if not raw_text.startswith("---"):
    raw_text = re.sub(r'^.*?(?=---)', '', raw_text, flags=re.DOTALL)

# Extract a slug from the first non-YAML line
lines = [l for l in raw_text.split('\n') if l.strip() and '---' not in l]
title_text = lines[0].replace('#', '').strip() if lines else f"post_{today}"
slug = re.sub(r'[^\w\s]', '', title_text).lower().replace(' ', '_')

# Prevent "Double Title" by removing any # Header that matches the title
clean_content = re.sub(r'^#\s+.*?\n', '', raw_text, count=1, flags=re.MULTILINE)

# --- 5. Save ---
os.makedirs("docs/posts", exist_ok=True)
filename = f"docs/posts/{slug}.md"
with open(filename, "w", encoding="utf-8") as f:
    f.write(clean_content)

# Update History
history.append(slug)
with open(HISTORY_FILE, "w") as f:
    json.dump(history, f, indent=4)

print(f"Post generated: {filename}")