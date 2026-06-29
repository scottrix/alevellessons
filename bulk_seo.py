#!/usr/bin/env python3
"""
Bulk SEO enhancement for GCSE topic and landing pages.
Adds: OG/Twitter meta tags, FAQ Page schema.org, related topics links, share buttons.
"""
import os
import re
import json
import html
from pathlib import Path
from bs4 import BeautifulSoup

BASE = Path('/home/scott/src/gcserevise')
BASE_URL = 'https://scottrix.github.io/gcserevise'

def get_relative_depth(filepath):
    parts = filepath.relative_to(BASE).parts
    if 'topics' in parts:
        return '../../'
    return ''

def extract_qa_pairs(soup):
    pairs = []
    for ex in soup.select('div.example'):
        texts = ex.get_text(separator=' ', strip=True)
        q_match = re.search(r'Question:\s*(.+?)(?=Answer:|$)', texts, re.DOTALL)
        a_match = re.search(r'Answer:\s*(.+?)$', texts, re.DOTALL)
        if q_match and a_match:
            q = q_match.group(1).strip()[:300]
            a = a_match.group(1).strip()[:300]
            if q and a:
                pairs.append((q, a))
        if len(pairs) >= 8:
            break
    if len(pairs) >= 2:
        return pairs
    practice_qs = soup.select('div.question p')
    answers_section = None
    for sec in soup.select('section.section'):
        h = sec.find(['h2', 'h3'])
        if h and 'answers' in h.get_text(separator=' ', strip=True).lower():
            answers_section = sec
            break
    if practice_qs and answers_section:
        answers_items = answers_section.select('li')
        for i, q_el in enumerate(practice_qs):
            if i < len(answers_items):
                q_text = q_el.get_text(strip=True)
                q_text = re.sub(r'^Q\d+:\s*', '', q_text)[:300]
                a_text = answers_items[i].get_text(strip=True)[:300]
                if q_text and a_text:
                    pairs.append((q_text, a_text))
                if len(pairs) >= 8:
                    break
    return pairs if len(pairs) >= 2 else []

def build_faq_schema(qa_pairs):
    if not qa_pairs:
        return None
    main_entity = []
    for q, a in qa_pairs:
        main_entity.append({
            "@type": "Question",
            "name": q,
            "acceptedAnswer": {
                "@type": "Answer",
                "text": a
            }
        })
    schema = {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": main_entity
    }
    return json.dumps(schema, ensure_ascii=False)

def get_subject_from_path(filepath):
    rel = filepath.relative_to(BASE)
    parts = rel.parts
    if 'topics' in parts:
        idx = parts.index('topics')
        if idx + 1 < len(parts):
            strand = parts[idx + 1]
            return strand
    return None

def get_sibling_topics(filepath):
    rel = filepath.relative_to(BASE)
    parts = rel.parts
    if 'topics' not in parts:
        return []
    idx = parts.index('topics')
    strand_dir = BASE / 'topics' / parts[idx + 1]
    siblings = []
    for f in sorted(strand_dir.glob('*.html')):
        if f != filepath:
            with open(f, 'r', encoding='utf-8') as fh:
                content = fh.read()
            title_match = re.search(r'<title>(.+?)</title>', content)
            name = title_match.group(1).split(' - ')[0].strip() if title_match else f.stem
            siblings.append((name, f.name))
    return siblings[:6]

def get_link_subjects(filepath):
    rel = filepath.relative_to(BASE)
    parts = rel.parts
    if 'topics' in parts:
        subject_files = list(BASE.glob('*.html'))
        subject_files = [f for f in subject_files if f.name not in ('index.html', 'privacy.html')]
        return [f.name for f in sorted(subject_files)[:8]]
    return []

def add_og_twitter_tags(head_html, og_title, og_desc, og_url, og_type='article'):
    tags = f'''<meta property="og:site_name" content="GCSE Revise">
<meta property="og:locale" content="en_US">
<meta name="twitter:card" content="summary">
<meta name="twitter:title" content="{html.escape(og_title)}">
<meta name="twitter:description" content="{html.escape(og_desc)}">'''
    canonical_line = f'<link rel="canonical" href="{og_url}">'
    if canonical_line in head_html:
        head_html = head_html.replace(canonical_line, canonical_line + '\n' + tags)
    return head_html

def add_faq_schema(head_html, qa_pairs):
    schema_json = build_faq_schema(qa_pairs)
    if not schema_json:
        return head_html
    schema_tag = f'<script type="application/ld+json">{schema_json}</script>'
    stylesheet_match = re.search(r'<link rel="stylesheet"[^>]*>', head_html)
    if stylesheet_match:
        head_html = head_html.replace(stylesheet_match.group(0), schema_tag + '\n' + stylesheet_match.group(0))
    return head_html

