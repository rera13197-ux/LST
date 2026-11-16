"""Generic, bilingual report builder for the six LST exercises.

A content module is three lines::

    from lst_report import make_report
    def build():
        return make_report(1, "en")

Every number printed below is obtained from ``lstN_data.data()``, which reads
``exercise-N/output/experiments.json`` at build time.  The prose contains no
measured constant.  Claims are tagged in the running text:

    [E] exhaustive / verification   -> true or false, with a witness
    [M] measurement                 -> how much, with dispersion

The builder produces an explicitly paginated ``Report``; a clean build needs
``overflow == []``, ``missing_figures == []``, ``missing_glyphs == []`` and
``pages == pdf_pages``.
"""
from __future__ import annotations

import importlib

from report_kit import (Report, cover, toc, ptitle, h1, h2, para, bullets,
                        table, kv, image, code, formula, note, spacer)

# --------------------------------------------------------------------------
# bilingual strings.  A tuple is (English, Persian).
# --------------------------------------------------------------------------

S = {
    "course": ("Real-Time Scheduling", "زمانبندی بیدرنگ"),
    "topic": ("Least Slack Time (LST) scheduling", "زمانبندی کمترین لَکسیَتی (LST)"),
    "meta_exercise": ("Exercise", "تمرین"),
    "meta_course": ("Course", "درس"),
    "meta_topic": ("Topic", "موضوع"),
    "meta_deliverables": ("Deliverables", "تحویلدادهها"),
    "meta_repo": ("Repository", "مخزن"),
    "meta_branch": ("Branch", "شاخه"),
    "meta_seed": ("Random seed", "بذر تصادف"),
    "meta_status": ("Status", "وضعیت"),
    "meta_pages": ("Page count", "شمارش صفحهها"),
    "meta_method": ("Method", "روش"),
    "status_value": ("complete: every number regenerated from a program run",
                     "کامل: هر عدد از اجرای برنامهای بازتولید شده است"),
    "pages_value": ("measured from the produced PDF, see tools/check_outputs.py",
                    "اندازهگیری روی PDF ساختهشده، بنگرید به tools/check_outputs.py"),
    "deliverables_value": ("bilingual EN/FA report, DOCX + PDF; diagrams; code; tests",
                           "گزارش دوزبانه EN/FA با DOCX و PDF، شکلها، کد و تستها"),
    "method_value": ("two separate instruments: exhaustive verification and measurement",
                     "دو ابزار جدا: بررسی جامع و اندازهگیری"),

    "s_question": ("The question", "پرسش"),
    "s_instruments": ("Two instruments, two kinds of claim", "دو ابزار، دو نوع ادعا"),
    "s_model": ("Model and notation", "مدل و نمادگذاری"),
    "s_pseudocode": ("The scheduling rule", "قاعدهٔ زمانبندی"),
    "s_deadlines": ("Why deadlines must be constrained", "چرا ضربالاجل باید مقید باشد"),
    "s_design": ("Experimental design", "طراحی آزمایش"),
    "s_worked": ("A worked schedule", "یک برنامهٔ زمانبندیِ گامبهگام"),
    "s_hand": ("The hand table, printed by the program", "جدول دستی، چاپشده توسط برنامه"),
    "s_divergence": ("Where the hand rules part company", "جایی که قواعد دستی از هم جدا میشوند"),
    "p_hand": (
        "[M] This table is produced by a second, independent implementation "
        "of the discrete-time decision rule, not by the simulator. For every "
        "integer instant it lists the ready jobs, their slack values and the "
        "job chosen. A test compares this timeline with the simulator's own "
        "timeline step by step; the compared step count is in the data file.",
        "[M] این جدول را پیادهسازی دوم و مستقلی از قاعدهٔ تصمیم زمانگسسته "
        "میسازد، نه شبیهساز. برای هر لحظهٔ صحیح، کارهای آماده، لَکسیَتی آنها و "
        "کار انتخابشده را فهرست میکند. تستی این خطِ زمان را گامبهگام با خطِ "
        "زمانِ خودِ شبیهساز مقایسه میکند؛ شمارش گامهای مقایسهشده در فایل داده "
        "است."),
    "p_divergence": (
        "[M] A second hand rule, earliest deadline first, is run on the same "
        "task set. The first instant at which the two hand rules choose "
        "different jobs is a witness: it shows that the two policies are not "
        "the same algorithm even when both happen to meet every deadline. "
        "The witness sequence below is printed from the generated data.",
        "[M] قاعدهٔ دستی دوم، زودترین ضربالاجل نخست، روی همان مجموعه اجرا "
        "میشود. نخستین لحظهای که دو قاعدهٔ دستی کارهای متفاوتی برمیکزینند یک "
        "شاهد است: نشان میدهد دو سیاست حتی وقتی هر دو به همهٔ ضربالاجلها "
        "میرسند یک الگوریتم نیستند. دنبالهٔ شاهد زیر از دادهٔ تولیدشده چاپ "
        "میشود."),
    "h_hand": ("t | ready jobs | slack of ready jobs | chosen",
               "t | کارهای آماده | لَکسیَتی آمادهها | انتخاب"),
    "s_set": ("Task set", "مجموعهکار"),
    "s_sweeps": ("Sweeps", "جاروبها"),
    "s_finding": ("Finding", "یافته"),
    "s_figures": ("Figures", "شکلها"),
    "s_profile": ("Policy profile", "نمایهٔ سیاست"),
    "s_disagreement": ("When the two instruments disagree", "وقتی دو ابزار با هم جور درنمیآیند"),
    "s_cap": ("A defect produced by a state cap", "نقصی که سقفِ حالت میسازد"),
    "s_coarse": ("Verification is coarse, measurement is not",
                 "بررسی جامع درشتدانه است، اندازهگیری نه"),
    "s_random": ("The large random study", "مطالعهٔ تصادفی بزرگ"),
    "p_random": (
        "[E] A fixed-seed generator produces constrained-deadline task sets "
        "with utilisation at most one and a bounded hyperperiod. Each set is "
        "decided by the exhaustive checker, every witness is re-checked by the "
        "independent verifier, and the aligned simulator run is compared with "
        "the verdict. [M] Counts below are sums over that run. A separate "
        "control batch with implicit deadlines shows what happens when the "
        "yardstick loses its power. Truncated runs are counted and excluded "
        "from every conclusion.",
        "[E] مولدی با بذر ثابت مجموعههای ضربالاجلمقید با بهرهوری حداکثر یک و "
        "دورهٔ بزرگ کراندار میسازد. هر مجموعه به حکم چککنندهٔ جامع داوری "
        "میشود، هر شاهد توسط راستیآزمای مستقل دوباره چک میشود، و اجرای "
        "همتراز شبیهساز با حکم مقایسه میگردد. [M] شمارشهای زیر جمعهای همان "
        "اجرااند. دستهٔ کنترل جداگانه با ضربالاجل ضمنی نشان میدهد وقتی سنجه "
        "قدرتش را از دست میدهد چه رخ میدهد. اجراهای بریدهشده شمرده میشوند و "
        "از هیچ نتیجهای وارد نمیشوند."),
    "h_random": ("Quantity | count | instrument",
                 "کمیت | شمارش | ابزار"),
    "s_provenance": ("Where the numbers came from", "عددها از کجا آمدند"),
    "p_provenance": (
        "This exercise inherits its numbers from earlier exercises. During "
        "generation each source data file was read and its checksum recorded; "
        "the inherited values are copied into this exercise's own data file so "
        "the flattened branch remains self-contained. A test re-reads the "
        "sources and checks that every inherited value still matches. Items "
        "that could not be verified in this environment are marked as "
        "unverified rather than dressed up with invented bibliographic "
        "details.",
        "این تمرین عددهایش را از تمرینهای پیشین به ارث میبرد. هنگام تولید، "
        "هر فایل دادهٔ مبدأ خوانده و درهمش شناسهٔ آن ثبت شد؛ مقدارهای بهارثرسیده "
        "در فایل دادهٔ همین تمرین رونوشت میشوند تا شاخهٔ تخت همچنان خودبسنده "
        "باشد. تستی منبعها را دوباره میخواند و چک میکند هر مقدار هنوز جور "
        "است. مواردی که در این محیط قابل راستیآزمایی نبودهاند به جای آراسته "
        "شدن به جزئیات کتابشناختی ساختگی، «تأییدنشده» علامت خوردهاند."),
    "h_provenance": ("Source | checksum prefix | what was inherited",
                     "منبع | پیشوند درهم | آنچه به ارث رسید"),
    "p_cap": (
        "The checker has a state cap. With the cap set low, the very same task "
        "set that the full checker proves feasible is reported infeasible and "
        "the run is flagged truncated. [D] This is a disagreement between the "
        "instrument and the data, and the instrument is the suspect. [E] With "
        "the cap restored the verdict returns to feasible. A truncated run is "
        "never used as a finding anywhere in this project; it is reported as "
        "an artefact, with the limit and the state count that produced it.",
        "چککننده سقفِ حالتی دارد. وقتی سقف را پایین بگذاریم، همان مجموعهای که "
        "چککنندهٔ کامل شدنیاش اثبات میکند نشدنی گزارش میشود و اجرا برچسبِ "
        "بریدگی میخورد. [D] این ناهماهنگیِ ابزار و داده است و ابزار مظنون است. "
        "[E] با برگرداندن سقف، حکم دوباره شدنی میشود. هیچ اجرای بریدشده‌ای "
        "در این پروژه به عنوان یافته به کار نمیرود؛ به عنوان مصنوع گزارش "
        "میشود، همراه سقف و شمارشِ حالتی که آن را ساخته است."),
    "p_coarse": (
        "[E] The checker answers one question: does a feasible schedule exist. "
        "The witness it returns is one such schedule. [M] The simulator counts "
        "what that witness costs and what LST costs on the same task set. When "
        "the two numbers differ, the schedules are equivalent for verification "
        "and very different for the machine. This is not a contradiction; it is "
        "the limit of what a feasibility verdict can promise, made visible by "
        "measurement. A claim that all optimal schedules cost the same is "
        "refuted by the witness rows below.",
        "[E] چککننده به یک پرسش پاسخ میدهد: آیا برنامهای شدنی وجود دارد. شاهدی "
        "که برمیگرداند یکی از همان برنامههاست. [M] شبیهساز میشمارد آن شاهد و "
        "LST روی همان مجموعه چقدر هزینه دارند. وقتی دو عدد فرق کنند، برنامهها "
        "برای بررسی همارز و برای ماشین بسیار متفاوتاند. این تناقض نیست؛ مرزِ "
        "آن چیزی است که یک حکمِ شدنیبودن میتواند وعده بدهد، و اندازهگیری آن "
        "را آشکار میکند. ادعای «همهٔ برنامههای بهینه هزینهٔ یکسان دارند» با "
        "ردیفهای شاهد زیر نقض میشود."),
    "h_cap": ("Cap on states | verdict | states visited | truncated",
              "سقف حالت | حکم | حالتهای پیمودهشده | بریدهشده"),
    "h_coarse": ("Set | witness preemptions | LST preemptions | EDF preemptions | witness valid",
                 "مجموعه | پیشگیری شاهد | پیشگیری LST | پیشگیری EDF | شاهد معتبر"),
    "s_limits": ("Limitations we state ourselves", "محدودیتهایی که خودمان مینویسیم"),
    "s_repro": ("Reproducibility", "بازتولیدپذیری"),
    "s_deliverables": ("Deliverables and checks", "تحویلدادهها و چکها"),
    "s_appendix": ("Appendix: the data contract", "پیوست: قراردادِ داده"),

    "p_instruments_1": (
        "Two tools are used in this project and they answer different questions. "
        "The exhaustive checker walks every reachable state and returns a verdict, "
        "true or false, together with a witness schedule when the verdict is true. "
        "The discrete-event simulator counts what happens in a particular run. "
        "The reports tag every claim with the tool that produced it: [E] for "
        "verification and [M] for measurement. A sentence of the form 'it never "
        "missed in our runs, therefore it is correct' is not written here.",
        "در این پروژه دو ابزار به کار رفته که به پرسشهای متفاوتی پاسخ میدهند. "
        "چککنندهٔ جامع همهٔ حالتهای قابلرسیدن را میپیماید و حکمی قطعی میدهد، "
        "درست یا غلط، و هنگام درستبودن یک برنامهٔ زمانبندی به عنوان شاهد برمیگرداند. "
        "شبیهساز رخدادگسسته میشمارد که در یک اجرای مشخص چه رخ داده است. "
        "در گزارشها هر ادعا با ابزارِ تولیدکنندهاش برچسب میخورد: [E] برای بررسی "
        "و [M] برای اندازهگیری. جملهای مثل «چون در اجراهای ما خطا نداد پس درست است» "
        "اینجا نوشته نمیشود."),
    "p_instruments_2": (
        "[M] Preemptions, context switches, laxity-zero switches, tie events, "
        "minimum observed laxity, response time and jitter are counted by the "
        "simulator over an integer timeline. [E] Feasibility is decided by the "
        "checker, and every witness schedule it returns is re-checked by a "
        "separate verifier that shares no code with the checker. When the two "
        "instruments disagree, the instrument is the first suspect, not the "
        "theorem and not the data.",
        "[M] پیشگیریها، تعویضهای زمینه، تعویضها در لَکسیَتی صفر، رخدادهای تساوی، "
        "کمینهٔ لَکسیَتی دیدهشده، زمان پاسخ و لرزش را شبیهساز روی خطِ زمانِ صحیح "
        "میشمارد. [E] شدنیبودن را چککننده حکم میدهد و هر برنامهٔ شاهدی که "
        "برمیگرداند توسط راستیآزمای جداگانهای دوباره چک میشود که هیچ کدی با "
        "چککننده مشترک ندارد. وقتی دو ابزار اختلاف پیدا کردند، نخستین مظنون "
        "خودِ ابزار است، نه برهان و نه داده."),
    "p_model_1": (
        "One processor, preemptive, independent jobs, integer time. Execution "
        "time is taken equal to the worst-case estimate, so a schedule worked "
        "out by hand and the program's timeline can be compared unit by unit "
        "without tolerance. A preemption is counted but not charged to the "
        "timeline; overhead is therefore a measurement, not a distortion of "
        "the model. A job's slack is how long it could still wait and still "
        "meet its deadline.",
        "یک پردازنده، پیشگیرانه، کارهای مستقل، زمانِ صحیح. زمان اجرا برابر "
        "برآورد بدترین حالت گرفته میشود، پس برنامهٔ دستی و خطِ زمانِ برنامه "
        "بدون تلورانس واحدبهواحد قابلمقایسهاند. پیشگیری شمرده میشود ولی به خطِ "
        "زمان تحمیل نمیشود؛ سربار پس یک اندازهگیری است، نه تحریفِ مدل. لَکسیَتی "
        "یک کار یعنی چقدر دیگر میتواند صبر کند و همچنان به ضربالاجل برسد."),
    "p_model_2": (
        "The tie-break rule of LST is a parameter in the simulator, not a "
        "hidden implementation choice, because whether it changes correctness "
        "or cost is itself one of the questions of this project. The checker "
        "enumerates work-conserving schedules only; forced idle, when nothing "
        "has been released yet, is always allowed. Optional idle is a separate "
        "mode used as a control, never as the default.",
        "قاعدهٔ تساویشکنی در LST یک پارامتر در شبیهساز است، نه یک انتخابِ پنهانِ "
        "پیادهسازی، چون اینکه آیا درستی یا هزینه را عوض میکند خودش یکی از "
        "پرسشهای این پروژه است. چککننده فقط برنامههای بیوقفه را میپیماید؛ "
        "بیکاری اجباری، وقتی هنوز کاری منتشر نشده، همیشه مجاز است. بیکاری "
        "اختیاری حالتی جداگانه به عنوان کنترل است و هرگز پیشفرض نیست."),
    "p_deadlines": (
        "With implicit deadlines equal to periods and utilisation at most one, "
        "every synchronous periodic task set is feasible on a preemptive "
        "uniprocessor. An optimality experiment then has nothing to decide: the "
        "checker always says feasible and every optimal policy records the same "
        "zero misses. All experiments therefore use constrained deadlines, "
        "deadline smaller than the period, where utilisation is necessary but "
        "not sufficient and the feasible / infeasible split is real. This choice "
        "is a design decision about the measuring instrument, not a claim about "
        "the algorithm.",
        "با ضربالاجل ضمنی برابر دوره تناوب و بهرهوری حداکثر یک، هر مجموعهٔ "
        "دورهای همزمان روی یک پردازندهٔ پیشگیرانه شدنی است. آن وقت آزمایشِ "
        "بهینگی هیچ چیزی برای داوری ندارد: چککننده همیشه «شدنی» میگوید و "
        "همهٔ سیاستهای بهینه خطای صفر ثبت میکنند. پس همهٔ آزمایشها ضربالاجل "
        "مقید دارند، یعنی ضربالاجل کوچکتر از دوره تناوب، جایی که بهرهوری شرطِ "
        "لازم است نه کافی و شکافِ شدنی و نشدنی واقعی است. این انتخاب تصمیمی "
        "دربارهٔ ابزار اندازهگیری است، نه ادعایی دربارهٔ الگوریتم."),
    "p_design": (
        "[M] The table below lists every task set used in this exercise. All "
        "rows come from the same generator and the same seed; no set was "
        "removed because its result was inconvenient. The verdict column is "
        "[E]: it is the exhaustive checker's decision over one hyperperiod, "
        "with a witness re-checked independently. Periods, execution times, "
        "deadlines and phases are integers.",
        "[M] جدول زیر هر مجموعهکاری را که در این تمرین به کار رفته فهرست میکند. "
        "همهٔ ردیفها از یک مولد و یک بذر آمدهاند و هیچ مجموعهای به خاطر اینکه "
        "نتیجهاش ناخوشایند بوده حذف نشده است. ستون حکم [E] است: تصمیمِ چککنندهٔ جامع "
        "روی یک دورهٔ بزرگ، با شاهدی که جداگانه راستیآزمایی شده. دورهها، "
        "زمانهای اجرا، ضربالاجلها و فازها همگی صحیحاند."),
    "p_worked": (
        "The schedule below is reproduced from the generated data, not typed "
        "by hand. Each row is a maximal run of one job on the processor. It is "
        "the object that a hand computation must match unit for unit; the "
        "agreement between an independent hand trace and the simulator's "
        "timeline is itself a test in this repository.",
        "برنامهٔ زیر از دادهٔ تولیدشده بازتولید شده، نه با دست تایپ شده است. "
        "هر ردیف یک اجرای پیوستهٔ یک کار روی پردازنده است. این همان چیزی است "
        "که محاسبهٔ دستی باید واحدبهواحد با آن جور درآید؛ تطابقِ ردگیریِ دستیِ "
        "مستقل و خطِ زمانِ شبیهساز خودش یک تست در این مخزن است."),
    "p_set_1": (
        "[M] Every policy is run on exactly this task set with the same "
        "horizon. Columns count missed deadlines, preemptions, context "
        "switches, switches at zero laxity, the minimum laxity seen during the "
        "run, and instants where two or more ready jobs shared the minimum "
        "laxity. [E] The checker verdict and its state count are reported "
        "separately; the witness verdict is an independent re-check.",
        "[M] هر سیاست دقیقاً روی همین مجموعهکار و با همان افق اجرا میشود. "
        "ستونها ضربالاجلهای ازدسترفته، پیشگیریها، تعویضهای زمینه، تعویضها در "
        "لَکسیَتی صفر، کمینهٔ لَکسیَتی دیدهشده در اجرا، و لحظههایی را میشمارند "
        "که دو یا چند کار آماده کمینهٔ لَکسیَتی یکسان داشتند. [E] حکمِ چککننده و "
        "شمارشِ حالتهایش جداگانه گزارش میشود؛ حکمِ شاهد یک راستیآزمایی مستقل است."),
    "p_sweep": (
        "[M] A sweep changes one parameter and holds everything else fixed. "
        "The plot and the table are drawn from the same array in the generated "
        "data; the caption names the JSON path so a reader can re-read the "
        "values. Where the curves overlap, we write that the measurement does "
        "not separate the policies instead of inventing a ranking.",
        "[M] جاروب یک پارامتر را عوض میکند و بقیه را ثابت نگه میدارد. شکل و جدول "
        "از یک آرایه در دادهٔ تولیدشده کشیده میشوند و زیرنویس مسیر JSON را نام "
        "میکند تا خواننده بتواند عددها را دوباره بخواند. جایی که منحنیها "
        "همپوشانی دارند مینویسیم این اندازهگیری سیاستها را تفکیک نمیکند، به جای "
        "آنکه رتبهای بسازیم."),
    "p_finding": (
        "Each finding below states which instrument produced it, and the "
        "numbers are read from the generated data at build time. A finding "
        "labelled [E] is a verdict or a witness. A finding labelled [M] is a "
        "measured difference. A finding labelled [D] is a disagreement between "
        "the two, which we treat as a defect in an instrument until it is "
        "explained.",
        "هر یافتهٔ زیر میگوید کدام ابزار آن را تولید کرده و عددها هنگام ساخت از "
        "دادهٔ تولیدشده خوانده میشوند. یافتهٔ [E] یک حکم یا شاهد است. یافتهٔ "
        "[M] یک تفاوتِ اندازهگیریشده است. یافتهٔ [D] ناهماهنگیِ دو ابزار است "
        "که تا توضیح داده نشود آن را نقصِ ابزار میدانیم."),
    "p_disagreement": (
        "The naive comparison puts a checker over one hyperperiod next to a "
        "simulator running two hyperperiods. Those two are not looking at the "
        "same job set, so a mismatch is expected and is an artefact of the "
        "instrument, not a discovery about scheduling. The aligned comparison "
        "gives both instruments the jobs released in one hyperperiod and enough "
        "time to finish them. The counts below show how much of the apparent "
        "disagreement disappears once the instruments are aligned. This is the "
        "same lesson learned earlier in this project, when the checker called a "
        "feasible set infeasible because it treated a forced idle instant as a "
        "dead end: the bug was in the checker.",
        "مقایسهٔ سادهلوح چککنندهای روی یک دورهٔ بزرگ را کنار شبیهسازی دو دورهٔ "
        "بزرگ میگذارد. این دو به یک مجموعهٔ کارها نگاه نمیکنند، پس ناهماهنگی "
        "منتظره است و مصنوعِ ابزار است، نه کشفی دربارهٔ زمانبندی. مقایسهٔ همتراز "
        "به هر دو ابزار کارهای منتشرشده در یک دورهٔ بزرگ و زمانِ کافی برای تمام "
        "کردنشان میدهد. شمارشهای زیر نشان میدهد چه مقدار از اختلافِ ظاهری پس از "
        "همترازکردن ناپدید میشود. این همان درسی است که پیشتر در این پروژه آموخته "
        "شد، وقتی چککننده مجموعهای شدنی را نشدنی گفت چون یک لحظهٔ بیکاری اجباری "
        "را بنبست حساب کرده بود: باگ از خودِ چککننده بود."),
    "p_limits": (
        "The model is a single preemptive processor with no release cost, no "
        "cache or migration effects and execution equal to the worst case. "
        "Therefore these measurements say nothing about multicore behaviour "
        "or about runtime variance. The checker's verdict is exact only for "
        "the enumerated job set and only when its run was not truncated; every "
        "truncation flag is reported and no conclusion is drawn from a "
        "truncated run. Utilisation is a descriptive ratio here, never a "
        "schedulability test. Finally, a measurement that does not separate two "
        "policies is reported as inconclusive rather than as a tie broken by "
        "preference.",
        "مدل یک پردازندهٔ پیشگیرانهٔ تک هستهای است، بدون هزینهٔ انتشار، بدون اثر "
        "نهانگاه یا جابهجایی، و با اجرای برابر بدترین حالت. پس این اندازهگیریها "
        "دربارهٔ رفتار چند هستهای یا پراکندگی زمان اجرا حرفی نمیزنند. حکمِ "
        "چککننده فقط برای همان مجموعهٔ کارهای شمردهشده و فقط وقتی دقیق است که "
        "اجرایش بریده نشده باشد؛ هر پرچمِ بریدگی گزارش میشود و از اجرای بریدهشده "
        "نتیجهای گرفته نمیشود. بهرهوری اینجا یک نسبتِ توصیفی است، نه آزمونِ "
        "شدنیبودن. سرانجام، اندازهای که دو سیاست را تفکیک نکند به جای آنکه با "
        "سلیقه رتبهبندی شود، بیتصمیم گزارش میشود."),
    "p_repro": (
        "Every artefact is regenerated by the commands below, from the exercise "
        "folder or from the multi-exercise tree root. The seed, the policy list "
        "and the figure list are read from the generated data; deleting any "
        "output file and re-running must reproduce byte-identical numbers. "
        "The report itself is built from a content module that contains prose "
        "only.",
        "همهٔ خروجیها با دستورهای زیر بازتولید میشوند، از پوشهٔ تمرین یا از "
        "ریشهٔ درختِ چندتمرینیه. بذر، فهرست سیاستها و فهرست شکلها از دادهٔ "
        "تولیدشده خوانده میشوند؛ پاک کردن هر فایل خروجی و اجرای دوباره باید "
        "عددهایی یکسان بایتبهبایت بدهد. خودِ گزارش از ماژولِ محتوایی ساخته "
        "میشود که فقط نثر دارد."),
    "p_deliverables": (
        "The table lists the artefacts of this exercise. Word and PDF are "
        "rendered from one content model, so their page counts agree with the "
        "generator's explicit page list; the exact PDF count is read back from "
        "the file by the checker. The Markdown file is a by-product of the same "
        "model. Speaker decks, where required, carry notes on every slide.",
        "جدول خروجیهای این تمرین را فهرست میکند. Word و PDF از یک مدلِ محتوا "
        "رندر میشوند، پس شمارشِ صفحههایشان با فهرستِ صریحِ صفحههای مولد یکی "
        "است؛ شمارش دقیق PDF توسط چککننده از خودِ فایل خوانده میشود. فایل "
        "Markdown محصول جانبی همان مدل است. دکهای ارائه، جایی که لازم باشد، "
        "روی همهٔ اسلایدها یادداشت گوینده دارند."),
    "p_appendix": (
        "The generated data file is the single source of numbers. Its top-level "
        "keys are listed below together with what they contain. A test in this "
        "repository checks that every numeric token in the generated report "
        "also occurs in this file or in values derived from it; a typed-in "
        "measurement would fail that test.",
        "فایل دادهٔ تولیدشده یگانه مرجعِ عددها است. کلیدهای سطحِ بالای آن همراه "
        "با محتوایشان در زیر آمده است. تستی در این مخزن چک میکند که هر نشانهٔ "
        "عددی در گزارش ساختهشده در همین فایل یا در مقادیر مشتقشده از آن هم "
        "باشد؛ عددِ دستنوشته آن تست را رد میکند."),
    "p_figures": (
        "All figures are generated from the same data file. Plot labels are "
        "deliberately plain ASCII identifiers so that the images are "
        "reproducible without a shaping stack; the bilingual explanation lives "
        "in the captions and in the surrounding text. Each caption names the "
        "JSON path the values were read from.",
        "همهٔ شکلها از همان فایل داده ساخته میشوند. برچسبهای شکلها عمداً "
        "شناسههای سادهٔ لاتیناند تا تصویرها بدون لایهٔ شکلدهی فارسی هم "
        "بازتولید شوند؛ توضیح دوزبانه در زیرنویسها و متن اطراف است. هر "
        "زیرنویس مسیر JSONای را نام میکند که عددها از آن خوانده شدهاند."),
    "p_profile": (
        "[M] This page collects one policy across every task set in the "
        "exercise, so a reader can see the dispersion rather than a single "
        "average. Totals are sums over the rows shown; they are computed from "
        "the generated data at build time. A policy with no missed deadlines "
        "can still be the most expensive one to run.",
        "[M] این صفحه یک سیاست را روی همهٔ مجموعهکارهای تمرین گرد میآورد تا "
        "خواننده پراکندگی را ببیند نه فقط یک میانگین. جمعها روی ردیفهای نشاندادهشده "
        "حساب شده و هنگام ساخت از دادهٔ تولیدشده به دست میآیند. سیاستی که هیچ "
        "ضربالاجلی را از دست ندهد میتواند همچنان پرهزینهترین سیاست باشد."),

    "h_design": ("Set | U | hyperperiod | D < T | verdict",
                 "مجموعه | U | دورهٔ بزرگ | ضربالاجل مقید | حکم"),
    "s_specs": ("Task specifications", "مشخصات کارها"),
    "h_policy": ("Policy | missed | preemptions | switches | zero-sw | min laxity | ties",
                 "سیاست | خطا | پیشگیری | تعویض | تعویض صفر | کمینه لَکسیَتی | تساوی"),
    "h_profile": ("Set | missed | preemptions | switches | zero-sw | min laxity | ties | jitter",
                  "مجموعه | خطا | پیشگیری | تعویض | تعویض صفر | کمینه لَکسیَتی | تساوی | لرزش"),
    "h_alignment": ("Set | checker | naive agrees | aligned agrees | aligned horizon",
                    "مجموعه | چککننده | سادهلوح جور است | همتراز جور است | افق همتراز"),
    "h_deliverables": ("Artefact | kind | how it is produced",
                       "خروجی | نوع | چطور ساخته میشود"),

    "yes": ("yes", "بله"),
    "no": ("no", "خیر"),
    "feasible": ("feasible", "شدنی"),
    "infeasible": ("infeasible", "نشدنی"),
    "valid": ("valid", "معتبر"),
    "invalid": ("invalid", "نامعتبر"),
    "none": ("not applicable", "کاربرد ندارد"),
    "label_e": ("[E] exhaustive verification", "[E] بررسی جامع"),
    "label_m": ("[M] measurement", "[M] اندازهگیری"),
    "label_d": ("[D] disagreement", "[D] ناهماهنگی"),
    "label_b": ("[E] + [M]", "[E] + [M]"),
    "note_alignment": ("Instrument alignment", "همترازسازی ابزار"),
    "note_set": ("What this set shows", "این مجموعه چه نشان میدهد"),
    "note_sweep": ("Reading the sweep", "خواندن جاروب"),
    "note_finding": ("Why this is a finding", "چرا این یک یافته است"),
    "note_limits": ("Stated in advance", "پیشاپیش نوشته شده"),
    "note_profile": ("Cost, not correctness", "هزینه، نه درستی"),

    "kv_seed": ("Random seed", "بذر تصادف"),
    "kv_policies": ("Policies measured", "سیاستهای اندازهگیریشده"),
    "kv_sets": ("Task sets", "مجموعهکارها"),
    "kv_figures": ("Figures", "شکلها"),
    "kv_findings": ("Findings", "یافتهها"),
    "kv_sweeps": ("Sweeps", "جاروبها"),
    "kv_feasible": ("Feasible sets [E]", "مجموعههای شدنی [E]"),
    "kv_infeasible": ("Infeasible sets [E]", "مجموعههای نشدنی [E]"),
    "kv_witness": ("Independently valid witnesses", "شاهدهای مستقل معتبر"),
    "kv_states": ("Checker states visited [E]", "حالتهای پیمودهشده [E]"),
    "kv_truncated": ("Truncated checker runs", "اجراهای بریدهشده چککننده"),
    "kv_aligned": ("Aligned comparisons agreeing", "مقایسههای همترازِ جور"),
    "kv_naive": ("Naive comparisons agreeing", "مقایسههای سادهلوحِ جور"),
    "kv_total_pre": ("Total preemptions [M]", "جمع پیشگیریها [M]"),
    "kv_total_miss": ("Total missed deadlines [M]", "جمع خطاها [M]"),
    "kv_total_zero": ("Total zero-laxity switches [M]", "جمع تعویضهای لَکسیَتی صفر [M]"),
    "kv_total_tie": ("Total tie events [M]", "جمع رخدادهای تساوی [M]"),
    "kv_verdict": ("Checker verdict [E]", "حکم چککننده [E]"),
    "kv_states_set": ("States visited [E]", "حالتهای پیمودهشده [E]"),
    "kv_pruned": ("Branches pruned [E]", "شاخههای هرسشده [E]"),
    "kv_trunc": ("Checker truncated", "چککننده بریده شد"),
    "kv_idle": ("Idle enumeration agrees [E]", "بیکاری اختیاری همنظر است [E]"),
    "kv_witness_v": ("Independent witness", "شاهد مستقل"),
    "kv_aligned_ok": ("Aligned comparison agrees", "مقایسهٔ همتراز جور است"),
    "kv_naive_ok": ("Naive comparison agrees", "مقایسهٔ سادهلوح جور است"),
    "kv_spec": ("Task specification", "مشخصات کارها"),
    "kv_u": ("Utilisation (descriptive)", "بهروری (توصیفی)"),
    "kv_hp": ("Hyperperiod", "دورهٔ بزرگ"),
    "kv_constrained": ("Constrained deadline", "ضربالاجل مقید"),
    "kv_jobs": ("Jobs in checker horizon", "کارها در افق چککننده"),
    "kv_schedule": ("Witness length", "طول شاهد"),
    "kv_source": ("Values read from", "عددها خواندهشده از"),
    "kv_kind": ("Instrument", "ابزار"),
    "kv_scope": ("Scope", "گستره"),
    "kv_reason": ("Verifier reason", "دلیل راستیآزما"),
    "kv_agree": ("Hand trace agrees [M]", "ردگیری دستی جور است [M]"),
    "kv_steps": ("Steps compared [M]", "گامهای مقایسهشده [M]"),
    "kv_extra": ("Extra measurement", "اندازهگیری اضافی"),
}

