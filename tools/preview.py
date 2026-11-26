#!/usr/bin/env python3
"""Builds a local look-alike of the organisation page from profile/README.md, in preview/ (not committed).
Usage: preview.py REPO_DIR, then open preview/index.html (wide) or preview/phone.html."""
import sys
from pathlib import Path
import markdown
root = Path(sys.argv[1])
md = (root / 'profile/README.md').read_text().replace('https://raw.githubusercontent.com/yourplace3d/.github/main/profile/assets/', '../profile/assets/')
body = markdown.markdown(md, extensions=['fenced_code', 'tables'])
css = """
:root{--bg:#fff;--fg:#1f2328;--muted:#59636e;--line:#d1d9e0;--code:#f6f8fa;--link:#0969da}
@media (prefers-color-scheme:dark){:root{--bg:#0d1117;--fg:#f0f6fc;--muted:#9198a1;--line:#3d444d;--code:#151b23;--link:#4493f8}}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--fg);font:16px/1.5 -apple-system,BlinkMacSystemFont,'Segoe UI','Noto Sans',Helvetica,Arial,sans-serif}
.top{display:flex;gap:16px;align-items:center;max-width:var(--w);margin:0 auto;padding:24px 16px 8px}
.top img{width:72px;height:72px;border-radius:8px;border:1px solid var(--line)}.top b{font-size:24px}.top span{display:block;color:var(--muted);font-size:14px}
.box{max-width:calc(var(--w) - 32px);margin:16px auto 40px;border:1px solid var(--line);border-radius:6px;padding:24px}
.box>small{color:var(--muted);font:12px ui-monospace,SFMono-Regular,Menlo,monospace;display:block;margin-bottom:16px}
h2{font-size:1.5em;border-bottom:1px solid var(--line);padding-bottom:.3em;margin:24px 0 16px}h3{font-size:1.25em;margin:16px 0 8px}
img{max-width:100%;vertical-align:middle}p{margin:0 0 16px}a{color:var(--link);text-decoration:none}
pre{background:var(--code);border-radius:6px;padding:16px;overflow:auto;font:13.6px/1.45 ui-monospace,SFMono-Regular,Menlo,Consolas,monospace}
table{border-collapse:collapse;display:block;width:100%}td{border:1px solid var(--line);padding:6px 13px}
sub{color:var(--muted);font-size:12px}
"""
html = f"""<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>yourplace3d: preview</title><style>{css}</style></head><body style="--w:WIDTHpx">
<div class="top"><div><b>Your Place</b><span>preview of github.com/yourplace3d</span></div></div>
<div class="box"><small>README.md</small>{body}</div></body></html>"""
(root / 'preview').mkdir(exist_ok=True)
(root / 'preview/index.html').write_text(html.replace('WIDTH', '930'))
(root / 'preview/phone.html').write_text(html.replace('WIDTH', '420'))
print('built')
