#!/usr/bin/env python3
"""Add lesson-template sections to alevellessons biology pages."""
import glob
import os
import re
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))

# Per-topic lesson content
BIO = {
    "biochemistry-and-respiration": {
        "starter": "Quick-fire recall: name the four main biological molecules, draw the general structure of an amino acid, and state the bond formed in a condensation reaction. Use mini-whiteboards.",
        "script_l1": "Begin by asking students to list the four biological molecules and their monomers. Draw the condensation/hydrolysis cycle on the board, emphasising the role of water. Introduce the glycosidic, peptide and ester bonds with colour-coded diagrams. Test for reducing sugars (Benedict's), starch (iodine) and protein (biuret) as demonstrations — students record colour changes.",
        "script_l2": "Build on L1 by exploring enzyme structure and the induced-fit model. Draw the active site and substrate interaction. Discuss how temperature and pH affect enzyme activity using graph sketches. Introduce competitive and non-competitive inhibition with statin and cyanide as examples.",
        "script_l3": "Connect biochemistry to respiration: glycolysis splits glucose into two pyruvate molecules (net 2 ATP, 2 NADH). Draw the link reaction converting pyruvate to acetyl CoA. Emphasise where each stage occurs (cytoplasm vs mitochondrial matrix vs inner membrane).",
        "script_l4": "Work through an exam question on enzyme activity graphs. Model the answer structure: describe the trend, explain using collision theory and enzyme-substrate complex formation, then evaluate using data from the graph.",
        "misconceptions": [
            ["Enzymes are 'used up' in reactions", "Enzymes are biological catalysts — they are NOT consumed. They can be reused thousands of times per second."],
            ["All respiration produces lactic acid", "Only ANAEROBIC respiration in muscles produces lactic acid. Aerobic respiration produces CO2 and water."],
            ["ATP is a store of energy", "ATP is an immediate ENERGY SOURCE — it is not stored. Cells maintain only a small pool and regenerate it constantly (a human recycles ~50kg of ATP daily)."],
        ],
        "cfu": "Hinge question: 'If the temperature rises from 37°C to 60°C, what happens to the rate of an enzyme-catalysed reaction and why?' Expected: rate initially increases then drops sharply as the enzyme denatures (hydrogen bonds break, tertiary structure lost, active site distorted). Students who say 'rate continues to increase' need to revisit protein structure.",
        "support": "Provide a partially completed diagram of the glycolysis pathway with some labels filled in. Students fill the gaps using the word bank.",
        "stretch": "Ask students to calculate the ATP yield from a 24-carbon fatty acid (vs glucose) and explain why fats yield more ATP per gram but are slower to mobilise.",
        "practical": "Required Practical 1 (AQA): Investigation of the effect of a variable on the rate of an enzyme-controlled reaction. Variables: temperature, pH, enzyme concentration, substrate concentration. Use catalase and hydrogen peroxide, or amylase and starch.",
        "maths": "Rates of reaction from graph gradients; Student's t-test for comparing two means; standard deviation for measuring spread of data around a mean.",
        "synoptic": "Links to: Nucleic acids (DNA codes for enzyme primary structure), Transport across membranes (enzyme location), Populations (selection pressure on enzyme variants).",
    },
}

# Generic fallbacks for other biology topics
GENERIC = {
    "starter": "Quick recall: 3 questions from the previous lesson on this topic. Use mini-whiteboards or paper. Focus on definitions and key processes.",
    "script_l1": "Introduce the topic using the key definitions above. Draw the central diagram on the board, labelling each component. Connect to prior learning and explain why this topic matters for the exam.",
    "script_l2": "Work through the core concepts section by section. At each stage, ask a check-for-understanding question before moving on. Address misconceptions as they arise.",
    "script_l3": "Apply the concepts to exam-style scenarios. Model one answer on the board, showing how to structure responses for the command word used.",
    "script_l4": "Work through past-paper questions. Focus on mark-scheme language, timing (1 mark per minute) and how to structure longer answers.",
    "misconceptions": [
        ["Students confuse correlation with causation", "Always ask: has a mechanism been demonstrated, or just an association?"],
        ["Students think larger sample size proves causation", "Larger samples reduce random error but do not eliminate confounding variables."],
        ["Students confuse mitosis and meiosis", "Mitosis = 2 identical diploid cells (growth/repair). Meiosis = 4 genetically different haploid cells (gametes)."],
    ],
    "cfu": "Hinge question: ask students to explain the key concept in their own words to their partner. Listen for correct use of terminology and logical structure. Address gaps before moving to independent practice.",
    "support": "Provide a scaffolded worksheet with sentence starters and a word bank for the main task.",
    "stretch": "Ask students to apply the concept to an unfamiliar organism or context, or to evaluate experimental design limitations.",
    "practical": "Refer to the required practical for this topic in your board's practical handbook. Ensure students can describe the method, variables and expected results.",
    "maths": "Apply relevant maths skills: percentages, ratios, graph interpretation, standard deviation, or statistical testing as appropriate to this topic.",
    "synoptic": "Link this topic to related areas across the specification — identify which prior topics feed in and which later topics build on this foundation.",
}