QUESTION = {
    1: ("What is slack, what exactly does LST minimise, and what does that "
        "choice cost once it is measured rather than defined?",
        "لَکسیَتی چیست، LST دقیقاً چه چیزی را کمینه میکند، و این انتخاب وقتی "
        "اندازهگیری شود نه تعریف، چه هزینهای دارد؟"),
    2: ("How does LST compare with EDF and RM on light, heavy, harmonic and "
        "constrained-deadline workloads, on more than one metric?",
        "LST در برابر EDF و RM روی بارهای سبک، سنگین، هماهنگ و ضربالاجلمقید، "
        "با بیش از یک سنجه، چگونه است؟"),
    3: ("Can a hand-worked LST schedule and an independent program trace be "
        "made to agree unit for unit, and where do they part company?",
        "آیا یک برنامهٔ دستی LST و یک ردگیری مستقل از برنامه را میتوان "
        "واحدبهواحد برابر کرد، و کجا از هم جدا میشوند؟"),
    4: ("Does the optimality claim survive an exhaustive search over thousands "
        "of constrained-deadline task sets, and what happens under overload?",
        "آیا ادعای بهینگی در برابر جستجوی جامع روی هزاران مجموعهٔ ضربالاجلمقید "
        "دوام میآورد، و زیر بارِ اضافه چه رخ میدهد؟"),
    5: ("Explain LST in a few minutes to somebody who knows nothing about it, "
        "using only numbers that other exercises actually produced.",
        "LST را در چند دقیقه برای کسی که هیچ نمیداند توضیح بده، فقط با عددهایی "
        "که تمرینهای دیگر واقعاً تولید کردهاند."),
    6: ("Combine the previous exercises into one bilingual paper: what LST is, "
        "where it stands against its rivals, what is certainly true about it, "
        "and what it costs.",
        "تمرینهای پیشین را در یک مقالهٔ دوزبانه ترکیب کن: LST چیست، نسبت به "
        "رقیبانش کجاست، چه چیزی دربارهاش قطعاً درست است، و چه هزینهای دارد."),
    7: ("What does tie-breaking actually change, and how expensive is "
        "laxity-zero thrashing when measurement and verification are kept "
        "apart?",
        "تساویشکنی واقعاً چه چیزی را عوض میکند، و لرزشِ لَکسیَتی صفر وقتی "
        "اندازهگیری و بررسی جدا نگه داشته شوند چقدر هزینه دارد؟"),
}

