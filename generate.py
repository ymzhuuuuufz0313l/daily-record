#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generate a static daily-record site for GitHub Pages.
Reads Markdown files from E:\每日记录 and outputs a single index.html.
"""

import json
import os
from datetime import datetime

ROOT = r"E:\每日记录"
OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_HTML = os.path.join(OUTPUT_DIR, "index.html")

EXCLUDED_DIRS = {
    "daily-record-site",
    "daily-record-site-github",
    ".git",
    ".claude",
    ".opencode",
    ".daily-record-backups",
    ".daily-record-exports",
    ".daily-record-tasks.json",
}

EXCLUDED_FILES = {
    ".daily-record-tasks.json",
}


def should_include(root, file):
    rel_dir = os.path.relpath(root, ROOT)
    parts = rel_dir.split(os.sep)
    # Exclude hidden/system dirs
    if any(p in EXCLUDED_DIRS or p.startswith(".") for p in parts):
        return False
    if file in EXCLUDED_FILES or file.startswith("."):
        return False
    if not file.lower().endswith(".md"):
        return False
    return True


def collect_files():
    files = []
    for root, dirs, _ in os.walk(ROOT):
        # Prune excluded dirs
        dirs[:] = [d for d in dirs if d not in EXCLUDED_DIRS and not d.startswith(".")]
        for f in os.listdir(root):
            full = os.path.join(root, f)
            if os.path.isfile(full) and should_include(root, f):
                rel = os.path.relpath(full, ROOT).replace("\\", "/")
                files.append(rel)
    return sorted(files)


def load_contents(file_list):
    data = {}
    for rel in file_list:
        full = os.path.join(ROOT, rel)
        try:
            with open(full, "r", encoding="utf-8") as fh:
                text = fh.read()
        except Exception as e:
            text = f"<!-- failed to read: {e} -->"
        data[rel] = text
    return data


def build_tree(file_list):
    tree = {}
    for rel in file_list:
        parts = rel.split("/")
        node = tree
        for part in parts[:-1]:
            node = node.setdefault("__dirs__", {}).setdefault(part, {})
        node.setdefault("__files__", []).append(parts[-1])
    return tree


def render_html(file_list, contents):
    data_json = json.dumps(contents, ensure_ascii=False)
    tree_json = json.dumps(build_tree(file_list), ensure_ascii=False)
    generated = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>每日记录 - Daily Record Site</title>
  <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
  <style>
    :root {{
      --bg: #f4f6f8;
      --surface: #ffffff;
      --surface-strong: #f9fafb;
      --line: #d9e0e7;
      --text: #17212b;
      --muted: #607080;
      --accent: #176b5b;
      --accent-soft: #dcefe9;
      --shadow: 0 12px 28px rgba(26,36,46,0.08);
    }}
    body.dark-theme {{
      --bg: #101820;
      --surface: #17212b;
      --surface-strong: #202b36;
      --line: #344252;
      --text: #edf2f7;
      --muted: #a9b6c4;
      --accent: #45b39d;
      --accent-soft: #183b35;
    }}
    * {{ box-sizing: border-box; }}
    html, body {{ height: 100%; margin: 0; overflow: hidden; }}
    body {{
      background: var(--bg);
      color: var(--text);
      font-family: "Microsoft YaHei", "Segoe UI", Arial, sans-serif;
      font-size: 14px;
      line-height: 1.6;
    }}
    .app-shell {{
      display: grid;
      grid-template-columns: 300px 1fr;
      height: 100vh;
    }}
    .sidebar {{
      background: var(--surface);
      border-right: 1px solid var(--line);
      display: flex;
      flex-direction: column;
      overflow: hidden;
    }}
    .sidebar-header {{
      padding: 14px 16px;
      border-bottom: 1px solid var(--line);
      background: var(--surface-strong);
    }}
    .sidebar-header h1 {{
      margin: 0;
      font-size: 16px;
      color: var(--accent);
    }}
    .sidebar-header .meta {{
      margin-top: 4px;
      font-size: 11px;
      color: var(--muted);
    }}
    .search-box {{
      padding: 10px 14px;
      border-bottom: 1px solid var(--line);
    }}
    .search-box input {{
      width: 100%;
      padding: 8px 10px;
      border: 1px solid var(--line);
      border-radius: 6px;
      background: var(--bg);
      color: var(--text);
      outline: none;
    }}
    .file-tree {{
      flex: 1;
      overflow-y: auto;
      padding: 8px 0;
    }}
    .dir, .file {{
      padding: 5px 16px;
      cursor: pointer;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }}
    .dir:hover, .file:hover {{ background: var(--accent-soft); }}
    .dir {{ font-weight: 600; color: var(--accent); }}
    .file {{ padding-left: 28px; color: var(--text); }}
    .file.active {{ background: var(--accent-soft); font-weight: 600; }}
    .main {{
      overflow-y: auto;
      padding: 32px 48px;
      background: var(--bg);
    }}
    .content {{
      max-width: 900px;
      margin: 0 auto;
      background: var(--surface);
      border-radius: 12px;
      padding: 36px 44px;
      box-shadow: var(--shadow);
    }}
    .content h1 {{ font-size: 26px; border-bottom: 2px solid var(--line); padding-bottom: 12px; }}
    .content h2 {{ font-size: 20px; margin-top: 28px; }}
    .content h3 {{ font-size: 17px; margin-top: 22px; }}
    .content table {{
      border-collapse: collapse;
      width: 100%;
      margin: 14px 0;
    }}
    .content th, .content td {{
      border: 1px solid var(--line);
      padding: 8px 12px;
      text-align: left;
    }}
    .content th {{ background: var(--surface-strong); }}
    .content code {{
      background: var(--surface-strong);
      padding: 2px 5px;
      border-radius: 4px;
      font-family: Consolas, monospace;
    }}
    .content pre {{
      background: var(--surface-strong);
      padding: 14px;
      border-radius: 8px;
      overflow-x: auto;
    }}
    .content pre code {{ padding: 0; background: transparent; }}
    .content blockquote {{
      border-left: 4px solid var(--accent);
      margin: 14px 0;
      padding: 8px 16px;
      background: var(--accent-soft);
      color: var(--text);
    }}
    .toolbar {{
      position: fixed;
      top: 14px;
      right: 18px;
      display: flex;
      gap: 8px;
    }}
    .toolbar button {{
      padding: 6px 12px;
      border-radius: 6px;
      background: var(--surface);
      border: 1px solid var(--line);
      color: var(--text);
      font-size: 12px;
    }}
    .toolbar button:hover {{ background: var(--accent-soft); }}
    .empty-state {{
      text-align: center;
      color: var(--muted);
      padding: 80px 20px;
    }}
    @media (max-width: 768px) {{
      .app-shell {{ grid-template-columns: 1fr; }}
      .sidebar {{ display: none; }}
      .main {{ padding: 16px; }}
      .content {{ padding: 20px; }}
    }}
  </style>
</head>
<body>
  <div class="toolbar">
    <button onclick="toggleTheme()">🌓 主题</button>
  </div>
  <div class="app-shell">
    <aside class="sidebar">
      <div class="sidebar-header">
        <h1>每日记录</h1>
        <div class="meta">生成时间: {generated}</div>
      </div>
      <div class="search-box">
        <input type="text" id="searchInput" placeholder="搜索文件名..." oninput="filterFiles(this.value)">
      </div>
      <nav class="file-tree" id="fileTree"></nav>
    </aside>
    <main class="main" id="main">
      <div class="content" id="content">
        <div class="empty-state">
          <h2>欢迎使用每日记录站点</h2>
          <p>请从左侧选择一篇日报查看。</p>
        </div>
      </div>
    </main>
  </div>

  <script>
    const FILE_CONTENTS = {data_json};
    const FILE_TREE = {tree_json};
    const ALL_FILES = Object.keys(FILE_CONTENTS).sort().reverse();

    function renderTree(tree, parentPath = "") {{
      let html = "";
      const dirs = tree.__dirs__ || {{}};
      const files = tree.__files__ || [];

      for (const dirName of Object.keys(dirs).sort()) {{
        const fullPath = parentPath ? parentPath + "/" + dirName : dirName;
        html += `<div class="dir" onclick="toggleDir(this)">📁 ${{dirName}}</div>`;
        html += `<div class="dir-children" style="display:block">${{renderTree(dirs[dirName], fullPath)}}</div>`;
      }}

      for (const file of files.sort().reverse()) {{
        const fullPath = parentPath ? parentPath + "/" + file : file;
        html += `<div class="file" data-path="${{fullPath}}" onclick="openFile('${{fullPath}}')">📝 ${{file}}</div>`;
      }}
      return html;
    }}

    function toggleDir(el) {{
      const children = el.nextElementSibling;
      if (children) {{
        children.style.display = children.style.display === "none" ? "block" : "none";
      }}
    }}

    function openFile(path) {{
      document.querySelectorAll(".file").forEach(f => f.classList.remove("active"));
      const fileEl = document.querySelector(`.file[data-path="${{path}}"]`);
      if (fileEl) fileEl.classList.add("active");

      const raw = FILE_CONTENTS[path] || "文件不存在";
      const title = path.split("/").pop().replace(/\.md$/i, "");
      document.getElementById("content").innerHTML =
        `<h1>${{title}}</h1><hr>` + marked.parse(raw);
      document.title = title + " - 每日记录";
      window.location.hash = encodeURIComponent(path);
    }}

    function filterFiles(keyword) {{
      keyword = keyword.toLowerCase();
      document.querySelectorAll(".file").forEach(f => {{
        const path = f.getAttribute("data-path").toLowerCase();
        f.style.display = path.includes(keyword) ? "block" : "none";
      }});
      document.querySelectorAll(".dir-children").forEach(d => {{
        d.style.display = keyword ? "block" : "block";
      }});
    }}

    function toggleTheme() {{
      document.body.classList.toggle("dark-theme");
      localStorage.setItem("daily-record-theme", document.body.classList.contains("dark-theme") ? "dark" : "light");
    }}

    // Init
    document.getElementById("fileTree").innerHTML = renderTree(FILE_TREE);

    if (localStorage.getItem("daily-record-theme") === "dark") {{
      document.body.classList.add("dark-theme");
    }}

    // Open from hash
    if (window.location.hash) {{
      const path = decodeURIComponent(window.location.hash.slice(1));
      if (FILE_CONTENTS[path]) openFile(path);
    }} else if (ALL_FILES.length > 0) {{
      openFile(ALL_FILES[0]);
    }}
  </script>
</body>
</html>
"""
    with open(OUTPUT_HTML, "w", encoding="utf-8") as fh:
        fh.write(html)
    print(f"Generated: {OUTPUT_HTML}")
    print(r"Total files: " + str(len(file_list)))


def main():
    file_list = collect_files()
    contents = load_contents(file_list)
    render_html(file_list, contents)


if __name__ == "__main__":
    main()
