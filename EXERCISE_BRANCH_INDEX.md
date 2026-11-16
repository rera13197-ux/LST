# فهرست تمرینها و برنچها — LST

هر تمرین روی یک برنچ بلندعمر است و برنچها **تخت** هستند: محتوای پوشهٔ تمرین 
در ریشهٔ برنچ مینشیند، پس با باز کردنِ برنچ همان لحظه README تمرین دیده میشود. 
هش جدول، هش **کامیتِ محتوا** است؛ کامیتِ کوچکی که این فایلِ هشها را حمل 
میکند فرزند آن است (نمیتوان هشِ کامیتی را در همان کامیت نوشت).

| تمرین | برنچ | محدوده | وضعیت | هش کامیت والد |
|---|---|---|---|---|
| 1 | `Exercise-1-LST-Introduction` | تعریف لَکسیَتی، شبهکد، مثال دستی، نخستین اندازهگیریها — گزارشها: EN 36 / FA 36 صفحه | منتشر شده | `86ce4a96` |
| 2 | `Exercise-2-LST-EDF-RM-Comparison` | LST در برابر EDF و RM روی بارهای کاری مختلف — گزارشها: EN 36 / FA 36 صفحه | منتشر شده | `d24f5160` |
| 3 | `Exercise-3-LST-Manual-Scheduling` | زمانبندی دستی که برنامه همان را چاپ کند — گزارشها: EN 36 / FA 36 صفحه | منتشر شده | `59657c5f` |
| 4 | `Exercise-4-LST-Optimality-And-Overload` | آیا ادعای بهینگی در برابر جستجوی جامع دوام میآورد — گزارشها: EN 37 / FA 37 صفحه | منتشر شده | `5360ad6e` |
| 5 | `Exercise-5-LST-Presentation` | دک کوتاه دوزبانه با متن گوینده — گزارشها: EN 35 / FA 35 صفحه | منتشر شده | `965eae0e` |
| 6 | `Exercise-6-LST-Paper-And-Seminar` | مقاله دوزبانه + دو دک سمینار، عددها از ۱ تا ۵ — گزارشها: EN 36 / FA 36 صفحه | منتشر شده | `130437a8` |
| 7 | `Exercise-7-LST-Tie-Breaking-And-Thrashing` | readers‑writers: هفت مکانیزم، بررسی جامع گرسنگیِ عادلانه، اندازهگیری انتظار — گزارشها: EN 39 / FA 39 صفحه | منتشر شده | `f5f41836` |

## وضعیت انتشار

`main` درخت کامل (همهٔ تمرینها کنار هم) + دو فایل وضعیت + ابزارها را دارد؛ 
هر برنچ تمرین فقط همان تمرین را در ریشه دارد، به همراه 
`PROJECT_PROGRESS.md` و این فایل. هش کامل همهٔ برنچها در 
`output/push_hashes.json` همان برنچ ثبت شده است.

> **یادداشت:** تمرین ۷ دربارهٔ الگوریتم خواننده-نویسنده است. نام 
> `Exercise-7-LST-Tie-Breaking-And-Thrashing` از اسکلت اولیهٔ LST به 
> ارث رسیده و برای پیوستگیِ برنچهای منتشرشده تغییر نکرده است.

| برنچ | هش کامل کامیت محتوا |
|---|---|
| `main` | `f91f62a1eae96283064fdecfc0ff7b522e2f2d82` |
| `Exercise-1-LST-Introduction` | `86ce4a9645351c53e70cc9e07a85e9bec4fa1e4c` |
| `Exercise-2-LST-EDF-RM-Comparison` | `d24f51607d36b7564a508959d32e452e14168453` |
| `Exercise-3-LST-Manual-Scheduling` | `59657c5f50b6217260def10989cc956dd17e3301` |
| `Exercise-4-LST-Optimality-And-Overload` | `5360ad6ea96ef82d29769767ed7a0d1956c50adb` |
| `Exercise-5-LST-Presentation` | `965eae0eabd37c6c025ab994d6bbbb390c97917b` |
| `Exercise-6-LST-Paper-And-Seminar` | `130437a82a60fcbd1085648355c70aee7b124034` |
| `Exercise-7-LST-Tie-Breaking-And-Thrashing` | `f5f41836ec241ff1f97f219b4680cf6938bab325` |

## قراردادها

* برنچ `main`: درخت کامل (همهٔ تمرینها کنار هم) + این فایل + `PROJECT_PROGRESS.md`.
* برنچ هر تمرین: فقط آن تمرین، در ریشه، به همراه `PROJECT_PROGRESS.md` و این فایل.
* هسته یک مرجع دارد (`core/lst_core.py`) و با `python3 tools/vendor_core.py` 
  به تمرینها رونوشت میشود؛ `tools/vendor_lab.py` هم `lab_kit.py` و 
  `make_decks.py` را همتراز نگه میدارد. هر دو `--check` دارند.
* هر عددی که در هر گزارش میآید هنگام ساخت از `output/experiments.json` 
  همان تمرین خوانده میشود؛ `tests/test_reports.py` این را چک میکند.
* ساخت تمیز: `overflow == []`، `missing_figures == []`، 
  `missing_glyphs == []` و `pages == pdf_pages`.