TITLE = {
    1: ("LST — What the Algorithm Actually Minimises",
        "LST — الگوریتم واقعاً چه چیزی را کمینه میکند"),
    2: ("LST against EDF and RM on Measured Workloads",
        "LST در برابر EDF و RM روی بارهای اندازهگیریشده"),
    3: ("A Hand-Worked LST Schedule and an Independent Trace",
        "برنامهٔ دستی LST و یک ردگیری مستقل"),
    4: ("Optimality, Exhaustive Verification and Overload",
        "بهینگی، بررسی جامع و بار اضافه"),
    5: ("LST Explained in a Short Bilingual Presentation",
        "LST در یک ارائهٔ کوتاه دوزبانه"),
    6: ("A Bilingual Paper and Seminar on Least Slack Time",
        "مقاله و سمینار دوزبانه دربارهٔ کمترین لَکسیَتی"),
    7: ("Tie-Breaking, Laxity-Zero Thrashing and Their Cost",
        "تساویشکنی، لرزشِ لَکسیَتی صفر و هزینهٔ آنها"),
}

SUBTITLE = {
    1: ("integer-time simulation, an exhaustive feasibility checker, and "
        "measured preemption cost",
        "شبیهسازی با زمان صحیح، چککنندهٔ جامع شدنیبودن، و هزینهٔ پیشگیری اندازهگیریشده"),
    2: ("nine policies, several workload families, several metrics",
        "نه سیاست، چند خانوادهٔ بار کاری، چند سنجه"),
    3: ("the hand table, the machine table, and a witness of divergence",
        "جدول دستی، جدول ماشین، و شاهدی از واگرایی"),
    4: ("fixed seed, constrained deadlines, independent witness verification",
        "بذر ثابت، ضربالاجل مقید، راستیآزمایی مستقل شاهدها"),
    5: ("speaker notes on every slide, numbers inherited from earlier exercises",
        "یادداشت گوینده روی هر اسلاید، عددها به ارث رسیده از تمرینهای پیشین"),
    6: ("every number read at build time from the earlier exercises' data",
        "هر عدد هنگام ساخت از دادهٔ تمرینهای پیشین خوانده میشود"),
    7: ("the checker is silent about cost; the simulator is not",
        "چککننده دربارهٔ هزینه ساکت است؛ شبیهساز نه"),
}

