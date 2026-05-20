import os
import re
import base64

def compile_to_html():
    md_path = r"d:\ex_work\AirQualityReview_Project\AQR_User_Manual.md"
    html_out = r"d:\ex_work\AirQualityReview_Project\AQR_User_Manual.html"
    screenshots_dir = r"d:\ex_work\AirQualityReview_Project\validation_docs\screenshots"
    
    if not os.path.exists(md_path):
        print(f"Error: Markdown file not found at {md_path}")
        return
        
    print(f"Reading markdown: {md_path}")
    with open(md_path, "r", encoding="utf-8") as f:
        lines = f.readlines()
        
    html_content = []
    
    # ----------------------------------------------------
    # Header & CSS Styles (Premium Light & Clean Aesthetic)
    # ----------------------------------------------------
    html_content.append("""<!DOCTYPE html>
<html lang="th">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Air Quality Review (AQR) - SOP & User Manual</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        :root {
            --bg-color: #f8f9fa;
            --container-bg: #ffffff;
            --text-color: #212529;
            --text-muted: #6c757d;
            --border-color: #dee2e6;
            --primary: #0d6efd;
            --primary-light: #e7f1ff;
            --success: #198754;
            --success-light: #d1e7dd;
            --warning: #ffc107;
            --warning-light: #fff3cd;
            --danger: #dc3545;
            --danger-light: #f8d7da;
            --info: #0dcaf0;
            --info-light: #cff4fc;
        }

        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }

        body {
            font-family: 'Inter', sans-serif;
            background-color: var(--bg-color);
            color: var(--text-color);
            line-height: 1.6;
            padding: 40px 20px;
        }

        .container {
            max-width: 960px;
            margin: 0 auto;
            background-color: var(--container-bg);
            padding: 50px 60px;
            border-radius: 12px;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.05);
            border: 1px solid var(--border-color);
        }

        h1, h2, h3, h4, h5 {
            color: #0f172a;
            font-weight: 600;
            margin-top: 1.8em;
            margin-bottom: 0.6em;
            line-height: 1.3;
        }

        h1 {
            font-size: 2.2rem;
            margin-top: 0;
            border-bottom: 2px solid var(--primary);
            padding-bottom: 12px;
            color: var(--primary);
        }

        h2 {
            font-size: 1.6rem;
            border-bottom: 1px solid var(--border-color);
            padding-bottom: 8px;
        }

        h3 { font-size: 1.25rem; }
        h4 { font-size: 1.1rem; }

        p, ul, ol {
            margin-bottom: 1.25rem;
            font-size: 0.975rem;
            color: #334155;
        }

        ul, ol {
            padding-left: 24px;
        }

        li {
            margin-bottom: 0.4rem;
        }

        hr {
            margin: 2.5rem 0;
            border: 0;
            border-top: 1px solid var(--border-color);
        }

        /* Tables formatting */
        table {
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 1.5rem;
            font-size: 0.9rem;
        }

        th, td {
            padding: 12px 16px;
            border: 1px solid var(--border-color);
            text-align: left;
        }

        th {
            background-color: #f1f5f9;
            font-weight: 600;
            color: #0f172a;
        }

        tr:nth-child(even) td {
            background-color: #f8fafc;
        }

        /* Alerts */
        .alert {
            padding: 16px 20px;
            margin-bottom: 1.5rem;
            border-radius: 8px;
            border-left: 4px solid;
            font-size: 0.95rem;
        }

        .alert-note {
            background-color: var(--primary-light);
            border-color: var(--primary);
            color: #084298;
        }

        .alert-important {
            background-color: var(--danger-light);
            border-color: var(--danger);
            color: #842029;
        }

        .alert-tip {
            background-color: var(--success-light);
            border-color: var(--success);
            color: #0f5132;
        }

        .alert-warning {
            background-color: var(--warning-light);
            border-color: var(--warning);
            color: #664d03;
        }

        .alert-title {
            font-weight: 600;
            margin-bottom: 4px;
            display: flex;
            align-items: center;
            gap: 8px;
        }

        /* Code formatting */
        pre {
            background-color: #0f172a;
            color: #f8fafc;
            padding: 20px;
            border-radius: 8px;
            overflow-x: auto;
            margin-bottom: 1.5rem;
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.875rem;
            border: 1px solid #1e293b;
        }

        code {
            font-family: 'JetBrains Mono', monospace;
            background-color: #f1f5f9;
            color: #0f172a;
            padding: 2px 6px;
            border-radius: 4px;
            font-size: 0.875rem;
        }

        pre code {
            background-color: transparent;
            color: inherit;
            padding: 0;
            border-radius: 0;
        }

        /* Image styling */
        .image-wrapper {
            margin: 2rem 0;
            text-align: center;
        }

        .image-wrapper img {
            max-width: 100%;
            height: auto;
            border-radius: 8px;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.08);
            border: 1px solid var(--border-color);
        }

        .image-caption {
            font-size: 0.85rem;
            color: var(--text-muted);
            margin-top: 8px;
            font-style: italic;
        }

        /* Checkbox lists */
        .task-list-item {
            list-style-type: none;
            display: flex;
            align-items: center;
            gap: 10px;
            margin-bottom: 0.4rem;
        }
        
        .task-list-item input {
            pointer-events: none;
        }

        /* Navigation or Quick Links */
        .toc-box {
            background-color: #f8fafc;
            border: 1px solid var(--border-color);
            border-radius: 8px;
            padding: 20px 24px;
            margin-bottom: 2rem;
        }

        .toc-box h3 {
            margin-top: 0;
            color: #0f172a;
            border-bottom: 1px solid var(--border-color);
            padding-bottom: 8px;
            margin-bottom: 12px;
        }

        .toc-box ul {
            list-style-type: none;
            padding-left: 0;
        }

        .toc-box ul li {
            margin-bottom: 6px;
        }

        .toc-box a {
            color: var(--primary);
            text-decoration: none;
            font-size: 0.95rem;
        }

        .toc-box a:hover {
            text-decoration: underline;
        }
    </style>
</head>
<body>
<div class="container">
""")

    # ----------------------------------------------------
    # Custom Parser Logic
    # ----------------------------------------------------
    in_code_block = False
    in_table = False
    table_headers = []
    table_rows = []
    
    in_alert = False
    alert_type = ""
    alert_lines = []
    
    in_list = False
    list_type = ""
    
    toc_links = []
    
    # Pre-parse for table of contents
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("## ") or stripped.startswith("### "):
            title = stripped.lstrip("#").strip()
            anchor = title.lower().replace(" ", "-").replace(".", "").replace("/", "").replace("(", "").replace(")", "").replace("`", "")
            toc_links.append((title, anchor, stripped.startswith("## ")))
            
    # Add TOC HTML block
    html_content.append('<div class="toc-box">')
    html_content.append('<h3>สารบัญคู่มือ (Table of Contents)</h3>')
    html_content.append('<ul>')
    for title, anchor, is_h2 in toc_links:
        prefix = "" if is_h2 else "&nbsp;&nbsp;&nbsp;&nbsp;• "
        html_content.append(f'<li>{prefix}<a href="#{anchor}">{title}</a></li>')
    html_content.append('</ul>')
    html_content.append('</div>')
    html_content.append('<hr>')

    for line in lines:
        stripped = line.strip()
        
        # 1. Handle Code Blocks
        if stripped.startswith("```"):
            if in_code_block:
                html_content.append("</code></pre>\n")
                in_code_block = False
            else:
                lang = stripped[3:].strip()
                html_content.append(f'<pre><code class="language-{lang}">')
                in_code_block = True
            continue
            
        if in_code_block:
            # Escape HTML characters in code blocks
            escaped = line.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            html_content.append(escaped)
            continue
            
        # 2. Handle GxP Alert Boxes
        if stripped.startswith("> [!"):
            in_alert = True
            alert_type = stripped[4:-1].lower() # e.g. "note", "important", "tip", "warning"
            alert_lines = []
            continue
            
        if in_alert:
            if stripped.startswith(">"):
                alert_text = stripped[1:].strip()
                alert_lines.append(alert_text)
                continue
            else:
                # Render Alert Box
                icon = "fa-info-circle"
                if alert_type == "important": icon = "fa-exclamation-triangle"
                elif alert_type == "tip": icon = "fa-lightbulb"
                elif alert_type == "warning": icon = "fa-exclamation-circle"
                
                html_content.append(f'<div class="alert alert-{alert_type}">')
                html_content.append(f'  <div class="alert-title"><i class="fa-solid {icon}"></i> {alert_type.upper()}</div>')
                html_content.append(f'  <p>{" ".join(alert_lines)}</p>')
                html_content.append('</div>\n')
                in_alert = False
                
        # 3. Handle Tables
        if stripped.startswith("|"):
            # Check if separator
            if re.match(r"^\|[\s:-|]+$", stripped):
                continue
                
            cells = [c.strip() for c in stripped.split("|")[1:-1]]
            if not in_table:
                in_table = True
                table_headers = cells
                table_rows = []
            else:
                table_rows.append(cells)
            continue
        elif in_table:
            # Render the Table
            html_content.append("<table>\n<thead>\n<tr>\n")
            for header in table_headers:
                html_content.append(f"  <th>{header}</th>\n")
            html_content.append("</tr>\n</thead>\n<tbody>\n")
            for row in table_rows:
                html_content.append("<tr>\n")
                for cell in row:
                    # Parse bold in cell
                    cell_html = re.sub(r"\*\*(.*?)\*\*", r"<strong>\1</strong>", cell)
                    cell_html = re.sub(r"`(.*?)`", r"<code>\1</code>", cell_html)
                    html_content.append(f"  <td>{cell_html}</td>\n")
                html_content.append("</tr>\n")
            html_content.append("</tbody>\n</table>\n")
            in_table = False
            
        # Skip empty lines
        if not stripped:
            html_content.append("<br>\n")
            continue
            
        # 4. Handle Headers
        if stripped.startswith("#"):
            level = len(stripped) - len(stripped.lstrip("#"))
            title = stripped.lstrip("#").strip()
            anchor = title.lower().replace(" ", "-").replace(".", "").replace("/", "").replace("(", "").replace(")", "").replace("`", "")
            
            # Format title text (remove backticks)
            title_formatted = title.replace("`", "")
            
            html_content.append(f'<h{level} id="{anchor}">{title_formatted}</h{level}>\n')
            continue
            
        # 5. Handle Image Links & Base64 Embed
        image_match = re.match(r"^!\[(.*?)\]\((.*?)\)$", stripped)
        if image_match:
            caption = image_match.group(1)
            img_path = image_match.group(2)
            
            # Find actual file basename
            img_filename = os.path.basename(img_path)
            
            # Locate image path
            full_img_path = os.path.join(screenshots_dir, img_filename)
            if not os.path.exists(full_img_path):
                # Fallback to brain folder
                full_img_path = os.path.join(r"C:\Users\thana\.gemini\antigravity\brain\aa85b059-14a1-4288-a587-0cefeb8d2e06", img_filename)
                
            if os.path.exists(full_img_path):
                print(f"Embedding image: {img_filename} ({os.path.getsize(full_img_path)} bytes)")
                with open(full_img_path, "rb") as img_file:
                    base64_data = base64.b64encode(img_file.read()).decode("utf-8")
                
                html_content.append('<div class="image-wrapper">')
                html_content.append(f'  <img src="data:image/png;base64,{base64_data}" alt="{caption}">')
                html_content.append(f'  <div class="image-caption">{caption}</div>')
                html_content.append('</div>\n')
            else:
                print(f"Warning: Image file not found: {img_filename}")
                html_content.append(f'<p style="color:red; font-weight:bold;">[ERROR: Image Not Found - {img_filename}]</p>')
            continue
            
        # 6. Parse Paragraph text, Bold, Inline Code, and Task lists
        line_html = stripped
        # Task checkboxes
        if line_html.startswith("- [x]") or line_html.startswith("- [X]"):
            line_html = f'<div class="task-list-item"><input type="checkbox" checked disabled> <span>{line_html[5:].strip()}</span></div>'
        elif line_html.startswith("- [ ]"):
            line_html = f'<div class="task-list-item"><input type="checkbox" disabled> <span>{line_html[5:].strip()}</span></div>'
        else:
            # Inline bold
            line_html = re.sub(r"\*\*(.*?)\*\*", r"<strong>\1</strong>", line_html)
            # Inline code
            line_html = re.sub(r"`(.*?)`", r"<code>\1</code>", line_html)
            # Standard bullets
            if line_html.startswith("* "):
                line_html = f"<li>{line_html[2:].strip()}</li>"
            elif line_html.startswith("- "):
                line_html = f"<li>{line_html[2:].strip()}</li>"
            elif re.match(r"^\d+\.\s", line_html):
                # Numbered list
                num_match = re.match(r"^(\d+)\.\s(.*)$", line_html)
                line_html = f"<li>{num_match.group(2).strip()}</li>"
            else:
                line_html = f"<p>{line_html}</p>"
                
        html_content.append(line_html + "\n")

    # Close document
    html_content.append("""</div>
</body>
</html>
""")

    print(f"Writing single-file HTML manual: {html_out}")
    with open(html_out, "w", encoding="utf-8") as f:
        f.writelines(html_content)
        
    # Copy to brain folder too for reference
    brain_html = r"C:\Users\thana\.gemini\antigravity\brain\aa85b059-14a1-4288-a587-0cefeb8d2e06\AQR_User_Manual.html"
    print(f"Copying HTML manual to brain directory: {brain_html}")
    with open(brain_html, "w", encoding="utf-8") as f:
        f.writelines(html_content)
        
    print("Success! Self-contained HTML manual built perfectly with embedded base64 images.")

if __name__ == "__main__":
    compile_to_html()
