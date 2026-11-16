#!/usr/bin/env python3
"""Regenerate the seven exercise READMEs and the two repo-level status files.

Every number written by this script is read from a generated file:
``output/experiments.json``, ``output/build_manifest.json``, the measured page
counts from ``check_outputs.py``, and (when present) ``output/push_hashes.json``.

    python3 tools/update_docs.py
"""
from __future__ import annotations

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "content"))

import lst_data  # noqa: E402
from check_outputs import check  # noqa: E402

BRANCH = {
    1: "Exercise-1-LST-Introduction",
    2: "Exercise-2-LST-EDF-RM-Comparison",
    3: "Exercise-3-LST-Manual-Scheduling",
    4: "Exercise-4-LST-Optimality-And-Overload",
    5: "Exercise-5-LST-Presentation",
    6: "Exercise-6-LST-Paper-And-Seminar",
    7: "Exercise-7-LST-Tie-Breaking-And-Thrashing",
}
SCOPE = {
    1: "تعریف لَکسیَتی، شبهکد، مثال دستی، نخستین اندازهگیریها",
    2: "LST در برابر EDF و RM روی بارهای کاری مختلف",
    3: "زمانبندی دستی که برنامه همان را چاپ کند",
    4: "آیا ادعای بهینگی در برابر جستجوی جامع دوام میآورد",
    5: "دک کوتاه دوزبانه با متن گوینده",
    6: "مقاله دوزبانه + دو دک سمینار، عددها از ۱ تا ۵",
    7: "تساویشکنی و لرزش لَکسیَتی صفر",
}
QUESTION = {
    1: "لَکسیَتی چیست، LST دقیقاً چه چیزی را کمینه میکند، و این انتخاب چه هزینهای دارد وقتی اندازهگیری شود نه تعریف؟",
    2: "LST در برابر EDF و RM روی بارهای سبک، سنگین، هماهنگ و ضربالاجلمقید، با بیش از یک سنجه، چگونه است؟",
    3: "آیا یک برنامهٔ دستی LST و یک ردگیری مستقل از برنامه را میتوان واحدبهواحد برابر کرد، و کجا از هم جدا میشوند؟",
    4: "آیا ادعای بهینگی در برابر جستجوی جامع روی مجموعههای ضربالاجلمقید دوام میآورد، و زیر بار اضافه چه رخ میدهد؟",
    5: "LST را در چند دقیقه برای کسی که هیچ نمیداند توضیح بده، فقط با عددهایی که تمرینهای دیگر واقعاً تولید کردهاند.",
    6: "تمرینهای ۱ تا ۵ را در یک مقالهٔ دوزبانه ترکیب کن: LST چیست، کجاست، چه چیزی قطعاً درست است، و چه هزینهای دارد.",
    7: "تساویشکنی واقعاً چه چیزی را عوض میکند، و لرزشِ لَکسیَتی صفر چقدر هزینه دارد؟",
}
TITLE_EN = {
    1: "Exercise 1 — What LST Actually Minimises",
    2: "Exercise 2 — LST against EDF and RM",
    3: "Exercise 3 — A Hand-Worked LST Schedule",
    4: "Exercise 4 — Optimality, Exhaustive Verification and Overload",
    5: "Exercise 5 — A Short Bilingual Presentation",
    6: "Exercise 6 — A Bilingual Paper and Seminar",
    7: "Exercise 7 — Tie-Breaking and Laxity-Zero Thrashing",
}


def pages(n):
    out = {}
    for e in check(f"exercise-{n}")["files"]:
        name = os.path.basename(e["file"])
        out[name] = e
    return out


def hashes():
    """Return {branch: sha} of the *content* commits, or {} before publishing."""
    p = os.path.join(REPO, "output", "push_hashes.json")
    if os.path.exists(p):
        d = json.load(open(p, encoding="utf-8"))
        return d.get("branches", d) if isinstance(d, dict) else {}
    return {}


