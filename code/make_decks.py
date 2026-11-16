#!/usr/bin/env python3
"""Build the bilingual speaker decks for exercises 5 and 6.

Usage from the multi-exercise tree root::

    python3 tools/make_decks.py            # builds both exercises
    python3 tools/make_decks.py 5

The same file is vendored into ``exercise-5/code/`` and ``exercise-6/code/``;
run there with no arguments and it builds that one exercise from its own data
file, so a flattened branch stays self-contained.

Every slide gets speaker notes.  Standalone speaker-text Markdown files are
written too.  All slide text and notes come from ``output/experiments.json``;
no number is typed in this file.
"""
from __future__ import annotations

import os
import sys

from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE

FONT = "Vazirmatn"
INK = RGBColor(0x1B, 0x2A, 0x41)
ACCENT = RGBColor(0x37, 0x61, 0x8E)
MUTED = RGBColor(0x55, 0x5F, 0x70)

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)


def _data(exercise_root: str) -> dict:
    import json
    p = os.path.join(exercise_root, "output", "experiments.json")
    with open(p, "r", encoding="utf-8") as f:
        return json.load(f)


def _shape_text(slide, x, y, w, h, lines, lang, size, bold_first=False):
    box = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = box.text_frame
    tf.word_wrap = True
    for i, line in enumerate(lines):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.text = str(line)
        p.font.name = FONT
        p.font.size = Pt(size)
        p.font.bold = bool(bold_first and i == 0)
        p.font.color.rgb = INK if i == 0 else MUTED
        p.alignment = PP_ALIGN.RIGHT if lang == "fa" else PP_ALIGN.LEFT
        pPr = p._p.get_or_add_pPr()
        pPr.set("rtl", "1" if lang == "fa" else "0")
        p.level = 0
    return box


def build_one(exercise_root: str, lang: str, file_name: str,
              slides: list) -> str:
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank = prs.slide_layouts[6]
    diagrams = os.path.join(exercise_root, "diagrams")
    for s in slides:
        slide = prs.slides.add_slide(blank)
        bg = slide.background.fill
        bg.solid()
        bg.fore_color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
        # accent bar
        bar = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.0), Inches(0.0),
                                     Inches(0.14), Inches(7.5))
        bar.fill.solid()
        bar.fill.fore_color.rgb = ACCENT
        bar.line.fill.background()
        title = s["title_fa"] if lang == "fa" else s["title_en"]
        body = s["body_fa"] if lang == "fa" else s["body_en"]
        notes = s["notes_fa"] if lang == "fa" else s["notes_en"]
        _shape_text(slide, 0.65, 0.35, 12.0, 1.05, [title], lang, 30,
                    bold_first=True)
        _shape_text(slide, 0.75, 1.65, 11.7, 3.6,
                    [f"- {b}" for b in body], lang, 18)
        if s.get("figure"):
            path = os.path.join(diagrams, s["figure"])
            if os.path.exists(path):
                slide.shapes.add_picture(path, Inches(7.6), Inches(4.4),
                                         width=Inches(5.0))
        # speaker notes on EVERY slide
        slide.notes_slide.notes_text_frame.text = str(notes)
    docs = os.path.join(exercise_root, "docs")
    os.makedirs(docs, exist_ok=True)
    path = os.path.join(docs, file_name)
    prs.save(path)
    return path


def speaker_markdown(exercise_root: str, lang: str, file_name: str,
                     slides: list) -> str:
    docs = os.path.join(exercise_root, "docs")
    os.makedirs(docs, exist_ok=True)
    lines = ["# " + ("Speaker notes — English" if lang == "en"
                     else "متن گوینده — فارسی"), ""]
    for i, s in enumerate(slides, start=1):
        lines.append(f"## Slide {i}. " + (s["title_en"] if lang == "en"
                                         else s["title_fa"]))
        lines.append("")
        for b in (s["body_en"] if lang == "en" else s["body_fa"]):
            lines.append(f"- {b}")
        lines.append("")
        lines.append("**" + ("Speaker text" if lang == "en" else "متن گوینده") + ":** "
                     + (s["notes_en"] if lang == "en" else s["notes_fa"]))
        lines.append("")
        if s.get("source"):
            lines.append(f"*{'Source' if lang == 'en' else 'منبع'}: {s['source']}*")
            lines.append("")
    path = os.path.join(docs, file_name)
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    return path


def build_exercise(exercise_root: str) -> dict:
    data = _data(exercise_root)
    decks = data.get("decks", {})
    slides = decks.get("slides", [])
    if not slides:
        return {"exercise": os.path.basename(exercise_root), "decks": []}
    made = []
    for name in decks.get("files", []):
        lang = "fa" if name.upper().endswith(("_FA.PPTX", "_FA.MD")) else "en"
        if name.lower().endswith(".pptx"):
            made.append(build_one(exercise_root, lang, name, slides))
        elif name.lower().endswith(".md"):
            made.append(speaker_markdown(exercise_root, lang, name, slides))
    return {"exercise": os.path.basename(exercise_root),
            "slides": len(slides),
            "notes_on_every_slide": all(s.get("notes_en") and s.get("notes_fa")
                                        for s in slides),
            "outputs": made}


def main(argv):
    # tree mode: exercises-N live under ROOT; flat mode: this file is in code/
    if os.path.isdir(os.path.join(ROOT, "exercise-5")):
        nums = [int(a) for a in argv[1:]] or [5, 6]
        roots = [os.path.join(ROOT, f"exercise-{n}") for n in nums]
    else:
        roots = [os.path.dirname(HERE)]
    import json
    out = [build_exercise(r) for r in roots]
    print(json.dumps(out, ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
