---
name: irshop
description: جستجوی محصول در فروشگاه‌های اینترنتی ایران. هر محصولی (الکترونیک، پوشاک، لوازم خانگی و...) را در دیجی‌کالا، ترب، باسلام، و سایر سایت‌ها مقایسه کن.
version: 1.0.0
author: demonariya
tags:
  - shopping
  - iran
  - price-comparison
  - digikala
  - torob
  - ecommerce
---

# irshop 🇮🇷

جستجو و مقایسه محصولات در فروشگاه‌های اینترنتی ایران.

## Quick Start

```
/irshop Samsung Galaxy A56
```

## Features

- 🔍 جستجو در چندین فروشگاه
- 💰 مقایسه قیمت
- 📊 نمودار قیمت
- ⭐ تحلیل نظرات
- 🏷️ کدهای تخفیف
- 🚚 بررسی ارسال
- 📱 پشتیبانی از فارسی و انگلیسی

## Commands

| دستور | توضیح |
|-------|-------|
| `{product}` | جستجوی محصول |
| `{product} مقایسه` | مقایسه مدل‌ها |
| `{product} تخفیف` | کدهای تخفیف |
| `{product} پیگیری` | هشدار قیمت |
| `{product} جایگزین` | محصولات مشابه |
| `{product} نظرات` | تحلیل نظرات |
| `{product} اقساط` | شرایط اقساط |
| `{product} گارانتی` | مقایسه گارانتی |
| `{product} زمان تحویل` | زمان ارسال |
| `{product} نمودار` | روند قیمت |
| `{product} لیست خرید` | اضافه به لیست |
| `لیست خرید` | نمایش لیست |
| `صادرات` | خروجی CSV/JSON |

## Supported Shops

### فروشگاه‌های اصلی
- [torob.com](https://torob.com) — مقایسه‌کننده قیمت
- [digikala.com](https://digikala.com) — بزرگ‌ترین فروشگاه
- [bashgah.com](https://bashgah.com) — باسلام
- [emalls.ir](https://emalls.ir) — مقایسه قیمت

### فروشگاه‌های تخصصی
- [elecmake.ir](https://elecmake.ir) — قطعات الکترونیک
- [arvidtech.com](https://arvidtech.com) — آرویدتک
- [micromike.ir](https://micromike.ir) — میکرومیک
- [caferobot.com](https://caferobot.com) — رباتیک
- [utmel.com](https://utmel.com) — قطعات الکترونیک

## Installation

### Claude Code (Recommended)

```bash
# از مارکت رسمی
/plugin marketplace add demonariya/irshop
/plugin install irshop@irshop-marketplace

# یا نصب مستقیم
npx skills add demonariya/irshop
```

### Manual Installation

```bash
git clone https://github.com/demonariya/irshop.git ~/.claude/skills/irshop
```

## Configuration

### فروشگاه‌های پیش‌فرض

فروشگاه‌ها در فایل `references/shops.json` قابل تنظیم هستند.

### هشدار قیمت

برای فعال‌سازی هشدار قیمت، فایل `~/.claude/irshop/config.json` را بسازید:

```json
{
  "alerts": {
    "enabled": true,
    "check_interval": "daily",
    "notification": "console"
  }
}
```

## Examples

### جستجوی ساده
```
/irshop کیبورد مکانیکی
```

### مقایسه
```
/irshop iPhone 16 vs Galaxy S25 مقایسه
```

### پیگیری قیمت
```
/irshop PlayStation 5 پیگیری قیمت هدف 25 میلیون
```

### لیست خرید
```
/irshop لیست خرید
/irshop Galaxy A56 افزودن به لیست 1
```

## How It Works

1. **جستجو**: ابتدا از `torob.com` شروع می‌کند (پوشش چندصد فروشگاه)
2. **تکمیل**: سپس فروشگاه‌های تخصصی را جستجو می‌کند
3. **فیلتر**: نتایج تکراری و ناموجود حذف می‌شوند
4. **مرتب‌سازی**: بر اساس قیمت (ارزان‌ترین اول)
5. **نمایش**: جدول با عکس، قیمت، و لینک مستقیم

## Privacy & Security

- 🔒 هیچ اطلاعات شخصی ذخیره نمی‌شود
- 🚫 API Key نیاز ندارد (فقط وب‌اسکرپینگ)
- 🛡️ فقط سایت‌های معتبر فهرست شده‌اند
- ⚠️ مسئولیت خرید با کاربر است

## Contributing

به استقبال کمک‌های شما هستیم!

1. Fork کنید
2. Branch بسازید (`git checkout -b feature/amazing`)
3. Commit کنید (`git commit -m 'Add amazing feature'`)
4. Push کنید (`git push origin feature/amazing`)
5. Pull Request بزنید

### اضافه کردن فروشگاه جدید

فایل `references/shops.json` را ویرایش کنید:

```json
{
  "name": "فروشگاه جدید",
  "url": "https://example.com",
  "search_pattern": "https://example.com/search?q={query}",
  "category": "general",
  "enabled": true
}
```

## License

MIT License — استفاده آزاد

## Support

- 🐛 [Issues](https://github.com/demonariya/irshop/issues)
- 💬 [Discussions](https://github.com/demonariya/irshop/discussions)
- 📧 Email: [your-email]

---

**ساخته شده با ❤️ برای خریداران ایرانی**