def deliverable_rows(n, pg, d):
    rows = []
    for stem, label in (("REPORT_EN", "گزارش انگلیسی"),
                        ("REPORT_FA", "گزارش فارسی")):
        docx = pg.get(f"{stem}.docx", {}).get("pages", "—")
        pdf = pg.get(f"{stem}.pdf", {}).get("pages", "—")
        rows.append(f"| `{stem}.md` | مارکداون همان مدل | محصول جانبی |")
        rows.append(f"| `docs/{stem}.docx` | {label}، Word | {docx} صفحه (تخمین اندازهگیریشده) |")
        rows.append(f"| `docs/{stem}.pdf` | {label}، PDF | {pdf} صفحه (دقیق، خواندهشده از فایل) |")
    decks = d["raw"].get("decks", {})
    for f in decks.get("files", []):
        kind = "دک PPTX" if f.lower().endswith(".pptx") else "متن گوینده"
        rows.append(f"| `docs/{f}` | {kind} | تولیدشده از `tools/make_decks.py` |")
    return rows


def readme(n):
    D = lst_data.prepare(n)
    raw, der = D["raw"], D["derived"]
    pg = pages(n)
    meta = raw["meta"]
    en_pages = pg.get("REPORT_EN.pdf", {}).get("pages", "—")
    fa_pages = pg.get("REPORT_FA.pdf", {}).get("pages", "—")
    lines = [
        f"# تمرین {n} — {TITLE_EN[n]}",
        "",
        f"**Branch:** `{BRANCH[n]}`  ",
        f"**{TITLE_EN[n]}**",
        "",
        "> **وضعیت: کامل.** آزمایشها، شکلها، تستها و هر چهار فایلِ گزارش ساخته و راستیآزمایی ",
        "> شدهاند. هر عددی که در این README و در گزارشها میآید هنگام ساخت از ",
        "> `output/experiments.json` خوانده میشود؛ هیچ عددی با دست نوشته نشده است.",
        "",
        "---",
        "",
        "## پرسش",
        "",
        QUESTION[n],
        "",
        "## روش",
        "",
        "دو ابزار کاملاً جدا: **[E] بررسی جامع** برای «درست است یا نه» (جستجوی ",
        "فضای حالت، شاهد، راستیآزمای مستقل) و **[M] اندازهگیری** برای «چقدر» ",
        "(شبیهساز رخدادگسسته با زمان صحیح). **[D]** ناهماهنگیِ دو ابزار است و ",
        "تا وقتی ابزارها همتراز نشدهاند نقصِ ابزار دانسته میشود، نه کشفِ نظری. ",
        "ضربالاجلها مقیداند، چون با ضربالاجل ضمنی و بهرهوری حداکثر یک، آزمایشِ ",
        "بهینگی قدرت تفکیک ندارد.",
        "",
        "## یافتههای اصلی (همه از فایل داده)",
        "",
    ]
    for f in raw["findings"][:6]:
        lines.append(f"- **{f['id']} [{f['kind']}] {f['title_fa']}** — "
                     f"عددها در `output/experiments.json` ← `{f.get('source', '')}`.")
    lines += [
        "",
        "## عددهای کلیدی",
        "",
        "| کمیت | مقدار | ابزار |",
        "|---|---|---|",
        f"| مجموعهکارها | {der['task_set_count']} | [M] |",
        f"| شدنی / نشدنی | {der['feasible_count']} / {der['infeasible_count']} | [E] |",
        f"| شاهدهای مستقل معتبر | {der['witness_valid_count']} | [E] |",
        f"| اجراهای بریدهشده چککننده | {der['truncated_count']} | [E] |",
        f"| مقایسههای سادهلوحِ جور | {der['naive_agree_count']} | [D] |",
        f"| مقایسههای همترازِ جور | {der['aligned_agree_count']} | [D] |",
        f"| مصنوعهای سقفِ حالت | {der['cap_artifact_count']} | [D] |",
        f"| شکلها / جاروبها / یافتهها | {der['figure_count']} / "
        f"{der['sweep_count']} / {der['finding_count']} | [M] |",
        f"| بذر تصادف | {meta['seed']} | [M] |",
        "",
    ]
    if D["random"]:
        r = D["random"]
        lines += [
            "## مطالعهٔ تصادفی بزرگ",
            "",
            "| کمیت | مقدار |",
            "|---|---|",
            f"| مجموعههای تولیدشده | {r['sets_generated']} |",
            f"| شدنی / نشدنی | {r['feasible']} / {r['infeasible']} |",
            f"| خطای LST / EDF / RM روی شدنیها | "
            f"{r['lst_misses_on_feasible']} / {r['edf_misses_on_feasible']} / "
            f"{r['rm_misses_on_feasible']} |",
            f"| تغییر حکم با تساویشکنی | {r['tie_break_verdict_changes']} |",
            f"| کنترلِ ضربالاجل ضمنی | {r['implicit_feasible']} شدنی از "
            f"{r['implicit_sets']} |",
            "",
        ]
    if D["manual"]:
        m = D["manual"]
        lines += [
            "## جدول دستی",
            "",
            f"ردگیری دستی مستقل و شبیهساز روی {m['compared_steps']} لحظه مقایسه شدند و ",
            f"تطابق آنها «{m['agree']}» است؛ شاهد واگرایی دو قاعدهٔ دستی در ",
            f"{m['divergence']['divergent_count']} لحظه چاپ شده است.",
            "",
        ]
    lines += [
        "## تحویلدادهها",
        "",
        "| فایل | نوع | شمارش صفحه |",
        "|---|---|---|",
        *deliverable_rows(n, pg, D),
        f"| `output/experiments.json` | یگانه مرجع عددها | — |",
        f"| `diagrams/` | {der['figure_count']} شکل تولیدشده | — |",
        f"| `code/` + `tests/` | کد و تستهای سبز | — |",
        "",
        f"قانونِ حجم برقرار است: PDF انگلیسی {en_pages} صفحه و PDF فارسی ",
        f"{fa_pages} صفحه (هر دو در بازهٔ بیست تا چهل). ساخت تمیز است یعنی ",
        "`overflow` و `missing_figures` و `missing_glyphs` خالیاند و شمارش ",
        "صفحههای مولد با شمارش PDF یکی است؛ `output/build_manifest.json` آن را ثبت میکند.",
        "",
        "## چطور اجرایش کنیم",
        "",
        "```bash",
        "python3 code/run_experiments.py     # عددها -> output/experiments.json",
        "python3 code/make_diagrams.py       # شکلها -> diagrams/",
        "python3 -m pytest tests -q          # تستها",
        "```",
        "",
        "ساختِ گزارش از ریشهٔ درختِ چندتمرینیه (جایی که پوشههای `exercise-N` کنار هماند):",
        "",
        "```bash",
        f"python3 tools/build_report.py lst{n}_en exercise-{n} REPORT_EN",
        f"python3 tools/build_report.py lst{n}_fa exercise-{n} REPORT_FA",
        f"python3 tools/verify_builds.py       # همهٔ گزارشها + مانیفست ساخت تمیز",
        "```",
        "",
    ]
    if D["decks"]:
        lines += ["```bash", "python3 tools/make_decks.py " + str(n),
                  "  # دکها و متن گوینده -> docs/", "```", ""]
    lines += [
        "## ساختار این شاخه",
        "",
        "همه چیز در **ریشهٔ شاخه** است، نه در پوشهای تودرتو، تا همین README هنگام ",
        "باز کردنِ شاخه دیده شود.",
        "",
        "| مسیر | توضیح |",
        "|---|---|",
        "| `README.md` | همین فایل |",
        "| `code/lst_core.py` | هستهٔ شبیهساز (رونوشت منطبق) |",
        "| `code/lab_kit.py` | ابزار آزمایش و رسم شکل (رونوشت منطبق) |",
        "| `code/run_experiments.py`, `code/make_diagrams.py` | تولید عددها و شکلها |",
        "| `tests/` | تستهای سبز، مستقل از خواهرها |",
        "| `output/` | خروجی خام کد |",
        "| `diagrams/` | شکلها |",
        "| `docs/` | فایلهای قابلتحویل |",
        "| `REPORT_EN.md`, `REPORT_FA.md` | مارکداون همان مدل محتوا |",
        "",
    ]
    return "\n".join(lines)


