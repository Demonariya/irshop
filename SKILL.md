---
name: irshop
description: "Search and compare current product prices on Iranian shopping sites, show product image thumbnails when available, and check the seller's Enamad trust badge. Use for Persian or English product searches requiring verified variants, Toman prices, stock status, seller links, cautious Enamad verification, deduplication, and a ranked Markdown comparison table."
license: MIT
metadata:
  version: "1.3.0"
  author: "Demonariya"
  tags: "shopping, iran, price-comparison, persian, ecommerce"
---

# irshop — Iranian Product Search and Price Comparison

Search Iranian stores for a requested product, verify live offers, normalize prices, remove duplicate listings, and return a useful comparison. The implemented scope is **live search and price comparison**; this skill does not persist state or run scheduled jobs.

## Use When

- The user asks to find a product or compare current prices from Iranian online shops.
- The user supplies a model, SKU, product name, budget, or key specifications to match.
- The user wants a concise price table with seller links and stock status.

## Don't Use When

- The user asks for historical price charts, scheduled alerts, persistent shopping lists, coupon validation, review sentiment analysis, delivery estimates, or CSV exports. These are not implemented. Explain the limitation and offer the live search/comparison workflow instead.
- The task is only general product advice and does not require current offers.
- The product is prohibited by applicable safety rules or the user asks to evade a shop's access controls.

## Workflow

### 1. Parse the request and select tools

1. Identify the exact product and any required variant: model number, capacity, color, region, warranty, pack size, or other attributes that materially change price.
2. If a critical model detail is ambiguous, search using the supplied wording and keep variants separate; do not stop for clarification unless comparison would otherwise be misleading.
3. Inspect the tools actually available in the current agent runtime. Prefer its browser automation tool to inspect rendered pages. Depending on the runtime, navigation may be exposed as open_page or browser_tab, and rendered page inspection may be exposed as a DOM snapshot, accessibility tree, locator, or page-evaluation action. Use only tools that are actually available; never invent a tool name.
4. If browser automation is unavailable, use the available web-search and open-page tools. Search snippets may discover candidates, but do not treat a snippet alone as proof of current price or stock when the product page can be opened.
5. Read **references/shops.json** before choosing sites. Start with Torob, then use general shops and relevant specialist shops. Search at most five sites per request unless the user asks for broader coverage.

### 2. Search, starting with Torob

1. Search Torob first using the encoded query in its search_url_template. Search in Persian first for Persian-market products; add an English/model-number query when that is likely to uncover more exact matches.
2. Inspect result cards and follow promising product links. Torob is an aggregator: when a product detail page exposes individual seller offers, treat each seller/price pair as a separate offer. Prefer the seller's direct product URL when the page explicitly provides one. Otherwise link to the Torob product/offer page and identify the source as Torob; do not label it as a direct shop link.
3. Search the most relevant of Digikala, Basalam, and eMalls next. Use specialist shops only when their category matches the product. If a saved search URL fails, open that site's home page and use its visible search form instead of guessing new query parameters.
4. Inspect the first useful result pages, then open the actual product or offer pages for candidates likely to enter the final comparison. Collect a small set of credible offers rather than many weak matches.
5. Keep the exact model/variant in the candidate record. Exclude products that merely share a brand or a broad keyword.

### 3. Extract each candidate from the live page

For each candidate, collect the fields below before adding it to the comparison:

- product_name: visible product title, cleaned of irrelevant page chrome.
- variant: exact model/configuration details shown by the seller.
- price_raw: the visible current selling price and nearby currency/unit text.
- price_toman: normalized numeric Toman value, or null if it cannot be established.
- availability: in_stock, out_of_stock, or unknown.
- seller: named seller/store when shown; otherwise the shop or aggregator name.
- shop: the website where the offer was found.
- url: the canonical product/offer URL actually opened or found in the page.
- image_url: a usable direct HTTP(S) URL for the main image of this exact product/variant, or null if no suitable image can be identified.
- evidence: brief note describing the visible price/stock evidence when a field is uncertain.
- checked_at: current date/time only if the runtime exposes it reliably.

