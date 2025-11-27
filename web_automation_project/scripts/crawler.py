"""
Crawler scaffold using Playwright.
Safe, read-only crawling that discovers links within the same domain.

Usage (example):
    python -m scripts.crawler --start-url "https://jiffy.secondavenue.com/" --max-depth 2 --headless

Outputs a JSON file of discovered URLs when `--output` is provided.
"""
from playwright.sync_api import sync_playwright
from urllib.parse import urljoin, urlparse
import argparse
import json
import time


def normalize_url(base, href):
    if href.startswith("//"):
        parsed = urlparse(base)
        return f"{parsed.scheme}:{href}"
    return urljoin(base, href)


def same_domain(base, url):
    try:
        return urlparse(base).netloc == urlparse(url).netloc
    except Exception:
        return False


def crawl(start_url, max_depth=2, headless=True, delay=0.0, limit=None):
    visited = set()
    to_visit = [(start_url, 0)]
    discovered = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=headless)
        page = browser.new_page()

        while to_visit:
            url, depth = to_visit.pop(0)
            if url in visited or depth > max_depth:
                continue
            try:
                page.goto(url, timeout=30000)
            except Exception:
                visited.add(url)
                continue

            visited.add(url)
            discovered.append(url)

            if limit and len(discovered) >= limit:
                break

            # collect links
            anchors = page.locator('a[href]').element_handles()
            for a in anchors:
                try:
                    href = a.get_attribute('href')
                except Exception:
                    href = None
                if not href:
                    continue
                absolute = normalize_url(url, href)
                if same_domain(start_url, absolute) and absolute not in visited:
                    to_visit.append((absolute, depth + 1))

            if delay:
                time.sleep(delay)

        browser.close()

    return discovered


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Simple Playwright crawler')
    parser.add_argument('--start-url', required=True)
    parser.add_argument('--max-depth', type=int, default=2)
    parser.add_argument('--headless', action='store_true')
    parser.add_argument('--delay', type=float, default=0.0, help='Delay between page visits (seconds)')
    parser.add_argument('--limit', type=int, default=None, help='Max number of pages to discover')
    parser.add_argument('--output', help='Write discovered URLs to a JSON file')

    args = parser.parse_args()
    urls = crawl(args.start_url, max_depth=args.max_depth, headless=args.headless, delay=args.delay, limit=args.limit)

    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump({'start_url': args.start_url, 'discovered': urls}, f, indent=2)
    else:
        for u in urls:
            print(u)