def add_related_topics_section(html_content, siblings, subject_files, rel_depth):
    if not siblings and not subject_files:
        return html_content
    links_html = ''
    if siblings:
        links_html += '<div class="related-group"><h4>Related Topics</h4><ul>\n'
        for name, href in siblings:
            links_html += f'<li><a href="{href}">{html.escape(name)}</a></li>\n'
        links_html += '</ul></div>\n'
    if subject_files:
        links_html += '<div class="related-group"><h4>Related Subjects</h4><ul>\n'
        for sf in subject_files:
            subject_name = sf.replace('.html', '').replace('-', ' ').title()
            links_html += f'<li><a href="{rel_depth}{sf}">{html.escape(subject_name)}</a></li>\n'
        links_html += '</ul></div>\n'
    section = f'\n<section class="section related-topics">\n<h2>Related</h2>\n{links_html}</section>\n'
    cta_pattern = '<section class="section affiliate-cta-end">'
    if cta_pattern in html_content:
        html_content = html_content.replace(cta_pattern, section + cta_pattern)
    else:
        main_end = '</main>'
        if main_end in html_content:
            html_content = html_content.replace(main_end, section + main_end, 1)
    return html_content

def add_share_section(html_content, page_url, page_title):
    share_html = f'''<section class="section share-section">
<h2>Share this page</h2>
<div class="share-buttons">
<a class="share-btn share-twitter" href="https://twitter.com/intent/tweet?url={html.escape(page_url)}&text={html.escape(page_title)}" target="_blank" rel="noopener" title="Share on Twitter">Twitter</a>
<a class="share-btn share-facebook" href="https://www.facebook.com/sharer/sharer.php?u={html.escape(page_url)}" target="_blank" rel="noopener" title="Share on Facebook">Facebook</a>
<a class="share-btn share-linkedin" href="https://www.linkedin.com/sharing/share-offsite/?url={html.escape(page_url)}" target="_blank" rel="noopener" title="Share on LinkedIn">LinkedIn</a>
<a class="share-btn share-whatsapp" href="https://wa.me/?text={html.escape(page_title)}%20{html.escape(page_url)}" target="_blank" rel="noopener" title="Share on WhatsApp">WhatsApp</a>
<a class="share-btn share-copy" href="#" data-url="{html.escape(page_url)}" title="Copy link">Copy Link</a>
</div>
</section>
'''
    related_section = '<section class="section related-topics">'
    if related_section in html_content:
        html_content = html_content.replace(related_section, share_html + related_section)
    else:
        cta_pattern = '<section class="section affiliate-cta-end">'
        if cta_pattern in html_content:
            html_content = html_content.replace(cta_pattern, share_html + cta_pattern)
        else:
            main_end = '</main>'
            if main_end in html_content:
                html_content = html_content.replace(main_end, share_html + main_end, 1)
    return html_content

def add_copy_link_script(html_content):
    script = '''<script>
document.querySelectorAll('.share-copy').forEach(function(btn){btn.addEventListener('click',function(e){e.preventDefault();var url=this.getAttribute('data-url');navigator.clipboard.writeText(url).then(function(){btn.textContent='Copied!';setTimeout(function(){btn.textContent='Copy Link'},2000)});});});
</script>
'''
    if '.share-copy' not in html_content and 'share-copy' not in html_content:
        body_end = '</body>'
        html_content = html_content.replace(body_end, script + body_end, 1)
    return html_content

def process_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    rel = filepath.relative_to(BASE)
    is_topic = 'topics' in rel.parts
    rel_depth = '../../' if is_topic else ''

    title_match = re.search(r'<title>(.+?)</title>', content)
    desc_match = re.search(r'<meta name="description" content="([^"]+)"', content)
    canonical_match = re.search(r'<link rel="canonical" href="([^"]+)"', content)
    og_url_match = re.search(r'<meta property="og:url" content="([^"]+)"', content)

    if not title_match:
        return False

    title = title_match.group(1)
    desc = desc_match.group(1) if desc_match else ''
    canonical_url = canonical_match.group(1) if canonical_match else (og_url_match.group(1) if og_url_match else '')
    og_title = title.split(' - ')[0].strip() if ' - ' in title else title

    og_site_name = 'og:site_name' in content
    twitter_card = 'twitter:card' in content

    modified = False

    if is_topic:
        if not og_site_name:
            content = add_og_twitter_tags(content, og_title, desc, canonical_url)
            modified = True

        if not twitter_card:
            pass

        soup = BeautifulSoup(content, 'html.parser')
        qa_pairs = extract_qa_pairs(soup)

        if qa_pairs and 'FAQPage' not in content:
            content = add_faq_schema(content, qa_pairs)
            modified = True

        siblings = get_sibling_topics(filepath)
        subject_files = get_link_subjects(filepath)

        if 'related-topics' not in content:
            content = add_related_topics_section(content, siblings, subject_files, rel_depth)
            modified = True

        if 'share-section' not in content:
            content = add_share_section(content, canonical_url, og_title)
            modified = True

            if 'share-copy' not in content:
                content = add_copy_link_script(content)

    else:
        if not og_site_name or not twitter_card:
            content = add_og_twitter_tags(content, og_title, desc, canonical_url, 'website')
            modified = True

        if 'share-section' not in content:
            content = add_share_section(content, canonical_url, og_title)
            modified = True

            if 'share-copy' not in content:
                content = add_copy_link_script(content)

    if modified:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)

    return modified

count = 0
for html_file in sorted(BASE.rglob('*.html')):
    if process_file(html_file):
        count += 1
        if count % 100 == 0:
            print(f'  Processed {count} files...')

print(f'\nDone. Modified {count} files.')
