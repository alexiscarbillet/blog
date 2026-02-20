import os
import json
import re
from google import genai
from datetime import datetime

# --- 1. Setup ---
api_key = os.environ.get("GEMINI_API_KEY")
client = genai.Client(api_key=api_key)
HISTORY_FILE = "topic_history.json"

# --- 2. Load History ---
history = []
if os.path.exists(HISTORY_FILE):
    try:
        with open(HISTORY_FILE, "r") as f:
            history = json.load(f)
    except Exception:
        pass

# --- 3. Gemini 2.0 Prompt ---
today = datetime.now().strftime('%Y-%m-%d')
prompt = f"""
Write a professional engineering blog post.
Start with this EXACT frontmatter:
---
date: {today}
authors: [gemini]
categories: [Tech]
---

Rules:
1. Immediately after the frontmatter, write a catchy title (NO '#' symbol).
2. Write one engaging intro paragraph.
3. Insert the exact tag: 4. Continue with ## and ### for sections.
5. Provide a code example.
Recent topics to avoid: {", ".join(history[-5:])}
"""

print("Consulting Gemini 2.0 Flash...")
response = client.models.generate_content(model="gemini-2.0-flash", contents=prompt)
raw_text = response.text.strip()

# --- 4. Advanced Sanitization ---

# Ensure frontmatter is at the top
if not raw_text.startswith("---"):
    raw_text = re.sub(r'^.*?(?=---)', '', raw_text, flags=re.DOTALL)

# Extract Title: Look for the first line that isn't frontmatter or empty
content_lines = raw_text.split('\n')
title_candidate = ""
in_frontmatter = False
frontmatter_count = 0

for line in content_lines:
    if line.strip() == "---":
        frontmatter_count += 1
        continue
    if frontmatter_count >= 2 and line.strip():
        title_candidate = line.strip().replace('#', '')
        break

# Fallback slug logic
if not title_candidate:
    title_candidate = f"tech_update_{today}"

slug = re.sub(r'[^\w\s-]', '', title_candidate).lower().strip().replace(' ', '_')

# Prevent Double Title: Remove the title from the body so MkDocs can render its own
clean_content = raw_text.replace(title_candidate, "", 1)

# --- 5. Save ---
os.makedirs("docs/posts", exist_ok=True)
filename = f"docs/posts/{slug}.md"
with open(filename, "w", encoding="utf-8") as f:
    f.write(clean_content)

# Update History
history.append(slug)
with open(HISTORY_FILE, "w") as f:
    json.dump(history, f, indent=4)

print(f"Post generated: {filename} (Slug: {slug})")