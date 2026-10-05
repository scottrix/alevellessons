# A-Level Lessons — Site Improvement Brief (for AI agent)

**Site live:** https://scottrix.github.io/alevellessons
**Canonical repo:** `/home/scott/src/alevellessons`
**Mirror repo (must apply same edits):** `/home/scott/src/github/alevellessons`
**Date of audit:** 2026-09-28
**Goal:** Best UK A-Level homeschool lesson resource. LESSONS not revision: teach from scratch in 50-minute parent-delivered sessions with filled teaching scripts, plenty of worked examples with full steps, guided + independent practice, checks for understanding, misconceptions, support/stretch (including Grade A/A* stretch), materials, timings, homework, assessment. A-Level adds: Year 12→13 progression, required practicals (AQA 12 / Edexcel 16 core / OCR PAGs), maths skills, synoptic links, essay/data-response frames, NEA where applicable. Reference: gcselessons (sister site, correct lesson template), Oak Academy, Massolit, tutor2u, savemyexams smart lessons.

---

## 1. Current state (verified)

- `subjects.json`: 35 subjects, 140 topics. Per-subject board lists are HONEST (e.g. economics AQA/Edexcel/OCR only, philosophy AQA only, law AQA/OCR/WJEC, CCEA total 12) — better than alevelrevise's false 28-each claim. Homepage counts (AQA 27 / Edexcel 20 / OCR 24 / WJEC-Eduqas 25 / CCEA 12) match JSON — keep this generated-from-JSON approach.
- `topics/`: **101 files in 28 dirs** (same shape as alevelrevise: `topics/{subject}/{topic}.html`, no board/tier subdirs). **39 JSON topics have no file** (all of ancient-history 6, classical-civilisation 6, geology 6, statistics 6, film-studies 6, dance 4, design-and-technology 5 — full missing list in §7 command). Those 7 subject pages have zero topic links (verified `ancient-history.html`: no `topics/` hrefs).
- Page size avg **1,124 words incl. boilerplate** (~113k total) — thinnest of the four sites; far below lesson needs.
- Template is the REVISION template (📌 Key Points / 🎯 Learning Objectives / 💡 Worked Example / ❓ Practice / video / past papers / further reading / flashcard+exam+target+smart-lesson containers). Lesson markers sitewide: teaching script 0, starter 0, plenary 0, homework 0, CFU 0, misconception 0, differentiation 13, worked example 101, practice question 101. **This is a revision clone, not a lessons site.**
- `search-index.json`: 28 subjects / 101 topics (stale vs JSON 35/140). `sitemap.xml`: 432 URLs. `smart-lessons/` ~102 JSON vs `exam-questions/` 1, `flashcards/` 1, `target-tests/` 1, `mock-exams/` 0.
- alevelrevise↔alevellessons cross-links exist (`nav-lesson` "Full lesson on Smart Lessons →" on revise pages; reverse link assumed here — verify).
- 40 root HTML incl. duplicates (`business`/`business-studies`, `drama`/`drama-and-theatre`, `pe`/`physical-education` — same dup pattern as alevelrevise).

## 2. Defects (prioritised)

### P0-1. Identity crisis — decide what this site is, then brand it
- `index.html` title/meta/JSON-LD/schema say "A-Level Revise … Revision Notes", nav links "../" to alevelrevise, footer GitHub + contact email point at `alevelrevise`. `biology.html` title says "Free Lessons Notes" (grammar + inconsistent). Homepage webfetch renders as revision site.
- **Task:** Rebrand fully to lessons: title/meta/headers "A-Level Lessons — Parent-Delivered Plans", homeschool-guide banner (copy gcselessons pattern, A-Level-adapted), contact `alevellessons@…`, GitHub link to alevellessons repo, lesson promise list (objectives, prerequisites, scripts, examples, differentiation, starter/plenary, assessment, homework). Fix "Lessons Notes" grammar everywhere. Acceptance: zero "Revise"/"Revision Notes" strings outside cross-links; zero alevelrevise contact/URLs except intentional cross-links.

### P0-2. Convert revision pages → real lesson template (the main job)
- Adopt the gcselessons structure per file: Overview → Objectives → Prerequisites (with Year 12/13 + GCSE assumed knowledge) → Materials → Sub-lessons (Intro / Core / Application / Exam Practice, 50 min each, starter + timed script + plenary) → Homework → Resources → Smart Lesson container. Fill ALL script brackets (gcselessons has ~799 unfilled — do NOT copy that bug; every hook/goal/vocab/troubleshooting/example must be topic-specific from day one).
- A-Level lesson must-haves: ≥4 worked examples with full steps (maths: every algebraic line; sciences: data + uncertainties + PAG mapping; essays: thesis → PEEL paragraphs with quotations; languages: model sentences + manipulation drills), hinge/CFU questions with answers, 3–4 misconceptions with correction scripts, support scaffold vs A/A* stretch, required-practical box (AQA 12 / Edexcel core / OCR PAG codes), maths-skills box, synoptic-link box, board-notes box (papers, option routes, NEA), exam-technique (command words, AO1/AO2/AO3 splits, timing).
- **Task:** Rewrite all 101 files to lesson template, then create the 39 missing (ancient-history, classical-civ, geology, statistics, film, dance, D&T first — they currently 404/empties). Target ≥2,000 real words/file for sciences/maths, ≥1,500 humanities/languages. Acceptance: lesson-marker grep (teaching script/starter/plenary/homework/misconception/CFU) → 101+39 hits each; bracket-placeholder grep → 0.

