"""
Agentic AI Certification Program — Client Preview Server
Serves the course content as a polished, browsable platform.

Usage: python3 preview_server.py
Then open http://localhost:8888
"""

import http.server
import json
import os
import re
import urllib.parse
from pathlib import Path

PORT = 8888
BASE = Path(__file__).parent
STATIC_MODE = os.environ.get("STATIC_BUILD") == "1"

# ── Markdown → HTML (lightweight, no dependencies) ─────────────

def md_to_html(md: str) -> str:
    """Convert markdown to HTML with support for common patterns."""
    html = md

    # Extract mermaid blocks FIRST and protect them from further processing
    mermaid_blocks = {}
    def stash_mermaid(m):
        key = f"%%MERMAID_{len(mermaid_blocks)}%%"
        mermaid_blocks[key] = f'<div class="mermaid">{m.group(1).strip()}</div>'
        return key
    html = re.sub(r'```mermaid\n(.*?)```', stash_mermaid, html, flags=re.DOTALL)

    # Fenced code blocks (``` ... ```)
    def replace_code_block(m):
        lang = m.group(1) or ""
        code = m.group(2)
        code = code.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        # Collapse runs of 2+ blank lines into 1
        code = re.sub(r'\n{2,}', '\n', code)
        code = code.strip('\n')
        lang_class = f' class="language-{lang}"' if lang else ""
        return f'<pre class="line-numbers"><code{lang_class}>{code}</code></pre>'
    html = re.sub(r'```(\w*)\n(.*?)```', replace_code_block, html, flags=re.DOTALL)

    # Inline code
    html = re.sub(r'`([^`]+)`', r'<code class="inline">\1</code>', html)

    # Tables
    def replace_table(m):
        lines = m.group(0).strip().split("\n")
        if len(lines) < 2:
            return m.group(0)
        rows = []
        for i, line in enumerate(lines):
            line = line.strip().strip("|")
            if re.match(r'^[\s\-:|]+$', line):
                continue
            cells = [c.strip() for c in line.split("|")]
            tag = "th" if i == 0 else "td"
            row = "".join(f"<{tag}>{c}</{tag}>" for c in cells)
            rows.append(f"<tr>{row}</tr>")
        header = rows[0] if rows else ""
        body = "".join(rows[1:])
        return f'<table><thead>{header}</thead><tbody>{body}</tbody></table>'
    html = re.sub(r'(?:^\|.+\|$\n?)+', replace_table, html, flags=re.MULTILINE)

    # Headers
    html = re.sub(r'^######\s+(.+)$', r'<h6>\1</h6>', html, flags=re.MULTILINE)
    html = re.sub(r'^#####\s+(.+)$', r'<h5>\1</h5>', html, flags=re.MULTILINE)
    html = re.sub(r'^####\s+(.+)$', r'<h4>\1</h4>', html, flags=re.MULTILINE)
    html = re.sub(r'^###\s+(.+)$', r'<h3>\1</h3>', html, flags=re.MULTILINE)
    html = re.sub(r'^##\s+(.+)$', r'<h2>\1</h2>', html, flags=re.MULTILINE)
    html = re.sub(r'^#\s+(.+)$', r'<h1>\1</h1>', html, flags=re.MULTILINE)

    # Bold and italic
    html = re.sub(r'\*\*\*(.+?)\*\*\*', r'<strong><em>\1</em></strong>', html)
    html = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', html)
    html = re.sub(r'\*(.+?)\*', r'<em>\1</em>', html)

    # Checkboxes
    html = re.sub(r'- \[x\]', r'<span class="check done">✅</span>', html)
    html = re.sub(r'- \[ \]', r'<span class="check">☐</span>', html)

    # Unordered lists
    html = re.sub(r'^- (.+)$', r'<li>\1</li>', html, flags=re.MULTILINE)

    # Ordered lists
    html = re.sub(r'^\d+\.\s+(.+)$', r'<li>\1</li>', html, flags=re.MULTILINE)

    # Blockquotes
    html = re.sub(r'^>\s*(.+)$', r'<blockquote>\1</blockquote>', html, flags=re.MULTILINE)

    # Links
    html = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2" target="_blank">\1</a>', html)

    # Horizontal rules
    html = re.sub(r'^---+$', r'<hr>', html, flags=re.MULTILINE)

    # Paragraphs (wrap loose text)
    lines = html.split("\n")
    result = []
    for line in lines:
        stripped = line.strip()
        if stripped and not stripped.startswith("<") and not stripped.startswith("%%MERMAID_"):
            result.append(f"<p>{stripped}</p>")
        else:
            result.append(line)
    html = "\n".join(result)

    # Restore mermaid blocks (protected from paragraph wrapping)
    for key, block in mermaid_blocks.items():
        html = html.replace(key, block)

    return html


