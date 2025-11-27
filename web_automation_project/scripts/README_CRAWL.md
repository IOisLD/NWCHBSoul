# Crawler & Scraper - Quick Usage Guide

This project includes powerful, read-only **crawler** and **scraper** utilities for reconnaissance and data extraction from the target website. Both are safe by design—they only read and extract data; they do not modify anything on the remote site.

---

## Setup

From the project root, activate your venv and install dependencies:

```powershell
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
playwright install
```

---

## Quick Examples

### 1. Crawl a Website (Discover URLs)

**Purpose:** Navigate the site, follow links, and collect all discovered URLs up to a certain depth.

```powershell
python -m scripts.crawler --start-url "https://jiffy.secondavenue.com/" --max-depth 1 --headless --output results/discovered_urls.json
```

**What happens:**
- Launches a headless Chrome browser (no UI window).
- Navigates to the start URL.
- Scans for all `<a href>` links and follows them (stays within the same domain).
- Limits to depth 1 (start page + direct links only; set `--max-depth 2` for deeper crawl).
- Saves discovered URLs to `results/discovered_urls.json`.

**Output example:**
```json
{
  "start_url": "https://jiffy.secondavenue.com/",
  "discovered": [
    "https://jiffy.secondavenue.com/",
    "https://jiffy.secondavenue.com/residents",
    "https://jiffy.secondavenue.com/payments"
  ]
}
```

---

### 2. Scrape Data from a Single Page

**Purpose:** Extract structured data (title, lists, API URLs, table rows) from a single URL.

```powershell
python -m scripts.scraper --url "https://jiffy.secondavenue.com/residents" --headless --output results/scraped_page.json
```

**What happens:**
- Navigates to the URL.
- Extracts:
  - Page title (`<h1>` or `<title>`).
  - All list items (`<ul><li>` elements).
  - All detected API URLs (using regex on page HTML).
  - Sample table rows (useful for identifying the DOM structure).
- Saves results to JSON.

**Output example:**
```json
{
  "url": "https://jiffy.secondavenue.com/residents",
  "title": "Resident Management",
  "list_items": ["Item 1", "Item 2"],
  "api_urls": ["https://api.example.com/api/residents"],
  "sample_rows": [
    {
      "cells": ["John Doe", "Apt 101", "Active"],
      "name": "John Doe",
      "href": "/residents/123"
    }
  ]
}
```

---

### 3. Combined Crawl + Scrape

**Purpose:** Crawl the site to discover pages, then scrape data from each discovered page.

```powershell
python -m scripts.crawl_scrape_runner --start-url "https://jiffy.secondavenue.com/" --max-depth 1 --headless --output results/crawled_scraped.json
```

**What happens:**
- Runs the crawler to discover all pages.
- For each discovered page, runs the scraper to extract data.
- Saves all results to a single JSON file.

**Output example:**
```json
{
  "start_url": "https://jiffy.secondavenue.com/",
  "results": [
    {
      "url": "https://jiffy.secondavenue.com/",
      "title": "Home",
      "api_urls": [],
      "sample_rows": []
    },
    {
      "url": "https://jiffy.secondavenue.com/residents",
      "title": "Residents",
      "api_urls": ["https://api.example.com/api/residents"],
      "sample_rows": [...]
    }
  ]
}
```

---

## CLI Options

### `crawler.py`

```
--start-url TEXT           Starting URL (required)
--max-depth INT            Max crawl depth (default: 2)
--headless                 Run in headless mode (no UI window)
--delay FLOAT              Delay between page visits in seconds (default: 0.0)
--limit INT                Max number of pages to discover (default: unlimited)
--output FILE              Save discovered URLs to JSON file (optional)
```

### `scraper.py`

```
--url TEXT                 URL to scrape (required)
--headless                 Run in headless mode
--output FILE              Save scraped data to JSON file (optional)
```

### `crawl_scrape_runner.py`

```
--start-url TEXT           Starting URL (required)
--max-depth INT            Max crawl depth (default: 1)
--headless                 Run in headless mode
--limit INT                Max number of pages to scrape (optional)
--output FILE              Save results to JSON file (optional)
```