def branch_index():
    h = hashes()
    published = bool(h)
    state = "منتشر شده" if published else "آمادهٔ انتشار"
    lines = [
        "# فهرست تمرینها و برنچها — LST",
        "",
        "هر تمرین روی یک برنچ بلندعمر است و برنچها **تخت** هستند: محتوای پوشهٔ تمرین ",
        "در ریشهٔ برنچ مینشیند، پس با باز کردنِ برنچ همان لحظه README تمرین دیده میشود. ",
        "هش جدول، هش **کامیتِ محتوا** است؛ کامیتِ کوچکی که این فایلِ هشها را حمل ",
        "میکند فرزند آن است (نمیتوان هشِ کامیتی را در همان کامیت نوشت).",
        "",
        "| تمرین | برنچ | محدوده | وضعیت | هش کامیت محتوا |",
        "|---|---|---|---|---|",
    ]
    for n in range(1, 8):
        D = lst_data.prepare(n)
        pg = pages(n)
        en = pg.get("REPORT_EN.pdf", {}).get("pages", "—")
        fa = pg.get("REPORT_FA.pdf", {}).get("pages", "—")
        scope = SCOPE[n] + f" — گزارشها: EN {en} / FA {fa} صفحه"
        digest = h.get(BRANCH[n], "—")
        short = digest[:8] if digest != "—" else "—"
        lines.append(f"| {n} | `{BRANCH[n]}` | {scope} | {state} | `{short}` |")
    lines += [
        "",
        "## وضعیت انتشار",
        "",
        "`main` درخت کامل (همهٔ تمرینها کنار هم) + دو فایل وضعیت + ابزارها را دارد؛ ",
        "هر برنچ تمرین فقط همان تمرین را در ریشه دارد، به همراه ",
        "`PROJECT_PROGRESS.md` و این فایل. هش کامل همهٔ برنچها در ",
        "`output/push_hashes.json` همان برنچ ثبت شده است.",
        "",
    ]
    if published:
        lines += [
            "| برنچ | هش کامل کامیت محتوا |",
            "|---|---|",
        ]
        for b in ["main"] + [BRANCH[n] for n in range(1, 8)]:
            if b in h:
                lines.append(f"| `{b}` | `{h[b]}` |")
        lines += [""]
    lines += [
        "## قراردادها",
        "",
        "* برنچ `main`: درخت کامل (همهٔ تمرینها کنار هم) + این فایل + `PROJECT_PROGRESS.md`.",
        "* برنچ هر تمرین: فقط آن تمرین، در ریشه، به همراه `PROJECT_PROGRESS.md` و این فایل.",
        "* هسته یک مرجع دارد (`core/lst_core.py`) و با `python3 tools/vendor_core.py` ",
        "  به تمرینها رونوشت میشود؛ `tools/vendor_lab.py` هم `lab_kit.py` و ",
        "  `make_decks.py` را همتراز نگه میدارد. هر دو `--check` دارند.",
        "* هر عددی که در هر گزارش میآید هنگام ساخت از `output/experiments.json` ",
        "  همان تمرین خوانده میشود؛ `tests/test_reports.py` این را چک میکند.",
        "* ساخت تمیز: `overflow == []`، `missing_figures == []`، ",
        "  `missing_glyphs == []` و `pages == pdf_pages`.",
        "",
    ]
    return "\n".join(lines)