def notebook_to_html(nb_path: Path) -> str:
    """Convert a .ipynb notebook to HTML content."""
    with open(nb_path) as f:
        nb = json.load(f)

    # Build Colab badge
    rel_path = nb_path.relative_to(BASE)
    colab_url = f"{COLAB_BASE}/{rel_path}"
    badge = (
        f'<div class="colab-banner">'
        f'<a href="{colab_url}" target="_blank" class="colab-btn">'
        f'<img src="https://colab.research.google.com/assets/colab-badge.svg" alt="Open In Colab" height="28">'
        f'</a>'
        f'<span class="colab-hint">Run this notebook interactively in Google Colab — free, no setup required</span>'
        f'</div>'
    )

    cells_html = [badge]
    for cell in nb.get("cells", []):
        source = "".join(cell.get("source", []))
        if cell["cell_type"] == "markdown":
            cells_html.append(f'<div class="nb-cell nb-markdown">{md_to_html(source)}</div>')
        elif cell["cell_type"] == "code":
            code = source.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            code = re.sub(r'\n{3,}', '\n\n', code).strip('\n')
            cells_html.append(
                f'<div class="nb-cell nb-code">'
                f'<div class="cell-label">In [ ]:</div>'
                f'<pre class="line-numbers"><code class="language-python">{code}</code></pre>'
                f'</div>'
            )

    return "\n".join(cells_html)


# ── Course Structure ───────────────────────────────────────────

MODULES = [
    {
        "id": "module-1-foundations",
        "number": 1,
        "title": "Foundations of Agentic AI",
        "subtitle": "What It Is, What It Isn't, and How to Build Your First Agent",
        "color": "#6366f1",
        "icon": "🧠",
        "duration": "7 hours",
        "status": "complete",
        "files": [
            ("README.md", "Module Overview", "overview"),
            ("curriculum.md", "Full Curriculum", "curriculum"),
            ("labs/lab_01_hello_agent.ipynb", "Lab 1: Hello Agent", "lab"),
            ("labs/lab_02_tool_use_agent.ipynb", "Lab 2: Tool-Use Agent", "lab"),
            ("labs/lab_03_multi_step_agent.ipynb", "Lab 3: Multi-Step Agent", "lab"),
            ("labs/capstone_starter.ipynb", "Capstone Starter", "lab"),
            ("capstone.md", "Capstone Brief", "capstone"),
            ("case_study.md", "Case Study: OpenClaw", "case_study"),
        ],
    },
    {
        "id": "module-2-professional-development",
        "number": 2,
        "title": "AI Agents for Professional Development",
        "subtitle": "Resume, Job Search, Interview, and Career Coaching Agents",
        "color": "#8b5cf6",
        "icon": "💼",
        "duration": "9.5 hours",
        "status": "in_progress",
        "files": [
            ("README.md", "Module Overview", "overview"),
            ("curriculum.md", "Full Curriculum", "curriculum"),
            ("capstone.md", "Capstone Brief", "capstone"),
            ("case_study.md", "Case Study: IAI Career Platform", "case_study"),
        ],
    },
    {
        "id": "module-3-research",
        "number": 3,
        "title": "AI Agents for Research",
        "subtitle": "Data Ingestion, Synthesis, and Autonomous Research Assistants",
        "color": "#06b6d4",
        "icon": "🔬",
        "duration": "~9 hours",
        "status": "planned",
        "files": [],
    },
    {
        "id": "module-4-financial",
        "number": 4,
        "title": "AI Agents for Financial Endeavors",
        "subtitle": "Market Analysis, Portfolio Assessment, and Financial Intelligence",
        "color": "#10b981",
        "icon": "📊",
        "duration": "~9 hours",
        "status": "planned",
        "files": [],
    },
]

GITHUB_REPO = "moltbot47/agentic-ai-course"
COLAB_BASE = f"https://colab.research.google.com/github/{GITHUB_REPO}/blob/main"

