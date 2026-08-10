#!/usr/bin/env python3
"""
canonical_fix.py - Installs a JS client-side redirect on every HTML page in
the gcserevise repo so GitHub Pages' silently-served duplicate URLs (the
extensionless form and the /index.html form) 301-equivalent redirect to the
canonical .html or directory-URL form.

Eliminates Google Search Console's "Alternative page with proper canonical
tag" cluster by making duplicate URLs redirect rather than serve identical
content with self-canonical.

Idempotent: re-running does nothing once `gcanonical-redirect` is present.
"""
import re
from pathlib import Path

SIGNATURE = 'gcanonical-redirect'

SCRIPT = (
    '<script>/* ' + SIGNATURE + ' */'
    '(function(){'
    'var p=location.pathname,q=location.search,h=location.hash,'
    'm=/^(.*)\\/index\\.html$/.exec(p);'
    'if(m){location.replace(m[1]+"/"+q+h);return}'
    'if(!p.endsWith("/")&&!/\\.[a-z0-9]{1,10}$/i.test(p))'
    '{location.replace(p+".html"+q+h)}'
    '})();</script>'
)

HEAD_RE = re.compile(r'(<head[^>]*>)', re.IGNORECASE)

BASE = Path('/home/scott/src/gcserevise')

added = 0
skipped = 0
missing_head = 0
files = sorted(set(list(BASE.glob('*.html')) + list(BASE.glob('topics/**/*.html'))))
print(f'Scanning {len(files)} HTML files...')

for f in files:
    text = f.read_text(encoding='utf-8')
    if SIGNATURE in text:
        skipped += 1
        continue
    new, n = HEAD_RE.subn(r'\1\n' + SCRIPT, text, count=1)
    if n == 0:
        print(f'  WARNING: no <head> in {f.relative_to(BASE)}')
        missing_head += 1
        continue
    f.write_text(new, encoding='utf-8')
    added += 1
    if added % 100 == 0:
        print(f'  ...installed in {added} files')

print(f'\nAdded JS redirect:   {added}')
print(f'Already installed:   {skipped}')
print(f'No <head> tag found: {missing_head}')
print(f'Total HTML scanned:  {len(files)}')