Use this extraction order:

1. Inspect visible, rendered product details and accessible labels. Confirm the title, selected variant, price, and stock state from the same offer.
2. Inspect HTML script elements of type application/ld+json for Product, Offer, or AggregateOffer when present. Useful fields include name, sku, offers.price, priceCurrency, availability, seller, and url. Validate structured data against the visible page; stale or contradictory JSON-LD must not override the current rendered offer.
3. If structured data is absent, use the product card or product page DOM. Locate a product link first, then extract price and stock text from that same card or page. Do not grab the first price on the page, because it may belong to a promotion banner, a related product, shipping, an installment, or an old crossed-out price.
4. Prefer a seller's direct product link. Accept only valid HTTP or HTTPS URLs that lead to the relevant product or offer. Remove tracking parameters only when doing so preserves the working product URL.
5. Treat selector hints in references/shops.json as starting points, not guarantees. Inspect the current DOM before using them. Prefer semantic attributes, structured data, and links adjacent to the matching product title over positional selectors such as div:nth-child(4).

#### Site-specific extraction

- **Torob:** identify the matching product result; open it and inspect its seller-offer list. Record each distinct seller and price separately when available. A Torob listing is not proof that the external seller currently has stock; verify an external seller page when accessible. If only Torob is accessible, keep the Torob URL and mark stock unknown unless explicit stock evidence exists.
- **Digikala:** open the product URL and verify the currently selected variant. Product links often include /product/ or a dkp- identifier, but paths and rendered attributes can change. Read the current selling price and the page's stock/purchase state; do not use a price for a different capacity, color, seller, or configuration.
- **Basalam:** use the current search UI if the saved query pattern fails. Extract the product title, displayed price, seller/booth name, and product URL from the same card/page. Do not infer free shipping or stock from the shop name or an unrelated badge.
- **eMalls:** treat the result as an aggregator. Identify whether a price belongs to a specific shop, then follow the offer to the merchant when possible. Keep a result labeled as eMalls if no direct merchant offer can be verified.
- **Specialist shops:** first inspect the page for JSON-LD Product/Offer. Some shops may use WooCommerce-like markup (li.product, a.woocommerce-LoopProduct-link, .price, .stock), but only use these hints after confirming they exist on that site's live DOM. Find the title, price, availability, and link within the same product card; verify candidates on their detail page.

### Extract a product image

For each offer, collect `image_url` only when it can be tied to the matching product and preferably the selected variant. This is optional evidence; never invent an image URL to fill the table.

Use this source priority:

1. The main product image currently rendered on the exact product page or matching result card. Prefer the browser's resolved/current image URL (such as `currentSrc`) over a lazy-loading placeholder.
2. The `image` field of Product JSON-LD, after checking that it corresponds to the same product and does not contradict the visible page.
3. The page's `og:image` metadata only when it is clearly the product image, not a site-wide banner.
4. Lazy-load attributes such as `data-src` or an appropriate entry from `srcset`, but only after resolving it against the page URL and confirming it is not a placeholder.

Image handling rules:

- Accept only a real absolute `http://` or `https://` URL. Resolve relative URLs against the actual page URL when the browser/runtime supports it. Do not use `data:`, `blob:`, JavaScript URLs, broken-image fallbacks, tracking pixels, store logos, avatars, category banners, or a different product's image.
- Prefer the primary product image with enough detail to identify the item. Keep variants separate; do not attach a different color/capacity/model image merely because the title is similar.
- Do not assume a URL is a valid image just because it appears in metadata. Prefer a source visibly rendered as the product image or one confirmed by the page's product metadata; if it cannot be validated, use no image.
- Do not download, rehost, or modify product images as part of this Skill. Use the source image URL and respect the shop's access rules.
- The table renderer may not display remote Markdown images in every agent UI. If remote images are stripped or unsupported, render a clickable `[تصویر محصول](image_url)` link instead and keep the product-page link in its own column.
- If no suitable image is found, write `بدون تصویر`; do not insert an unrelated, guessed, or decorative image.

