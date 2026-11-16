# فهرست تمرینها و برنچها — LST

هر تمرین روی یک برنچ بلندعمر است و برنچها **تخت** هستند: محتوای پوشهٔ تمرین 
در ریشهٔ برنچ مینشیند، پس با باز کردنِ برنچ همان لحظه README تمرین دیده میشود. 
هش جدول، هش **کامیتِ محتوا** است؛ کامیتِ کوچکی که این فایلِ هشها را حمل 
میکند فرزند آن است (نمیتوان هشِ کامیتی را در همان کامیت نوشت).

| تمرین | برنچ | محدوده | وضعیت | هش کامیت والد |
|---|---|---|---|---|
| 1 | `Exercise-1-LST-Introduction` | تعریف لَکسیَتی، شبهکد، مثال دستی، نخستین اندازهگیریها — گزارشها: EN 36 / FA 36 صفحه | منتشر شده | `4c4e6cb4` |
| 2 | `Exercise-2-LST-EDF-RM-Comparison` | LST در برابر EDF و RM روی بارهای کاری مختلف — گزارشها: EN 36 / FA 36 صفحه | منتشر شده | `18f824ef` |
| 3 | `Exercise-3-LST-Manual-Scheduling` | زمانبندی دستی که برنامه همان را چاپ کند — گزارشها: EN 36 / FA 36 صفحه | منتشر شده | `7ab4e72e` |
| 4 | `Exercise-4-LST-Optimality-And-Overload` | آیا ادعای بهینگی در برابر جستجوی جامع دوام میآورد — گزارشها: EN 37 / FA 37 صفحه | منتشر شده | `5a94c0d3` |
| 5 | `Exercise-5-LST-Presentation` | دک کوتاه دوزبانه با متن گوینده — گزارشها: EN 35 / FA 35 صفحه | منتشر شده | `7e2bc216` |
| 6 | `Exercise-6-LST-Paper-And-Seminar` | مقاله دوزبانه + دو دک سمینار، عددها از ۱ تا ۵ — گزارشها: EN 36 / FA 36 صفحه | منتشر شده | `9d39700c` |
| 7 | `Exercise-7-LST-Tie-Breaking-And-Thrashing` | readers‑writers: هفت مکانیزم، بررسی جامع گرسنگیِ عادلانه، اندازهگیری انتظار — گزارشها: EN 39 / FA 39 صفحه | منتشر شده | `20d546d9` |

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
| `main` | `1441b0c188cc914e972b0b49a6cabe35ce0a1f79` |
| `Exercise-1-LST-Introduction` | `4c4e6cb4fa712608ce349ecb36d569f2dd35ba3d` |
| `Exercise-2-LST-EDF-RM-Comparison` | `18f824ef4e80e71954c41ba058adc6221e98e6f9` |
| `Exercise-3-LST-Manual-Scheduling` | `7ab4e72e07adf53233c3b94ef5d5c3e113a35ba6` |
| `Exercise-4-LST-Optimality-And-Overload` | `5a94c0d3c67a3326a8aab7916cd9713eaeacaf6f` |
| `Exercise-5-LST-Presentation` | `7e2bc216cadaa7c4634be89931f27132efb0134f` |
| `Exercise-6-LST-Paper-And-Seminar` | `9d39700c97d5d2d0227f39554ade14a838e284bc` |
| `Exercise-7-LST-Tie-Breaking-And-Thrashing` | `20d546d9126c06cfa4c65c77129adbd463e1634f` |

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