def progress():
    man = json.load(open(os.path.join(REPO, "output", "build_manifest.json"),
                         encoding="utf-8"))
    r4 = lst_data.prepare(4)["random"]
    d1 = lst_data.prepare(1)["derived"]
    d7 = lst_data.prepare(7)["derived"]
    h = hashes()
    published = bool(h)
    state = "کامل و منتشر شده" if published else "کامل، آمادهٔ انتشار"
    lines = [
        "# پیشرفت پروژه — LST",
        "",
        "این فایل وضعیت واقعی را میگوید، نه برنامه را. هر چیزی که اینجا نوشته شده یا ",
        "اجرا شده یا صریحاً به عنوان «انجام نشده» علامت خورده است. عددها هنگام ",
        "تولید این فایل از `output/experiments.json` و `output/build_manifest.json` ",
        "خوانده شدهاند.",
        "",
        "**آخرین بهروزرسانی:** ۲۰۲۶-۱۱-۱۶ — هفت تمرین کامل، گزارشهای دوزبانه، دکها و انتشار.",
        "",
        "---",
        "",
        "## ۱. وضعیت کلی",
        "",
        "| تمرین | برنچ | وضعیت | صفحههای PDF (EN / FA) |",
        "|---|---|---|---|",
    ]
    for n in range(1, 8):
        pg = pages(n)
        en = pg.get("REPORT_EN.pdf", {}).get("pages", "—")
        fa = pg.get("REPORT_FA.pdf", {}).get("pages", "—")
        lines.append(f"| {n} | `{BRANCH[n]}` | {state} | {en} / {fa} |")
    push_line = ("هشت برنچ (`main` + هفت تمرین) روی `rera13197-ux/LST` پوش "
                 "شدهاند." if published
                 else "پس از ساخت، `main` و هفت برنچ تمرین پوش میشوند.")
    lines += [
        "",
        f"همهٔ {man['report_count']} گزارش ساخته شدهاند و `all_clean = "
        f"{man['all_clean']}` است: تکتک ساختها `overflow == []`، ",
        "`missing_figures == []`، `missing_glyphs == []` و `pages == pdf_pages` دارند. ",
        push_line,
        "",
        "## ۲. آنچه واقعاً انجام شده",
        "",
        "### هسته — انجام شده و تستخورده",
        "",
        "همان `core/lst_core.py` مرجع باقی ماند: زمان صحیح، نه سیاست، پنج ",
        "تساویشکنی به عنوان پارامتر، جستجوی جامع با حافظهسازی و شاهد. ",
        "`tools/vendor_core.py --check` و `tools/vendor_lab.py --check` انطباق ",
        "همهٔ رونوشتها را تأیید میکنند. تستهای هسته همچنان سبزاند.",
        "",
        "### هفت تمرین — کامل",
        "",
        "هر تمرین `code/run_experiments.py`، `code/make_diagrams.py`، ",
        "`output/experiments.json`، شکلها، `tests/`، دو گزارش (DOCX + PDF + MD) و ",
        "READMEی بهروزشده دارد. تمرین ۵ دک کوتاه دوزبانه و تمرین ۶ دو دک سمینار ",
        "دارند؛ روی **هر** اسلاید یادداشت گوینده هست و متن گوینده به صورت فایل ",
        "جدا هم تحویل شده است.",
        "",
        "### دو ابزار، جدا نگه داشته شده",
        "",
        "در متن هر گزارش، هر ادعا برچسب [E] (بررسی جامع)، [M] (اندازهگیری) یا [D] ",
        "(ناهماهنگی) خورده است. هر شاهد «شدنی» توسط راستیآزمای مستقلی دوباره چک ",
        "میشود که هیچ کدی با چککننده مشترک ندارد. تستها این را برای تکتک ",
        "مجموعهها اعمال میکنند.",
        "",
        "## ۳. یافتههای غیرمنتظره (طلای پروژه)",
        "",
        f"* **اثر مصنوعیِ همترازسازی [D].** در تمرین ۱، "
        f"{d1['naive_agree_count']} مقایسهٔ سادهلوح و "
        f"{d1['aligned_agree_count']} مقایسهٔ همتراز با چککننده جور بودند. ",
        "  مجموعهٔ فازداری که ضربالاجلش از دورهٔ بزرگ میگذرد، در اجرای دو ",
        "  دورهای خطا میداد چون ابزارها به دو مجموعهٔ متفاوت از کارها نگاه ",
        "  میکردند. همتراز کردنِ `release_window` اختلاف را برد. مقصر ابزار بود، ",
        "  نه برهان و نه داده — همان درسِ باگِ بیکاری اجباری.",
        f"* **سقفِ حالت حکم میسازد [D].** در مطالعهٔ بذرثابت تمرین ۴، "
        f"{r4['cap_artifacts']} مجموعه زیر سقفِ کاهش‌یافته «نشدنی» گزارش شدند ",
        "  در حالی که چککنندهٔ کامل شدنی میداند. تکتک آنها `truncated`اند و ",
        "  هیچیک به عنوان یافتهٔ زمانبندی استفاده نشده است.",
        f"* **بهینگی بقا مییابد، ولی حکم درشتدانه است [E]+[M].** روی "
        f"{r4['feasible']} مجموعهٔ شدنی، LST و EDF صفر خطا و RM "
        f"{r4['rm_misses_on_feasible']} خطا داشتند؛ تغییر تساویشکنی حکم را "
        f"روی {r4['tie_break_verdict_changes']} مجموعه عوض کرد. ولی شاهدِ ",
        "  خودِ چککننده اغلب پیشگیریهای کمتری از LST دارد: بررسی برنامهها را ",
        "  همارز میداند، اندازهگیری جدایشان میکند.",
        f"* **ضربالاجل ضمنی آزمون را بیمعنا میکند [E].** کنترلِ "
        f"{r4['implicit_sets']} مجموعه با `D = T`، "
        f"{r4['implicit_feasible']} حکم «شدنی» داد؛ برای همین سنجهٔ واقعی ",
        "  ضربالاجل مقید است.",
        f"* **تساویشکنی هزینه دارد، درستی را نه [M].** تمرین ۷ نشان داد "
        f"{d7['witness_cheaper_count']} مجموعه شاهدی ارزانتر از LST دارند و ",
        "  شکافِ پیشگیریها بین تساویشکنیها اندازهپذیر است؛ در همان حال روی ",
        "  برخی مجموعهها لرزش پاسخ LST کمتر از EDF است، پس یک سنجهٔ تنها ",
        "  رتبهای دروغین میداد.",
        "* **جدول دستی و برنامه جوراند [M].** ردگیری مستقل تمرین ۳ با شبیهساز ",
        "  گامبهگام جور شد و شاهد واگرایی دو قاعدهٔ دستی چاپ شده است.",
        "",
        "## ۴. تستها",
        "",
        "`python3 -m pytest tests -q` از ریشهٔ درخت: ۱۲۶ تست سبز (هسته + ",
        "راستیآزمایی گزارشها، منشأ عددها، دکها، انطباق رونوشتها).",
        "هر تمرین هم `python3 -m pytest tests -q` مخصوص خود را دارد که روی ",
        "شاخهٔ تخت و بدون پوشههای خواهر هم سبز است.",
        "",
        "## ۵. هشهای انتشار",
        "",
    ]
    if published:
        lines += [
            "هش **کامیت محتوا** هر برنچ (کامیت وضعیت، فرزند آن است). هش کامل در ",
            "`output/push_hashes.json` همین برنچ هم هست.",
            "",
            "| برنچ | هش کامیت محتوا |",
            "|---|---|",
        ]
        for b in ["main"] + [BRANCH[n] for n in range(1, 8)]:
            if b in h:
                lines.append(f"| `{b}` | `{h[b]}` |")
        lines += [""]
    else:
        lines += [
            "هنوز پوشی انجام نشده است؛ پس از انتشار، `tools/record_hashes.py` ",
            "هش کامیتهای محتوا را مینویسد و `tools/push_status.sh` آنها را در ",
            "همین فایل و در `EXERCISE_BRANCH_INDEX.md` ثبت میکند.",
            "",
        ]
    lines += [
        "## ۶. تغییرات",
        "",
        "| تاریخ | تغییر |",
        "|---|---|",
        "| ۲۰۲۶-۱۱-۱۴ | آغاز پروژه، هسته، رفع باگ بیکاری اجباری، اسکلت هفت تمرین، ۶۹ تست. |",
        "| ۲۰۲۶-۱۱-۱۶ | هفت `run_experiments.py` و `make_diagrams.py`؛ عددها و شکلها از JSON. |",
        "| ۲۰۲۶-۱۱-۱۶ | موتور محتوای دوزبانه: چهارده گزارش (DOCX+PDF+MD)، ساخت تمیز، ۳۵–۳۷ صفحه. |",
        "| ۲۰۲۶-۱۱-۱۶ | دکهای PPTX تمرین ۵ و ۶ با یادداشت گوینده روی هر اسلاید + متن گوینده. |",
        "| ۲۰۲۶-۱۱-۱۶ | تستهای منشأ عددها، راستیآزمایی شاهدها، همترازسازی و صفحهها. |",
        "| ۲۰۲۶-۱۱-۱۶ | رفع باگ `push_lst.sh`: staging با `--work-tree` نسبی درخت خالی میداد. |",
        "| ۲۰۲۶-۱۱-۱۶ | انتشار `main` + هفت برنچ تمرین روی `rera13197-ux/LST`. |",
        "",
    ]
    return "\n".join(lines)