### Enamad verification for seller offers

Before labeling an offer's seller status, inspect the seller's own domain and look for a clickable Enamad badge in its footer, About, or Contact page.

1. Open the actual seller homepage and find the badge anchor, not just an image or text claiming «دارای اینماد».
2. Follow the badge link only if the destination hostname is trustseal.enamad.ir or enamad.ir, or a subdomain of those official hosts. Do not treat lookalike hosts or a seller-hosted page as official verification.
3. On the official page, compare the registered hostname to the exact seller hostname. Read the displayed validity/expiry status. A matching domain with no readable validity status is not confirmed active.
4. Use these labels consistently:
   - «تأیید رسمی»: official page reached, exact domain matches, and current validity is explicitly confirmed.
   - «منقضی»: the official page explicitly says the symbol is expired.
   - «عدم تطبیق دامنه»: the official page identifies a different domain.
   - «لینک اینماد دیده شد؛ اعتبار نامشخص»: clickable badge found, but official verification cannot be reached or its validity is not readable.
   - «بررسی‌نشده»: no check was completed. Do not translate this to “بدون اینماد”.
   - «نشان در صفحه قابل مشاهده نبود»: no official link found in fetched HTML. On client-rendered sites, inspect the rendered page before concluding.
5. If the official site is blocked, times out, returns 403/429, or produces a tunnel/network error, do not bypass controls. Mark the status unknown and continue with another source.
6. For Torob and eMalls, check the individual merchant when an offer links to an external store. An aggregator's Enamad badge is not evidence about the merchant selling the item.
7. A current Enamad match is only one trust signal. Do not describe a shop as safe, authentic, or guaranteed solely because it has a symbol.
8. When Python and repository files are available, run python scripts/check_enamad.py --limit 12 --update-registry for a limited polite check, or python scripts/check_enamad.py --all --update-registry for the whole registry. The helper never marks a symbol active automatically; manually inspect any official page that requires interpretation. Skip sites whose crawl permissions are unclear or that block access.

Current registry note: on 2026-10-10, clickable official Enamad links were found on Digikala, Technolife, Torob, eMalls, Basalam, and Kalatik, but the official verification host failed with ERR_TUNNEL_CONNECTION_FAILED. Therefore none of these six is marked officially active; the registered-domain match and expiration are unknown. The other registry entries are marked بررسی‌نشده until checked.

### 4. Normalize prices and availability

1. Preserve the original price text until parsing is complete. Convert Persian digits (۰۱۲۳۴۵۶۷۸۹) and Arabic-Indic digits (٠١٢٣٤٥٦٧٨٩) to Western digits for calculation.
2. Treat Persian/Arabic thousands separators (٬, ٫, ،), commas, and clearly grouped spaces carefully. Example: ۹۶٬۵۰۰٬۰۰۰ تومان becomes 96500000 Toman, displayed as ۹۶٬۵۰۰٬۰۰۰ تومان.
3. If the source explicitly says **ریال / IRR**, convert to Toman by dividing the amount by 10. If it explicitly says **تومان / تومن / Toman**, do not convert it. Interpret explicit units such as میلیون or هزار as multipliers. Never infer a unit solely from the size of the number.
4. Use the bundled helper when Python is available. Pass the visible price label as the argument to scripts/parse_price.py. The script uses only the Python standard library. If Python is unavailable, apply the same normalization rules manually. Use the helper's assume-toman option only when the page's price unit is clear from surrounding page text or a site-wide label, not merely because the shop is Iranian.
5. Use the current selling price, not the struck-through list price, monthly installment, deposit, shipping charge, cashback, or coupon price that requires an unverified condition. Explain conditional discounts separately only when the condition is explicit.
6. Detect out-of-stock signals such as ناموجود, اتمام موجودی, موجود نیست, فعلاً موجود نیست, sold out, out of stock, or unavailable. An explicit out-of-stock signal takes precedence over generic text such as “buy” elsewhere on the page.
7. Set stock to in_stock only when the page explicitly indicates availability or an active purchase action clearly belongs to that exact offer. Set out_of_stock for explicit unavailability. Otherwise use unknown; never turn missing evidence into “موجود”.
8. If price or unit remains ambiguous, set the numeric comparable price to null and explain why. Do not rank or average that offer as though it had a verified Toman price.