EXTRA_HEAD = """
    <!-- Prism.js Syntax Highlighting (One Dark theme) -->
    <link href="https://cdn.jsdelivr.net/npm/prismjs@1.29.0/themes/prism-tomorrow.min.css" rel="stylesheet">

    <!-- Mermaid.js Diagrams -->
    <script type="module">
      import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.esm.min.mjs';
      mermaid.initialize({ startOnLoad: true, theme: 'base', themeVariables: {
        primaryColor: '#e8f0fe', primaryBorderColor: '#3182ce', primaryTextColor: '#1a365d',
        lineColor: '#718096', secondaryColor: '#f7fafc', tertiaryColor: '#ffffff',
        fontFamily: 'Inter, sans-serif', fontSize: '14px'
      }});
    </script>
"""

EXTRA_SCRIPTS = """
    <!-- Prism.js Core + Python + JSON + Bash -->
    <script src="https://cdn.jsdelivr.net/npm/prismjs@1.29.0/prism.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/prismjs@1.29.0/components/prism-python.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/prismjs@1.29.0/components/prism-json.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/prismjs@1.29.0/components/prism-bash.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/prismjs@1.29.0/components/prism-yaml.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/prismjs@1.29.0/components/prism-markdown.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/prismjs@1.29.0/plugins/line-numbers/prism-line-numbers.min.js"></script>
"""

# ── HTML Templates ─────────────────────────────────────────────

