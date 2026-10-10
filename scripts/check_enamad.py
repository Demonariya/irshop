#!/usr/bin/env python3
"""Polite, conservative Enamad badge/link checker for the irshop registry.

This is a verification helper, not a storefront scraper. It never logs in, bypasses
CAPTCHAs, rotates identities, or treats a badge image as proof of current validity.
"""
from __future__ import annotations

import argparse
import json
import re
import time
from datetime import datetime, timezone
from html import unescape
from html.parser import HTMLParser
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin, urlparse
from urllib.request import Request, urlopen
from urllib.robotparser import RobotFileParser

ROOT = Path(__file__).resolve().parent.parent
REGISTRY = ROOT / "references" / "shops.json"
USER_AGENT = "irshop-enamad-check/1.0"
OFFICIAL_SUFFIXES = ("enamad.ir",)
MAX_PAGE_BYTES = 2_000_000


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def normalized_host(url_or_host: str) -> str:
    raw = url_or_host.strip()
    parsed = urlparse(raw if "://" in raw else "//" + raw)
    host = (parsed.hostname or "").lower().rstrip(".")
    return host[4:] if host.startswith("www.") else host


def is_official_enamad_url(url: str) -> bool:
    try:
        parsed = urlparse(url)
        host = (parsed.hostname or "").lower().rstrip(".")
    except ValueError:
        return False
    if parsed.scheme not in ("http", "https"):
        return False
    return any(host == suffix or host.endswith("." + suffix) for suffix in OFFICIAL_SUFFIXES)


class BadgeLinkParser(HTMLParser):
    """Collect links that point to the official Enamad host, not logo images alone."""

    def __init__(self, base_url: str):
        super().__init__(convert_charrefs=True)
        self.base_url = base_url
        self.links: list[str] = []

    def _inspect(self, attrs: list[tuple[str, str | None]]) -> None:
        values = {key.lower(): (value or "") for key, value in attrs}
        candidates = []
        if values.get("href"):
            candidates.append(values["href"])
        onclick = values.get("onclick", "")
        candidates.extend(
            re.findall(r"""(?:https?:)?//[^'"\s<>]*enamad\.ir[^'"\s<>]*""", onclick, re.I)
        )
        for candidate in candidates:
            candidate = unescape(candidate.strip())
            if candidate.startswith("//"):
                candidate = "https:" + candidate
            candidate = urljoin(self.base_url, candidate)
            if is_official_enamad_url(candidate) and candidate not in self.links:
                self.links.append(candidate)

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag.lower() == "a":
            self._inspect(attrs)

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag.lower() == "a":
            self._inspect(attrs)


