import os
import json
import google.generativeai as genai
from datetime import datetime

# 1. Setup
genai.configure(api_key=os.environ["GEMINI_API_KEY"])
model = genai.GenerativeModel('gemini-1.5-flash')

# 2. History Check
HISTORY_FILE = "topic_history.json"
with open(HISTORY_FILE, "r") as f:
    history = json.load(f)

# 3. AI Prompt with Frontmatter Instructions
prompt = f"""
Generate a technical IT blog post. 
Previous topics to avoid: {", ".join(history)}.

IMPORTANT: Start the response with this exact YAML frontmatter format:
---
date: {datetime.now().strftime('%Y-%m-%d')}
authors: [gemini]
categories: [Tech, Automation]
---
# <Title Here>
<Content Here>
"""

# 4. Generate & Save
response = model.generate_content(prompt)
content = response.text

# Use the title for the filename (simplified)
title_line = [l for l in content.split('\n') if l.startswith('# ')][0]
clean_title = title_line.replace('# ', '').strip().replace(' ', '_').lower()
filename = f"docs/posts/{clean_title}.md"

with open(filename, "w") as f:
    f.write(content)

# 5. Update History
history.append(clean_title)
with open(HISTORY_FILE, "w") as f:
    json.dump(history, f, indent=4)