def build_sections(topic_key, existing_headings):
    data = BIO.get(topic_key, GENERIC)
    # Build the lesson sections HTML
    mis_items = ''.join(
        f'<div class="key-point"><p><strong>If a student says:</strong> "{m[0]}"</p>'
        f'<p><strong>Respond:</strong> {m[1]}</p></div>'
        for m in data['misconceptions']
    )
    sections = (
        '<section class="section">\n<h2>🚀 Starter Activity (5 minutes)</h2>\n'
        f'<div class="key-point"><p>{data["starter"]}</p></div>\n</section>\n\n'

        '<section class="section">\n<h2>📋 Teaching Script (35 minutes)</h2>\n'
        '<div class="key-point">\n'
        '<p><strong>Mins 0–5 — Hook & Recap:</strong> ' + data['starter'] + '</p>\n'
        '<p><strong>Mins 5–15 — Direct Instruction (Lesson 1):</strong> ' + data['script_l1'] + '</p>\n'
        '<p><strong>Mins 15–25 — Core Concepts (Lesson 2):</strong> ' + data['script_l2'] + '</p>\n'
        '<p><strong>Mins 25–30 — Application (Lesson 3):</strong> ' + data['script_l3'] + '</p>\n'
        '<p><strong>Mins 30–35 — Exam Technique (Lesson 4):</strong> ' + data['script_l4'] + '</p>\n'
        '</div>\n</section>\n\n'

        '<section class="section">\n<h2>⚠️ Common Misconceptions</h2>\n'
        + mis_items + '\n</section>\n\n'

        '<section class="section">\n<h2>✅ Check for Understanding</h2>\n'
        f'<div class="key-point"><p><strong>Hinge question:</strong> {data["cfu"]}</p></div>\n</section>\n\n'

        '<section class="section">\n<h2>📊 Differentiation</h2>\n'
        '<div class="key-point">\n'
        f'<p><strong>Support scaffold:</strong> {data["support"]}</p>\n'
        f'<p><strong>Stretch & Challenge (Grade A/A*):</strong> {data["stretch"]}</p>\n'
        '</div>\n</section>\n\n'

        '<section class="section">\n<h2>🧪 Required Practical & Maths Skills</h2>\n'
        '<div class="key-point">\n'
        f'<p><strong>Required practical:</strong> {data["practical"]}</p>\n'
        f'<p><strong>Maths skills:</strong> {data["maths"]}</p>\n'
        f'<p><strong>Synoptic links:</strong> {data["synoptic"]}</p>\n'
        '</div>\n</section>\n\n'

        '<section class="section">\n<h2>📝 Homework & Consolidation</h2>\n'
        '<div class="key-point">\n'
        '<p><strong>Consolidation (15 min):</strong> Write a summary paragraph of the key concepts in your own words.</p>\n'
        '<p><strong>Retrieval (10 min):</strong> Create 5 flashcards from the key definitions above.</p>\n'
        '<p><strong>Exam practice (20 min):</strong> Complete one past-paper question. Self-mark using the mark scheme.</p>\n'
        '<p><strong>Extension (optional, 20 min):</strong> Research a real-world application or recent development.</p>\n'
        '</div>\n</section>'
    )
    return sections


def main():
    only = sys.argv[1:] or None
    n = 0
    for path in sorted(glob.glob(f'{ROOT}/topics/biology/*.html')):
        slug = os.path.basename(path)[:-5]
        if only and slug not in only:
            continue
        h = open(path, encoding='utf-8').read()
        if 'Starter Activity' in h or 'Teaching Script' in h:
            continue
        # Find the first spec-referenced content section (e.g. "Carbohydrates, lipids...")
        # Insert lesson sections BEFORE it
        content_start = None
        for m in re.finditer(r'<h2[^>]*>([^<]+)</h2>', h):
            t = m.group(1).strip()
            if not t.startswith(('🎯', '📋', '📌', '💡', '❓', '🎬', '📄', '🔗', '🧠', '📝', 'Board Notes',
                                 'Reference Diagram', 'Draw-Along', 'Topics')):
                content_start = m.start()
                break
        if content_start is None:
            # fallback: insert before the first section with a 💡 or after Key Points
            content_start = h.find('</section>')
            # skip to the second section boundary
            second = h.find('</section>', content_start + 1)
            content_start = second + 10 if second != -1 else content_start

        lesson_html = build_sections(slug, [])
        h = h[:content_start] + lesson_html + '\n\n' + h[content_start:]
        open(path, 'w', encoding='utf-8').write(h)
        n += 1
    print(f'lesson-template sections added: {n} biology pages')


if __name__ == '__main__':
    main()
