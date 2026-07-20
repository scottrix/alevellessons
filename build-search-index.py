#!/usr/bin/env python3
"""Build search-index.json from subjects.json and the subject landing pages.

For every GCSE subject we collect:
  * subject metadata (id, name, category, papers, boards, url, aliases)
  * every topic-card found on that subject's landing page, enriched with
    strand name (from the section heading) and, where data/{id}.json exists,
    the topic description and skills list.

The resulting search-index.json is loaded client-side by app.js so the home
page search box can match both subjects (~37 items) and topics (~1200 items).
"""

import html
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))

TOPIC_CARD_RE = re.compile(
    r'<a\s+href="(?P<href>topics/[^"]+)"\s+class="topic-card[^"]*">\s*'
    r'<span class="topic-id">(?P<tid>[^<]+)</span>\s*'
    r'<span class="topic-name">(?P<name>[^<]+)</span>',
    re.DOTALL,
)

# Match sections like <section id="cell-biology" class="section"><h2>🧬 Cell Biology (5 Topics)</h2>
SECTION_RE = re.compile(
    r'<section\s+id="([^"]+)"[^>]*>\s*<h2[^>]*>([^<]+)</h2>',
    re.DOTALL,
)
# Match optional img inside h2 (some pages prefix an emoji image)
STRAND_TITLE_CLEAN_RE = re.compile(r"\s*\(\d+\s*Topics?\)\s*$", re.IGNORECASE)

# Common aliases / short forms so "maths" matches "Mathematics", etc.
ALIASES = {
    "mathematics": ["maths", "math"],
    "english-language": ["english lang", "english language"],
    "english-literature": ["english lit", "english literature"],
    "religious-studies": ["rs", "re", "religious studies", "religion"],
    "physical-education": ["pe", "sport", "physical education"],
    "computer-science": ["computing", "computer science", "cs"],
    "combined-science": ["combined sci", "trilogy science", "double science"],
    "design-and-technology": ["dt", "design & technology", "design and tech"],
    "food-preparation-nutrition": ["food", "cooking", "food prep", "food tech"],
    "business": ["business studies", "bs"],
    "media-studies": ["media"],
    "film-studies": ["film"],
    "citizenship-studies": ["citizenship"],
    "classical-civilisation": ["classics", "class civ"],
    "ancient-history": ["ancient hist"],
    "art-and-design": ["art"],
}


def clean_strand_title(raw):
    title = raw.strip()
    # Strip leading emoji if present (split on first non-emoji whitespace safe to keep)
    title = re.sub(r"^[^\w\s]+", "", title).strip()
    title = STRAND_TITLE_CLEAN_RE.sub("", title).strip()
    return title


def parse_landing_page(subject_id):
    """Return list of topics scraped from the landing page, with strand name."""
    fname = os.path.join(ROOT, f"{subject_id}.html")
    if not os.path.exists(fname):
        return []

    html = open(fname, encoding="utf-8").read()

    # Sections in document order with their byte positions
    sections = [
        (m.start(), m.group(1), clean_strand_title(m.group(2)))
        for m in SECTION_RE.finditer(html)
    ]

    topics = []
    for m in TOPIC_CARD_RE.finditer(html):
        tid = m.group("tid").strip()
        name = m.group("name").strip()
        href = m.group("href").strip()
        strand_id = ""
        strand_name = ""
        # Find the most recent section before this topic card
        for sec_pos, sec_id, sec_name in reversed(sections):
            if sec_pos < m.start():
                strand_id, strand_name = sec_id, sec_name
                break
        topics.append({
            "id": tid,
            "name": name,
            "strandId": strand_id,
            "strandName": strand_name,
            "url": href.replace("topics/", "topics/"),
            "subject": subject_id,
        })
    return topics


def load_data_index(subject_id):
    """Load data/{id}.json if present and return a map of topic_id -> {description, skills}."""
    path = os.path.join(ROOT, "data", f"{subject_id}.json")
    if not os.path.exists(path):
        return {}
    data = json.load(open(path, encoding="utf-8"))
    out = {}
    for strand in data.get("strands", []):
        for topic in strand.get("topics", []):
            out[topic["id"]] = {
                "description": topic.get("description", ""),
                "skills": " ".join(topic.get("skills", [])),
            }
    return out


def build_subject(subject):
    return {
        "id": subject["id"],
        "name": subject["name"],
        "category": subject["category"],
        "papers": subject.get("papers", 0),
        "boards": subject.get("boards", []),
        "aliases": ALIASES.get(subject["id"], []),
        "url": f'{subject["id"]}.html',
    }


def build_topics(subject):
    topics = parse_landing_page(subject["id"])
    data_idx = load_data_index(subject["id"])
    for t in topics:
        tid = t["id"]
        extra = data_idx.get(tid, {"description": "", "skills": ""})
        description = extra["description"]
        skills = extra["skills"]
        # Decode any HTML entities (& -> &, &#x27; -> ', etc.) from the
        # page-scraped topic names so the searchText uses real characters and
        # the user can search for "voltage & resistance" with a real &.
        name_decoded = html.unescape(t["name"])
        strand_decoded = html.unescape(t["strandName"])
        # Concatenated searchable text: id + name + strand + subject + description + skills
        parts = [
            tid,
            name_decoded,
            strand_decoded,
            subject["name"],
            description,
            skills,
        ]
        t["searchText"] = " ".join(p for p in parts if p).lower()
        t["name"] = name_decoded
        t["strandName"] = strand_decoded
        t["subjectName"] = subject["name"]
        t["category"] = subject["category"]
    return topics


def main():
    subjects_path = os.path.join(ROOT, "subjects.json")
    subjects = json.load(open(subjects_path, encoding="utf-8"))["subjects"]

    index = {
        "subjects": [build_subject(s) for s in subjects],
        "topics": [],
    }
    for s in subjects:
        index["topics"].extend(build_topics(s))

    out_path = os.path.join(ROOT, "search-index.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(index, f, ensure_ascii=False, separators=(",", ":"))

    with_desc = sum(1 for t in index["topics"] if t["searchText"].count(" ") > 5)
    print(
        f"Wrote {out_path}: {len(index['subjects'])} subjects, "
        f"{len(index['topics'])} topics "
        f"({os.path.getsize(out_path)} bytes)"
    )


if __name__ == "__main__":
    sys.exit(main())
