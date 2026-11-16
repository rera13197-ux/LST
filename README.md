


---

## وضعیت فعلی (تولیدشده از داده)

هفت تمرین کاملاند: آزمایشها، شکلها، تستها، گزارشهای دوزبانه (DOCX + PDF + MD)
و دکها. تمرین ۷ دربارهٔ الگوریتم خواننده-نویسنده است (بررسی جامع گرسنگیِ
عادلانه و اندازهگیری انتظار)، نه تساویشکنی LST. جزئیات و هشها در
[PROJECT_PROGRESS.md](PROJECT_PROGRESS.md) و
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
pip install --break-system-packages pytest python-docx reportlab fonttools \
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