CSS = """
/* ── ARIA Academic Design System ────────────────────────────── */
:root {
    --color-primary: #1a365d;
    --color-secondary: #2c5282;
    --color-accent: #3182ce;
    --color-accent-light: #63b3ed;
    --color-warm: #dd6b20;
    --color-success: #38a169;
    --color-text: #1a202c;
    --color-text-secondary: #2d3748;
    --color-text-muted: #5a6577;
    --color-bg: #ffffff;
    --color-bg-alt: #f7fafc;
    --color-bg-code: #1e293b;
    --color-border: #e2e8f0;
    --font-serif: 'Source Serif 4', Georgia, serif;
    --font-sans: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    --font-mono: 'JetBrains Mono', 'Fira Code', monospace;
    --max-width: 1100px;
}

* { margin: 0; padding: 0; box-sizing: border-box; }

html { scroll-behavior: smooth; font-size: 17px; }

body {
    font-family: var(--font-sans);
    color: var(--color-text);
    line-height: 1.7;
    background: var(--color-bg);
    -webkit-font-smoothing: antialiased;
}

h1, h2, h3, h4, h5, h6 {
    font-family: var(--font-serif);
    font-weight: 500;
    line-height: 1.3;
    color: var(--color-primary);
}

a { color: var(--color-accent); text-decoration: none; }
a:hover { text-decoration: underline; color: var(--color-secondary); }

p { color: var(--color-text); }

/* ── Top Nav ── */
.topnav {
    position: fixed; top: 0; left: 0; right: 0; z-index: 100;
    background: rgba(255, 255, 255, 0.98);
    backdrop-filter: blur(12px);
    border-bottom: 1px solid var(--color-border);
    padding: 0 2rem;
    height: 64px;
    display: flex; align-items: center; justify-content: space-between;
}
.topnav .brand {
    display: flex; align-items: center; gap: 10px;
    font-family: var(--font-serif);
    font-size: 1.25rem; font-weight: 600; color: var(--color-primary);
    text-decoration: none;
}
.topnav .brand:hover { text-decoration: none; }
.topnav .brand span { color: var(--color-accent); }
.topnav .client-badge {
    background: var(--color-primary);
    color: white;
    border-radius: 20px;
    padding: 6px 16px;
    font-size: 0.7rem;
    font-weight: 600;
    letter-spacing: 0.05em;
    text-transform: uppercase;
}

/* ── Layout ── */
.main { padding-top: 64px; }

/* ── Landing Page ── */
.hero {
    text-align: center;
    padding: 6rem 2rem 4rem;
    background: linear-gradient(180deg, var(--color-bg-alt) 0%, var(--color-bg) 100%);
}
.hero-badge {
    display: inline-block;
    background: var(--color-primary);
    color: white;
    font-size: 0.7rem;
    font-weight: 600;
    padding: 0.4rem 1rem;
    border-radius: 20px;
    margin-bottom: 1.5rem;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    font-family: var(--font-sans);
}
.hero h1 {
    font-size: 3rem;
    font-weight: 600;
    color: var(--color-primary);
    margin-bottom: 1rem;
    letter-spacing: -0.02em;
}
.hero .hero-subtitle {
    font-family: var(--font-serif);
    font-size: 1.25rem;
    font-style: italic;
    color: var(--color-text-muted);
    margin-bottom: 1rem;
}
.hero p {
    color: var(--color-text-secondary);
    font-size: 1.05rem;
    max-width: 620px;
    margin: 0 auto 1rem;
    line-height: 1.7;
}
.hero .meta {
    display: flex; gap: 1.5rem; justify-content: center; margin-top: 2.5rem;
    flex-wrap: wrap;
}
.hero .meta-item {
    background: white;
    border: 1px solid var(--color-border);
    border-radius: 12px;
    padding: 1.2rem 1.8rem;
    text-align: center;
    transition: all 0.2s;
}
.hero .meta-item:hover {
    border-color: var(--color-accent);
    box-shadow: 0 4px 20px rgba(49, 130, 206, 0.08);
}
.hero .meta-item .number {
    font-family: var(--font-serif);
    font-size: 2rem; font-weight: 600; color: var(--color-accent-light);
    line-height: 1;
    margin-bottom: 0.4rem;
}
.hero .meta-item .label {
    font-size: 0.75rem; color: var(--color-text-muted);
    text-transform: uppercase; letter-spacing: 0.08em;
    font-weight: 500;
}

/* ── Module Cards ── */
.modules-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 1.5rem;
    max-width: var(--max-width);
    margin: 0 auto;
    padding: 0 2rem 4rem;
}
.module-card {
    background: white;
    border: 1px solid var(--color-border);
    border-radius: 12px;
    padding: 2rem;
    transition: all 0.2s;
    text-decoration: none;
    color: var(--color-text);
    display: block;
    position: relative;
    overflow: hidden;
}
.module-card:hover {
    border-color: var(--color-accent);
    box-shadow: 0 4px 24px rgba(49, 130, 206, 0.1);
    transform: translateY(-2px);
    text-decoration: none;
}
.module-card .card-accent {
    position: absolute; top: 0; left: 0; right: 0; height: 3px;
}
.module-card .icon { font-size: 2.2rem; margin-bottom: 1rem; }
.module-card .module-num {
    font-family: var(--font-sans);
    font-size: 0.7rem; text-transform: uppercase; letter-spacing: 0.1em;
    color: var(--color-text-muted); margin-bottom: 0.3rem;
    font-weight: 600;
}
.module-card h3 {
    font-family: var(--font-serif);
    font-size: 1.25rem; font-weight: 500; margin-bottom: 0.5rem;
    color: var(--color-primary);
}
.module-card .subtitle { color: var(--color-text-muted); font-size: 0.9rem; margin-bottom: 1rem; line-height: 1.5; }
.module-card .card-footer {
    display: flex; justify-content: space-between; align-items: center;
    margin-top: 1rem;
    padding-top: 1rem;
    border-top: 1px solid var(--color-border);
}
.module-card .duration { font-size: 0.85rem; color: var(--color-text-muted); }
.status {
    font-family: var(--font-sans);
    font-size: 0.7rem; font-weight: 600; padding: 4px 12px;
    border-radius: 20px; text-transform: uppercase; letter-spacing: 0.05em;
}
.status.complete { background: #f0fff4; color: var(--color-success); border: 1px solid #c6f6d5; }
.status.in_progress { background: #fffbeb; color: #d97706; border: 1px solid #fde68a; }
.status.planned { background: var(--color-bg-alt); color: var(--color-text-muted); border: 1px solid var(--color-border); }

/* ── Module Detail ── */
.module-detail {
    max-width: 900px;
    margin: 0 auto;
    padding: 2rem;
}
.breadcrumb {
    font-size: 0.85rem; color: var(--color-text-muted); margin-bottom: 2rem;
}
.breadcrumb a { color: var(--color-text-muted); }
.breadcrumb a:hover { color: var(--color-accent); text-decoration: none; }
.module-header {
    margin-bottom: 2.5rem;
    padding-bottom: 2rem;
    border-bottom: 1px solid var(--color-border);
}
.module-header .icon { font-size: 3rem; margin-bottom: 1rem; }
.module-header h1 {
    font-family: var(--font-serif);
    font-size: 2rem; font-weight: 500; margin-bottom: 0.5rem;
    color: var(--color-primary);
}
.module-header .subtitle { color: var(--color-text-muted); font-size: 1.05rem; font-family: var(--font-serif); font-style: italic; }

.file-list { display: flex; flex-direction: column; gap: 0.6rem; }
.file-link {
    display: flex; align-items: center; gap: 1rem;
    background: white;
    border: 1px solid var(--color-border);
    border-radius: 10px;
    padding: 1rem 1.5rem;
    color: var(--color-text);
    transition: all 0.2s;
    text-decoration: none;
}
.file-link:hover {
    border-color: var(--color-accent);
    box-shadow: 0 2px 12px rgba(49, 130, 206, 0.08);
    text-decoration: none;
}
.file-link .file-icon { font-size: 1.4rem; }
.file-link .file-info { flex: 1; }
.file-link .file-title { font-weight: 500; color: var(--color-primary); }
.file-link .file-name { font-size: 0.8rem; color: var(--color-text-muted); font-family: var(--font-mono); }
.file-link .arrow { color: var(--color-text-muted); font-size: 1.1rem; }
.file-link .colab-link {
    display: flex; align-items: center;
    opacity: 0.7; transition: opacity 0.2s;
    flex-shrink: 0;
}
.file-link .colab-link:hover { opacity: 1; text-decoration: none; }

/* ── Content View ── */
.content-view {
    max-width: 820px;
    margin: 0 auto;
    padding: 2rem;
}
.content-body {
    background: white;
    border: 1px solid var(--color-border);
    border-radius: 12px;
    padding: 3rem;
}
.content-body h1 {
    font-family: var(--font-serif);
    font-size: 1.8rem; font-weight: 500; margin: 2.5rem 0 1rem;
    color: var(--color-primary);
}
.content-body h1:first-child { margin-top: 0; }
.content-body h2 {
    font-family: var(--font-serif);
    font-size: 1.5rem; font-weight: 500; margin: 2.5rem 0 0.8rem;
    color: var(--color-primary);
    padding-top: 1.5rem;
    border-top: 1px solid var(--color-border);
}
.content-body h3 {
    font-family: var(--font-serif);
    font-size: 1.2rem; font-weight: 500; margin: 1.5rem 0 0.6rem;
    color: var(--color-secondary);
}
.content-body h4 {
    font-family: var(--font-serif);
    font-size: 1.05rem; font-weight: 500; margin: 1.2rem 0 0.5rem;
    color: var(--color-text);
}
.content-body p {
    margin: 0.6rem 0;
    color: var(--color-text);
    line-height: 1.8;
}
.content-body li {
    margin: 0.4rem 0; padding-left: 0.5rem;
    color: var(--color-text);
    line-height: 1.7;
}
.content-body blockquote {
    border-left: 4px solid var(--color-accent);
    padding: 1rem 1.5rem;
    margin: 1.5rem 0;
    background: var(--color-bg-alt);
    border-radius: 0 8px 8px 0;
    font-family: var(--font-serif);
    font-style: italic;
    color: var(--color-text);
}
.content-body hr {
    border: none; border-top: 1px solid var(--color-border);
    margin: 2.5rem 0;
}
.content-body pre {
    background: var(--color-bg-code);
    border: 1px solid #334155;
    border-radius: 8px;
    padding: 1rem 1.2rem;
    overflow-x: auto;
    margin: 1.2rem 0;
    font-family: var(--font-mono);
    font-size: 0.82rem;
    line-height: 1.45;
    color: #e2e8f0;
    max-height: 500px;
    overflow-y: auto;
}
.content-body code.inline {
    background: #edf2f7;
    padding: 2px 7px;
    border-radius: 4px;
    font-size: 0.88em;
    font-family: var(--font-mono);
    color: var(--color-secondary);
}
.content-body table {
    width: 100%;
    border-collapse: collapse;
    margin: 1.2rem 0;
    font-size: 0.9rem;
}
.content-body th {
    background: var(--color-bg-alt);
    padding: 0.7rem 1rem;
    text-align: left;
    font-weight: 600;
    font-family: var(--font-sans);
    font-size: 0.8rem;
    text-transform: uppercase;
    letter-spacing: 0.04em;
    color: var(--color-text-muted);
    border-bottom: 2px solid var(--color-border);
}
.content-body td {
    padding: 0.65rem 1rem;
    border-bottom: 1px solid var(--color-border);
    color: var(--color-text);
}
.content-body .check { margin-right: 0.3rem; }
.content-body strong { color: var(--color-text); font-weight: 600; }

/* ── Colab Banner ── */
.colab-banner {
    display: flex;
    align-items: center;
    gap: 1rem;
    background: linear-gradient(135deg, #f0f7ff 0%, #e8f4f8 100%);
    border: 1px solid #bee3f8;
    border-radius: 10px;
    padding: 0.9rem 1.4rem;
    margin-bottom: 2rem;
}
.colab-btn { display: flex; align-items: center; flex-shrink: 0; }
.colab-btn:hover { opacity: 0.85; text-decoration: none; }
.colab-hint {
    font-size: 0.85rem;
    color: var(--color-text-secondary);
    line-height: 1.4;
}

/* ── Prism.js Overrides ── */
pre[class*="language-"] {
    background: var(--color-bg-code) !important;
    border: 1px solid #334155 !important;
    border-radius: 8px !important;
    padding: 1rem 1.2rem !important;
    margin: 1.2rem 0 !important;
    font-family: var(--font-mono) !important;
    font-size: 0.82rem !important;
    line-height: 1.5 !important;
    max-height: 500px;
    overflow-y: auto;
}
code[class*="language-"] {
    font-family: var(--font-mono) !important;
    font-size: 0.82rem !important;
}
.token.comment { color: #6b7280 !important; }
.token.keyword { color: #c084fc !important; }
.token.string { color: #86efac !important; }
.token.function { color: #7dd3fc !important; }
.token.number { color: #fbbf24 !important; }
.token.operator { color: #94a3b8 !important; }
.token.class-name { color: #67e8f9 !important; }
.token.decorator { color: #f472b6 !important; }
.token.builtin { color: #7dd3fc !important; }
.token.boolean { color: #fbbf24 !important; }

/* ── Mermaid Diagrams ── */
.mermaid {
    background: var(--color-bg-alt);
    border: 1px solid var(--color-border);
    border-radius: 10px;
    padding: 1.5rem;
    margin: 1.5rem 0;
    text-align: center;
    overflow-x: auto;
}

/* ── Notebook Cells ── */
.nb-cell { margin: 1.5rem 0; }
.nb-markdown { }
.nb-code {
    background: var(--color-bg-code);
    border: 1px solid #334155;
    border-radius: 8px;
    overflow: hidden;
}
.nb-code .cell-label {
    padding: 0.5rem 1.2rem;
    font-size: 0.75rem;
    color: #94a3b8;
    font-family: var(--font-mono);
    background: #162032;
    border-bottom: 1px solid #334155;
}
.nb-code pre {
    margin: 0;
    border: none;
    border-radius: 0;
    max-height: 500px;
    overflow-y: auto;
    font-size: 0.82rem;
    line-height: 1.45;
}

/* ── Footer ── */
.footer {
    text-align: center;
    padding: 3rem 2rem;
    color: var(--color-text-muted);
    font-size: 0.85rem;
    border-top: 1px solid var(--color-border);
    margin-top: 3rem;
}

/* ── Stats Bar ── */
.stats-bar {
    background: var(--color-primary);
    padding: 2rem 0;
}
.stats-bar .container {
    max-width: var(--max-width);
    margin: 0 auto;
    padding: 0 2rem;
}

/* ── Progress Bar ── */
.progress-section {
    max-width: var(--max-width);
    margin: 0 auto 3rem;
    padding: 0 2rem;
}
.progress-bar-outer {
    background: white;
    border: 1px solid var(--color-border);
    border-radius: 12px;
    padding: 1.5rem 2rem;
}
.progress-bar-outer h3 {
    font-family: var(--font-sans);
    font-size: 0.75rem; color: var(--color-text-muted); margin-bottom: 1rem;
    text-transform: uppercase; letter-spacing: 0.08em;
    font-weight: 600;
}
.progress-track {
    background: #edf2f7;
    border-radius: 6px;
    height: 8px;
    overflow: hidden;
    margin-bottom: 0.8rem;
}
.progress-fill {
    height: 100%;
    border-radius: 6px;
    background: linear-gradient(90deg, var(--color-primary), var(--color-accent));
    transition: width 0.5s;
}
.progress-stats {
    display: flex; gap: 2rem; font-size: 0.85rem; color: var(--color-text-muted);
}
.progress-stats strong { color: var(--color-text); }

@media (max-width: 768px) {
    html { font-size: 16px; }
    .hero h1 { font-size: 2.2rem; }
    .modules-grid { grid-template-columns: 1fr; }
    .content-body { padding: 1.5rem; }
    .hero .meta { gap: 0.8rem; }
    .hero { padding: 4rem 1.5rem 3rem; }
}
"""