---

## Customizing Selectors (For Hardened Extraction)

The scraper includes a helper function `extract_resident_rows()` that extracts table rows with enhanced features:

**Python code example:**

```python
from scripts.scraper import extract_resident_rows
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page()
    page.goto("https://jiffy.secondavenue.com/residents")
    
    # Extract resident rows with specific selectors
    rows = extract_resident_rows(
        page,
        row_selector='tr',           # CSS selector for table rows
        name_cell_index=0,           # Column index for resident name
        href_attr='data-href'        # Attribute to search for href
    )
    
    for row in rows:
        print(f"Name: {row['name']}, Href: {row['href']}")
    
    browser.close()
```

**If the target site uses a different structure** (e.g., `td.MuiTableroot` or custom classes), adjust:
- `row_selector`: e.g., `'tr.resident-row'` or `'div[role="row"]'`
- `name_cell_index`: adjust if name is not the first column
- `href_attr`: change to `'data-url'`, `'data-link'`, etc. if different

---

## Real-World Workflow

### Step 1: Reconnaissance
```powershell
# Discover the site structure
python -m scripts.crawl_scrape_runner --start-url "https://jiffy.secondavenue.com/" --max-depth 0 --headless --output results/site_structure.json

# Open results/site_structure.json and review the JSON
# Identify the resident list page URL
```

### Step 2: Inspect Page Structure
```powershell
# Scrape the resident list page to see the table structure
python -m scripts.scraper --url "https://jiffy.secondavenue.com/residents" --output results/residents_page.json

# Open the JSON and review sample_rows to understand the HTML structure
```

### Step 3: Refine Main Pipeline
Use the insights from Steps 1–2 to:
1. Update `dom_actions.py`'s `find_resident_href()` with the actual CSS selectors.
2. Update `smart_match.py`'s tenant matching logic based on extracted names.
3. Run `main.py` in dry-run mode to validate the end-to-end flow.

---

## Safety & Performance

- **Read-only:** All scripts only read from the remote site. They never submit forms or make API calls.
- **Headless mode:** Use `--headless` for faster execution and to run on servers without a display.
- **Delays:** Use `--delay 1.0` to add a 1-second pause between page visits if rate-limiting is a concern.
- **Limits:** Use `--limit 10` to test with a small number of pages before full crawl.

---

## Troubleshooting

### "No module named 'playwright'"
```powershell
pip install playwright
playwright install
```

### "Connection refused" or "timeout"
- Check your internet connection and firewall.
- Verify the URL is correct and reachable.
- Try without `--headless` to see the browser's console for errors.

### "Element not found" or incorrect data extraction
- Run the scraper on the page to inspect `sample_rows`.
- Manually review the page structure (right-click → Inspect in browser).
- Update the selector in your calling code or in `scraper.py`.

### Large crawls are slow
- Reduce `--max-depth` or use `--limit`.
- Add `--delay 0.1` or run multiple smaller crawls in parallel.

---

## Integration with `main.py`

The crawl/scrape results can feed into the main automation pipeline:

1. **Run a crawl** to identify all resident pages.
2. **Extract href/names** using the scraper.
3. **Populate your input Excel** with the discovered resident data.
4. **Run `main.py`** to automate the update process.

Example integration (pseudocode):
```python
# 1. Scrape resident list
scraped_data = scrape_page(page)  # from scraper.py
resident_rows = extract_resident_rows(page)

# 2. Build DataFrame for main.py input
residents_df = pd.DataFrame([
    {'name': row['name'], 'href': row['href']}
    for row in resident_rows
])
residents_df.to_excel('input_data/input.xlsx', index=False)

# 3. Run main automation
# python -m scripts.main --dry-run
```

---

For questions or to extend the crawl/scrape logic, review the source files:
- `scripts/crawler.py`: Crawl logic
- `scripts/scraper.py`: Scrape helper functions
- `scripts/crawl_scrape_runner.py`: Combined runner