### P0-3. Placeholders + thin content
- 25 files contain "Demonstrate clear conceptual understanding" generic Q&A (same bug as alevelrevise). Delete all; write real exam-style Qs with mark-scheme answers.
- Single-mega-topic subjects (sociology/politics/law/philosophy/languages/PE/etc., 1 page each) cannot be taught in any depth — split per the alevelrevise report's Tier-2 table (8–12 lessons each), reusing its topic splits.
- **Task:** Same split plan as alevelrevise Tier 2, but each split unit written as lesson (not revision note). Update JSON + sidebar + subject pages + search + sitemap.

### P0-4. Board badges contradict JSON
- Subject pages (e.g. `biology.html`) show "All Boards (AQA, Edexcel, OCR, WJEC, CCEA)" while JSON is per-subject. Lessons stay board-agnostic single files (like gcselessons) — but each needs a board-notes box (papers, options, practicals, NEA, tiers N/A at A-Level except maths).
- **Task:** Replace generic badge with JSON-derived board list + board-notes box per lesson. Homepage counts already correct — keep generated.

### P0-5. Orphans/dups/nav/sitemap/search/canonical (same family bugs)
- 39 missing files (§1); 7 empty subject pages; dup roots (business/drama/pe pairs — 301 to canonical); `search-index` (28/101) and `sitemap` (432) out of sync with JSON (35/140); canonicals point at `www.scottrix.co.uk/alevellessons/` vs live `scottrix.github.io/alevellessons`; check `robots.txt` present and correct.
- **Task:** Create missing 39, dedupe roots with redirects, regen search/sitemap/dashboard data from filesystem+JSON, single canonical domain, robots with Sitemap line. Acceptance: 0 missing, 0 dups, counts match.

### P0-6. Diagrams + interactives
- 0 SVG expected (same generator as alevelrevise); all `<img>` affiliate banners. Lessons need stepped draw-alongs + inline SVG (mechanisms, fields, spectra, graphs, essay structures, grammar trees). `exam-questions/`(1)/`flashcards/`(1)/`target-tests/`(1)/`mock-exams/`(0) vs `smart-lessons/`(~102) — backfill or hide empty containers.
- **Task:** ≥1 figure/draw-along per visual lesson; backfill JSON or hide empties.

## 3. Execution order
1. P0-1 rebrand (cheap, high trust).
2. P0-5 missing files + dups + search/sitemap/canonical/robots (site integrity).
3. P0-2 lesson-template conversion (one subject at a time; sciences/maths first).
4. P0-3 placeholders + Tier-2 splits as lessons.
5. P0-4 board boxes + bidirectional alevelrevise↔alevellessons links verified.
6. P0-6 figures + interactives.
7. Mirror every edit to `/home/scott/src/github/alevellessons`.

## 4. Sources (not just savemyexams)
Official specs + specimen mark schemes + examiners' reports + practical handbooks (AQA/Edexcel/OCR/WJEC-Eduqas/CCEA); gcselessons template (structure only — write A-Level content fresh); Oak/Massolit/tutor2u (pedagogy); PMT/TLMaths/Dr Frost (Qs); Chemguide/IOP/RSC; set texts/critics for lit/languages. Never copy — synthesise, cite spec codes.

## 5. Reproduce-audit commands
```
cd /home/scott/src/alevellessons
python3 -c "import json;d=json.load(open('subjects.json'));s=d['subjects'];print(len(s),sum(len(x.get('topics',[])) for x in s))"
python3 -c "import json,os;d=json.load(open('subjects.json'));m=[t['page'] for s in d['subjects'] for t in s.get('topics',[]) if t.get('page') and not os.path.exists(t['page'])];print(len(m));print('\n'.join(m))"
find topics -type f | wc -l
grep -rl "Demonstrate clear conceptual understanding" topics | wc -l
grep -rli "teaching script\|starter activity\|plenary\|check for understanding\|misconception" topics | wc -l
grep -m1 "<title>" index.html biology.html
python3 -c "import json;d=json.load(open('search-index.json'));print({k:len(v) for k,v in d.items()})"
python3 -c "import re;print('sitemap:',len(re.findall('<loc>',open('sitemap.xml').read()))))"
diff -q topics/mathematics/algebraic-expressions.html /home/scott/src/alevelrevise/topics/mathematics/algebraic-expressions.html
```

## 6. Acceptance criteria
- [ ] Lessons branding everywhere; zero revise contact/repo strings except cross-links.
- [ ] All 140 JSON topics exist as lesson-template files; 7 empty subjects filled.
- [ ] Zero bracket placeholders; zero generic Q&A.
- [ ] Every lesson: scripts + ≥4 worked examples + CFU + misconceptions + support/stretch + practical/maths/synoptic/board boxes + homework.
- [ ] search/sitemap == filesystem+JSON; single canonical; robots OK; dups redirected.
- [ ] Figures on all visual lessons; no empty interactive containers.
- [ ] Both repo copies identical for changed files.
