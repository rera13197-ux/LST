"""Bilingual (EN/FA) report builder for exercise 7 -- readers-writers.

Every number printed below comes from ``rw7_data.prepare()``, which reads
``exercise-7/output/experiments.json`` at build time.  Claims are tagged:

    [E] exhaustive finite-state checking -> true/false with a witness
    [M] seeded measurement               -> how much, with dispersion
    [D] instrument disagreement          -> suspect the instrument first

The builder produces an explicitly paginated Report; a clean build needs
``overflow == []``, ``missing_figures == []``, ``missing_glyphs == []`` and
``pages == pdf_pages``.
"""
from __future__ import annotations

from report_kit import (Report, cover, toc, ptitle, h1, h2, para, bullets,
                        table, kv, image, code, formula, note, spacer)

import rw7_data


def ef(lang, en, fa):
    return en if lang == "en" else fa


S = {
    "question": (
        "Which readers-writers mechanisms actually guarantee mutual exclusion, "
        "deadlock freedom and freedom from starvation, and what does each "
        "guarantee cost in completed operations and waiting time?",
        "کدام مکانیزمهای خواننده-نویسنده واقعاً انحصار متقابل، نبود بنبست و "
        "نبود گرسنگی را تضمین میکنند، و هر تضمین از نظر عملیات انجامشده و "
        "زمان انتظار چقدر هزینه دارد؟"),
    "instruments": (
        "[E] The exhaustive checker enumerates every reachable global state of a "
        "small protocol instance. It answers yes/no questions and returns a "
        "witness schedule for every counterexample. [M] The seeded simulator "
        "runs a finite workload and counts operations and waiting times. The two "
        "instruments are never substituted for one another: a verdict is not a "
        "cost, and a cost is not a verdict.",
        "[E] چککنندهٔ جامع تکتک حالتهای سراسری قابلدسترسیِ یک نمونهٔ کوچک "
        "پروتکل را برمیشمرد. به پرسشهای بله/خیر پاسخ میدهد و برای هر نقض، "
        "شاهدی بهشکل زمانبندی میدهد. [M] شبیهساز بذرثابت بارِ کاری محدودی را "
        "اجرا میکند و عملیاتها و زمانهای انتظار را میشمرد. این دو ابزار هرگز "
        "بهجای هم بهکار نمیروند: حکم، هزینه نیست و هزینه، حکم نیست."),
    "model": (
        "Each process is thinking, waiting, or inside the critical section. "
        "The global state is a tuple of per-process states, the entry queue, "
        "the signalled process and a turn variable. There is no unbounded "
        "counter, so the reachable graph is finite and a lasso is a genuine "
        "infinite execution. Readers may share the critical section; a writer "
        "must have it alone.",
        "هر فرایند یا در حال فکر است، یا منتظر، یا درون ناحیهٔ بحرانی. حالت "
        "سراسری تاپلی از حالتهای فرایندها، صف ورود، فرایند بیدارشده و متغیر "
        "نوبت است. شمارندهای بی کران وجود ندارد، پس گراف قابلدسترسی متناهی "
        "است و یک حلقه، اجرای بینهایت واقعی است. خوانندگان میتوانند ناحیهٔ "
        "بحرانی را همزمان استفاده کنند؛ نویسنده باید تنها باشد."),
    "checker": (
        "[E] A breadth-first search from the all-thinking state records every "
        "reachable state and transition. Mutual exclusion and deadlock are "
        "checked on every state. Starvation is a reachable cycle on which the "
        "waiting process never gets its grant enabled while some other process "
        "does enter the critical section: a fair cycle, not merely an unlucky "
        "schedule. Bounded waiting is reported as minus one when such a cycle "
        "exists, because worst-case waiting is then infinite.",
        "[E] جستجوی سطحاول از حالتی که همه در حال فکراند، تکتک حالتها و "
        "گذرهای قابلدسترسی را ثبت میکند. انحصار متقابل و بنبست روی تکتک "
        "حالتها بررسی میشود. گرسنگی، دوری قابلدسترسی است که در آن اجازهٔ ورود "
        "فرایند منتظر هرگز فعال نمیشود، در حالی که فرایند دیگری وارد ناحیهٔ "
        "بحرانی میشود: دورِ عادلانه، نه صرفاً زمانبندی بدشانس. انتظار "
        "کراندار، وقتی چنین دوری باشد، منفیک یک گزارش میشود، چون بدترین "
        "حالت انتظار آنگاه بینهایت است."),
    "verifier": (
        "[E] No counterexample is accepted on the checker's word. An "
        "independent interpreter, written separately and sharing no "
        "transition function with the checker, replays the prefix and then the "
        "cycle twice. It re-derives every admission decision, checks that the "
        "starving process stays waiting, and checks mutual exclusion after "
        "every action. The table records the result for every witness.",
        "[E] هیچ نقضی با حرفِ چککننده پذیرفته نمیشود. مفسری مستقل، که جدا "
        "نوشته شده و هیچ تابع گذری با چککننده مشترک ندارد، پیشوند و سپس "
        "دور را دو بار بازپخش میکند. تکتک تصمیمهای پذیرش را دوباره میسنجد، "
        "بررسی میکند فرایند گرسنه همچنان منتظر بماند، و پس از هر کنش انحصار "
        "متقابل را وارسی میکند. جدول، نتیجهٔ تکتک شاهدها را ثبت میکند."),
    "measurement": (
        "[M] A seeded discrete-event simulator advances in integer steps. At "
        "each step it finishes due service, admits new requests with a fixed "
        "arrival probability, and grants as many compatible processes as the "
        "mechanism allows. It records completed reads and writes, the mean and "
        "maximum waiting time, throughput and the number of finite runs with "
        "zero writer completions. The mechanism's admission rule is shared with "
        "the checker on purpose: the policy is the object under study, not the "
        "instrument.",
        "[M] شبیهساز رخدادگسستهٔ بذرثابت با گامهای صحیح پیش میرود. در هر گام "
        "کارهای سررسیده را تمام میکند، با احتمال ورود ثابت درخواست تازه "
        "میپذیرد، و به همان تعداد که مکانیزم اجازه میدهد ورود میدهد. خواندنها "
        "و نوشتنهای انجامشده، میانگین و بیشینهٔ انتظار، توان عملیاتی و شمار "
        "اجراهای محدودی که صفر عملیات نویسنده دارند ثبت میشود. قاعدهٔ پذیرش "
        "مکانیزم آگاهانه با چککننده مشترک است: سیاست، پدیدهٔ تحت بررسی است، "
        "نه ابزار."),
    "figures": (
        "[M] Every chart is drawn from output/experiments.json by "
        "code/make_diagrams.py. Captions name the data source; no value is "
        "typed into a figure or into this report.",
        "[M] تکتک نمودارها از output/experiments.json و بهدست "
        "code/make_diagrams.py کشیده میشوند. زیرنویسها منبع داده را نام "
        "میکنند؛ هیچ عددی در شکل یا در این گزارش تایپ نشده است."),
    "limits": (
        "The exhaustive results hold for the checked small configurations, "
        "not for an unbounded number of processes. The simulator uses a seeded "
        "synthetic workload rather than a particular operating system's lock "
        "implementation, so absolute waiting times are not portable even "
        "though the ordering is reproducible. No external author, year, DOI or "
        "page number is claimed: the references table states the verification "
        "status of every entry.",
        "نتایج جامع برای پیکربندیهای کوچک بررسیشده برقرارند، نه برای شمار "
        "بیکران فرایندها. شبیهساز بارِ کاری مصنوعی بذرثابتی بهکار میبرد، نه "
        "پیادهسازی قفلِ سیستمعامل خاصی؛ پس زمانهای انتظار مطلق قابل حمل "
        "نیستند، هرچند ترتیبشان بازتولیدپذیر است. هیچ نویسنده، سال، DOI یا "
        "شمارهٔ صفحهای خارجی ادعا نشده: جدول مراجع وضعیت راستیآزمایی تکتک "
        "مدخلها را میگوید."),
}


