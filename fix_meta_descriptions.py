#!/usr/bin/env python3
"""
fix_meta_descriptions.py - Bing Webmaster Tools flagged 9 gcserevise pages
for "meta description too short". This script replaces the existing short
content on the description, og:description, and twitter:description meta
tags with new 150-160 char descriptions grounded in the actual strand
structure of each subject.

Idempotent: re-running after the fix is a no-op (the OLD short descriptions
are no longer present, so each file is left unchanged).
"""
import re
from pathlib import Path

NEW_DESCRIPTIONS = {
    'biology.html': "Free GCSE Biology revision notes across 7 strands: Cell Biology, Organisation, Infection and Response, Bioenergetics, Homeostasis, Inheritance, Ecology.",
    'geography.html': "Free GCSE Geography revision notes across 8 strands: Natural Hazards, Living World, UK Physical Landscapes, Urban Issues, Economic World, Resource Management.",
    'physics.html': "Free GCSE Physics revision notes across 7 strands: Energy, Electricity, Particle Model, Atomic Structure, Forces, Waves, Magnetism. 30 topics, all exam boards.",
    'english-language.html': "Free GCSE English Language revision across 4 strands: Reading Skills, Creative Writing, Transactional and Persuasive Writing, SPaG. 23 topics. All exam boards.",
    'spanish.html': "Free GCSE Spanish notes across 32 topics and 3 themes (Identity and Culture; Local/National/Global Issues; Future Study) plus grammar. All exam boards.",
    'chemistry.html': "Free GCSE Chemistry revision notes across 10 strands: Atomic Structure, Bonding, Quantitative, Chemical Changes, Rates, Organic, Atmosphere, Using Resources.",
    'english-literature.html': "Free GCSE English Literature revision notes across 6 strands: Literary Analysis, Shakespeare, Poetry, 19th Century Novel, Modern Texts, Literature Writing.",
    'pe.html': "Free GCSE PE revision notes across 6 strands: Anatomy & Physiology, Movement Analysis, Physical Training, Sports Psychology, Socio-Cultural, Health & Wellbeing.",
    'topics/movement-analysis/PE11-movement-analysis-sport.html': "GCSE PE revision: types of movement at joints in sport. Flexion, extension, abduction and adduction at the shoulder, elbow, hip, knee and ankle joints.",
}

# Map each OLD short description content to its replacement.
# We do this by reading the file, finding the description content, and rewriting
# every meta tag that uses that exact content (description, og:description,
# twitter:description on these pages all share the same content).
TOTAL_CHANGED = 0
for relpath, new_desc in NEW_DESCRIPTIONS.items():
    p = Path(relpath)
    text = p.read_text(encoding='utf-8')

    # Find the current meta name="description" content
    m = re.search(r'<meta name="description" content="([^"]*)"', text)
    if not m:
        print(f'  WARNING: no description meta in {relpath}')
        continue
    old_desc = m.group(1)
    if old_desc == new_desc:
        print(f'  SKIP (already updated): {relpath}')
        continue

    # Replace ALL occurrences of the old content (description, og:description,
    # twitter:description typically all use the same text on these pages).
    new_text = text.replace('content="' + old_desc + '"', 'content="' + new_desc + '"')
    replacements = text.count('content="' + old_desc + '"')
    p.write_text(new_text, encoding='utf-8')
    print(f'  Updated {relpath}: {len(old_desc)} -> {len(new_desc)} chars ({replacements} meta tags)')
    TOTAL_CHANGED += 1

print(f'\nFiles changed: {TOTAL_CHANGED}/{len(NEW_DESCRIPTIONS)}')
