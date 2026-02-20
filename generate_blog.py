import os
import json
from google import genai
from datetime import datetime
import re

# 1. Setup
api_key = os.environ.get("GEMINI_API_KEY")
client = genai.Client(api_key=api_key, http_options={'api_version': 'v1'})

# 2. History Check
HISTORY_FILE = "topic_history.json"
history = []
if os.path.exists(HISTORY_FILE):
    try:
        with open(HISTORY_FILE, "r", encoding="utf-8-sig") as f:
            history = json.load(f)
    except:
        history = []

# 3. Prompt
today = datetime.now().strftime('%Y-%m-%d')
prompt = f"Write a technical blog post. Start with YAML frontmatter (date: {today}, authors: [gemini], categories: [Tech]). Then # Title and content."

# 4. Generate & Sanitize
print("Consulting Gemini...")
response = client.models.generate_content(model="gemini-2.0-flash", contents=prompt)
raw_text = response.text

# --- THE FIX: Find the frontmatter and force it to the top ---
# This regex looks for anything between two sets of ---
match = re.search(r'---\s*\n(.*?)\n\s*---', raw_text, re.DOTALL)
if match:
    metadata = match.group(0) # The full --- block
    content = raw_text.replace(metadata, "").strip()
    # Remove any leading triple backticks if the AI wrapped the code
    content = re.sub(r'^```markdown\s*', '', content)
    content = re.sub(r'```$', '', content)
    
    final_output = f"{metadata}\n\n{content}"
else:
    # Emergency fallback if AI failed to generate metadata
    final_output = f"---\ndate: {today}\nauthors: [gemini]\ncategories: [Tech]\n---\n\n{raw_text}"

# 5. Extract Title for Slug
title_match = re.search(r'^#\s+(.*)', final_output, re.MULTILINE)
title_text = title_match.group(1) if title_match else f"post_{today}"
slug = re.sub(r'[^\w\s]', '', title_text).lower().replace(' ', '_')

# 6. Save
os.makedirs("docs/posts", exist_ok=True)
filename = f"docs/posts/{slug}.md"
with open(filename, "w", encoding="utf-8") as f:
    f.write(final_output)

# 7. History
history.append(slug)
with open(HISTORY_FILE, "w", encoding="utf-8") as f:
    json.dump(history, f, indent=4)

print(f"Verified & Saved: {filename}")