def yn(lang, b):
    return ef(lang, "yes" if b else "no", "بله" if b else "خیر")


def _cov(lang, D):
    m, c = D["meta"], D["counts"]
    return [
        (ef(lang, "Exercise", "تمرین"), ef(lang, "Exercise 7", "تمرین ۷")),
        (ef(lang, "Course", "درس"), ef(lang, "Real-Time Scheduling",
                                        "زمانبندی بیدرنگ")),
        (ef(lang, "Topic", "موضوع"), ef(lang, "Readers-writers",
                                        "خواننده-نویسنده")),
        (ef(lang, "Repository", "مخزن"), "github.com/rera13197-ux/LST"),
        (ef(lang, "Branch", "شاخه"),
         "Exercise-7-LST-Tie-Breaking-And-Thrashing"),
        (ef(lang, "Random seed", "بذر تصادف"), str(m["seed"])),
        (ef(lang, "Protocols", "پروتکلها"), str(c["protocol_count"])),
        (ef(lang, "Figures", "شکلها"), str(c["figure_count"])),
        (ef(lang, "Method", "روش"),
         ef(lang, "two separate instruments: exhaustive checking and measurement",
            "دو ابزار جدا: بررسی جامع و اندازهگیری")),
        (ef(lang, "Status", "وضعیت"),
         ef(lang, "complete: every number regenerated from a program run",
            "کامل: هر عدد از اجرای برنامهای بازتولید شده است")),
    ]