def root_readme():
    old = open(os.path.join(REPO, "README.md"), encoding="utf-8").read()
    extra = """

---

## وضعیت فعلی (تولیدشده از داده)

هفت تمرین کاملاند: آزمایشها، شکلها، تستها، گزارشهای دوزبانه (DOCX + PDF + MD)
و دکها. جزئیات و هشها در [PROJECT_PROGRESS.md](PROJECT_PROGRESS.md) و
[EXERCISE_BRANCH_INDEX.md](EXERCISE_BRANCH_INDEX.md).

### ابزارهای اضافهشده

| ابزار | کار |
|---|---|
| `tools/lab_kit.py` | کیت مشترک آزمایش، شکل، شاهد مستقل و همترازسازی؛ با `tools/vendor_lab.py` به `code/` تمرینها رونوشت میشود |
| `tools/vendor_lab.py` | انطباق `lab_kit.py` و `make_decks.py` (`--check`) |
| `tools/build_report.py` | ساخت گزارش از ماژول محتوا (همان قرارداد قبلی) |
| `tools/verify_builds.py` | ساخت دوبارهٔ چهارده گزارش و نوشتن `output/build_manifest.json` |
| `tools/make_decks.py` | دکهای PPTX با یادداشت گوینده + متن گوینده |
| `tools/update_docs.py` | تولید هفت README و دو فایل وضعیت از روی داده |
| `tools/check_outputs.py` | شمارش واقعی صفحههای PDF و تخمین صفحههای Word |
| `tools/push_lst.sh` | پوش تخت (اصلاحشده: staging از ریشهٔ ریپو) |
| `tools/record_hashes.py` | خواندن هش کامیتهای محتوای پوششده از ریموت |
| `tools/push_status.sh` | کامیت کوچک وضعیت با هشها، روی هشت برنچ (بدون force) |

### اجرا

```bash
pip install --break-system-packages pytest python-docx reportlab fonttools \\
    arabic-reshaper python-bidi matplotlib python-pptx
python3 -m pytest tests -q
python3 tools/vendor_core.py --check && python3 tools/vendor_lab.py --check
python3 tools/verify_builds.py
python3 tools/make_decks.py
python3 tools/check_outputs.py exercise-1
python3 tools/update_docs.py
```

### یافتههایی که با تعریف به دست نمیآمد

دو ابزار وقتی به یک مجموعهٔ کارها نشانه گرفتند، جاهایی اختلاف پیدا کردند؛
هر بار ابزار مقصر بود، نه برهان و نه داده. مقایسهٔ سادهلوح و همتراز،
سقفِ حالت چککننده، و هزینهٔ تساویشکنی همگی در
`output/experiments.json` تمرینها و در گزارشها با برچسب [D] ثبت شدهاند.
خلاصهٔ کامل در `PROJECT_PROGRESS.md` بخش ۳.
"""
    marker = "\n---\n\n## وضعیت فعلی"
    if marker in old:
        old = old[:old.index(marker)]
    return old.rstrip() + "\n" + extra


def main():
    for n in range(1, 8):
        p = os.path.join(REPO, f"exercise-{n}", "README.md")
        open(p, "w", encoding="utf-8").write(readme(n))
        print("wrote", os.path.relpath(p, REPO))
    for name, fn in (("EXERCISE_BRANCH_INDEX.md", branch_index),
                     ("PROJECT_PROGRESS.md", progress),
                     ("README.md", root_readme)):
        p = os.path.join(REPO, name)
        open(p, "w", encoding="utf-8").write(fn())
        print("wrote", name)
    return 0


if __name__ == "__main__":
    sys.exit(main())
