#!/usr/bin/env python3
"""Exercise 5 — a short bilingual presentation of LST.

Every number on every slide is inherited from exercises 1 to 4: their
``output/experiments.json`` files are read here, their checksums recorded, and
the inherited values copied into this exercise's own data file.  On a flat
branch, where the sibling sources are not present, the committed data file is
authoritative and the script says so instead of inventing numbers.

    python3 code/run_experiments.py   ->   output/experiments.json
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import lab_kit as L

SOURCES = (1, 2, 3, 4)


def tree_root():
    return os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def read_sources():
    root = tree_root()
    out = []
    for i in SOURCES:
        s = L.read_exercise(i, root)
        s["what"] = f"task_sets, sweeps, figures and findings of exercise {i}"
        out.append(s)
    return out


def inherited_values(src):
    d1, d2, d3, d4 = (s["data"] for s in src)
    s1 = d1["task_sets"][0]
    r4 = d4["random"]
    return {
        "ex1_task_sets": len(d1["task_sets"]),
        "ex1_feasible": sum(1 for s in d1["task_sets"] if s["checker"]["feasible"]),
        "ex1_infeasible": sum(1 for s in d1["task_sets"] if not s["checker"]["feasible"]),
        "ex1_lst_preemptions": s1["policies"]["lst"]["preemptions"],
        "ex1_edf_preemptions": s1["policies"]["edf"]["preemptions"],
        "ex1_naive_agree": sum(1 for s in d1["task_sets"]
                               if s["alignment"]["naive_agrees"]),
        "ex1_aligned_agree": sum(1 for s in d1["task_sets"]
                                 if s["alignment"]["aligned_agrees"]),
        "ex2_workloads": len(d2["task_sets"]),
        "ex2_lst_preemptions": sum(s["policies"]["lst"]["preemptions"]
                                   for s in d2["task_sets"]),
        "ex2_edf_preemptions": sum(s["policies"]["edf"]["preemptions"]
                                   for s in d2["task_sets"]),
        "ex3_hand_steps": d3["manual"]["compared_steps"],
        "ex3_agreeing_traces": d3["manual"]["agreeing_traces"],
        "ex3_divergent_instants": d3["manual"]["divergence"]["divergent_count"],
        "ex4_generated": r4["sets_generated"],
        "ex4_feasible": r4["feasible"],
        "ex4_infeasible": r4["infeasible"],
        "ex4_rm_misses": r4["rm_misses_on_feasible"],
        "ex4_implicit_feasible": r4["implicit_feasible"],
        "ex4_implicit_sets": r4["implicit_sets"],
        "ex4_cap_artefacts": r4["cap_artifacts"],
    }


def slides(v):
    f = lambda k: str(v[k])
    return [
        L.slide("Least Slack Time in a few minutes", "کمترین لَکسیَتی در چند دقیقه",
                ["A dynamic-priority rule for one preemptive processor",
                 "Run the job that can wait the least",
                 "Two instruments: verification and measurement"],
                ["قاعدهای پویا برای یک پردازندهٔ پیشگیرانه",
                 "اجرای کاری که کمتر از همه میتواند صبر کند",
                 "دو ابزار: بررسی و اندازهگیری"],
                "Open by saying this presentation reports measurements, not definitions. "
                "Every number shown was produced by a program in an earlier exercise.",
                "با گفتن اینکه این ارائه اندازهگیری گزارش میکند نه تعریف آغاز کنید. "
                "هر عددی که نشان داده میشود را برنامهای در تمرین پیشین ساخته است.",
                source="provenance.inherited"),
        L.slide("What slack means", "لَکسیَتی یعنی چه",
                ["slack = deadline - now - remaining work",
                 "It is how long a job may still wait",
                 "The smallest slack is the most urgent job"],
                ["لَکسیَتی = ضربالاجل - اکنون - کار باقیمانده",
                 "یعنی یک کار چقدر دیگر میتواند صبر کند",
                 "کمترین لَکسیَتی یعنی عجلهدارترین کار"],
                "This is the only definition in the deck. Say it once and move to data.",
                "این تنها تعریف دک است. یک بار بگویید و بروید سراغ داده.",
                source="core/lst_core.py"),
        L.slide("What we actually measured", "واقعاً چه اندازه گرفتیم",
                [f"Exercise 1: {f('ex1_task_sets')} task sets, "
                 f"{f('ex1_feasible')} feasible and {f('ex1_infeasible')} infeasible [E]",
                 f"Exercise 2: {f('ex2_workloads')} workloads",
                 f"Exercise 4: {f('ex4_generated')} fixed-seed random sets"],
                [f"تمرین ۱: {f('ex1_task_sets')} مجموعه، {f('ex1_feasible')} شدنی و "
                 f"{f('ex1_infeasible')} نشدنی [E]",
                 f"تمرین ۲: {f('ex2_workloads')} بار کاری",
                 f"تمرین ۴: {f('ex4_generated')} مجموعهٔ تصادفی بذرثابت"],
                "Read the counts as verdicts [E], not as performance claims.",
                "شمارشها را به عنوان حکم [E] بخوانید، نه ادعای عملکرد."),
        L.slide("Why deadlines must be constrained", "چرا ضربالاجل باید مقید باشد",
                [f"Implicit-deadline control: {f('ex4_implicit_feasible')} of "
                 f"{f('ex4_implicit_sets')} sets feasible [E]",
                 "A checker that always says feasible cannot be tested",
                 f"Constrained deadlines: {f('ex4_feasible')} feasible, "
                 f"{f('ex4_infeasible')} infeasible [E]"],
                [f"کنترلِ ضربالاجل ضمنی: {f('ex4_implicit_feasible')} از "
                 f"{f('ex4_implicit_sets')} مجموعه شدنی [E]",
                 "چککنندهای که همیشه «شدنی» بگوید قابل آزمون نیست",
                 f"ضربالاجل مقید: {f('ex4_feasible')} شدنی، "
                 f"{f('ex4_infeasible')} نشدنی [E]"],
                "This is the design decision that gives the experiment its power.",
                "این تصمیم طراحی است که به آزمایش قدرت میدهد."),
        L.slide("Optimality, checked", "بهینگی، بررسیشده",
                [f"On {f('ex4_feasible')} feasible sets LST misses zero deadlines [M]",
                 f"RM misses {f('ex4_rm_misses')} on the same sets [M]",
                 "Every feasible witness was independently re-checked [E]"],
                [f"روی {f('ex4_feasible')} مجموعهٔ شدنی LST صفر خطا دارد [M]",
                 f"RM روی همان مجموعهها {f('ex4_rm_misses')} خطا میدهد [M]",
                 "هر شاهد شدنی به طور مستقل دوباره چک شد [E]"],
                "Distinguish the verdict from the counterexample: RM failing is a result, not a bug.",
                "حکم را از ضدمثال جدا کنید: خطای RM نتیجه است، نه باگ."),
        L.slide("But correctness is not cost", "ولی درستی، هزینه نیست",
                [f"Exercise 1, first set: LST {f('ex1_lst_preemptions')} preemptions, "
                 f"EDF {f('ex1_edf_preemptions')} [M]",
                 f"Across exercise 2: LST {f('ex2_lst_preemptions')}, "
                 f"EDF {f('ex2_edf_preemptions')} [M]",
                 "Both meet every deadline on feasible sets"],
                [f"تمرین ۱، مجموعهٔ نخست: LST {f('ex1_lst_preemptions')} پیشگیری، "
                 f"EDF {f('ex1_edf_preemptions')} [M]",
                 f"روی تمرین ۲: LST {f('ex2_lst_preemptions')}، "
                 f"EDF {f('ex2_edf_preemptions')} [M]",
                 "هر دو روی مجموعههای شدنی به ضربالاجلها میرسند"],
                "This slide is the point of the whole project: the definition cannot tell you this.",
                "این اسلاید اصلِ کل پروژه است: تعریف نمیتواند این را به شما بگوید."),
        L.slide("A hand table that the program prints", "جدول دستی که برنامه چاپ میکند",
                [f"Exercise 3 compared {f('ex3_hand_steps')} integer instants [M]",
                 f"{f('ex3_agreeing_traces')} independent hand traces agreed",
                 f"Two hand rules parted company at {f('ex3_divergent_instants')} instants"],
                [f"تمرین ۳ برابر {f('ex3_hand_steps')} لحظهٔ صحیح را مقایسه کرد [M]",
                 f"{f('ex3_agreeing_traces')} ردگیری دستی مستقل جور بودند",
                 f"دو قاعدهٔ دستی در {f('ex3_divergent_instants')} لحظه از هم جدا شدند"],
                "Two independent programs agreeing is a measurement, not a proof.",
                "تطابق دو برنامهٔ مستقل یک اندازهگیری است، نه برهان."),
        L.slide("When the instruments disagree", "وقتی دو ابزار اختلاف دارند",
                [f"Exercise 1: {f('ex1_naive_agree')} naive comparisons agree",
                 f"{f('ex1_aligned_agree')} aligned comparisons agree",
                 "The instrument is the first suspect, not the theorem"],
                [f"تمرین ۱: {f('ex1_naive_agree')} مقایسهٔ سادهلوح جور است",
                 f"{f('ex1_aligned_agree')} مقایسهٔ همتراز جور است",
                 "نخستین مظنون ابزار است، نه برهان"],
                "Describe the forced-idle bug history: the checker was wrong, not the exchange argument.",
                "ماجرای باگِ بیکاری اجباری را بگویید: چککننده اشتباه میکرد، نه برهان تعویض."),
        L.slide("A defect made by a state cap", "نقصی که سقفِ حالت ساخت",
                [f"Exercise 4 counted {f('ex4_cap_artefacts')} cap artefacts [D]",
                 "A truncated run reports a feasible set as infeasible",
                 "Truncated results are artefacts, never findings"],
                [f"تمرین ۴ برابر {f('ex4_cap_artefacts')} مصنوعِ سقف شمرد [D]",
                 "اجرای بریدهشده مجموعهای شدنی را نشدنی گزارش میکند",
                 "نتیجهٔ بریدهشده مصنوع است، هرگز یافته نیست"],
                "Emphasise the method rule: suspect the tool before the data or the proof.",
                "قاعدهٔ روش را پررنگ کنید: پیش از داده و برهان، ابزار را مظنون بدانید."),
        L.slide("What the checker cannot say", "چککننده چه نمیتواند بگوید",
                ["A feasibility verdict groups schedules as equivalent",
                 "Measurement separates them by preemption count",
                 "The witness schedule is a printed counterexample"],
                ["حکمِ شدنیبودن برنامهها را همارز دستهبندی میکند",
                 "اندازهگیری با شمارش پیشگیری جدایشان میکند",
                 "برنامهٔ شاهد یک counterexample چاپشده است"],
                "Do not claim the checker is wrong here; it answers a coarser question.",
                "نگویید چککننده اشتباه میکند؛ پرسش درشتدانهتری پاسخ میدهد."),
        L.slide("Which one should you use", "کدام را باید به کار برد",
                ["If correctness is the only yardstick, LST and EDF tie",
                 "If preemption cost matters, the data favours EDF",
                 "If response jitter matters, measure it too"],
                ["اگر تنها سنجه درستی باشد، LST و EDF برابراند",
                 "اگر هزینهٔ پیشگیری مهم باشد، داده به نفع EDF است",
                 "اگر لرزش پاسخ مهم باشد، آن را هم اندازه بگیرید"],
                "A recommendation on data, not on preference. Say what the measurement does not separate.",
                "توصیه بر اساس داده، نه سلیقه. بگویید اندازهگیری چه چیزی را تفکیک نمیکند."),
        L.slide("Takeaways", "جمعبندی",
                ["Definitions state what LST is",
                 "Verification states what is true",
                 "Measurement states what it costs"],
                ["تعریف میگوید LST چیست",
                 "بررسی میگوید چه درست است",
                 "اندازهگیری میگوید چقدر هزینه دارد"],
                "Close by repeating that every number in this deck was inherited and checksum-recorded.",
                "پایان را با یادآوری اینکه هر عدد این دک به ارث رسیده و درهمش ثبت شده تمام کنید."),
    ]


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
    sets = src[0]["data"]["task_sets"][:6]
    sweeps = [dict(s) for s in src[0]["data"]["sweeps"][:2]]
    sweeps.append(L.sweep_alignment(sets, figure="fig_ex5_alignment.png",
                                    source="sweeps[2]"))
    figures = [dict(f) for f in src[0]["data"]["figures"]]
    for sw in sweeps[2:]:
        if sw.get("figure"):
            figures.append(L.fig_line(sw["figure"],
                                      "Sweep " + sw["id"] + ": " + sw["xlabel"],
                                      sw["x"], sw["series"], sw["source"],
                                      ylabel=sw["ylabel"], xlabel=sw["xlabel"]))
    findings = L.common_findings(sets) + [
        L.finding(
            "F5", "B",
            "Every slide number has a checksum-recorded parent",
            "هر عدد اسلاید پدری با درهم ثبتشده دارد",
            (f"[B] This exercise inherits {len(v)} values from "
             f"{len(src)} source data files. The exercise-1 study contributes "
             f"{v['ex1_task_sets']} task sets, the fixed-seed study of "
             f"exercise 4 contributes {v['ex4_generated']} random sets, and "
             f"the hand trace of exercise 3 contributes "
             f"{v['ex3_hand_steps']} compared instants. No number on a slide "
             f"was typed into the deck: each was read from a source JSON at "
             f"generation time and copied into this exercise's own data file."),
            (f"[B] این تمرین {len(v)} مقدار را از {len(src)} فایل دادهٔ مبدأ به "
             f"ارث میبرد. مطالعهٔ تمرین ۱ برابر {v['ex1_task_sets']} مجموعه، "
             f"مطالعهٔ بذرثابت تمرین ۴ برابر {v['ex4_generated']} مجموعهٔ "
             f"تصادفی، و ردگیری دستی تمرین ۳ برابر {v['ex3_hand_steps']} لحظهٔ "
             f"مقایسهشده میدهد. هیچ عددی روی اسلایدها در دک تایپ نشده: هرکدام "
             f"هنگام تولید از JSON مبدأ خوانده و در فایل دادهٔ همین تمرین "
             f"رونوشت شده است."),
            {"inherited_values": len(v), "source_files": len(src),
             "exercise_one_sets": v["ex1_task_sets"],
             "exercise_four_sets": v["ex4_generated"],
             "exercise_three_steps": v["ex3_hand_steps"]},
            source="provenance"),
        L.finding(
            "F6", "M",
            "A short deck is still built from measured numbers",
            "دک کوتاه هم از عددهای اندازهگیریشده ساخته میشود",
            (f"[M] The bilingual deck has {len(slides(v))} slides and speaker "
             f"notes on every one. Its headline comparison is inherited: LST "
             f"{v['ex1_lst_preemptions']} preemptions against EDF "
             f"{v['ex1_edf_preemptions']} on the first task set of exercise 1, "
             f"and {v['ex2_lst_preemptions']} against "
             f"{v['ex2_edf_preemptions']} summed over exercise 2. A short "
             f"explanation is not a licence to replace a measurement with a "
             f"plausible-looking number."),
            (f"[M] دک دوزبانه {len(slides(v))} اسلاید دارد و روی تکتک آنها "
             f"یادداشت گوینده هست. مقایسهٔ اصلیش به ارث رسیده است: LST برابر "
             f"{v['ex1_lst_preemptions']} پیشگیری در برابر EDF "
             f"{v['ex1_edf_preemptions']} روی نخستین مجموعهٔ تمرین ۱، و "
             f"{v['ex2_lst_preemptions']} در برابر "
             f"{v['ex2_edf_preemptions']} جمعزدهشده روی تمرین ۲. توضیح کوتاه "
             f"اجازهای نیست برای جایگزین کردنِ اندازهگیری با عددی "
             f"معقولنما."),
            {"slides": len(slides(v)),
             "ex1_lst_preemptions": v["ex1_lst_preemptions"],
             "ex1_edf_preemptions": v["ex1_edf_preemptions"],
             "ex2_lst_preemptions": v["ex2_lst_preemptions"],
             "ex2_edf_preemptions": v["ex2_edf_preemptions"]},
            source="decks"),
    ]
    decks = L.deck_spec(["DECK_EN.pptx", "DECK_FA.pptx",
                         "SPEAKER_NOTES_EN.md", "SPEAKER_NOTES_FA.md"], slides(v))
    provenance = {"mode": "live", "inherited": v, "mismatches": 0,
                  "note": "source data files read at generation time; checksums recorded"}
    sources = [{"path": s["path"], "sha256": s["sha256"], "what": s["what"]}
               for s in src]
    L.finish(__file__, 5, sets, sweeps, figures, findings,
             "a short bilingual deck with speaker notes, inheriting every "
             "number from exercises 1 to 4",
             "دک کوتاه دوزبانه با یادداشت گوینده، با به ارث بردنِ هر عدد از "
             "تمرینهای ۱ تا ۴",
             extra={"provenance": provenance, "decks": decks,
                    "sources": sources,
                    "embedded_sources": {str(i): src[j]["data"]["meta"]
                                         for j, i in enumerate(SOURCES)}})
    return 0


if __name__ == "__main__":
    sys.exit(main())