def _fig_caption(lang, f):
    return (f["title_en"] + ". " + f["caption_en"]) if lang == "en" else (
        f["title_fa"] + ". " + f["caption_fa"])


def make_report(lang: str) -> Report:
    D = rw7_data.prepare()
    meta, C = D["meta"], D["counts"]
    protos, meas = D["protocols"], D["measurements"]
    finds, figs, sweeps = D["findings"], D["figures"], D["sweeps"]
    rand, hand = D["random"], D["hand"]
    div, prov = D["divergence"], D["provenance"]

    title = ef(lang, "Readers-Writers: Verification and Measurement",
               "خواننده-نویسنده: بررسی و اندازهگیری")
    subtitle = ef(lang, "Exercise 7 - bilingual report (EN/FA)",
                  "تمرین ۷ - گزارش دوزبانه (فارسی/انگلیسی)")
    r = Report(title, subtitle, lang, cover_meta=_cov(lang, D))
    pages = []

    def add(*blocks):
        pages.append(list(blocks))

    # 1-2 -----------------------------------------------------------------
    add(cover(_cov(lang, D)))
    add(toc())

    # 3 question ----------------------------------------------------------
    add(ptitle(ef(lang, "The question", "پرسش")),
        para(S["question"][0 if lang == "en" else 1]),
        para(ef(lang,
                "This report states what was asked and how it was answered "
                "before giving any result, so a reader can try to refute the "
                "claim.",
                "این گزارش نخست میگوید چه پرسیده شد و چگونه پاسخ داده شد، بعد "
                "نتیجه میدهد، تا خواننده بتواند سعی کند ادعا را رد کند.")))

    # 4 instruments -------------------------------------------------------
    add(ptitle(ef(lang, "Two instruments, two kinds of claim",
                  "دو ابزار، دو نوع ادعا")),
        para(S["instruments"][0 if lang == "en" else 1]),
        bullets([
            ef(lang, "[E] asks whether a property holds in every reachable state.",
               "[E] میپرسد آیا ویژگی در تکتک حالتهای قابلدسترسی برقرار است."),
            ef(lang, "[M] asks how much work the mechanism completes.",
               "[M] میپرسد مکانیزم چقدر کار انجام میدهد."),
            ef(lang, "[D] is what happens when the two are compared carelessly.",
               "[D] آن است که وقتی این دو بیدقت مقایسه شوند پیش میآید."),
        ]),
        note(ef(lang,
                "When the tools disagree, suspect the tool first, not the data.",
                "وقتی ابزارها با هم جور درنمیآیند، نخست ابزار را مظنون بدان، "
                "نه داده را.")))

    # 5 model -------------------------------------------------------------
    add(ptitle(ef(lang, "Model and notation", "مدل و نمادگذاری")),
        para(S["model"][0 if lang == "en" else 1]),
        formula(ef(lang,
                   "state = (process states, entry queue, signalled, turn)\n"
                   "process state: 0 thinking, 1 waiting, 2 in critical section\n"
                   "readers may share; a writer requires an empty section",
                   "حالت = (حالت فرایندها، صف ورود، بیدارشده، نوبت)\n"
                   "حالت فرایند: ۰ فکر، ۱ انتظار، ۲ درون ناحیهٔ بحرانی\n"
                   "خوانندگان همزمان وارد میشوند؛ نویسنده ناحیهٔ خالی میخواهد")),
        kv([[ef(lang, "Mechanisms", "مکانیزمها"), str(C["mechanism_count"])],
            [ef(lang, "Configurations", "پیکربندیها"),
             str(len(meta["configs"]))],
            [ef(lang, "Protocol instances", "نمونهٔ پروتکل"),
             str(C["protocol_count"])],
            [ef(lang, "State limit", "سقف حالت"), str(meta["state_limit"])]]))

    # 6-7 mechanisms ------------------------------------------------------
    mech_lines = [
        "readers_preference  : readers bypass waiting writers",
        "writers_preference  : a waiting writer blocks new readers",
        "fair_fifo           : entry queue, leading readers batched",
        "mesa_signal         : signal without a place in the entry queue",
    ]
    mech_lines2 = [
        "hoare_signal        : signal with immediate handoff at the head",
        "dekker2             : two participants, turn alternates on release",
        "peterson2           : two participants, turn set on request",
    ]
    add(ptitle(ef(lang, "Mechanisms, part one", "مکانیزمها، بخش نخست")),
        para(ef(lang,
                "The mechanism is a parameter, not an implementation detail. "
                "These four are semaphore-style or monitor-style admission "
                "rules over the same shared state.",
                "مکانیزم پارامتر است، نه جزئیات پیادهسازی. این چهار، قواعد "
                "پذیرش بهسبک سمافور یا مانیتور روی همان حالت مشترکاند.")),
        code(mech_lines, caption=ef(lang, "Admission rules, part one",
                                    "قواعد پذیرش، بخش نخست")),
        note(ef(lang, "Preference trades one kind of starvation for another.",
                "اولویت، یک نوع گرسنگی را با نوع دیگری عوض میکند.")))
    add(ptitle(ef(lang, "Mechanisms, part two", "مکانیزمها، بخش دوم")),
        para(ef(lang,
                "Hoare-style handoff gives the woken thread a place. Dekker and "
                "Peterson carry the mutual-exclusion pattern only between two "
                "participants; the checker only admits them in that "
                "configuration.",
                "تحویلِ Hoare به فرایند بیدارشده جایی میدهد. دِکِر و پِترسون "
                "الگوی انحصار متقابل را فقط بین دو شرکتکننده نگه میدارند؛ "
                "چککننده آنها را تنها در همان پیکربندی میپذیرد.")),
        code(mech_lines2, caption=ef(lang, "Admission rules, part two",
                                     "قواعد پذیرش، بخش دوم")),
        note(ef(lang, "Two-participant patterns cannot be assumed for a third.",
                "نمیتوان الگوی دو شرکتکننده را برای سومی مفروض گرفت.")))

    # 8 checker design ----------------------------------------------------
    add(ptitle(ef(lang, "[E] Exhaustive checker", "[E] چککنندهٔ جامع")),
        para(S["checker"][0 if lang == "en" else 1]),
        bullets([
            ef(lang, "Breadth-first exploration with memoisation.",
               "پیمایش سطحاول با حافظهسازی."),
            ef(lang, "Fair-cycle search with a separate independent verifier.",
               "جستجوی دورِ عادلانه با راستیآزمای مستقل جداگانه."),
            ef(lang, "Truncated runs are counted and excluded from conclusions.",
               "اجراهای بریدهشده شمرده میشوند و از نتیجهگیری کنار گذاشته میشوند."),
        ]),
        kv([[ef(lang, "Reachable states", "حالتهای قابلدسترسی"),
             str(C["states_total"])],
            [ef(lang, "Transitions", "گذرها"), str(C["transitions_total"])],
            [ef(lang, "Truncated checks", "بررسیهای بریدهشده"),
             str(C["truncated_checks"])]]))

    # 9-10 verdicts -------------------------------------------------------
    vhead = [ef(lang, "protocol", "پروتکل"), ef(lang, "states", "حالتها"),
             ef(lang, "ME", "انحصار"), ef(lang, "DL-free", "بینبست"),
             ef(lang, "SF", "بینگرسنگی"),
             ef(lang, "starving", "گرسنه")]
    def vrow(c):
        return [c["id"], str(c["states"]), yn(lang, c["mutual_exclusion"]),
                yn(lang, c["deadlock_free"]), yn(lang, c["starvation_free"]),
                str(len(c["starving_processes"]))]
    for part in range(2):
        chunk = protos[part * 6:(part + 1) * 6]
        vlabel = (ef(lang, "Verdicts, part one", "احکام، بخش نخست")
                  if part == 0 else
                  ef(lang, "Verdicts, part two", "احکام، بخش دوم"))
        add(ptitle(vlabel),
            para(ef(lang,
                    "[E] Every row is a separate protocol instance: one "
                    "mechanism under one reader/writer configuration.",
                    "[E] هر ردیف یک نمونهٔ پروتکل جدا است: یک مکانیزم زیر یک "
                    "پیکربندی خواننده/نویسنده.")),
            table(vhead, [vrow(c) for c in chunk],
                  caption=ef(lang, "Exhaustive verdicts [E]", "احکام جامع [E]")))

    # 11 mutual exclusion & deadlock --------------------------------------
    add(ptitle(ef(lang, "Mutual exclusion and deadlock",
                  "انحصار متقابل و بنبست")),
        para(ef(lang,
                "[E] Both properties are checked on every reachable state, not "
                "on a sample of runs. The counts below are sums over all "
                "protocol instances.",
                "[E] هر دو ویژگی روی تکتک حالتهای قابلدسترسی بررسی میشوند، "
                "نه روی نمونهای از اجراها. شمارشهای زیر جمع روی همهٔ نمونههای "
                "پروتکلاند.")),
        kv([[ef(lang, "Mutual-exclusion violations", "نقض انحصار متقابل"),
             str(C["mutual_exclusion_violations"])],
            [ef(lang, "Deadlock states", "حالتهای بنبست"),
             str(C["deadlock_states"])],
            [ef(lang, "Starving protocol instances", "نمونهٔ گرسنهکننده"),
             str(C["starving_protocols"])],
            [ef(lang, "Starvation-free instances", "نمونهٔ بدون گرسنگی"),
             str(C["starvation_free_protocols"])]]),
        note(ef(lang,
                "Zero violations here is a property of the model, not a claim "
                "about any particular runtime lock.",
                "صفر بودن نقضها ویژگیِ مدل است، نه ادعایی دربارهٔ قفلِ یک "
                "زمان اجرای خاص.")))

    # 12 fair cycle -------------------------------------------------------
    add(ptitle(ef(lang, "What counts as starvation", "گرسنگی یعنی چه")),
        para(ef(lang,
                "A process waiting a long time is not yet starved. Starvation "
                "requires an infinite fair execution in which it never enters. "
                "The checker therefore looks for a reachable cycle with two "
                "conditions.",
                "انتظار طولانی هنوز گرسنگی نیست. گرسنگی اجرای بینهایت و "
                "عادلانهای میخواهد که فرایند هرگز وارد نشود. پس چککننده دنبال "
                "دورِ قابلدسترسی با دو شرط میگردد.")),
        bullets([
            ef(lang, "the waiting process's grant is never enabled on the cycle;",
               "اجازهٔ ورود فرایند منتظر روی هیچ حالتِ دور فعال نیست؛"),
            ef(lang, "some other process does enter the critical section on the cycle.",
               "فرایند دیگری روی همان دور وارد ناحیهٔ بحرانی میشود."),
        ]),
        note(ef(lang, "Without the second condition a stuttering schedule would fake starvation.",
                "بدون شرط دوم، زمانبندیای که هیچ کاری نمیکند گرسنگی جلوه میداد.")))

    # 13 bounded waiting --------------------------------------------------
    add(ptitle(ef(lang, "Bounded waiting verdict", "حکم انتظار کراندار")),
        para(ef(lang,
                "[E] Minus one means a fair starvation cycle exists, so "
                "worst-case waiting is infinite. Other entries are the largest "
                "shortest path into the critical section, counted in state "
                "transitions.",
                "[E] منفیک یک یعنی دورِ گرسنگیِ عادلانه هست، پس بدترین انتظار "
                "بینهایت است. بقیهٔ درایهها بزرگترین کوتاهترین مسیر به ناحیهٔ "
                "بحرانیاند، بهشمار گذرهای حالت.")),
        table([ef(lang, "protocol", "پروتکل"),
               ef(lang, "max bound", "بیشینهٔ کران")],
              [[c["id"], str(min(c["bounded_wait"].values()))]
               for c in protos[:8]],
              caption=ef(lang, "Bounded waiting [E]", "انتظار کراندار [E]")),
        note(ef(lang, "Transitions are not time steps; see the divergence page.",
                "گذرهای حالت، گامهای زمانی نیستند؛ صفحهٔ ناهماهنگی را ببینید.")))

    # 14 verifier + witness ----------------------------------------------
    wit = next((p["witness"]["cycle"] for p in protos if p["witness"]), [])
    add(ptitle(ef(lang, "Independent verifier", "راستیآزمای مستقل")),
        para(S["verifier"][0 if lang == "en" else 1]),
        table([ef(lang, "protocol", "پروتکل"), ef(lang, "process", "فرایند"),
               ef(lang, "steps", "گامها"), ef(lang, "valid", "معتبر")],
              [[v["protocol"], str(v["process"]), str(v["steps"]),
                yn(lang, v["valid"])] for v in D["verifications"]],
              caption=ef(lang, "Every witness re-checked [E]",
                         "بازبینی تکتک شاهدها [E]")),
        code([str(x) for x in wit[:10]],
             caption=ef(lang, "First starvation cycle (witness)",
                        "نخستین دورِ گرسنگی (شاهد)")),
        kv([[ef(lang, "Witnesses", "شاهدها"), str(C["witnesses"])],
            [ef(lang, "Verified valid", "معتبر تأییدشده"),
             str(C["witnesses_valid"])]]))

    # 15 hand table -------------------------------------------------------
    hrows = [[str(x["step"]), x["action"], x["checker"],
              yn(lang, x["agree"])] for x in hand["rows"]]
    add(ptitle(ef(lang, "A hand table, printed by two implementations",
                  "جدول دستی، چاپشده توسط دو پیادهسازی")),
        para(ef(lang,
                "[M] A small independent interpreter replays a fixed action "
                "sequence for writers preference. Its process-state timeline "
                "is compared step by step with the checker's transition "
                "function.",
                "[M] مفسر مستقل کوچکی دنبالهٔ کنش ثابتی را برای اولویت"
                "نویسنده بازپخش میکند. خطِ زمانِ حالتهای فرایندِ آن گامبهگام "
                "با تابع گذرِ چککننده مقایسه میشود.")),
        table([ef(lang, "step", "گام"), ef(lang, "action", "کنش"),
               ef(lang, "process states", "حالت فرایندها"),
               ef(lang, "agree", "جور")], hrows,
              caption=ef(lang, "Hand trace [M]", "ردگیری دستی [M]")),
        kv([[ef(lang, "Compared steps", "گامهای مقایسهشده"),
             str(hand["compared_steps"])],
            [ef(lang, "Agree", "جور است"), yn(lang, hand["agree"])]]))

    # 16 hand divergence --------------------------------------------------
    add(ptitle(ef(lang, "Where two hand rules part company",
                  "جایی که دو قاعدهٔ دستی از هم جدا میشوند")),
        para(ef(lang,
                "[M] On the same prefix, writers preference refuses a new "
                "reader while a writer waits, and readers preference admits "
                "it. The first differing step is a printed witness: the two "
                "rules are different algorithms.",
                "[M] روی همان پیشوند، اولویتنویسنده خوانندهٔ تازهای را وقتی "
                "نویسندهای منتظر است نمیپذیرد و اولویتخواننده میپذیرد. "
                "نخستین گام متفاوت، شاهدی چاپشده است: دو قاعده دو الگوریتم "
                "متفاوتاند.")),
        code(hand["divergence"]["witness"],
             caption=ef(lang, "Divergence witness", "شاهد واگرایی")),
        kv([[ef(lang, "First divergent step", "نخستین گام واگرا"),
             str(hand["divergence"]["first_step"])],
            [ef(lang, "Writers preference allows", "اولویتنویسنده اجازه میدهد"),
             yn(lang, hand["divergence"]["a_allows"])],
            [ef(lang, "Readers preference allows", "اولویتخواننده اجازه میدهد"),
             yn(lang, hand["divergence"]["b_allows"])],
            [ef(lang, "Divergent decisions", "تصمیمهای واگرا"),
             str(hand["divergence"]["divergent_count"])]]))

    # 17 measurement design ----------------------------------------------
    add(ptitle(ef(lang, "[M] Measurement design", "[M] طراحی اندازهگیری")),
        para(S["measurement"][0 if lang == "en" else 1]),
        kv([[ef(lang, "Random seed", "بذر تصادف"), str(meta["seed"])],
            [ef(lang, "Horizon", "افق"), str(meta["horizon"])],
            [ef(lang, "Trials", "تکرارها"), str(meta["trials"])],
            [ef(lang, "Arrival probability", "احتمال ورود"),
             str(meta["arrival"])],
            [ef(lang, "Reader service", "کار خواننده"),
             str(meta["service_read"])],
            [ef(lang, "Writer service", "کار نویسنده"),
             str(meta["service_write"])]]))

    # 18-19 measurement results ------------------------------------------
    mhead = [ef(lang, "protocol", "پروتکل"), ef(lang, "reads", "خواندن"),
             ef(lang, "writes", "نوشتن"), ef(lang, "ops", "عملیات"),
             ef(lang, "mean wait", "میانگین انتظار")]
    def mrow(m):
        return [m["id"], str(m["reads"]), str(m["writes"]),
                str(m["operations"]), str(m["mean_wait"])]
    for part in range(2):
        chunk = meas[part * 6:(part + 1) * 6]
        mlabel = (ef(lang, "Measurement results, part one",
                     "نتایج اندازهگیری، بخش نخست") if part == 0 else
                  ef(lang, "Measurement results, part two",
                     "نتایج اندازهگیری، بخش دوم"))
        add(ptitle(mlabel),
            para(ef(lang, "[M] Sums over the seeded trials for each instance.",
                    "[M] جمع روی تکرارهای بذرثابت برای هر نمونه.")),
            table(mhead, [mrow(m) for m in chunk],
                  caption=ef(lang, "Completed work [M]", "کار انجامشده [M]")))

    # 20-22 sweeps --------------------------------------------------------
    for sw in sweeps:
        add(ptitle(sw["title_en"] if lang == "en" else sw["title_fa"]),
            para(ef(lang,
                    "[M] One parameter is swept while the rest are held fixed. "
                    "The curve and the table are drawn from an array in the "
                    "generated data file.",
                    "[M] یک پارامتر جاروب میشود و بقیه ثابت میمانند. منحنی و "
                    "جدول از آرایهای در فایل دادهٔ تولیدشده کشیده میشوند.")),
            image(sw["figure"], width_cm=13.2,
                  caption=sw["xlabel_en"] + " / " + sw["ylabel_en"]
                  if lang == "en" else
                  sw["xlabel_fa"] + " / " + sw["ylabel_fa"]),
            table([ef(lang, "x", "x")] + [s["name"] for s in sw["series"]],
                  [[str(x)] + [str(s["values"][i]) for s in sw["series"]]
                   for i, x in enumerate(sw["x"])],
                  caption=ef(lang, "Sweep values [M]", "مقادیر جاروب [M]")))

    # 23-28 findings ------------------------------------------------------
    for f in finds:
        blocks = [ptitle(ef(lang, "Finding ", "یافتهٔ ") + f["id"] +
                         " [" + f["kind"] + "]"),
                  para(f["title_en"] if lang == "en" else f["title_fa"]),
                  para(f["detail_en"] if lang == "en" else f["detail_fa"]),
                  kv([[k.replace("_", " "), str(v)]
                      for k, v in f["numbers"].items()],
                     caption=ef(lang, "Numbers from the data file",
                                "عددها از فایل داده"))]
        if f["witness"]:
            blocks.append(code([str(x) for x in f["witness"][:10]],
                               caption=ef(lang, "Witness schedule [E]",
                                          "زمانبندی شاهد [E]")))
        blocks.append(note(ef(lang, "Source: ", "منبع: ") + f["source"]))
        add(*blocks)

    # 29-32 remaining figures --------------------------------------------
    used = {sw["figure"] for sw in sweeps}
    rest = [f for f in figs if f["file"] not in used]
    for i in range(0, len(rest), 2):
        chunk = rest[i:i + 2]
        blocks = [ptitle(ef(lang, "Figures, group ", "شکلها، گروه ") +
                         str(i // 2 + 1)),
                  para(S["figures"][0 if lang == "en" else 1])]
        for f in chunk:
            blocks.append(image(f["file"], width_cm=12.6,
                                caption=_fig_caption(lang, f)))
        add(*blocks)

    # 33 divergence -------------------------------------------------------
    add(ptitle(ef(lang, "[D] When the instruments disagree",
                  "[D] وقتی دو ابزار جور درنمیآیند")),
        para(finds[-1]["detail_en"] if lang == "en" else
             finds[-1]["detail_fa"]),
        kv([[ef(lang, "Checker clock", "ساعت چککننده"),
             div["checker_clock"]],
            [ef(lang, "Measurement clock", "ساعت اندازهگیری"),
             div["measurement_clock"]],
            [ef(lang, "Largest checker bound", "بزرگترین کران چککننده"),
             str(C["checker_max_bound"])],
            [ef(lang, "Largest measured wait", "بزرگترین انتظار اندازهگیریشده"),
             str(C["measurement_max_wait"])],
            [ef(lang, "Finite-window artefacts", "مصنوعهای پنجرهٔ محدود"),
             str(div["short_horizon_artefacts"])]],
           caption=ef(lang, "Different units [D]", "واحدهای متفاوت [D]")),
        note(div["detail_en"] if lang == "en" else div["detail_fa"]))

    # 34 random study -----------------------------------------------------
    add(ptitle(ef(lang, "The large seeded random study",
                  "مطالعهٔ تصادفی بزرگ بذرثابت")),
        para(ef(lang,
                "[M] A fixed-seed generator varies the reader population, the "
                "writer population, the arrival probability and both service "
                "lengths. Each workload is run once per mechanism in a short "
                "window. [D] Zero-writer runs are counted but never promoted "
                "into correctness verdicts.",
                "[M] مولدی بذرثابت جمعیت خوانندگان، جمعیت نویسندگان، احتمال "
                "ورود و هر دو طول کار را عوض میکند. هر بارِ کاری یکبار بهازای "
                "هر مکانیزم در پنجرهای کوتاه اجرا میشود. [D] اجراهای با صفر "
                "نویسنده شمرده میشوند ولی هرگز به حکمِ درستی ارتقا نمییابند.")),
        table([ef(lang, "mechanism", "مکانیزم"),
               ef(lang, "zero-writer runs", "اجراهای بینویسنده"),
               ef(lang, "artefacts", "مصنوعها"),
               ef(lang, "mean writer share", "میانگین سهم نویسنده")],
              [[m, str(v["writer_starved_runs"]),
                str(v["short_horizon_artefacts"]),
                str(v["mean_writer_share"])]
               for m, v in rand["per_mechanism"].items()],
              caption=ef(lang, "Random study [M]/[D]",
                         "مطالعهٔ تصادفی [M]/[D]")),
        kv([[ef(lang, "Workloads", "بارهای کاری"), str(rand["workloads"])],
            [ef(lang, "Measurements", "اندازهگیریها"),
             str(rand["measurements"])],
            [ef(lang, "Short horizon", "افق کوتاه"),
             str(rand["short_horizon"])],
            [ef(lang, "Truncated", "بریدهشده"), str(rand["truncated"])]]))

    # 35 provenance -------------------------------------------------------
    add(ptitle(ef(lang, "Provenance of every number", "منشأ تکتک عددها")),
        para(ef(lang,
                "A test collects every numeric token allowed by the data file "
                "and fails if the report prints a number that is not there. "
                "The three producer programs are checksummed below.",
                "تستی تکتک نشانههای عددی مجازِ فایل داده را گرد میآورد و اگر "
                "گزارش عددی چاپ کند که آنجا نباشد، رد میشود. درهمِ سه برنامهٔ "
                "تولیدکننده در پایین آمده است.")),
        table([ef(lang, "file", "فایل"), ef(lang, "bytes", "بایت"),
               ef(lang, "sha256 prefix", "پیشوند درهم")],
              [[s["path"], str(s["bytes"]), s["sha256"][:12]]
               for s in prov["files"]],
              caption=ef(lang, "Producer checksums", "درهمهای تولیدکننده")),
        kv([[ef(lang, "Checksum mismatches", "ناهماهنگی درهم"),
             str(prov["mismatches"])]]),
        note(prov["detail_en"] if lang == "en" else prov["detail_fa"]))

    # 36 limitations ------------------------------------------------------
    add(ptitle(ef(lang, "Limitations", "محدودیتها")),
        para(S["limits"][0 if lang == "en" else 1]),
        bullets([
            ef(lang, "Small configurations only for exhaustive results.",
               "نتایج جامع فقط برای پیکربندیهای کوچک."),
            ef(lang, "Synthetic seeded workload, not a specific OS lock.",
               "بارِ کاری مصنوعی بذرثابت، نه قفلِ سیستمعامل خاص."),
            ef(lang, "No external bibliographic metadata is claimed.",
               "هیچ فرادادهٔ کتابشناختی خارجی ادعا نشده است."),
        ]))

    # 37 reproduction -----------------------------------------------------
    add(ptitle(ef(lang, "How to reproduce", "چطور بازتولید کنیم")),
        para(ef(lang,
                "Run from the multi-exercise tree root for the reports, and "
                "from the exercise folder for the data and figures. On a "
                "flattened branch the code and tests sit at the root.",
                "برای گزارشها از ریشهٔ درخت چندتمرینیه و برای داده و شکلها از "
                "پوشهٔ تمرین اجرا کنید. روی شاخهٔ تخت، کد و تستها در ریشهاند.")),
        code([
            "python3 code/run_experiments.py",
            "python3 code/make_diagrams.py",
            "python3 -m pytest tests -q",
            "python3 tools/build_report.py rw7_en exercise-7 REPORT_EN",
            "python3 tools/build_report.py rw7_fa exercise-7 REPORT_FA",
            "python3 tools/verify_builds.py",
        ], caption=ef(lang, "Commands", "دستورها")))

    # 38 deliverables -----------------------------------------------------
    add(ptitle(ef(lang, "Deliverables", "تحویلدادهها")),
        para(ef(lang,
                "The English and Persian reports are rendered from one content "
                "model, so their page counts agree with the produced PDFs.",
                "گزارش انگلیسی و فارسی از یک مدل محتوا ساخته میشوند، پس "
                "شمارش صفحههایشان با PDFهای تولیدشده جور است.")),
        table([ef(lang, "path", "مسیر"), ef(lang, "what", "چیست")],
              [["REPORT_EN.md / REPORT_FA.md",
                ef(lang, "Markdown of the same model", "مارکداون همان مدل")],
               ["docs/REPORT_EN.docx / .pdf",
                ef(lang, "English Word and PDF", "ورد و PDF انگلیسی")],
               ["docs/REPORT_FA.docx / .pdf",
                ef(lang, "Persian Word and PDF", "ورد و PDF فارسی")],
               ["output/experiments.json",
                ef(lang, "the only source of numbers", "یگانه مرجع عددها")],
               ["diagrams/", ef(lang, "generated figures", "شکلهای تولیدشده")],
               ["code/ + tests/", ef(lang, "code and green tests", "کد و تستهای سبز")]],
              caption=ef(lang, "Artefact table", "جدول خروجیها")),
        kv([[ef(lang, "Figures", "شکلها"), str(C["figure_count"])],
            [ef(lang, "Findings", "یافتهها"), str(C["finding_count"])],
            [ef(lang, "Sweeps", "جاروبها"), str(C["sweep_count"])]]))

    # 39 references -------------------------------------------------------
    add(ptitle(ef(lang, "References and verification status",
                  "مراجع و وضعیت راستیآزمایی")),
        para(ef(lang,
                "Every entry states whether it was verified inside this "
                "repository or left explicitly unverified. No author, year, "
                "DOI or page number is invented.",
                "تکتک مدخلها میگویند درون همین مخزن تأیید شدهاند یا صریحاً "
                "تأییدنشده ماندهاند. هیچ نویسنده، سال، DOI یا شمارهٔ صفحهای "
                "ساخته نشده است.")),
        table([ef(lang, "item", "مدخل"), ef(lang, "status", "وضعیت")],
              [[x["title"], x["status"]] for x in D["references"]],
              caption=ef(lang, "Verified and unverified", "تأییدشده و تأییدنشده")))

    for blocks in pages:
        r.page(*blocks)
    return r