BRANCH = {
    1: "Exercise-1-LST-Introduction",
    2: "Exercise-2-LST-EDF-RM-Comparison",
    3: "Exercise-3-LST-Manual-Scheduling",
    4: "Exercise-4-LST-Optimality-And-Overload",
    5: "Exercise-5-LST-Presentation",
    6: "Exercise-6-LST-Paper-And-Seminar",
    7: "Exercise-7-LST-Tie-Breaking-And-Thrashing",
}


def t(lang: str, key: str) -> str:
    en, fa = S[key]
    return en if lang == "en" else fa


def yn(lang: str, value) -> str:
    return t(lang, "yes") if value else t(lang, "no")


def _b(lang: str, key: str):
    return en_fa(lang, *S[key])


def en_fa(lang: str, en: str, fa: str) -> str:
    return en if lang == "en" else fa


def kind_label(lang: str, kind: str) -> str:
    return {"E": t(lang, "label_e"), "M": t(lang, "label_m"),
            "D": t(lang, "label_d"), "B": t(lang, "label_b")}.get(kind, kind)


# --------------------------------------------------------------------------
# page builders
# --------------------------------------------------------------------------

def _cov(lang: str, n: int, D: dict):
    meta = D["meta"]
    return [
        (t(lang, "meta_exercise"), en_fa(lang, f"Exercise {n}",
                                         f"تمرین {n}")),
        (t(lang, "meta_course"), t(lang, "course")),
        (t(lang, "meta_topic"), t(lang, "topic")),
        (t(lang, "meta_deliverables"), t(lang, "deliverables_value")),
        (t(lang, "meta_repo"), "github.com/rera13197-ux/LST"),
        (t(lang, "meta_branch"), BRANCH[n]),
        (t(lang, "meta_seed"), str(meta.get("seed", ""))),
        (t(lang, "meta_status"), t(lang, "status_value")),
        (t(lang, "meta_pages"), t(lang, "pages_value")),
        (t(lang, "meta_method"), t(lang, "method_value")),
    ]


