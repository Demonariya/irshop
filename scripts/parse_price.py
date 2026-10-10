#!/usr/bin/env python3
"""Normalize an already-extracted Iranian price label and stock text.

This helper does not scrape pages. Pass only the price/availability text associated
with one product offer, not the entire page or product title.
"""
from __future__ import annotations

import argparse
import json
import re
import unicodedata
from decimal import Decimal, InvalidOperation
from typing import Any

_DIGITS = str.maketrans(
    "۰۱۲۳۴۵۶۷۸۹٠١٢٣٤٥٦٧٨٩",
    "01234567890123456789",
)
_OUT_OF_STOCK = re.compile(
    r"ناموجود|اتمام\s*موجودی|موجود\s*نیست|موجود\s*نمی.?باشد|فعلاً?\s*موجود\s*نیست|"
    r"فروخته\s*شد|sold\s*out|out\s*of\s*stock|unavailable",
    re.IGNORECASE,
)
_IN_STOCK = re.compile(
    r"موجود\s*است|موجود|افزودن\s*به\s*سبد|خرید\s*محصول|خرید\s*آنلاین|"
    r"add\s*to\s*cart|buy\s*now|in\s*stock|available",
    re.IGNORECASE,
)
_NO_PRICE = re.compile(
    r"تماس\s*بگیرید|استعلام\s*قیمت|قیمت\s*توافقی|برای\s*قیمت\s*تماس|price\s*on\s*request",
    re.IGNORECASE,
)
_NUMBER = re.compile(
    r"(?<![A-Za-z0-9])(?:\d{1,3}(?:[,\s]\d{3})+|\d+)(?:\.\d+)?(?![A-Za-z0-9])"
)


def normalize_digits(text: str) -> str:
    """Convert Persian/Arabic-Indic digits and normalize Unicode separators."""
    value = unicodedata.normalize("NFKC", text).translate(_DIGITS)
    return value.replace("\u00a0", " ").replace("\u202f", " ")


def detect_availability(text: str) -> str:
    """Return out_of_stock, in_stock, or unknown from explicit text signals."""
    normalized = normalize_digits(text)
    # Explicit unavailability wins over a generic purchase phrase elsewhere.
    if _OUT_OF_STOCK.search(normalized):
        return "out_of_stock"
    if _IN_STOCK.search(normalized):
        return "in_stock"
    return "unknown"


def _normalise_numeric_separators(text: str) -> str:
    value = normalize_digits(text)
    value = value.replace("٬", ",").replace("،", ",").replace("٫", ".")
    # Handle dot-grouped thousands such as 96.500.000, but keep decimals like 96.5.
    def fix_dotted_groups(match: re.Match[str]) -> str:
        token = match.group(0)
        if re.fullmatch(r"\d{1,3}(?:\.\d{3})+", token):
            return token.replace(".", "")
        return token

    return re.sub(r"\d+(?:\.\d+)+", fix_dotted_groups, value)


def _json_number(value: Decimal | None) -> int | float | None:
    if value is None:
        return None
    if value == value.to_integral_value():
        return int(value)
    return float(value)


def parse_price(text: str, assume_toman: bool = False) -> dict[str, Any]:
    """Parse one price label. Never guess the currency when its unit is unclear."""
    raw = text.strip()
    normalized = _normalise_numeric_separators(raw)
    availability = detect_availability(raw)

    if not raw or _NO_PRICE.search(normalized):
        return {
            "raw": raw,
            "normalized": normalized,
            "amount": None,
            "currency": "unknown",
            "price_toman": None,
            "price_status": "missing",
            "availability": availability,
        }

    # A decimal comma such as 96,5 is uncommon in Iranian price labels. This
    # helper deliberately expects the agent to isolate the visible price label.
    match = _NUMBER.search(normalized)
    if not match:
        return {
            "raw": raw,
            "normalized": normalized,
            "amount": None,
            "currency": "unknown",
            "price_toman": None,
            "price_status": "missing",
            "availability": availability,
        }

    numeric_text = match.group(0).replace(",", "").replace(" ", "")
    try:
        amount = Decimal(numeric_text)
    except InvalidOperation:
        amount = None

    if amount is None or amount < 0:
        return {
            "raw": raw,
            "normalized": normalized,
            "amount": None,
            "currency": "unknown",
            "price_toman": None,
            "price_status": "invalid",
            "availability": availability,
        }

    multiplier = Decimal(1)
    if re.search(r"میلیون|million|\bM\b", normalized, re.IGNORECASE):
        multiplier = Decimal(1_000_000)
    elif re.search(r"هزار|thousand|\bK\b", normalized, re.IGNORECASE):
        multiplier = Decimal(1_000)

    amount *= multiplier
    is_rial = bool(re.search(r"ریال|ریالی|\bIRR\b|\brials?\b", normalized, re.IGNORECASE))
    is_toman = bool(re.search(r"تومان|تومن|تومانی|\bIRT\b|\bTMN\b|\btomans?\b", normalized, re.IGNORECASE))

    if is_rial and is_toman:
        currency = "unknown"
        price_toman = None
        status = "unit_ambiguous"
    elif is_rial:
        currency = "rial"
        price_toman = amount / Decimal(10)
        status = "ok"
    elif is_toman or assume_toman:
        currency = "toman"
        price_toman = amount
        status = "ok"
    else:
        currency = "unknown"
        price_toman = None
        status = "unit_unknown"

    return {
        "raw": raw,
        "normalized": normalized,
        "amount": _json_number(amount),
        "currency": currency,
        "price_toman": _json_number(price_toman),
        "price_status": status,
        "availability": availability,
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Normalize one visible Persian/Arabic price label; this does not scrape websites."
    )
    parser.add_argument("text", help="The price label text for one offer")
    parser.add_argument(
        "--assume-toman",
        action="store_true",
        help="Treat a unitless amount as Toman only when the page context confirms that unit",
    )
    args = parser.parse_args()
    print(json.dumps(parse_price(args.text, assume_toman=args.assume_toman), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