class VisibleTextParser(HTMLParser):
    """Extract page text without script/style contents."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parts: list[str] = []
        self._skip = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag.lower() in ("script", "style", "noscript"):
            self._skip += 1

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() in ("script", "style", "noscript") and self._skip:
            self._skip -= 1

    def handle_data(self, data: str) -> None:
        if not self._skip:
            cleaned = " ".join(data.split())
            if cleaned:
                self.parts.append(cleaned)


def fetch_page(url: str, timeout: float) -> tuple[str, str]:
    request = Request(
        url,
        headers={
            "User-Agent": USER_AGENT,
            "Accept": "text/html,application/xhtml+xml;q=0.9,*/*;q=0.5",
        },
    )
    with urlopen(request, timeout=timeout) as response:
        final_url = response.geturl()
        raw = response.read(MAX_PAGE_BYTES)
        charset = response.headers.get_content_charset() or "utf-8"
    return final_url, raw.decode(charset, errors="replace")


def robots_allows(url: str, timeout: float) -> bool | None:
    """Return True/False; None means robots could not be read conservatively."""
    parsed = urlparse(url)
    robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"
    request = Request(robots_url, headers={"User-Agent": USER_AGENT})
    try:
        with urlopen(request, timeout=timeout) as response:
            raw = response.read(500_000).decode("utf-8", errors="replace")
    except HTTPError as exc:
        if exc.code in (404, 410):
            return True
        return None
    except (URLError, TimeoutError, OSError):
        return None
    parser = RobotFileParser()
    parser.set_url(robots_url)
    parser.parse(raw.splitlines())
    return parser.can_fetch(USER_AGENT, url)


def extract_registered_domain(text: str) -> str | None:
    patterns = [
        r"(?:دامنه(?:\s+ثبت(?:\s+شده)?)?|نشانی\s+سایت|آدرس\s+سایت|domain)\s*[:：]?\s*"
        r"((?:[\w-]+\.)+[a-z\u0600-\u06ff]{2,})",
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.I)
        if match:
            return match.group(1).strip(" .،؛;")
    return None


def exact_domain_appears(text: str, expected_host: str) -> bool:
    expected = normalized_host(expected_host)
    if not expected:
        return False
    pattern = r"(?<![A-Za-z0-9.-])" + re.escape(expected) + r"(?![A-Za-z0-9.-])"
    return re.search(pattern, text, re.I) is not None


def check_shop(shop: dict[str, Any], timeout: float = 12.0) -> dict[str, Any]:
    checked_at = now_iso()
    base_url = shop.get("base_url") or ""
    expected_host = normalized_host(base_url)
    result: dict[str, Any] = {
        "id": shop.get("id"),
        "name": shop.get("name"),
        "base_url": base_url,
        "expected_domain": expected_host,
        "checked_at": checked_at,
        "status": "not_checked",
        "badge_link_seen": False,
        "badge_link_seen_current_run": False,
        "badge_url": None,
        "verification_url": None,
        "official_page_reachable": False,
        "registered_domain": None,
        "official_domain_match": None,
        "expiry_or_validity_text": None,
        "officially_verified": False,
        "notes": [],
    }

    allowed = robots_allows(base_url, timeout)
    if allowed is False:
        result["status"] = "robots_disallow"
        result["notes"].append("robots.txt disallows this check or cannot authorize it; no page was fetched.")
        return result
    if allowed is None:
        result["status"] = "robots_unavailable"
        result["notes"].append("robots.txt could not be read; skipped this site rather than guessing permission.")
        return result

    try:
        final_home_url, homepage = fetch_page(base_url, timeout)
    except HTTPError as exc:
        result["status"] = "site_http_error"
        result["notes"].append(f"Homepage returned HTTP {exc.code}; no access-control bypass was attempted.")
        return result
    except Exception as exc:
        result["status"] = "site_unreachable"
        result["notes"].append(f"Homepage could not be fetched ({type(exc).__name__}); no bypass was attempted.")
        return result

    if urlparse(final_home_url).scheme not in ("http", "https"):
        result["status"] = "site_unreachable"
        result["notes"].append("Homepage did not resolve to an HTTP(S) page.")
        return result

    links = BadgeLinkParser(final_home_url)
    try:
        links.feed(homepage)
    except Exception:
        result["notes"].append("HTML parsing was partial; site may use a dynamic badge.")
    badge_url = links.links[0] if links.links else None
    old_enamad = shop.get("enamad") or {}
    known_url = old_enamad.get("verification_url") or old_enamad.get("badge_url")

    if badge_url:
        result["badge_link_seen"] = True
        result["badge_link_seen_current_run"] = True
        result["badge_url"] = badge_url
        result["verification_url"] = badge_url
    elif known_url and is_official_enamad_url(known_url):
        badge_url = known_url
        result["badge_link_seen"] = bool(old_enamad.get("badge_link_seen"))
        result["badge_url"] = known_url
        result["verification_url"] = known_url
        result["notes"].append("Reused a previously observed official badge URL; this run did not rediscover the badge link in fetched HTML.")
    else:
        result["status"] = "badge_link_not_found_in_fetched_html"
        result["notes"].append("No official Enamad link was found in fetched HTML. A dynamic badge may not appear in static HTML; this does not prove that the site has no badge.")
        return result

    try:
        final_verify_url, verification_html = fetch_page(badge_url, timeout)
    except Exception as exc:
        result["status"] = "badge_seen_official_check_unavailable"
        result["notes"].append(f"Official verification URL could not be loaded ({type(exc).__name__}). Validity remains unknown.")
        return result

    if not is_official_enamad_url(final_verify_url):
        result["status"] = "official_redirect_outside_domain"
        result["notes"].append("The badge URL redirected outside the official Enamad domain; no verification claim was made.")
        return result

    result["official_page_reachable"] = True
    visible = VisibleTextParser()
    try:
        visible.feed(verification_html)
    except Exception:
        pass
    text = " ".join(visible.parts)
    reported_domain = extract_registered_domain(text)
    if reported_domain:
        result["registered_domain"] = reported_domain
        matches = normalized_host(reported_domain) == expected_host
        result["official_domain_match"] = matches
        if not matches:
            result["status"] = "domain_mismatch"
            result["notes"].append("The domain shown by the verification page differs from the store domain.")
            return result
    elif exact_domain_appears(text, expected_host):
        result["registered_domain"] = expected_host
        result["official_domain_match"] = True
    else:
        result["status"] = "official_page_domain_unknown"
        result["notes"].append("Official page loaded, but a registered domain could not be extracted reliably.")
        return result

    result["status"] = "official_page_domain_match_needs_manual_validity_check"
    result["notes"].append("The domain appears to match, but this helper does not parse the Enamad expiry/status fields reliably enough to mark the symbol active.")
    result["notes"].append("Check the current validity/expiry state on the official page before changing officially_verified to true.")
    return result


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check public Enamad badge links conservatively; no login or access-control bypass."
    )
    parser.add_argument("--all", action="store_true", help="Check every enabled shop in the registry.")
    parser.add_argument("--limit", type=int, default=12, help="Maximum shops to check (default: 12; ignored with --all).")
    parser.add_argument("--timeout", type=float, default=12.0, help="Per-request timeout in seconds.")
    parser.add_argument("--delay", type=float, default=1.0, help="Seconds to wait between shops.")
    parser.add_argument("--update-registry", action="store_true", help="Write check results into references/shops.json.")
    parser.add_argument("--output", help="Optional path to write the JSON report.")
    args = parser.parse_args()

    if args.timeout <= 0 or args.delay < 0 or args.limit < 1:
        parser.error("--timeout must be positive, --delay non-negative, and --limit at least 1")

    with REGISTRY.open("r", encoding="utf-8") as handle:
        registry = json.load(handle)

    shops = [shop for shop in registry.get("shops", []) if shop.get("enabled", True)]
    if not args.all:
        shops = shops[: args.limit]

    results = []
    by_id = {shop.get("id"): shop for shop in registry.get("shops", [])}
    for index, shop in enumerate(shops):
        results.append(check_shop(shop, timeout=args.timeout))
        if index + 1 < len(shops) and args.delay:
            time.sleep(args.delay)

    report = {
        "checked_at": now_iso(),
        "checked_count": len(results),
        "active_verified_count": sum(row.get("officially_verified") is True for row in results),
        "note": "A badge/link does not prove current validity. This helper never sets officially_verified=true automatically.",
        "results": results,
    }

    if args.update_registry:
        for row in results:
            shop = by_id.get(row["id"])
            if not shop:
                continue
            old = dict(shop.get("enamad") or {})
            old.update({
                "status": row["status"],
                "badge_link_seen": row["badge_link_seen"],
                "badge_link_seen_current_run": row["badge_link_seen_current_run"],
                "badge_url": row["badge_url"],
                "verification_url": row["verification_url"],
                "official_page_reachable": row["official_page_reachable"],
                "registered_domain": row["registered_domain"],
                "official_domain_match": row["official_domain_match"],
                "officially_verified": False,
                "checked_at": row["checked_at"],
                "evidence": "; ".join(row["notes"]),
            })
            shop["enamad"] = old
        with REGISTRY.open("w", encoding="utf-8", newline="\n") as handle:
            json.dump(registry, handle, ensure_ascii=False, indent=2)
            handle.write("\n")

    output = json.dumps(report, ensure_ascii=False, indent=2)
    if args.output:
        Path(args.output).write_text(output + "\n", encoding="utf-8")
    print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
