"""
DOM Selector Calibration Helper.
Analyzes a page to extract table structure and suggest selectors.

Usage:
    python -m scripts.dom_calibrator --url "https://jiffy.secondavenue.com/residents" --output results/dom_analysis.json

Outputs a detailed analysis of table rows, cell patterns, and attribute findings
to help calibrate dom_actions.py selectors.
"""
import json
from playwright.sync_api import sync_playwright
from typing import Dict, List, Any


def analyze_table_structure(page) -> Dict[str, Any]:
    """Analyze the DOM to find table patterns and potential selectors."""
    analysis = {
        'tables_found': 0,
        'rows_found': 0,
        'table_patterns': [],
        'cell_patterns': [],
        'attribute_patterns': [],
        'sample_rows': [],
        'href_candidates': []
    }
    
    # Find all table elements
    try:
        tables = page.query_selector_all('table')
        analysis['tables_found'] = len(tables)
        
        for table in tables:
            rows = table.query_selector_all('tr')
            analysis['rows_found'] += len(rows)
            
            table_classes = table.get_attribute('class') or ''
            analysis['table_patterns'].append({
                'tag': 'table',
                'class': table_classes,
                'id': table.get_attribute('id') or '',
                'rows': len(rows)
            })
            
            # Sample first 3 rows
            for idx, row in enumerate(rows[:3]):
                try:
                    cells = row.query_selector_all('td')
                    cell_data = []
                    
                    for cell_idx, cell in enumerate(cells):
                        cell_text = cell.text_content().strip()[:50]  # first 50 chars
                        cell_classes = cell.get_attribute('class') or ''
                        
                        # Look for href in span or a tags
                        href = None
                        span_href_attrs = []
                        
                        spans = cell.query_selector_all('span')
                        for span in spans:
                            if span.get_attribute('data-href'):
                                span_href_attrs.append('data-href')
                                if not href:
                                    href = span.get_attribute('data-href')
                            if span.get_attribute('data-url'):
                                span_href_attrs.append('data-url')
                                if not href:
                                    href = span.get_attribute('data-url')
                            if span.get_attribute('href'):
                                span_href_attrs.append('href')
                                if not href:
                                    href = span.get_attribute('href')
                        
                        a_tag = cell.query_selector('a')
                        if a_tag and not href:
                            href = a_tag.get_attribute('href')
                        
                        cell_data.append({
                            'index': cell_idx,
                            'text': cell_text,
                            'class': cell_classes,
                            'tag': 'td',
                            'href': href,
                            'span_href_attrs': span_href_attrs
                        })
                        
                        if href:
                            analysis['href_candidates'].append({
                                'row': idx,
                                'cell': cell_idx,
                                'text': cell_text,
                                'href': href,
                                'source': 'span' if span_href_attrs else 'a'
                            })
                    
                    analysis['sample_rows'].append({
                        'row_index': idx,
                        'cells': cell_data
                    })
                    
                except Exception as e:
                    pass
    
    except Exception as e:
        analysis['error'] = str(e)
    
    # Look for div-based rows (e.g., Material-UI tables)
    try:
        rows = page.query_selector_all('div[role="row"]')
        if rows and len(rows) > analysis['rows_found']:
            analysis['rows_found'] = len(rows)
            analysis['table_patterns'].append({
                'tag': 'div[role="row"]',
                'class': '',
                'id': '',
                'rows': len(rows)
            })
            
            # Sample first row
            for idx, row in enumerate(rows[:1]):
                try:
                    cells = row.query_selector_all('[role="cell"]')
                    cell_data = []
                    for cell_idx, cell in enumerate(cells):
                        cell_text = cell.text_content().strip()[:50]
                        cell_data.append({
                            'index': cell_idx,
                            'text': cell_text,
                            'class': cell.get_attribute('class') or ''
                        })
                    analysis['sample_rows'].append({
                        'row_index': idx,
                        'row_type': 'div-based',
                        'cells': cell_data
                    })
                except Exception:
                    pass
    except Exception:
        pass
    
    return analysis


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser()
    parser.add_argument('--url', required=True)
    parser.add_argument('--headless', action='store_true', default=True)
    parser.add_argument('--output', help='Save analysis to JSON file')
    args = parser.parse_args()
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=args.headless)
        page = browser.new_page()
        page.goto(args.url)
        
        analysis = analyze_table_structure(page)
        
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                json.dump({
                    'url': args.url,
                    'analysis': analysis
                }, f, indent=2)
        else:
            print(json.dumps(analysis, indent=2))
        
        browser.close()
