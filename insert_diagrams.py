#!/usr/bin/env python3
"""P0-6: Insert inline SVG diagrams + draw-along boxes into alevellessons STEM pages."""
import glob
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, '/home/scott/src/gcselessons')
from insert_diagrams import SVGS, DRAWALONG

UNIT_MAP = {
    'biology': 'cell-diagram', 'chemistry': 'atom-diagram', 'physics': 'circuit-diagram',
    'mathematics': 'linear-graph', 'further-mathematics': 'linear-graph',
    'computer-science': 'flowchart', 'geography': 'greenhouse-effect',
    'economics': 'linear-graph', 'physical-education': 'heart-diagram',
    'psychology': 'flowchart', 'business': 'flowchart',
}


def drawalong(subject):
    return (f'Draw the key diagram for {subject}: start with the main structure, add labels with arrows, '
            'then annotate with the key facts from the lesson. Use a ruler for straight lines.')


def main():
    n_svg = n_da = 0
    for unit, dtype in UNIT_MAP.items():
        svg_fn = SVGS.get(dtype)
        da_text = DRAWALONG.get(dtype, drawalong(unit))
        for path in sorted(glob.glob(f'topics/{unit}/*.html')):
            h = open(path, encoding='utf-8').read()
            if 'draw-along' in h.lower() or '<svg' in h:
                continue
            svg_html = ''
            if svg_fn:
                svg = svg_fn()
                svg_html = (f'<section class="section">\n<h2>Reference Diagram</h2>\n'
                            f'<div style="text-align:center">{svg}</div>\n</section>')
                n_svg += 1
            da_html = (f'<section class="section">\n<h2>Draw-Along Instructions</h2>\n'
                       f'<div class="key-point"><p><strong>Parent/teacher:</strong> {da_text}</p>'
                       '<p>Display the reference diagram (or draw it live) while the student copies. '
                       'Check each label as it is added.</p></div>\n</section>')
            n_da += 1
            insert = (svg_html + '\n' + da_html) if svg_html else da_html
            for anchor in ('Further Reading', 'Past Papers', 'Board Notes', 'Video Resources'):
                m = re.search(r'<h2[^>]*>\s*' + re.escape(anchor), h)
                if m:
                    h = h[:m.start()] + insert + '\n' + h[m.start():]
                    break
            else:
                i = h.find('</main>')
                if i != -1:
                    h = h[:i] + insert + '\n' + h[i:]
            open(path, 'w', encoding='utf-8').write(h)
    print(f'SVG diagrams: {n_svg} | draw-along boxes: {n_da}')


if __name__ == '__main__':
    main()
