"""Assemble index.html from partials, then regenerate the section drawing.

Not a build step in the deploy sense: the output is committed and GitHub Pages
serves it directly. This just keeps the long document editable in one file.
"""
import re
import subprocess

html = open('index.html', encoding='utf8').read()
part = open('partials/document.html', encoding='utf8').read()
html = re.sub(r'(<!-- DOCUMENT:START -->).*?(<!-- DOCUMENT:END -->)',
              lambda m: m.group(1) + '\n' + part + '\n' + m.group(2),
              html, flags=re.S)
open('index.html', 'w', encoding='utf8').write(html)
print(f'document: {len(part):,} bytes')
subprocess.run(['python3', 'tools/build_section.py'], check=True)