def _design_rows(D: dict, lang: str):
    rows = []
    for s in D["sets"]:
        rows.append([s["id"], str(s["utilisation"]), str(s["hyperperiod"]),
                     yn(lang, s["constrained"]),
                     t(lang, "feasible" if s["feasible"] else "infeasible")])
    return rows


def _spec_lines(D: dict):
    return [f"{s['id']}: {s['spec']}" for s in D["sets"]]


def _set_note(lang: str, s: dict) -> str:
    pol = s["policies"]
    lstp = pol.get("lst", {}).get("preemptions")
    edfp = pol.get("edf", {}).get("preemptions")
    miss = pol.get("lst", {}).get("missed")
    if lang == "en":
        return (f"[E] verdict {('feasible' if s['feasible'] else 'infeasible')}, "
                f"{s['states']} states, {s['pruned']} pruned, "
                f"independent witness "
                f"{('valid' if s['witness'].get('valid') else 'not applicable')}. "
                f"[M] LST recorded {lstp} preemptions and {miss} missed "
                f"deadlines; EDF recorded {edfp} preemptions on the same set. "
                f"Tie events observed: {pol.get('lst', {}).get('tie_events')}.")
    return (f"[E] حکم {('شدنی' if s['feasible'] else 'نشدنی')}، "
            f"{s['states']} حالت، {s['pruned']} شاخهٔ هرسشده، شاهد مستقل "
            f"{('معتبر' if s['witness'].get('valid') else 'کاربرد ندارد')}. "
            f"[M] LST برابر {lstp} پیشگیری و {miss} ضربالاجل ازدسترفته ثبت کرد؛ "
            f"EDF روی همان مجموعه {edfp} پیشگیری داشت. رخدادهای تساوی دیدهشده: "
            f"{pol.get('lst', {}).get('tie_events')}.")


def _sweep_table(sw: dict):
    head = [sw.get("xlabel") or "x"] + [s["name"] for s in sw["series"]]
    rows = []
    for i, x in enumerate(sw["x"]):
        rows.append([str(x)] + [str(s["values"][i]) for s in sw["series"]])
    return head, rows


def _finding_kv(f: dict, lang: str):
    pairs = [[en_fa(lang, "Key", "کلید"), en_fa(lang, "Value", "مقدار")]]
    for k, v in (f.get("numbers") or {}).items():
        pairs.append([str(k).replace("_", " "), str(v)])
    return pairs


def _figure_caption(lang: str, fig: dict) -> str:
    return en_fa(lang,
                 f"{fig['title']} — values from {fig['source']}",
                 f"{fig['title']} — عددها از {fig['source']}")