def landing_page() -> str:
    cards = []
    for m in MODULES:
        status_class = m["status"]
        status_label = {"complete": "Complete", "in_progress": "In Progress", "planned": "Planned"}[m["status"]]
        href = f'/module/{m["id"]}' if m["files"] else "#"
        opacity = "opacity: 0.5;" if m["status"] == "planned" else ""
        cards.append(f'''
        <a href="{href}" class="module-card" style="{opacity}">
            <div class="card-accent" style="background: {m['color']};"></div>
            <div class="icon">{m['icon']}</div>
            <div class="module-num">Module {m['number']}</div>
            <h3>{m['title']}</h3>
            <div class="subtitle">{m['subtitle']}</div>
            <div class="card-footer">
                <span class="duration">{m['duration']}</span>
                <span class="status {status_class}">{status_label}</span>
            </div>
        </a>''')

    completed = sum(1 for m in MODULES if m["status"] == "complete")
    in_progress = sum(1 for m in MODULES if m["status"] == "in_progress")
    total_files = sum(len(m["files"]) for m in MODULES)
    pct = int((completed + in_progress * 0.5) / len(MODULES) * 100)

    return f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Agentic AI Certification — ConsultBae India</title>
    <link href="https://fonts.googleapis.com/css2?family=Source+Serif+4:opsz,wght@8..60,300;8..60,400;8..60,500;8..60,600&family=Inter:wght@300;400;500;600&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
    <style>{CSS}</style>
{EXTRA_HEAD}
</head>
<body>
    <nav class="topnav">
        <a href="/" class="brand">
            <span>⬡</span> Agentic AI Certification
        </a>
        <div class="client-badge">ConsultBae India — Client Preview</div>
    </nav>

    <div class="main">
        <section class="hero">
            <div class="hero-badge">Professional Certification Program</div>
            <h1>Agentic AI Certification</h1>
            <div class="hero-subtitle">Build Production AI Agent Systems</div>
            <p>A 4-module professional certification covering foundations, professional development, research, and financial applications. Hands-on labs, real-world case studies, and capstone projects.</p>
            <div class="meta">
                <div class="meta-item">
                    <div class="number">4</div>
                    <div class="label">Modules</div>
                </div>
                <div class="meta-item">
                    <div class="number">~35</div>
                    <div class="label">Hours</div>
                </div>
                <div class="meta-item">
                    <div class="number">12</div>
                    <div class="label">Hands-on Labs</div>
                </div>
                <div class="meta-item">
                    <div class="number">4</div>
                    <div class="label">Capstone Projects</div>
                </div>
            </div>
        </section>

        <section class="progress-section">
            <div class="progress-bar-outer">
                <h3>Development Progress</h3>
                <div class="progress-track">
                    <div class="progress-fill" style="width: {pct}%;"></div>
                </div>
                <div class="progress-stats">
                    <span><strong>{completed}</strong> modules complete</span>
                    <span><strong>{in_progress}</strong> in progress</span>
                    <span><strong>{total_files}</strong> deliverable files</span>
                    <span><strong>{pct}%</strong> overall</span>
                </div>
            </div>
        </section>

        <section class="modules-grid">
            {"".join(cards)}
        </section>
    </div>

    <footer class="footer">
        Agentic AI Certification Program &mdash; Built for ConsultBae India by Durayveon B.<br>
        Powered by Claude API &bull; Anthropic Python SDK
    </footer>
{EXTRA_SCRIPTS}
</body>
</html>'''


def module_page(module_id: str) -> str:
    mod = next((m for m in MODULES if m["id"] == module_id), None)
    if not mod:
        return "<h1>Module not found</h1>"

    file_icons = {
        "overview": "📋", "curriculum": "📖", "lab": "🧪",
        "capstone": "🏆", "case_study": "📰",
    }

    file_links = []
    for fname, title, ftype in mod["files"]:
        icon = file_icons.get(ftype, "📄")
        href = f'/view/{module_id}/{urllib.parse.quote(fname)}'
        colab_badge = ""
        if fname.endswith(".ipynb"):
            colab_url = f"{COLAB_BASE}/{module_id}/{fname}"
            colab_badge = (
                f'<a href="{colab_url}" target="_blank" class="colab-link" '
                f'title="Open in Google Colab" onclick="event.stopPropagation();">'
                f'<img src="https://colab.research.google.com/assets/colab-badge.svg" height="20"></a>'
            )
        file_links.append(f'''
        <a href="{href}" class="file-link">
            <span class="file-icon">{icon}</span>
            <div class="file-info">
                <div class="file-title">{title}</div>
                <div class="file-name">{fname}</div>
            </div>
            {colab_badge}
            <span class="arrow">→</span>
        </a>''')

    status_class = mod["status"]
    status_label = {"complete": "Complete", "in_progress": "In Progress", "planned": "Planned"}[mod["status"]]

    return f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Module {mod["number"]}: {mod["title"]}</title>
    <link href="https://fonts.googleapis.com/css2?family=Source+Serif+4:opsz,wght@8..60,300;8..60,400;8..60,500;8..60,600&family=Inter:wght@300;400;500;600&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
    <style>{CSS}</style>
{EXTRA_HEAD}
</head>
<body>
    <nav class="topnav">
        <a href="/" class="brand"><span>⬡</span> Agentic AI Certification</a>
        <div class="client-badge">ConsultBae India — Client Preview</div>
    </nav>

    <div class="main">
        <div class="module-detail">
            <div class="breadcrumb">
                <a href="/">All Modules</a> / Module {mod["number"]}
            </div>

            <div class="module-header">
                <div class="icon">{mod["icon"]}</div>
                <div style="display:flex;align-items:center;gap:1rem;">
                    <h1>Module {mod["number"]}: {mod["title"]}</h1>
                    <span class="status {status_class}">{status_label}</span>
                </div>
                <div class="subtitle">{mod["subtitle"]}</div>
                <div style="margin-top:0.8rem;color:var(--text-dim);font-size:0.9rem;">Duration: {mod["duration"]} &bull; {len(mod["files"])} files</div>
            </div>

            <div class="file-list">
                {"".join(file_links)}
            </div>
        </div>
    </div>

    <footer class="footer">
        Agentic AI Certification Program &mdash; Built for ConsultBae India
    </footer>
{EXTRA_SCRIPTS}
</body>
</html>'''


