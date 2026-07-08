import os
import html

files_to_include = [
    "README.md",
    "PROJECT_STRUCTURE.md",
    "app.py",
    "analysis_logic.py",
    "audit_trail.py",
    "templates/aqr.html",
    "templates/transform.html",
    "templates/audit_trail.html",
    "templates/index.html",
    "static/style.css",
    "static/script.js",
]

output_html = "codebase_export.html"

html_content = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Air Quality Review Project - Source Code</title>
    <style>
        body { font-family: Arial, sans-serif; background-color: #f4f4f9; padding: 20px; color: #333; }
        h1 { color: #222; text-align: center; }
        .toc { background: #fff; padding: 15px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); margin-bottom: 20px; }
        .toc ul { list-style-type: none; padding: 0; }
        .toc li { margin-bottom: 5px; }
        .toc a { color: #0056b3; text-decoration: none; font-weight: bold; }
        .toc a:hover { text-decoration: underline; }
        .file-container { background: #fff; margin-bottom: 20px; padding: 15px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .file-name { font-size: 1.2em; font-weight: bold; margin-bottom: 10px; color: #0056b3; border-bottom: 1px solid #eee; padding-bottom: 5px; }
        pre { background: #282c34; color: #abb2bf; padding: 15px; border-radius: 5px; overflow-x: auto; font-family: 'Consolas', 'Courier New', monospace; font-size: 13px; line-height: 1.5; }
        .back-to-top { display: inline-block; margin-top: 10px; font-size: 0.9em; color: #0056b3; text-decoration: none; }
    </style>
</head>
<body>
    <h1>Air Quality Review (AQR) Project - Source Code Export</h1>
    
    <div class="toc">
        <h2>Table of Contents</h2>
        <ul>
"""

# Generate Table of Contents
for file_path in files_to_include:
    if os.path.exists(file_path):
        safe_id = file_path.replace("/", "-").replace(".", "-")
        html_content += f'            <li><a href="#{safe_id}">{file_path}</a></li>\n'

html_content += """
        </ul>
    </div>
"""

# Generate File Content Blocks
for file_path in files_to_include:
    if os.path.exists(file_path):
        safe_id = file_path.replace("/", "-").replace(".", "-")
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            escaped_content = html.escape(content)
            html_content += f"""
    <div class="file-container" id="{safe_id}">
        <div class="file-name">{file_path}</div>
        <pre><code>{escaped_content}</code></pre>
        <a href="#" class="back-to-top">↑ Back to top</a>
    </div>
"""
        except Exception as e:
             html_content += f"""
    <div class="file-container" id="{safe_id}">
        <div class="file-name">{file_path} (Error reading file)</div>
        <pre><code>Error: {str(e)}</code></pre>
    </div>
"""

html_content += """
</body>
</html>
"""

with open(output_html, "w", encoding="utf-8") as f:
    f.write(html_content)

print(f"Successfully generated {output_html}")
