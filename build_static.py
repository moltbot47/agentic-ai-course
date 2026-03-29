"""
Build static HTML files from the preview server for GitHub Pages deployment.
Generates all pages into a /docs folder with proper relative links.
"""

import importlib.util
import os
import re
import shutil
from pathlib import Path

# Import the preview server module
spec = importlib.util.spec_from_file_location("server", Path(__file__).parent / "preview_server.py")
server = importlib.util.module_from_spec(spec)
spec.loader.exec_module(server)

OUT = Path(__file__).parent / "docs"
# Set to your GitHub Pages base path (repo name)
BASE_URL = "/agentic-ai-course"


def fix_links(html: str, current_depth: int = 0) -> str:
    """Rewrite /absolute links to relative paths for static hosting."""
    # Replace href="/view/... with proper relative path
    html = html.replace('href="/', f'href="{BASE_URL}/')
    # Fix the brand link to go to root
    html = html.replace(f'href="{BASE_URL}/"', f'href="{BASE_URL}/index.html"')
    # Fix module links
    html = re.sub(
        rf'href="{BASE_URL}/module/([^"]+)"',
        rf'href="{BASE_URL}/module/\1/index.html"',
        html
    )
    # Fix view links — convert slashes in filenames
    def fix_view_link(m):
        module_id = m.group(1)
        filename = m.group(2)
        safe = filename.replace("/", "__")
        return f'href="{BASE_URL}/view/{module_id}/{safe}/index.html"'

    html = re.sub(
        rf'href="{BASE_URL}/view/([^/]+)/([^"]+)"',
        fix_view_link,
        html
    )
    return html


def build():
    # Clean output
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir()

    # 1. Landing page
    print("  Building index.html")
    html = fix_links(server.landing_page())
    (OUT / "index.html").write_text(html)

    # 2. Module pages + content pages
    for mod in server.MODULES:
        mid = mod["id"]
        mod_dir = OUT / "module" / mid
        mod_dir.mkdir(parents=True, exist_ok=True)

        print(f"  Building module/{mid}")
        html = fix_links(server.module_page(mid))
        (mod_dir / "index.html").write_text(html)

        # Content pages
        for fname, title, ftype in mod["files"]:
            safe_fname = fname.replace("/", "__")
            view_dir = OUT / "view" / mid / safe_fname
            view_dir.mkdir(parents=True, exist_ok=True)

            print(f"  Building view/{mid}/{fname}")
            html = fix_links(server.content_page(mid, fname))
            (view_dir / "index.html").write_text(html)

    # 3. GitHub Pages config
    (OUT / ".nojekyll").write_text("")

    total = sum(1 for _ in OUT.rglob("*.html"))
    print(f"\n  Done! {total} HTML files in /docs")


if __name__ == "__main__":
    build()
