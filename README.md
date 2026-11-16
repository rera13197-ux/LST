# تمرین 5 — Exercise 5 — A Short Bilingual Presentation

**Branch:** `Exercise-5-LST-Presentation`  
**Exercise 5 — A Short Bilingual Presentation**

> **وضعیت: کامل.** آزمایشها، شکلها، تستها و هر چهار فایلِ گزارش ساخته و راستیآزمایی 
> شدهاند. هر عددی که در این README و در گزارشها میآید هنگام ساخت از 
> `output/experiments.json` خوانده میشود؛ هیچ عددی با دست نوشته نشده است.

---

## پرسش

LST را در چند دقیقه برای کسی که هیچ نمیداند توضیح بده، فقط با عددهایی که تمرینهای دیگر واقعاً تولید کردهاند.

## روش

دو ابزار کاملاً جدا: **[E] بررسی جامع** برای «درست است یا نه» (جستجوی 
فضای حالت، شاهد، راستیآزمای مستقل) و **[M] اندازهگیری** برای «چقدر» 
(شبیهساز رخدادگسسته با زمان صحیح). **[D]** ناهماهنگیِ دو ابزار است و 
تا وقتی ابزارها همتراز نشدهاند نقصِ ابزار دانسته میشود، نه کشفِ نظری. 
ضربالاجلها مقیداند، چون با ضربالاجل ضمنی و بهرهوری حداکثر یک، آزمایشِ 
بهینگی قدرت تفکیک ندارد.

## یافتههای اصلی (همه از فایل داده)

- **F1 [M] کمینه کردن لَکسیَتی، کمینه کردن سربار نیست** — عددها در `output/experiments.json` ← `task_sets[0].policies`.
- **F2 [B] ضربالاجل ضمنی، آزمون را از میان برمیدارد** — عددها در `output/experiments.json` ← `task_sets[*].checker`.
- **F3 [D] مقایسهٔ سادهلوح در برابر همتراز** — عددها در `output/experiments.json` ← `task_sets[*].alignment`.
- **F4 [D] سقفِ حالت، حکمِ نشدنیبودن میسازد** — عددها در `output/experiments.json` ← `task_sets[0].cap_control`.
- **F5 [B] هر عدد اسلاید پدری با درهم ثبتشده دارد** — عددها در `output/experiments.json` ← `provenance`.
- **F6 [M] دک کوتاه هم از عددهای اندازهگیریشده ساخته میشود** — عددها در `output/experiments.json` ← `decks`.

## عددهای کلیدی

| کمیت | مقدار | ابزار |
|---|---|---|
| مجموعهکارها | 6 | [M] |
| شدنی / نشدنی | 5 / 1 | [E] |
| شاهدهای مستقل معتبر | 5 | [E] |
| اجراهای بریدهشده چککننده | 0 | [E] |
| مقایسههای سادهلوحِ جور | 5 | [D] |
| مقایسههای همترازِ جور | 6 | [D] |
| مصنوعهای سقفِ حالت | 5 | [D] |
| شکلها / جاروبها / یافتهها | 9 / 3 / 6 | [M] |
| بذر تصادف | 20261116 | [M] |

## تحویلدادهها

| فایل | نوع | شمارش صفحه |
|---|---|---|
| `REPORT_EN.md` | مارکداون همان مدل | محصول جانبی |
| `docs/REPORT_EN.docx` | گزارش انگلیسی، Word | 35 صفحه (تخمین اندازهگیریشده) |
| `docs/REPORT_EN.pdf` | گزارش انگلیسی، PDF | 35 صفحه (دقیق، خواندهشده از فایل) |
| `REPORT_FA.md` | مارکداون همان مدل | محصول جانبی |
| `docs/REPORT_FA.docx` | گزارش فارسی، Word | 35 صفحه (تخمین اندازهگیریشده) |
| `docs/REPORT_FA.pdf` | گزارش فارسی، PDF | 35 صفحه (دقیق، خواندهشده از فایل) |
| `docs/DECK_EN.pptx` | دک PPTX | تولیدشده از `tools/make_decks.py` |
| `docs/DECK_FA.pptx` | دک PPTX | تولیدشده از `tools/make_decks.py` |
| `docs/SPEAKER_NOTES_EN.md` | متن گوینده | تولیدشده از `tools/make_decks.py` |
| `docs/SPEAKER_NOTES_FA.md` | متن گوینده | تولیدشده از `tools/make_decks.py` |
| `output/experiments.json` | یگانه مرجع عددها | — |
| `diagrams/` | 9 شکل تولیدشده | — |
| `code/` + `tests/` | کد و تستهای سبز | — |

قانونِ حجم برقرار است: PDF انگلیسی 35 صفحه و PDF فارسی 
35 صفحه (هر دو در بازهٔ بیست تا چهل). ساخت تمیز است یعنی 
`overflow` و `missing_figures` و `missing_glyphs` خالیاند و شمارش 
صفحههای مولد با شمارش PDF یکی است؛ `output/build_manifest.json` آن را ثبت میکند.

## چطور اجرایش کنیم

```bash
python3 code/run_experiments.py     # عددها -> output/experiments.json
python3 code/make_diagrams.py       # شکلها -> diagrams/
python3 -m pytest tests -q          # تستها
```

ساختِ گزارش از ریشهٔ درختِ چندتمرینیه (جایی که پوشههای `exercise-N` کنار هماند):

```bash
python3 tools/build_report.py lst5_en exercise-5 REPORT_EN
python3 tools/build_report.py lst5_fa exercise-5 REPORT_FA
python3 tools/verify_builds.py       # همهٔ گزارشها + مانیفست ساخت تمیز
```

```bash
python3 tools/make_decks.py 5
  # دکها و متن گوینده -> docs/
```

## ساختار این شاخه

همه چیز در **ریشهٔ شاخه** است، نه در پوشهای تودرتو، تا همین README هنگام 
باز کردنِ شاخه دیده شود.

| مسیر | توضیح |
|---|---|
| `README.md` | همین فایل |
| `code/lst_core.py` | هستهٔ شبیهساز (رونوشت منطبق) |
| `code/lab_kit.py` | ابزار آزمایش و رسم شکل (رونوشت منطبق) |
| `code/run_experiments.py`, `code/make_diagrams.py` | تولید عددها و شکلها |
| `tests/` | تستهای سبز، مستقل از خواهرها |
| `output/` | خروجی خام کد |
| `diagrams/` | شکلها |
| `docs/` | فایلهای قابلتحویل |
| `REPORT_EN.md`, `REPORT_FA.md` | مارکداون همان مدل محتوا |
