"""
Scraper helpers to extract data from a Playwright page.
Provides small extraction utilities (title, lists, API URL regex, resident row extractor).

Usage (example):
    from playwright.sync_api import sync_playwright
    from scripts.scraper import scrape_page

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto('https://example.com')
        data = scrape_page(page)
        print(data)

"""
import re
from typing import Dict, List

API_URL_REGEX = r"https?://[^\s\"']+/api/[^\s\"']+"


def extract_title(page) -> str:
    try:
        if page.locator('h1').count() > 0:
            return page.locator('h1').first.text_content().strip()
    except Exception:
        pass
    try:
        return page.title()
    except Exception:
        return ''


def extract_list_items(page, selector='ul li') -> List[str]:
    try:
        return page.locator(selector).all_text_contents()
    except Exception:
        return []


def extract_api_urls_from_html(html: str) -> List[str]:
    return re.findall(API_URL_REGEX, html)


def extract_api_urls_from_page(page) -> List[str]:
    try:
        html = page.content()
        return extract_api_urls_from_html(html)
    except Exception:
        return []


def extract_resident_rows(page, row_selector='tr', name_cell_index=0, href_attr='data-href') -> List[Dict]:
    """
    Extract resident rows from a table. Returns list of dicts with:
    - 'cells': list of cell text values
    - 'href': extracted href (from 'data-href', 'data-url', or <a> tag)
    - 'name': text of the name cell (typically first td)
    
    Args:
        page: Playwright page object
        row_selector: CSS selector for table rows (default: 'tr')
        name_cell_index: which cell contains the resident name (default: 0 = first td)
        href_attr: attribute name to look for href (e.g., 'data-href', 'data-url')
    """
    rows = []
    try:
        elements = page.locator(row_selector).element_handles()
        for el in elements:
            try:
                cells = el.query_selector_all('td')
                row_texts = [c.text_content().strip() if c and c.text_content() else '' for c in cells]
                
                # Extract href from first cell (or any td) if available
                href = None
                name = row_texts[name_cell_index] if name_cell_index < len(row_texts) else ''
                
                # Try to find href in span or a tags within the cells
                try:
                    first_cell = cells[name_cell_index] if name_cell_index < len(cells) else cells[0]
                    # Check span with data attributes
                    span = first_cell.query_selector(f'span[{href_attr}]')
                    if span:
                        href = span.get_attribute(href_attr)
                    # Fallback: check for <a> tag
                    if not href:
                        a = first_cell.query_selector('a[href]')
                        if a:
                            href = a.get_attribute('href')
                except Exception:
                    pass
                
                rows.append({
                    'cells': row_texts,
                    'name': name,
                    'href': href
                })
            except Exception:
                continue
    except Exception:
        pass
    return rows


def scrape_page(page) -> Dict:
    """Return a dict with common scraped fields: title, lists, api_urls, sample_rows."""
    return {
        'url': page.url,
        'title': extract_title(page),
        'list_items': extract_list_items(page),
        'api_urls': extract_api_urls_from_page(page),
        'sample_rows': extract_resident_rows(page, row_selector='tr')
    }


if __name__ == '__main__':
    import argparse
    from playwright.sync_api import sync_playwright
    import json

    parser = argparse.ArgumentParser()
    parser.add_argument('--url', required=True)
    parser.add_argument('--headless', action='store_true')
    parser.add_argument('--output', help='JSON file to save scraped data')
    args = parser.parse_args()

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=args.headless)
        page = browser.new_page()
        page.goto(args.url)
        data = scrape_page(page)
        browser.close()

    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
    else:
        print(data)