def content_page(module_id: str, filename: str) -> str:
    mod = next((m for m in MODULES if m["id"] == module_id), None)
    if not mod:
        return "<h1>Module not found</h1>"

    filepath = BASE / mod["id"] / filename
    if not filepath.exists():
        return f"<h1>File not found: {filepath}</h1>"

    file_entry = next((f for f in mod["files"] if f[0] == filename), None)
    title = file_entry[1] if file_entry else filename

    if filename.endswith(".ipynb"):
        body = notebook_to_html(filepath)
    elif filename.endswith(".md"):
        body = md_to_html(filepath.read_text())
    else:
        body = f"<pre>{filepath.read_text()}</pre>"

    return f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} — Module {mod["number"]}</title>
    <link href="https://fonts.googleapis.com/css2?family=Source+Serif+4:opsz,wght@8..60,300;8..60,400;8..60,500;8..60,600&family=Inter:wght@300;400;500;600&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
    <style>{CSS}</style>
{EXTRA_HEAD}
</head>
<body>
    <nav class="topnav">
        <a href="/" class="brand"><span>⬡</span> Agentic AI Certification</a>
        <div class="client-badge">ConsultBae India — Client Preview</div>
    </nav>

    <div class="main">
        <div class="content-view">
            <div class="breadcrumb">
                <a href="/">All Modules</a> /
                <a href="/module/{module_id}">Module {mod["number"]}</a> /
                {title}
            </div>

            <div class="content-body">
                {body}
            </div>
        </div>
    </div>

    <footer class="footer">
        Agentic AI Certification Program &mdash; Built for ConsultBae India
    </footer>
{EXTRA_SCRIPTS}
</body>
</html>'''


# ── HTTP Server ────────────────────────────────────────────────

class CourseHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        path = urllib.parse.unquote(self.path)

        if path == "/" or path == "":
            html = landing_page()
        elif path.startswith("/module/"):
            module_id = path.split("/module/")[1].strip("/")
            html = module_page(module_id)
        elif path.startswith("/view/"):
            parts = path.split("/view/")[1]
            slash_idx = parts.index("/")
            module_id = parts[:slash_idx]
            filename = parts[slash_idx + 1:]
            html = content_page(module_id, filename)
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b"Not found")
            return

        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(html.encode())

    def log_message(self, format, *args):
        pass  # Suppress request logs


if __name__ == "__main__":
    server = http.server.HTTPServer(("", PORT), CourseHandler)
    print(f"\n  ⬡ Agentic AI Certification — Client Preview")
    print(f"  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print(f"  Open: http://localhost:{PORT}")
    print(f"  Press Ctrl+C to stop\n")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n  Server stopped.")
        server.server_close()
