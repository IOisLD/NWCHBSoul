"""
Runner that uses `crawler.crawl` to discover pages, then `scraper.scrape_page` to extract data.
Writes combined results to a JSON file.

Usage:
    python -m scripts.crawl_scrape_runner --start-url https://jiffy.secondavenue.com/ --max-depth 1 --output results/crawled_scraped.json

This runner is intended as a safe, read-only reconnaissance tool.
"""
import argparse
import json
from scripts.crawler import crawl
from scripts.scraper import scrape_page
from scripts.utils import get_fetch_logger_script
from scripts.interactive_explorer import InteractiveExplorer
from playwright.sync_api import sync_playwright


def run(start_url, max_depth=1, headless=True, output=None, limit=None):
    urls = crawl(start_url, max_depth=max_depth, headless=headless, limit=limit)

    results = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=headless)
        page = browser.new_page()
        for u in urls:
            try:
                page.goto(u, timeout=30000)
                
                # Explore the page deeply (General, Request/Response Headers, Network Log, Forms, Buttons, Tables, API Patterns)
                explorer = InteractiveExplorer(page, headless=headless)
                explorer.inject_network_logger()
                
                # Allow a moment for any on-load network activity
                page.wait_for_timeout(2000)
                
                # Get basic scrape data
                data = scrape_page(page)
                
                # Merge explorer report into data
                report = explorer.generate_report()
                data['exploration_report'] = report
                
                results.append(data)
            except Exception:
                results.append({'url': u, 'error': 'failed to load or scrape'})
        browser.close()

    if output:
        with open(output, 'w', encoding='utf-8') as f:
            json.dump({'start_url': start_url, 'results': results}, f, indent=2)
    return results


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--start-url', required=True)
    parser.add_argument('--max-depth', type=int, default=1)
    parser.add_argument('--headless', action='store_true')
    parser.add_argument('--limit', type=int, default=None)
    parser.add_argument('--output', help='File to write JSON output')

    args = parser.parse_args()
    run(args.start_url, max_depth=args.max_depth, headless=args.headless, output=args.output, limit=args.limit)
