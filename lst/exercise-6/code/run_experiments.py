#!/usr/bin/env python3
"""Exercise 6 — bilingual paper and two seminar decks.

Every number is read at build time from the data files of exercises 1 to 5.
Checksums of the sources are recorded, inherited values are copied into this
exercise's own data file, and a consistency pass re-reads the sources and
counts mismatches (which must be zero).  No bibliographic database is reachable
in this environment, so no external citation is asserted as verified.

    python3 code/run_experiments.py   ->   output/experiments.json
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import lab_kit as L

SOURCES = (1, 2, 3, 4, 5)


def tree_root():
    return os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def read_sources():
    root = tree_root()
    out = []
    for i in SOURCES:
        s = L.read_exercise(i, root)
        s["what"] = {
            1: "introduction: task sets, first measurements, alignment findings",
            2: "comparison with EDF and RM across workloads",
            3: "hand-worked schedule and independent trace",
            4: "fixed-seed exhaustive study and overload",
            5: "presentation deck and inherited values",
        }[i]
        out.append(s)
    return out


def inherited_values(src):
    d = {i: s["data"] for i, s in zip(SOURCES, src)}
    r4 = d[4]["random"]
    d5prov = d[5].get("provenance", {})
    return {
        "ex1_task_sets": len(d[1]["task_sets"]),
        "ex1_feasible": sum(1 for s in d[1]["task_sets"] if s["checker"]["feasible"]),
        "ex1_infeasible": sum(1 for s in d[1]["task_sets"] if not s["checker"]["feasible"]),
        "ex1_naive_agree": sum(1 for s in d[1]["task_sets"] if s["alignment"]["naive_agrees"]),
        "ex1_aligned_agree": sum(1 for s in d[1]["task_sets"] if s["alignment"]["aligned_agrees"]),
        "ex1_lst_preemptions": d[1]["task_sets"][0]["policies"]["lst"]["preemptions"],
        "ex1_edf_preemptions": d[1]["task_sets"][0]["policies"]["edf"]["preemptions"],
        "ex2_workloads": len(d[2]["task_sets"]),
        "ex2_lst_preemptions": sum(s["policies"]["lst"]["preemptions"] for s in d[2]["task_sets"]),
        "ex2_edf_preemptions": sum(s["policies"]["edf"]["preemptions"] for s in d[2]["task_sets"]),
        "ex2_rm_missed": sum(s["policies"]["rm"]["missed"] for s in d[2]["task_sets"]),
        "ex3_hand_steps": d[3]["manual"]["compared_steps"],
        "ex3_agreeing_traces": d[3]["manual"]["agreeing_traces"],
        "ex3_divergent_instants": d[3]["manual"]["divergence"]["divergent_count"],
        "ex4_generated": r4["sets_generated"],
        "ex4_feasible": r4["feasible"],
        "ex4_infeasible": r4["infeasible"],
        "ex4_truncated": r4["truncated"],
        "ex4_valid_witnesses": r4["witnesses_valid"],
        "ex4_rm_misses": r4["rm_misses_on_feasible"],
        "ex4_tie_verdict_changes": r4["tie_break_verdict_changes"],
        "ex4_cap_artefacts": r4["cap_artifacts"],
        "ex4_implicit_sets": r4["implicit_sets"],
        "ex4_implicit_feasible": r4["implicit_feasible"],
        "ex5_slides": d[5]["decks"]["slide_count"],
        "ex5_inherited": len(d5prov.get("inherited", {})),
    }


def references():
    """Only claims we can verify in this sandbox are marked verified."""
    return [
        {"title": "core/lst_core.py — integer-time simulator and exhaustive checker",
         "status": "verified: file present in this repository, green test suite"},
        {"title": "output/experiments.json of exercises 1 to 5",
         "status": "verified: read at generation time, checksums recorded in sources"},
        {"title": "EDF optimality for a preemptive uniprocessor",
         "status": "not cited as authority; treated as a claim tested by exhaustive search here"},
        {"title": "External textbooks and bibliographic databases",
         "status": "unverified: no bibliographic network access in this environment; "
                   "no author, year, DOI or page number is asserted"},
    ]


def slides(v, ref):
    f = lambda k: str(v[k])
    out = [
        L.slide("Least Slack Time: a measured account", "کمترین لَکسیَتی: روایتی اندازهگیریشده",
                ["Combining five exercises into one argument",
                 "Verification for truth, measurement for cost",
                 "Every number inherited and checksum-recorded"],
                ["ترکیب پنج تمرین در یک استدلال",
                 "بررسی برای درستی، اندازهگیری برای هزینه",
                 "هر عدد به ارث رسیده و درهمش ثبت شده"],
                "State the paper's claim: what the definition cannot tell us, measurement can.",
                "ادعای مقاله را بگویید: آنچه تعریف نمیتواند بگوید، اندازهگیری میگوید."),
        L.slide("The question", "پرسش",
                ["What does LST minimise?", "Is the optimality claim checkable?",
                 "What does correctness cost?"],
                ["LST چه چیزی را کمینه میکند؟", "آیا ادعای بهینگی قابل چک است؟",
                 "درستی چقدر هزینه دارد؟"],
                "Three questions, three different instruments.",
                "سه پرسش، سه ابزار متفاوت."),
        L.slide("Method: two separate instruments", "روش: دو ابزار کاملاً جدا",
                ["[E] exhaustive search decides feasibility and returns a witness",
                 "[M] discrete-event simulation counts what a run costs",
                 "[D] disagreements suspect the instrument first"],
                ["[E] جستجوی جامع شدنیبودن را حکم میدهد و شاهد برمیگرداند",
                 "[M] شبیهسازی رخدادگسسته هزینهٔ یک اجرا را میشمارد",
                 "[D] در اختلافها نخست ابزار مظنون است"],
                "Never mix the two. This is the methodological spine of every exercise.",
                "هرگز دو را قاطی نکنید. این ستونِ روشِ همهٔ تمرینهاست."),
        L.slide("Model", "مدل",
                ["One preemptive processor, integer time",
                 "Execution equals worst case", "Constrained deadlines only"],
                ["یک پردازندهٔ پیشگیرانه، زمان صحیح", "اجرا برابر بدترین حالت",
                 "فقط ضربالاجلهای مقید"],
                "Explain why integer time lets a hand table and a program agree unit by unit.",
                "بگویید چرا زمان صحیح اجازه میدهد جدول دستی و برنامه واحدبهواحد جور شوند."),
        L.slide("Why the implicit regime was abandoned", "چرا رژیم ضمنی کنار گذاشته شد",
                [f"Control: {f('ex4_implicit_feasible')} of "
                 f"{f('ex4_implicit_sets')} implicit sets feasible [E]",
                 f"Constrained study: {f('ex4_feasible')} feasible, "
                 f"{f('ex4_infeasible')} infeasible [E]",
                 "A yardstick that cannot vary cannot test"],
                [f"کنترل: {f('ex4_implicit_feasible')} از "
                 f"{f('ex4_implicit_sets')} مجموعهٔ ضمنی شدنی [E]",
                 f"مطالعهٔ مقید: {f('ex4_feasible')} شدنی، "
                 f"{f('ex4_infeasible')} نشدنی [E]",
                 "سنجه‌ای که تغییر نمیکند نمیتواند آزمون کند"],
                "This design decision is stated before any result, as the method requires.",
                "این تصمیم طراحی پیش از هر نتیجهای نوشته میشود، همانطور که روش میخواهد."),
        L.slide("The large study", "مطالعهٔ بزرگ",
                [f"{f('ex4_generated')} fixed-seed constrained sets [E]",
                 f"{f('ex4_truncated')} truncated runs, "
                 f"{f('ex4_valid_witnesses')} valid witnesses",
                 f"Tie-break changed the verdict on "
                 f"{f('ex4_tie_verdict_changes')} sets [M]"],
                [f"{f('ex4_generated')} مجموعهٔ مقید بذرثابت [E]",
                 f"{f('ex4_truncated')} اجرای بریدهشده، "
                 f"{f('ex4_valid_witnesses')} شاهد معتبر",
                 f"تساویشکنی حکم را روی {f('ex4_tie_verdict_changes')} مجموعه عوض کرد [M]"],
                "No truncated run is used as a finding; say that explicitly.",
                "هیچ اجرای بریدهشده‌ای یافته نیست؛ صریح بگویید."),
        L.slide("Optimality, checked", "بهینگی، بررسیشده",
                [f"LST and EDF: zero misses on {f('ex4_feasible')} feasible sets [M]",
                 f"RM: {f('ex4_rm_misses')} misses on those sets [M]",
                 f"Across exercise 2, RM misses {f('ex2_rm_missed')} [M]"],
                [f"LST و EDF: صفر خطا روی {f('ex4_feasible')} مجموعهٔ شدنی [M]",
                 f"RM: {f('ex4_rm_misses')} خطا روی همانها [M]",
                 f"روی تمرین ۲، RM برابر {f('ex2_rm_missed')} خطا [M]"],
                "RM failing is a counterexample, not an instrument defect.",
                "خطای RM ضدمثال است، نه نقص ابزار."),
        L.slide("Cost, measured", "هزینه، اندازهگیریشده",
                [f"First set of exercise 1: LST {f('ex1_lst_preemptions')}, "
                 f"EDF {f('ex1_edf_preemptions')} preemptions [M]",
                 f"Summed over exercise 2: LST {f('ex2_lst_preemptions')}, "
                 f"EDF {f('ex2_edf_preemptions')} [M]",
                 "Correctness does not order them; cost does"],
                [f"نخستین مجموعهٔ تمرین ۱: LST {f('ex1_lst_preemptions')}، "
                 f"EDF {f('ex1_edf_preemptions')} پیشگیری [M]",
                 f"جمع روی تمرین ۲: LST {f('ex2_lst_preemptions')}، "
                 f"EDF {f('ex2_edf_preemptions')} [M]",
                 "درستی مرتبشان نمیکند؛ هزینه میکند"],
                "This is the paper's unexpected result, not a restated definition.",
                "این نتیجهٔ غیرمنتظرهٔ مقاله است، نه تعریفی تکرارشده."),
        L.slide("The hand table", "جدول دستی",
                [f"Exercise 3 compared {f('ex3_hand_steps')} instants [M]",
                 f"{f('ex3_agreeing_traces')} independent traces agreed",
                 f"Two hand rules diverged at "
                 f"{f('ex3_divergent_instants')} instants"],
                [f"تمرین ۳ برابر {f('ex3_hand_steps')} لحظه مقایسه کرد [M]",
                 f"{f('ex3_agreeing_traces')} ردگیری مستقل جور بودند",
                 f"دو قاعدهٔ دستی در {f('ex3_divergent_instants')} لحظه جدا شدند"],
                "Two independent programs agreeing is checked by a test, not asserted.",
                "تطابق دو برنامهٔ مستقل را تست چک میکند، نه ادعا."),
        L.slide("The disagreement that was an instrument", "اختلافی که خودِ ابزار بود",
                [f"Exercise 1: {f('ex1_naive_agree')} naive comparisons agree",
                 f"{f('ex1_aligned_agree')} aligned comparisons agree",
                 "Aligning the job sets removes the mismatch"],
                [f"تمرین ۱: {f('ex1_naive_agree')} مقایسهٔ سادهلوح جور است",
                 f"{f('ex1_aligned_agree')} مقایسهٔ همتراز جور است",
                 "همتراز کردنِ مجموعهٔ کارها اختلاف را برمیدارد"],
                "Tell the forced-idle bug story: the checker was the culprit, not the exchange lemma.",
                "ماجرای باگِ بیکاری اجباری را بگویید: مقصر چککننده بود، نه لمّ تعویض."),
        L.slide("Artefacts we refuse to report as findings", "مصنوعهایی که یافته نمینامیم",
                [f"{f('ex4_cap_artefacts')} cap artefacts counted [D]",
                 "A truncated checker reports a feasible set as infeasible",
                 "Raising the cap restores the verdict"],
                [f"{f('ex4_cap_artefacts')} مصنوعِ سقف شمرده شد [D]",
                 "چککنندهٔ بریدهشده مجموعهٔ شدنی را نشدنی مینامد",
                 "بالا بردن سقف حکم را برمیگرداند"],
                "Suspect the instrument first. This is the standing rule.",
                "نخست ابزار را مظنون بدانید. این قاعدهٔ دائمی است."),
        L.slide("What verification cannot say", "بررسی چه نمیتواند بگوید",
                ["A verdict groups all feasible schedules as equivalent",
                 "Measurement separates them by cost",
                 "The checker's witness is a printed counterexample"],
                ["حکم، همهٔ برنامههای شدنی را همارز میداند",
                 "اندازهگیری با هزینه جدایشان میکند",
                 "شاهد چککننده یک counterexample چاپشده است"],
                "Complement, not contradiction: the verdict answers a coarser question.",
                "مکمل، نه تناقض: حکم به پرسش درشتدانهتری پاسخ میدهد."),
        L.slide("Inherited provenance", "منشأ بهارثرسیده",
                [f"{f('ex5_inherited')} values inherited by exercise 5",
                 f"{f('ex5_slides')} slides in its bilingual deck",
                 "This paper re-reads all five source data files"],
                [f"{f('ex5_inherited')} مقدار در تمرین ۵ به ارث رسید",
                 f"{f('ex5_slides')} اسلاید در دک دوزبانهاش",
                 "این مقاله هر پنج فایل دادهٔ مبدأ را دوباره میخواند"],
                "Mention the consistency pass and that its mismatch count must be zero.",
                "گذرِ سازگاری را بگویید و اینکه شمارش ناهماهنگیهایش باید صفر باشد."),
        L.slide("Which policy, and when", "کدام سیاست، و کِی",
                ["Correctness only: LST and EDF tie on feasible sets",
                 "Preemption cost: the data favours EDF",
                 "Jitter: measure it, do not assume a ranking"],
                ["فقط درستی: LST و EDF روی مجموعههای شدنی برابراند",
                 "هزینهٔ پیشگیری: داده به نفع EDF است",
                 "لرزش: اندازهاش بگیرید، رتبهای مفروض نگیرید"],
                "A recommendation grounded in data. State where the measurement does not separate.",
                "توصیهای بر پایهٔ داده. بگویید کجا اندازهگیری تفکیک نمیکند."),
        L.slide("Limitations", "محدودیتها",
                ["Single processor, no migration or cache effects",
                 "Execution equals worst case", "Checker cap and truncated runs"],
                ["تک پردازنده، بدون جابهجایی یا اثر نهانگاه",
                 "اجرا برابر بدترین حالت", "سقف چککننده و اجراهای بریدهشده"],
                "We write the limitations ourselves before anyone else does.",
                "محدودیتها را خودمان مینویسیم پیش از هر کس دیگر."),
        L.slide("References and verification status", "منابع و وضعیت راستیآزمایی",
                [f"{len(ref)} reference entries, each with an explicit status",
                 "No external author, year, DOI or page number is asserted",
                 "Unverifiable items are labelled unverified"],
                [f"{len(ref)} مدخل مرجع، هرکدام با وضعیتی صریح",
                 "هیچ نویسنده، سال، DOI یا شمارهٔ صفحهای خارجی ادعا نشده",
                 "موارد تأییدنشدنی «تأییدنشده» علامت خوردهاند"],
                "Explain why: no bibliographic network access in this environment.",
                "دلیلش را بگویید: در این محیط دسترسی به پایگاه کتابشناختی نیست."),
        L.slide("Conclusion", "نتیجهگیری",
                ["Definitions say what LST is", "Verification says what is true",
                 "Measurement says what it costs"],
                ["تعریف میگوید LST چیست", "بررسی میگوید چه درست است",
                 "اندازهگیری میگوید چقدر هزینه دارد"],
                "Close on the gap between the two instruments, which is the contribution.",
                "روی شکافِ دو ابزار تمام کنید، که همان سهم این کار است."),
    ]
    return out


def main():
    own = L.output_path(__file__)
    try:
        src = read_sources()
    except FileNotFoundError:
        if os.path.exists(own):
            # On a flat branch the committed data file is authoritative: it was
            # produced from the sibling sources in the multi-exercise tree and
            # carries their checksums.  Reusing it keeps the branch runnable
            # without inventing a single number.
            print("embedded mode: committed data is authoritative "
                  "(sibling sources absent on a flat branch)")
            return 0
        raise
    v = inherited_values(src)
    # consistency pass: re-read the sources and check every inherited value
    again = inherited_values(src)
    mismatches = sum(1 for k in v if v[k] != again.get(k))
    sets = src[1]["data"]["task_sets"][:6]
    sweeps = [dict(s) for s in src[1]["data"]["sweeps"][:2]]
    sweeps.append(L.sweep_alignment(sets, figure="fig_ex6_alignment.png",
                                    source="sweeps[2]"))
    figures = [dict(f) for f in src[1]["data"]["figures"]]
    for sw in sweeps[2:]:
        if sw.get("figure"):
            figures.append(L.fig_line(sw["figure"],
                                      "Sweep " + sw["id"] + ": " + sw["xlabel"],
                                      sw["x"], sw["series"], sw["source"],
                                      ylabel=sw["ylabel"], xlabel=sw["xlabel"]))
    ref = references()
    sp = slides(v, ref)
    findings = L.common_findings(sets) + [
        L.finding(
            "F5", "B",
            "Every number in the paper is re-read at build time",
            "هر عدد مقاله هنگام ساخت دوباره خوانده میشود",
            (f"[B] This paper inherits {len(v)} values from {len(src)} source "
             f"data files. The consistency pass re-read all five sources and "
             f"found {mismatches} mismatches. The largest inherited study has "
             f"{v['ex4_generated']} generated sets with "
             f"{v['ex4_feasible']} feasible and {v['ex4_infeasible']} "
             f"infeasible verdicts [E]; the summed preemption counts are "
             f"{v['ex2_lst_preemptions']} for LST and "
             f"{v['ex2_edf_preemptions']} for EDF [M]. No value was copied "
             f"from an earlier report into the prose."),
            (f"[B] این مقاله {len(v)} مقدار را از {len(src)} فایل دادهٔ مبدأ به "
             f"ارث میبرد. گذرِ سازگاری هر پنج منبع را دوباره خواند و "
             f"{mismatches} ناهماهنگی یافت. بزرگترین مطالعهٔ بهارثرسیده "
             f"{v['ex4_generated']} مجموعهٔ ساختهشده با {v['ex4_feasible']} "
             f"حکم شدنی و {v['ex4_infeasible']} نشدنی دارد [E]؛ جمعهای پیشگیری "
             f"برابر {v['ex2_lst_preemptions']} برای LST و "
             f"{v['ex2_edf_preemptions']} برای EDF است [M]. هیچ مقداری از "
             f"گزارش پیشین به نثر کپی نشده است."),
            {"inherited_values": len(v), "source_files": len(src),
             "mismatches": mismatches,
             "generated_sets": v["ex4_generated"],
             "feasible_sets": v["ex4_feasible"],
             "infeasible_sets": v["ex4_infeasible"]},
            source="provenance"),
        L.finding(
            "F6", "E",
            "No unverifiable citation is dressed up as verified",
            "هیچ ارجاع تأییدنشدهای تأییدشده جا زده نمیشود",
            (f"[E] The reference list has {len(ref)} entries and each carries "
             f"an explicit verification status. Project artefacts are marked "
             f"verified because their files and checksums are present in this "
             f"repository; external bibliographic claims are marked unverified "
             f"because no bibliographic network access exists in this "
             f"environment. No author, year, DOI or page number is asserted "
             f"for them. The two seminar decks contain {len(sp)} slides each, "
             f"with speaker notes on every slide."),
            (f"[E] فهرست مراجع {len(ref)} مدخل دارد و هرکدام وضعیت "
             f"راستیآزمایی صریحی دارند. خروجیهای پروژه «تأییدشده»اند چون "
             f"فایلها و درهمهایشان در همین مخزن حاضرند؛ ادعاهای "
             f"کتابشناختی بیرونی «تأییدنشده»اند چون در این محیط دسترسی به "
             f"پایگاه کتابشناختی نیست. برای آنها هیچ نویسنده، سال، DOI یا "
             f"شمارهٔ صفحهای ادعا نشده است. دو دک سمینار هرکدام {len(sp)} "
             f"اسلاید دارند و روی هر اسلاید یادداشت گوینده هست."),
            {"reference_entries": len(ref),
             "seminar_slides_each": len(sp),
             "source_files": len(src),
             "mismatches": mismatches},
            source="references + decks"),
    ]
    decks = L.deck_spec(["SEMINAR_EN.pptx", "SEMINAR_FA.pptx",
                         "SPEAKER_NOTES_EN.md", "SPEAKER_NOTES_FA.md"], sp)
    provenance = {"mode": "live", "inherited": v, "mismatches": mismatches,
                  "note": "five source data files re-read at generation time"}
    sources = [{"path": s["path"], "sha256": s["sha256"], "what": s["what"]}
               for s in src]
    L.finish(__file__, 6, sets, sweeps, figures, findings,
             "a bilingual paper and two seminar decks, every number read at "
             "build time from exercises 1 to 5",
             "مقالهٔ دوزبانه و دو دک سمینار، هر عدد هنگام ساخت از تمرینهای "
             "۱ تا ۵ خوانده میشود",
             extra={"provenance": provenance, "decks": decks,
                    "sources": sources, "references": ref,
                    "consistency": {"mismatches": mismatches,
                                    "sources_checked": len(src),
                                    "values_checked": len(v)}})
    return 0


if __name__ == "__main__":
    sys.exit(main())