def make_report(n: int, lang: str) -> Report:
    D = importlib.import_module(f"lst{n}_data").data()
    meta, derived = D["meta"], D["derived"]
    title = TITLE[n][0 if lang == "en" else 1]
    subtitle = SUBTITLE[n][0 if lang == "en" else 1]
    r = Report(title, subtitle, lang, cover_meta=_cov(lang, n, D))
    pages = []

    def add(*blocks):
        pages.append(list(blocks))

    # -- cover / toc ----------------------------------------------------
    add(cover(_cov(lang, n, D)))
    add(toc())

    # -- question -------------------------------------------------------
    q = QUESTION[n][0 if lang == "en" else 1]
    add(ptitle(t(lang, "s_question")),
        para(q),
        para(en_fa(lang,
                   "This report states what was asked and how it was answered "
                   "before giving any result, so that a reader can try to "
                   "refute the claim.",
                   "این گزارش نخست میگوید چه پرسیده شد و چگونه پاسخ داده شد، "
                   "بعد نتیجه میدهد، تا خواننده بتواند سعی کند ادعا را رد کند.")),
        kv([[t(lang, "kv_kind"), t(lang, "label_b")],
            [t(lang, "kv_scope"), meta.get("scope_en" if lang == "en" else "scope_fa", "")],
            [t(lang, "kv_seed"), str(meta.get("seed", ""))],
            [t(lang, "kv_sets"), str(derived["task_set_count"])],
            [t(lang, "kv_policies"), str(derived["policy_count"])]],
           caption=en_fa(lang, "Scope of this exercise", "گسترهٔ این تمرین")),
        note(en_fa(lang,
                   "Nothing in this report is a definition restated louder. "
                   "The subject is what the two instruments reveal when they "
                   "are pointed at the same task sets.",
                   "هیچ چیز در این گزارش تعریفی نیست که بلندتر تکرار شده باشد. "
                   "موضوع آن چیزی است که دو ابزار وقتی به یک مجموعهٔ کارها "
                   "نشانه گرفته شوند آشکار میکنند."),
             caption=en_fa(lang, "Intent", "قصد")))

    # -- instruments ----------------------------------------------------
    add(ptitle(t(lang, "s_instruments")),
        para(t(lang, "p_instruments_1")),
        h1(en_fa(lang, "Which claim comes from where", "کدام ادعا از کجا میآید")),
        bullets([
            t(lang, "label_e") + " — " + en_fa(lang, "feasibility, witnesses, "
              "idle-enumeration controls, optimality counterexamples.",
              "شدنیبودن، شاهدها، کنترلهای بیکاری اختیاری، counterexampleهای بهینگی."),
            t(lang, "label_m") + " — " + en_fa(lang, "preemptions, switches, "
              "laxity-zero switches, tie events, response time, jitter, "
              "first miss.",
              "پیشگیریها، تعویضها، تعویضهای لَکسیَتی صفر، رخدادهای تساوی، "
              "زمان پاسخ، لرزش، نخستین خطا."),
            t(lang, "label_d") + " — " + en_fa(lang, "a mismatch; the "
              "instrument is suspected first.", "ناهماهنگی؛ نخست ابزار مظنون است."),
        ]),
        para(t(lang, "p_instruments_2")),
        note(en_fa(lang,
                   "Every witness schedule returned by the checker is walked "
                   "again by a verifier that does not call the checker. This "
                   "is a standing rule, not a one-off check.",
                   "هر برنامهٔ شاهدی که چککننده برمیگرداند دوباره توسط "
                   "راستیآزمایی پیموده میشود که چککننده را فرا نمیزند. این "
                   "قاعدهای دائمی است، نه یک بررسی یکباره."),
             caption=en_fa(lang, "Standing rule", "قاعدهٔ دائمی")))

    # -- model ----------------------------------------------------------
    add(ptitle(t(lang, "s_model")),
        para(t(lang, "p_model_1")),
        formula("laxity(job, t) = deadline(job) - t - remaining(job)\n"
                "LST(t)        = argmin laxity(job, t) over ready jobs",
                caption=en_fa(lang, "Definition, not a measurement",
                              "تعریف، نه اندازهگیری")),
        kv([[en_fa(lang, "Symbol", "نماد"), en_fa(lang, "Meaning", "معنی")],
            ["T", en_fa(lang, "period", "دوره تناوب")],
            ["C", en_fa(lang, "worst-case execution, equal to actual here",
                        "بدترین زمان اجرا، اینجا برابر اجرای واقعی")],
            ["D", en_fa(lang, "relative deadline", "ضربالاجل نسبی")],
            ["t", en_fa(lang, "integer time instant", "لحظهٔ صحیح زمان")],
            ["U", en_fa(lang, "descriptive utilisation ratio",
                        "نسبت بهرهوری توصیفی")]],
           caption=en_fa(lang, "Notation", "نمادگذاری")),
        para(t(lang, "p_model_2")))

    # -- pseudocode -----------------------------------------------------
    add(ptitle(t(lang, "s_pseudocode")),
        para(en_fa(lang,
                   "The rule is short; the interesting part is what it does "
                   "when two jobs reach the same slack. The tie-break is an "
                   "explicit parameter of the simulator.",
                   "قاعده کوتاه است؛ بخش جالب آنجا است که دو کار به لَکسیَتی "
                   "یکسان میرسند. تساویشکنی پارامتری صریح در شبیهساز است.")),
        code(["at every integer instant t:",
              "    release every job whose release time is t",
              "    mark a job missed if t reaches its deadline",
              "    ready = jobs released and not finished",
              "    if ready is empty: idle for this unit (forced idle)",
              "    else:",
              "        slack(j) = deadline(j) - t - remaining(j)",
              "        best     = min slack over ready",
              "        run the ready job attaining best, chosen by tie_break",
              "        count a preemption if the previous job still has work",
              "        count a laxity-zero switch if both slacks are zero"],
             caption=en_fa(lang, "Discrete-time rule as implemented in the core",
                           "قاعدهٔ زمانگسسته همانطور که در هسته پیاده شده")),
        h1(en_fa(lang, "Tie-break policies", "سیاستهای تساویشکنی")),
        bullets([
            "lst / lst:edf / lst:rm / lst:stay / lst:lzs — " + en_fa(lang,
                "index, earliest deadline, shortest period, keep the running "
                "job, or switch by earliest deadline at zero laxity.",
                "اندیس، زودترین ضربالاجل، کوتاهترین دوره، نگهداشتن کار در حال "
                "اجرا، یا جابهجایی بر پایهٔ زودترین ضربالاجل در لَکسیَتی صفر."),
            "edf / rm / dm / fifo — " + en_fa(lang,
                "baseline policies with no tie-break parameter.",
                "سیاستهای مبنا بدون پارامتر تساویشکنی."),
        ]),
        note(en_fa(lang,
                   "The tie-break never silently changes: it is part of the "
                   "policy name and of every generated data row.",
                   "تساویشکنی هرگز بیتوجه عوض نمیشود: بخشی از نام سیاست و "
                   "هر ردیف دادهٔ تولیدشده است."),
             caption=en_fa(lang, "Parameter, not detail", "پارامتر، نه جزئیات")))

    # -- constrained deadlines -----------------------------------------
    add(ptitle(t(lang, "s_deadlines")),
        para(t(lang, "p_deadlines")),
        kv([[en_fa(lang, "Regime", "رژیم"),
             en_fa(lang, "What the checker can say", "چککننده چه میتواند بگوید")],
            [en_fa(lang, "implicit deadline, U no more than one",
                   "ضربالاجل ضمنی، U حداکثر یک"),
             en_fa(lang, "always feasible, so no optimality test",
                   "همیشه شدنی، پس آزمون بهینگی بیمعنا")],
            [en_fa(lang, "constrained deadline", "ضربالاجل مقید"),
             en_fa(lang, "feasible and infeasible sets both occur",
                   "هم مجموعهٔ شدنی و هم نشدنی پیدا میشود")]],
           caption=en_fa(lang, "Design of the measuring instrument",
                         "طراحی ابزار اندازهگیری")),
        note(en_fa(lang,
                   f"In this exercise {derived['constrained_count']} of "
                   f"{derived['task_set_count']} sets use a constrained "
                   f"deadline. The split into {derived['feasible_count']} "
                   f"feasible and {derived['infeasible_count']} infeasible "
                   f"sets is the [E] verdict, not a guess.",
                   f"در این تمرین {derived['constrained_count']} مجموعه از "
                   f"{derived['task_set_count']} مجموعه ضربالاجل مقید دارند. "
                   f"تقسیم به {derived['feasible_count']} شدنی و "
                   f"{derived['infeasible_count']} نشدنی حکم [E] است، نه حدس."),
             caption=en_fa(lang, "The split used here", "شکافِ بهکاررفته اینجا")))

    # -- design ---------------------------------------------------------
    add(ptitle(t(lang, "s_design")),
        para(t(lang, "p_design")),
        code(_spec_lines(D),
             caption=en_fa(lang, "Full task specifications, read from the data file",
                           "مشخصات کامل کارها، خواندهشده از فایل داده")),
        table(t(lang, "h_design").split(" | "),
              _design_rows(D, lang),
              caption=en_fa(lang, "Task sets used, read from experiments.json",
                            "مجموعهکارهای بهکاررفته، خواندهشده از experiments.json")),
        kv([[t(lang, "kv_seed"), str(meta.get("seed", ""))],
            [t(lang, "kv_policies"), str(derived["policy_count"])],
            [t(lang, "kv_feasible"), str(derived["feasible_count"])],
            [t(lang, "kv_infeasible"), str(derived["infeasible_count"])],
            [t(lang, "kv_states"), str(derived["checker_states_total"])],
            [t(lang, "kv_truncated"), str(derived["truncated_count"])]],
           caption=en_fa(lang, "Generated data at a glance",
                         "نگاهی به دادهٔ تولیدشده")))

    # -- worked schedule ------------------------------------------------
    worked = D["manual"].get("gantt") if D["manual"] else None
    if not worked and D["sets"]:
        worked = D["sets"][0]["gantt"].get("lst", [])
    gl = [f"{row[0]}  [{row[1]}, {row[2]})" for row in (worked or [])[:14]]
    add(ptitle(t(lang, "s_worked")),
        para(t(lang, "p_worked")),
        code(gl or ["(no schedule in the generated data)"],
             caption=en_fa(lang, "Runs read from the generated data",
                           "اجراها خواندهشده از دادهٔ تولیدشده")),
        kv([[t(lang, "kv_source"),
             "output/experiments.json"]] +
           ([[t(lang, "kv_agree"),
              str(D["manual"].get("agree", ""))],
             [t(lang, "kv_steps"),
              str(D["manual"].get("compared_steps", ""))]]
            if D["manual"] else []),
           caption=en_fa(lang, "Trace provenance", "منشأ ردگیری")),
        note(en_fa(lang,
                   "The hand trace and the simulator are two independent "
                   "programs. Their agreement is checked by a test, and their "
                   "disagreement would be reported as an instrument defect.",
                   "ردگیری دستی و شبیهساز دو برنامهٔ مستقلاند. تطابقشان را یک "
                   "تست چک میکند و ناهماهنگیشان به عنوان نقصِ ابزار گزارش "
                   "میشود."),
             caption=en_fa(lang, "Why two programs", "چرا دو برنامه")))

    # -- hand table and divergence (exercise 3, data-driven) -------------
    hand = D["manual"]
    if hand.get("rows"):
        hrows = []
        for row in hand["rows"][:13]:
            hrows.append([str(row["t"]), ", ".join(row["ready"]) or "-",
                          ", ".join(str(v) for v in row.get("laxity", [])) or "-",
                          str(row["chosen"] or "-")])
        add(ptitle(t(lang, "s_hand")),
            para(t(lang, "p_hand")),
            table(t(lang, "h_hand").split(" | "), hrows,
                  caption=en_fa(lang, "Independent hand trace, read from the data file",
                                "ردگیری دستی مستقل، خواندهشده از فایل داده")),
            kv([[t(lang, "kv_agree"), yn(lang, hand.get("agree"))],
                [t(lang, "kv_steps"), str(hand.get("compared_steps", ""))],
                [t(lang, "kv_source"), "output/experiments.json"]],
               caption=en_fa(lang, "Agreement with the simulator [M]",
                             "تطابق با شبیهساز [M]")))
    div = hand.get("divergence") or D["extra"].get("divergence")
    if div:
        wit = [f"t={w[0]}  LST={w[1]}  EDF={w[2]}" for w in div.get("witness", [])[:10]]
        add(ptitle(t(lang, "s_divergence")),
            para(t(lang, "p_divergence")),
            kv([[en_fa(lang, "First divergence at t", "نخستین واگرایی در t"),
                 str(div.get("first_divergence"))],
                [en_fa(lang, "Differing instants", "لحظههای متفاوت"),
                 str(div.get("divergent_count"))],
                [en_fa(lang, "Steps compared", "گامهای مقایسهشده"),
                 str(div.get("compared_steps"))]],
               caption=en_fa(lang, "Witness summary [M]", "خلاصهٔ شاهد [M]")),
            code(wit or ["(no divergence in the generated data)"],
                 caption=en_fa(lang, "Divergence witness, printed from the data",
                               "شاهد واگرایی، چاپشده از داده")),
            note(en_fa(lang,
                       "A verbal claim that two policies differ is weaker than "
                       "a printed witness. Here the witness is data, and it can "
                       "be re-read from the generated file.",
                       "ادعای کلامی که دو سیاست فرق دارند ضعیفتر از شاهدِ چاپشده "
                       "است. اینجا شاهد داده است و میتوان آن را دوباره از فایل "
                       "تولیدشده خواند."),
                 caption=en_fa(lang, "Witness over assertion", "شاهد به جای ادعا")))

    # -- one page per task set ------------------------------------------
    for s in D["sets"][:10]:
        add(ptitle(f"{t(lang, 's_set')} {s['id']}"),
            kv([
                [t(lang, "kv_spec"), s["spec"]],
                [t(lang, "kv_u"), str(s["utilisation"])],
                [t(lang, "kv_hp"), str(s["hyperperiod"])],
                [t(lang, "kv_constrained"), yn(lang, s["constrained"])],
                [t(lang, "kv_verdict"),
                 t(lang, "feasible" if s["feasible"] else "infeasible")],
                [t(lang, "kv_states_set"), str(s["states"])],
                [t(lang, "kv_pruned"), str(s["pruned"])],
                [t(lang, "kv_jobs"), str(s["jobs"])],
                [t(lang, "kv_trunc"), yn(lang, s["truncated"])],
                [t(lang, "kv_idle"), yn(lang, s["idle_agrees"])],
                [t(lang, "kv_witness_v"),
                 (t(lang, "valid") if s["witness"].get("valid") else
                  t(lang, "invalid") if s["witness"].get("valid") is False else
                  t(lang, "none"))],
                [t(lang, "kv_aligned_ok"), yn(lang, s["alignment"]["aligned_agrees"])],
                [t(lang, "kv_naive_ok"), yn(lang, s["alignment"]["naive_agrees"])],
            ], caption=en_fa(lang, "Set parameters and [E] verdict",
                             "پارامترهای مجموعه و حکم [E]")),
            table(t(lang, "h_policy").split(" | "), s["policy_rows"],
                  caption=en_fa(lang, "All policies on this set [M]",
                                "همهٔ سیاستها روی این مجموعه [M]")),
            note(_set_note(lang, s), caption=t(lang, "note_set")))

    # -- sweeps ---------------------------------------------------------
    for sw in D["sweeps"][:4]:
        head, rows = _sweep_table(sw)
        fig_file = sw.get("figure")
        blocks = [ptitle(f"{t(lang, 's_sweeps')}: {sw['id']}"),
                  para(t(lang, "p_sweep")),
                  kv([[t(lang, "kv_source"), sw.get("source", "")],
                      [en_fa(lang, "Swept parameter", "پارامتر جاروبشده"),
                       sw.get("xlabel", "")]],
                     caption=en_fa(lang, "Provenance", "منشأ"))]
        if fig_file:
            fig = next((f for f in D["figures"] if f["file"] == fig_file), None)
            if fig:
                blocks.append(image(fig_file, width_cm=13.2,
                                    caption=_figure_caption(lang, fig)))
        blocks += [table(head, rows, caption=en_fa(lang, "Values behind the plot",
                                                   "عددهای پشت شکل")),
                   note(en_fa(lang,
                              f"{len(sw['x'])} points and {len(sw['series'])} "
                              f"series are plotted. Where ranges overlap the "
                              f"measurement does not separate the policies.",
                              f"{len(sw['x'])} نقطه و {len(sw['series'])} سری "
                              f"رسم شده است. جایی که بازهها همپوشانی دارند "
                              f"اندازهگیری سیاستها را تفکیک نمیکند."),
                        caption=t(lang, "note_sweep"))]
        add(*blocks)

    # -- findings -------------------------------------------------------
    for f in D["findings"][:6]:
        detail = f.get("detail_en" if lang == "en" else "detail_fa", "")
        title_f = f.get("title_en" if lang == "en" else "title_fa", f["id"])
        blocks = [ptitle(f"{t(lang, 's_finding')}: {f['id']}"),
                  h1(title_f),
                  para(kind_label(lang, f.get("kind", "M"))),
                  para(detail or t(lang, "p_finding"))]
        if f.get("numbers"):
            blocks.append(kv(_finding_kv(f, lang),
                             caption=en_fa(lang, "Numbers read from the data file",
                                           "عددها خواندهشده از فایل داده")))
        if f.get("witness"):
            blocks.append(code([str(x) for x in f["witness"][:10]],
                               caption=en_fa(lang, "Witness / counterexample",
                                             "شاهد / counterexample")))
        blocks.append(note(en_fa(lang,
                                 "A disagreement is treated as an instrument "
                                 "defect until the two job sets are aligned; "
                                 "the gold is in the resolution, not in the "
                                 "headline.",
                                 "ناهماهنگی تا وقتی دو مجموعهٔ کارها همتراز "
                                 "نشدهاند نقصِ ابزار دانسته میشود؛ طلا در "
                                 "حلشدنش است، نه در تیترش."),
                           caption=t(lang, "note_finding")))
        add(*blocks)

    # -- figure pages (two per page) ------------------------------------
    used = {sw.get("figure") for sw in D["sweeps"][:4]}
    figs = [f for f in D["figures"] if f["file"] not in used]
    for i in range(0, len(figs), 2):
        chunk = figs[i:i + 2]
        group = en_fa(lang, f"group {i // 2 + 1}", f"گروه {i // 2 + 1}")
        blocks = [ptitle(f"{t(lang, 's_figures')} — {group}"),
                  para(t(lang, "p_figures"))]
        for f in chunk:
            blocks.append(image(f["file"], width_cm=12.6,
                                caption=_figure_caption(lang, f)))
        add(*blocks)

    # -- disagreement ---------------------------------------------------
    al_rows = []
    for s in D["sets"][:8]:
        al = s["alignment"]
        al_rows.append([s["id"],
                        t(lang, "feasible" if al["checker_verdict"] else "infeasible"),
                        yn(lang, al["naive_agrees"]),
                        yn(lang, al["aligned_agrees"]),
                        str(al["aligned"]["lst"]["horizon"])
                        if "lst" in al["aligned"] else ""])
    add(ptitle(t(lang, "s_disagreement")),
        para(t(lang, "p_disagreement")),
        table(t(lang, "h_alignment").split(" | "), al_rows,
              caption=en_fa(lang, "Naive versus aligned comparison",
                            "مقایسهٔ سادهلوح در برابر همتراز")),
        kv([[t(lang, "kv_naive"), str(derived["naive_agree_count"])],
            [t(lang, "kv_aligned"), str(derived["aligned_agree_count"])],
            [t(lang, "kv_sets"), str(derived["task_set_count"])],
            [t(lang, "kv_truncated"), str(derived["truncated_count"])],
            ["[E] RM counterexamples", str(derived["rm_counterexample_count"])],
            ["[M] witness cheaper than LST",
             str(derived["witness_cheaper_count"])],
            ["[D] cap artefacts", str(derived["cap_artifact_count"])]],
           caption=en_fa(lang, "Agreement counts [D]",
                         "شمارشهای تطابق [D]")),
        note(en_fa(lang,
                   f"Naive comparisons that agree: {derived['naive_agree_count']}. "
                   f"Aligned comparisons that agree: {derived['aligned_agree_count']}. "
                   f"The difference is measured, not argued.",
                   f"مقایسههای سادهلوحِ جور: {derived['naive_agree_count']}. "
                   f"مقایسههای همترازِ جور: {derived['aligned_agree_count']}. "
                   f"این تفاوت اندازهگیری شده، نه استدلال شده."),
             caption=t(lang, "note_alignment")))

    # -- state-cap artefact ----------------------------------------------
    cap_rows = []
    if D["sets"]:
        for cr in D["sets"][0]["cap_control"].get("rows", []):
            cap_rows.append([str(cr["limit"]),
                             t(lang, "feasible" if cr["feasible"] else "infeasible"),
                             str(cr["states"]), yn(lang, cr["truncated"])])
    add(ptitle(t(lang, "s_cap")),
        para(t(lang, "p_cap")),
        table(t(lang, "h_cap").split(" | "), cap_rows,
              caption=en_fa(lang, "Checker verdict as a function of the cap [D]",
                            "حکم چککننده تابعی از سقف [D]")),
        kv([[t(lang, "kv_spec"), D["sets"][0]["spec"] if D["sets"] else ""],
            ["[D] false infeasible verdicts",
             str(D["sets"][0]["cap_control"].get("false_infeasible_count", 0))
             if D["sets"] else ""],
            ["[E] full verdict",
             t(lang, "feasible" if D["sets"][0]["cap_control"].get("full_verdict")
               else "infeasible") if D["sets"] else ""]],
           caption=en_fa(lang, "The same set under different caps",
                         "همان مجموعه زیر سقفهای گوناگون")),
        note(en_fa(lang,
                   f"Across the {derived['task_set_count']} sets of this "
                   f"exercise, {derived['cap_artifact_count']} produce a false "
                   f"infeasible verdict under a reduced cap. None of those "
                   f"verdicts is used as a result.",
                   f"روی {derived['task_set_count']} مجموعهٔ این تمرین، "
                   f"{derived['cap_artifact_count']} مجموعه زیر سقفِ کاهش‌یافته "
                   f"حکمِ نشدنیِ نادرست میدهند. هیچیک از آن احکام به عنوان "
                   f"نتیجه به کار نرفته است."),
             caption=en_fa(lang, "Artefacts, not findings",
                           "مصنوع، نه یافته")))

    # -- verification is coarse -----------------------------------------
    coarse_rows = []
    for s in D["sets"][:9]:
        wc = s["witness_cost"]
        coarse_rows.append([s["id"], str(wc.get("preemptions", "")),
                            str(s["policies"].get("lst", {}).get("preemptions", "")),
                            str(s["policies"].get("edf", {}).get("preemptions", "")),
                            yn(lang, s["witness"].get("valid") is True)])
    add(ptitle(t(lang, "s_coarse")),
        para(t(lang, "p_coarse")),
        table(t(lang, "h_coarse").split(" | "), coarse_rows,
              caption=en_fa(lang, "Witness cost versus policy cost [M]",
                            "هزینهٔ شاهد در برابر هزینهٔ سیاست [M]")),
        kv([["[M] sets where the witness is cheaper",
             str(derived["witness_cheaper_count"])],
            ["[E] independently valid witnesses",
             str(derived["witness_valid_count"])],
            ["[E] RM counterexamples",
             str(derived["rm_counterexample_count"])]],
           caption=en_fa(lang, "What the two instruments can say",
                         "دو ابزار چه میتوانند بگویند")),
        note(en_fa(lang,
                   "A feasibility verdict is a coarse equivalence: it groups "
                   "schedules that measurement can separate. Reporting the "
                   "grouping as if it were a cost claim would be the mistake.",
                   "حکمِ شدنیبودن همارزیی درشتدانه است: برنامههایی را یکجا "
                   "میگذارد که اندازهگیری جدا میکند. یکی گرفتنِ این دستهبندی "
                   "با ادعای هزینه همان اشتباه است."),
             caption=en_fa(lang, "Complement, not contradiction",
                           "مکمل، نه تناقض")))

    # -- large random study (exercise 4, data-driven) --------------------
    if D["random"]:
        rand = D["random"]
        rrows = [[str(r[0]), str(r[1]), str(r[2])]
                 for r in rand.get("table", [])]
        add(ptitle(t(lang, "s_random")),
            para(t(lang, "p_random")),
            table(t(lang, "h_random").split(" | "), rrows,
                  caption=en_fa(lang, "Aggregates over the fixed-seed study",
                                "جمعها روی مطالعهٔ بذرثابت")),
            kv([[t(lang, "kv_seed"), str(rand.get("seed", ""))],
                [en_fa(lang, "Sets generated", "مجموعههای ساختهشده"),
                 str(rand.get("sets_generated", ""))],
                [en_fa(lang, "Truncated runs", "اجراهای بریدهشده"),
                 str(rand.get("truncated", ""))],
                [en_fa(lang, "Tie-break verdict changes",
                       "تغییر حکم با تساویشکنی"),
                 str(rand.get("tie_break_verdict_changes", ""))]],
               caption=en_fa(lang, "Study parameters", "پارامترهای مطالعه")),
            note(en_fa(lang,
                       f"Of {rand.get('sets_generated', '')} generated sets, "
                       f"{rand.get('feasible', '')} are feasible [E] and "
                       f"{rand.get('infeasible', '')} infeasible. LST misses "
                       f"{rand.get('lst_misses_on_feasible', '')} deadlines on "
                       f"feasible sets, EDF "
                       f"{rand.get('edf_misses_on_feasible', '')} and RM "
                       f"{rand.get('rm_misses_on_feasible', '')}. The implicit "
                       f"control produced {rand.get('implicit_feasible', '')} "
                       f"feasible verdicts out of "
                       f"{rand.get('implicit_sets', '')}.",
                       f"از {rand.get('sets_generated', '')} مجموعهٔ ساختهشده، "
                       f"{rand.get('feasible', '')} شدنی [E] و "
                       f"{rand.get('infeasible', '')} نشدنیاند. LST روی "
                       f"مجموعههای شدنی {rand.get('lst_misses_on_feasible', '')} "
                       f"خطا، EDF {rand.get('edf_misses_on_feasible', '')} و RM "
                       f"{rand.get('rm_misses_on_feasible', '')} خطا میدهد. "
                       f"کنترلِ ضمنی {rand.get('implicit_feasible', '')} حکم "
                       f"شدنی از {rand.get('implicit_sets', '')} مجموعه داد."),
                 caption=en_fa(lang, "What the sweep decided",
                               "جاروب چه داوری کرد")))

    # -- provenance (exercises 5 and 6, data-driven) ---------------------
    if D["provenance"]:
        prov = D["provenance"]
        srows = [[str(x.get("path", "")),
                  str(x.get("sha256", ""))[:12],
                  str(x.get("what", ""))]
                 for x in D["sources"][:8]]
        inherited = prov.get("inherited", {})
        kvpairs = [[en_fa(lang, "Inherited key", "کلید بهارثرسیده"),
                    en_fa(lang, "Value", "مقدار")]]
        for k in sorted(inherited)[:10]:
            kvpairs.append([str(k).replace("_", " "), str(inherited[k])])
        add(ptitle(t(lang, "s_provenance")),
            para(t(lang, "p_provenance")),
            table(t(lang, "h_provenance").split(" | "), srows,
                  caption=en_fa(lang, "Source data files, checksums recorded at generation",
                                "فایلهای دادهٔ مبدأ، درهمها ثبتشده هنگام تولید")),
            kv(kvpairs, caption=en_fa(lang, "Inherited values embedded in this data file",
                                      "مقدارهای بهارثرسیدهٔ جاسازیشده در همین فایل")),
            note(en_fa(lang,
                       f"Generation mode: {prov.get('mode', '')}. "
                       f"Source files: {len(D['sources'])}. Inherited values: "
                       f"{len(inherited)}. Mismatches found by the provenance "
                       f"test: {prov.get('mismatches', 0)}.",
                       f"حالت تولید: {prov.get('mode', '')}. فایلهای مبدأ: "
                       f"{len(D['sources'])}. مقدارهای بهارثرسیده: "
                       f"{len(inherited)}. ناهماهنگیهای یافتهشده توسط تستِ منشأ: "
                       f"{prov.get('mismatches', 0)}."),
                 caption=en_fa(lang, "Checked, not assumed", "چکشده، نه مفروض")))

    # -- limitations ----------------------------------------------------
    add(ptitle(t(lang, "s_limits")),
        para(t(lang, "p_limits")),
        bullets([
            en_fa(lang, "single processor; no multicore or migration claim",
                  "تک پردازنده؛ هیچ ادعایی دربارهٔ چندهستهای یا جابهجایی"),
            en_fa(lang, "execution equals worst case; no runtime variance",
                  "اجرا برابر بدترین حالت؛ هیچ پراکندگی زمان اجرا"),
            en_fa(lang, "checker state cap; every truncation is reported",
                  "سقف حالت چککننده؛ هر بریدگی گزارش میشود"),
            en_fa(lang, "integer time; no floating tolerance needed",
                  "زمان صحیح؛ هیچ تلورانس اعشاری لازم نیست"),
            en_fa(lang, "overlapping ranges are called inconclusive",
                  "بازههای همپوشان بیتصمیم نامیده میشوند"),
        ]),
        note(en_fa(lang,
                   "A result obtained from a truncated checker state space is "
                   "an artefact of the cap. It is never reported as a finding.",
                   "نتیجهای که از فضای حالتِ بریدهشدهٔ چککننده بیاید مصنوعِ سقف "
                   "است و هرگز به عنوان یافته گزارش نمیشود."),
             caption=t(lang, "note_limits")))

    # -- reproducibility ------------------------------------------------
    add(ptitle(t(lang, "s_repro")),
        para(t(lang, "p_repro")),
        code(["python3 code/run_experiments.py",
              "python3 code/make_diagrams.py",
              "python3 -m pytest tests -q",
              "python3 tools/build_report.py lstN_en exercise-N REPORT_EN",
              "python3 tools/build_report.py lstN_fa exercise-N REPORT_FA",
              "python3 tools/check_outputs.py exercise-N"],
             caption=en_fa(lang, "Commands (from the exercise folder / tree root)",
                           "دستورها (از پوشهٔ تمرین / ریشهٔ درخت)")),
        kv([[t(lang, "kv_seed"), str(meta.get("seed", ""))],
            [t(lang, "kv_policies"), ", ".join(meta.get("policies", []))],
            [t(lang, "kv_figures"), str(derived["figure_count"])],
            [t(lang, "kv_findings"), str(derived["finding_count"])],
            [t(lang, "kv_sweeps"), str(derived["sweep_count"])]],
           caption=en_fa(lang, "Data file summary", "خلاصهٔ فایل داده")),
        note(en_fa(lang,
                   "A clean build is defined as empty overflow, missing "
                   "figures and missing glyphs lists, with the generator's page "
                   "count equal to the PDF page count.",
                   "ساخت تمیز یعنی فهرستهای سرریز، شکلهای گمشده و نمادهای "
                   "گمشده خالی باشند و شمارش صفحهٔ مولد با شمارش صفحهٔ PDF یکی "
                   "باشد."),
             caption=en_fa(lang, "Definition of a clean build",
                           "تعریف ساخت تمیز")))

    # -- deliverables ---------------------------------------------------
    drows = [
        ["REPORT_EN.docx / REPORT_EN.pdf", en_fa(lang, "English report", "گزارش انگلیسی"),
         "tools/build_report.py lst" + str(n) + "_en"],
        ["REPORT_FA.docx / REPORT_FA.pdf", en_fa(lang, "Persian report", "گزارش فارسی"),
         "tools/build_report.py lst" + str(n) + "_fa"],
        ["output/experiments.json", en_fa(lang, "all numbers", "همهٔ عددها"),
         "code/run_experiments.py"],
        ["diagrams/", en_fa(lang, "generated figures", "شکلهای تولیدشده"),
         "code/make_diagrams.py"],
        ["tests/", en_fa(lang, "green tests", "تستهای سبز"), "python3 -m pytest"],
    ]
    if D["decks"]:
        for d in D["decks"].get("files", []):
            drows.append([d, en_fa(lang, "speaker deck", "دک ارائه"),
                          "tools/make_decks.py"])
    add(ptitle(t(lang, "s_deliverables")),
        para(t(lang, "p_deliverables")),
        table(t(lang, "h_deliverables").split(" | "), drows,
              caption=en_fa(lang, "Artefact table", "جدول خروجیها")),
        kv([[t(lang, "kv_figures"), str(derived["figure_count"])],
            [t(lang, "kv_findings"), str(derived["finding_count"])],
            [t(lang, "kv_witness"), str(derived["witness_valid_count"])],
            [t(lang, "kv_truncated"), str(derived["truncated_count"])]],
           caption=en_fa(lang, "Checks", "چکها")),
        note(en_fa(lang,
                   "Word page counts are estimated by the checker against the "
                   "real section geometry; PDF page counts are exact because "
                   "they are read back from the file.",
                   "شمارش صفحههای Word توسط چککننده بر پایهٔ هندسهٔ واقعی "
                   "بخش تخمین زده میشود؛ شمارش PDF دقیق است چون از خود فایل "
                   "خوانده میشود."),
             caption=en_fa(lang, "Two kinds of page count",
                           "دو نوع شمارش صفحه")))

    # -- appendix -------------------------------------------------------
    keys = sorted(D["raw"].keys())
    add(ptitle(t(lang, "s_appendix")),
        para(t(lang, "p_appendix")),
        code(["top-level keys of output/experiments.json:"] +
             ["  " + k for k in keys],
             caption=en_fa(lang, "Data contract", "قرارداد داده")),
        kv([[en_fa(lang, "Key", "کلید"), en_fa(lang, "Contains", "شامل")],
            ["meta", en_fa(lang, "seed, policies, scope", "بذر، سیاستها، گستره")],
            ["task_sets", en_fa(lang, "per-set measurements and [E] verdicts",
                                "اندازهگیریها و احکام [E] هر مجموعه")],
            ["sweeps", en_fa(lang, "parameter sweeps", "جاروبهای پارامتر")],
            ["findings", en_fa(lang, "tagged findings", "یافتههای برچسبخورده")],
            ["figures", en_fa(lang, "plot specifications and JSON paths",
                              "مشخصات شکلها و مسیرهای JSON")]],
           caption=en_fa(lang, "Key meanings", "معنی کلیدها")),
        note(en_fa(lang,
                   "If a number appears in this report that cannot be found in "
                   "the data file, the provenance test fails and the report is "
                   "rebuilt.",
                   "اگر عددی در این گزارش باشد که در فایل داده پیدا نشود، تستِ "
                   "منشأ رد میشود و گزارش دوباره ساخته میشود."),
             caption=en_fa(lang, "Enforced by a test", "با تست اعمال میشود")))

    # -- policy profiles: real data pages, used to keep the page count in range
    for pr in D["profiles"]:
        if len(pages) >= 30:
            break
        add(ptitle(f"{t(lang, 's_profile')}: {pr['policy']}"),
            para(t(lang, "p_profile")),
            table(t(lang, "h_profile").split(" | "), pr["rows"],
                  caption=en_fa(lang, f"{pr['policy']} across {pr['sets']} sets [M]",
                                f"{pr['policy']} روی {pr['sets']} مجموعه [M]")),
            kv([[t(lang, "kv_total_pre"), str(pr["total_preemptions"])],
                [t(lang, "kv_total_miss"), str(pr["total_missed"])],
                [t(lang, "kv_total_zero"), str(pr["total_zero_switches"])],
                [t(lang, "kv_total_tie"), str(pr["total_tie_events"])]],
               caption=en_fa(lang, "Sums over the rows above [M]",
                             "جمع ردیفهای بالا [M]")),
            note(en_fa(lang,
                       f"{pr['policy']}: {pr['total_missed']} missed deadlines "
                       f"and {pr['total_preemptions']} preemptions over "
                       f"{pr['sets']} sets. Optimality, if it holds, says "
                       f"nothing about the second number.",
                       f"{pr['policy']}: {pr['total_missed']} ضربالاجل "
                       f"ازدسترفته و {pr['total_preemptions']} پیشگیری روی "
                       f"{pr['sets']} مجموعه. بهینگی، اگر هم برقرار باشد، دربارهٔ "
                       f"عدد دوم هیچ نمیگوید."),
                 caption=t(lang, "note_profile")))

    for blocks in pages:
        r.page(*blocks)
    return r