### 5. Deduplicate and validate offers

1. Normalize each URL: remove fragments, remove only known tracking parameters, and normalize an optional trailing slash without breaking query-based product IDs.
2. Remove duplicate captures of the same shop, same product/variant, and same URL. If URL identity is unavailable, compare normalized title, variant, seller, and price.
3. Keep offers from different sellers separate even when they sell the same product; that is the point of price comparison.
4. Never merge materially different variants, used/refurbished items with new items, bundles with single items, or products with different warranty/region information. If condition is unclear, mark it in the product cell or exclude it from the main comparison.
5. Before ranking, confirm that each remaining row is the requested product and that its price is numeric and in Toman.

### 6. Handle errors and access restrictions

1. If a search URL fails, try the shop's home page and visible search form once. If the site uses client-side rendering, wait for the page to finish rendering and inspect the live DOM.
2. If a page times out, retry once with a reasonable timeout. If the site returns a 403, 429, CAPTCHA, explicit bot challenge, or access-denied page, stop retrying that site and use other public sources. Do not bypass the challenge, rotate proxies to evade controls, automate login, or claim to have inspected blocked data.
3. If a shop is unreachable, state that it could not be checked. Keep working with accessible sites and mention partial coverage.
4. If search results are empty, try one useful spelling/model-number variant, then stop. Do not manufacture results to fill the table.
5. If no offer can be verified, say so directly and list which sources failed or had no matching product.

### 7. Build the comparison table

Return no more than **10 distinct offers**, sorted by normalized Toman price ascending. Put confirmed in-stock offers first. Unknown-stock offers may appear after them with نامشخص; exclude explicit out-of-stock offers from the main table and from all price summaries.

Use exactly these columns, in this order:

| # | تصویر | محصول و مدل دقیق | قیمت (تومان) | فروشگاه / فروشنده | موجودی | وضعیت اینماد | لینک مستقیم |
|---:|---|---|---:|---|---|---|---|

Formatting rules:

