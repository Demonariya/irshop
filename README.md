# irshop 🇮🇷

**اسکیل جستجو و مقایسه محصولات در فروشگاه‌های اینترنتی ایران**

[![Claude Code](https://img.shields.io/badge/Claude%20Code-Skill-blue)](https://github.com/demonariya/irshop)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)
[![Version](https://img.shields.io/badge/Version-1.0.0-orange)](VERSION)

---

## 🎯 ویژگی‌ها

- 🔍 **جستجوی هوشمند** در ۹+ فروشگاه اینترنتی
- 💰 **مقایسه قیمت** لحظه‌ای
- 📊 **نمودار قیمت** و روند بازار
- ⭐ **تحلیل نظرات** کاربران
- 🏷️ **کدهای تخفیف** فعال
- 🚚 **بررسی ارسال** و زمان تحویل
- 💳 **شرایط اقساط** فروشگاه‌ها
- 🛡️ **هشدار جعلی** و اصالت کالا
- 📱 **پشتیبانی فارسی** و انگلیسی

---

## 📦 نصب

### Claude Code (پیشنهادی)

```bash
# روش ۱: نصب از مارکت
/plugin marketplace add demonariya/irshop
/plugin install irshop@irshop-marketplace

# روش ۲: نصب مستقیم
npx skills add demonariya/irshop

# روش ۳: نصب دستی
git clone https://github.com/demonariya/irshop.git ~/.claude/skills/irshop
```

### سایر Agent‌ها

```bash
# Cursor, Copilot, etc.
npx @agent-native/skills add demonariya/irshop
```

---

## 🚀 استفاده

### جستجوی ساده

```
/irshop Samsung Galaxy A56
/irshop کیبورد مکانیکال
/irshop PlayStation 5
```

### دستورات پیشرفته

| دستور | توضیح | مثال |
|-------|-------|------|
| `مقایسه` | مقایسه مدل‌ها | `/irshop iPhone 16 مقایسه` |
| `تخفیف` | کدهای تخفیف | `/irshop دیجیکالا تخفیف` |
| `پیگیری` | هشدار قیمت | `/irshop PS5 پیگیری قیمت هدف 25M` |
| `جایگزین` | محصولات مشابه | `/irshop Galaxy A56 جایگزین` |
| `نظرات` | تحلیل نظرات | `/irshop Pixel 8a نظرات` |
| `اقساط` | شرایط اقساط | `/irshop iPhone اقساط` |
| `گارانتی` | مقایسه گارانتی | `/irshop Samsung گارانتی` |
| `زمان تحویل` | زمان ارسال | `/irshop تیپاکس زمان تحویل` |
| `نمودار` | روند قیمت | `/irshop دلار نمودار` |
| `لیست خرید` | مدیریت لیست | `/irshop Galaxy افزودن به لیست 1` |
| `صادرات` | خروجی CSV | `/irshop صادرات` |

---

## 🏪 فروشگاه‌های پشتیبانی شده

### فروشگاه‌های اصلی

| فروشگاه | نوع | ویژگی |
|---------|------|-------|
| [ترب](https://torob.com) | مقایسه‌کننده | تاریخچه قیمت، تخفیف |
| [دیجی‌کالا](https://digikala.com) | بازار | ارسال سریع، اقساط |
| [باسلام](https://bashgah.com) | اجتماعی | ارسال رایگان |
| [ایمالز](https://emalls.ir) | مقایسه‌کننده | مقایسه قیمت |

### فروشگاه‌های تخصصی

| فروشگاه | تخصص |
|---------|------|
| [الکترومیک](https://elecmake.ir) | قطعات الکترونیک |
| [آرویدتک](https://arvidtech.com) | ماژول‌ها و سنسورها |
| [میکرومیک](https://micromike.ir) | بردهای توسعه |
| [کافه ربات](https://caferobot.com) | رباتیک و آموزش |
| [اتمل](https://utmel.com) | نیمه‌رسانان |

---

## 📸 نمونه خروجی

### جستجو

```
## نتایج جستجو: Samsung Galaxy A56

| # | عکس | محصول | قیمت | فروشگاه | موجود | لینک |
|---|-----|-------|------|---------|-------|------|
| 1 | 📱 | Galaxy A56 128/8GB | ۹۶.۵M | آرویدتک | ✅ | [link] |
| 2 | 📱 | Galaxy A56 128/8GB | ۹۹M | دیجیکالا | ✅ | [link] |
| 3 | 📱 | Galaxy A56 256/8GB | ۱۰۴M | ترب | ✅ | [link] |

### خلاصه
- ارزان‌ترین: ۹۶.۵M (آرویدتک)
- میانگین: ۱۰۰M
```

### مقایسه

```
## مقایسه: Galaxy A56 vs Pixel 8a

| ویژگی | Galaxy A56 | Pixel 8a |
|-------|-----------|----------|
| نمایشگر | 6.7" AMOLED | 6.1" OLED |
| دوربین | 50MP | 64MP |
| باتری | 5000mAh | 4492mAh |
| قیمت | ۹۶.۵M | ۸۵M |

### برنده: Pixel 8a
دوربین بهتر، قیمت کمتر، آپدیت مستقیم گوگل
```

---

## ⚙️ پیکربندی

فایل `references/shops.json` قابل ویرایش است:

```json
{
  "shops": [
    {
      "id": "my_shop",
      "name": "فروشگاه من",
      "url": "https://myshop.ir",
      "search_pattern": "https://myshop.ir/search?q={query}",
      "enabled": true
    }
  ]
}
```

---

## 🤝 مشارکت

به استقبال کمک‌های شما هستیم!

### اضافه کردن فروشگاه

1. فایل `references/shops.json` را ویرایش کنید
2. الگوی جستجو را اضافه کنید
3. Pull Request بزنید

### گزارش باگ

[Issues](https://github.com/demonariya/irshop/issues)

---

## 📄 لایسنس

MIT License — استفاده آزاد

---

## 🙏 قدردانی

ساخته شده برای جامعه خریداران ایرانی ❤️

---

## 📞 تماس

- GitHub: [@demonariya](https://github.com/demonariya)
- Issues: [irshop/issues](https://github.com/demonariya/irshop/issues)