- Format full prices with Persian digits and the Persian thousands separator, for example ۹۶٬۵۰۰٬۰۰۰ تومان. Do not use shortened forms such as ۹۶.۵M.
- If price is not reliably comparable, display نامشخص rather than inventing or estimating it.
- Use stock labels موجود, ناموجود, and نامشخص. Use the distinct Enamad labels from the verification section; do not map بررسی‌نشده to a claim that the shop lacks Enamad. The main table should normally omit ناموجود offers.
- Use a real Markdown link such as [مشاهده محصول](https://...). Never output a placeholder such as [link] or link a shop home page as though it were a product page.
- Link to the merchant's product page when verified. Otherwise link to the exact aggregator listing and make the source clear in the seller/source cell.
- Always include the «تصویر» column immediately after «#». Show `![تصویر محصول](image_url)` only for a usable image URL extracted from the matching offer; otherwise show «بدون تصویر». If the runtime does not render Markdown images, use a clickable image URL instead.

### 8. Add a short summary under the table

After the table, add a **خلاصه** section with:

- **نتایج قابل مقایسه:** number of unique offers shown, and number of sites successfully checked when known.
- **ارزان‌ترین گزینه:** seller, price, and direct link; only if at least one comparable in-stock offer exists.
- **میانگین قیمت:** calculate only from verified, in-stock offers for the same exact variant with comparable Toman prices. Do not mix capacities, models, bundles, conditions, or ambiguous currencies.
- **بازه قیمت:** lowest to highest comparable in-stock price when at least two exist.
- **وضعیت اینماد:** distinguish officially verified active sellers from badge links whose validity could not be checked and from untested sellers.
- **محدودیت‌ها:** briefly state blocked/unreachable sites, unknown stock, excluded variants, or omitted shipping/conditional discounts.
- **زمان بررسی:** include the real check time only when available from the runtime; never invent a timestamp.

The summary should be short. If there is only one valid offer, report the cheapest offer and omit the average/range instead of implying statistical significance. Do not estimate shipping or final checkout cost unless a verified source provides it.

## Rules

- Use live evidence, not invented prices, sellers, stock states, review counts, coupons, or delivery dates.
- Treat current rendered content as primary evidence and structured data as a cross-check.
- Search Torob first; use other shops to extend coverage or verify merchant-level availability.
- Use references/shops.json for site-specific entry points, extraction hints, and timestamped Enamad observations, but validate the live site every time.
- Verify Enamad on the seller's own domain, never from a logo alone; aggregator status does not verify external merchants.
- Keep products and variants separate. Compare only prices expressed in the same currency/unit.
- Show the source link for every row and disclose partial coverage.
- Respect rate limits, robots directives, terms of service, login walls, CAPTCHA, and anti-bot restrictions. Never try to circumvent access controls.
- Do not claim persistent functionality. This skill does not save a watchlist, monitor prices in the background, send alerts, generate historical charts, validate coupons, analyze reviews, estimate delivery, or export CSV unless a separate working tool explicitly performs that action.

## Examples

### User request

~~~text
/irshop کیبورد مکانیکی مدل دقیق K
~~~

### Output format

~~~markdown
## مقایسه قیمت: کیبورد مکانیکی مدل دقیق K

| # | تصویر | محصول و مدل دقیق | قیمت (تومان) | فروشگاه / فروشنده | موجودی | وضعیت اینماد | لینک مستقیم |
|---:|---|---|---:|---|---|---|---|
| 1 | ![تصویر محصول](https://example.com/product-image.jpg) | نام و مدل دقیق | ۹۶٬۵۰۰٬۰۰۰ تومان | فروشنده‌ای که در صفحه دیده شد | موجود | بررسی‌نشده | [مشاهده محصول](https://example.com/product) |

### خلاصه
- نتایج قابل مقایسه: ۱ پیشنهاد از منابعی که واقعاً بررسی شدند.
- ارزان‌ترین گزینه: فروشنده و قیمت نمایش‌داده‌شده در جدول.
- محدودیت‌ها: هزینه ارسال بررسی نشده است.
~~~

The row above is a formatting example only, not a real offer. Never reuse its product, price, seller, or URL as search data.

## Edge Cases

- **No visible price:** show نامشخص; do not substitute a crossed-out price, a price from a similar SKU, or a search snippet without verification.
- **Price says “تماس بگیرید” or “استعلام قیمت”:** do not include it in numeric ranking or averages.
- **Price shown only in Rial:** convert only when the Rial label is explicit; mention the conversion if it materially affects the result.
- **Variant selection:** verify the chosen variant on the product page. If the variant cannot be selected or confirmed, mark the offer as uncertain or exclude it.
- **Contradictory stock indicators:** explicit sold-out text wins; if the exact offer's state cannot be resolved, use نامشخص.
- **Only one accessible shop:** provide the verified result and say that cross-shop coverage was limited.
- **All matches unavailable:** state that no in-stock comparable offer was verified; do not present an unavailable item as the cheapest purchase.
- **Unexpected page structure:** inspect semantic links, visible text, and JSON-LD; do not assume selectors from a different store work here.

## References

- **references/shops.json** — search entry points, shop types, selector hints, and extraction notes.
- **scripts/parse_price.py** — standard-library helper for Persian/Arabic numeral, currency, and stock-text normalization.
- **scripts/check_enamad.py** — polite badge-link discovery and domain cross-check helper; it does not auto-assert that a symbol is active.
- **examples/basic-usage.md** — sample request and output structure; examples are not live market data.
- Agent Skills format: https://agentskills.io/specification
