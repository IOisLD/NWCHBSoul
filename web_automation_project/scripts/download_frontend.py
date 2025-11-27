"""
Frontend Asset Downloader — Uses Playwright to download HTML, CSS, JS, and images from the live site
and save them locally for a testing playground.

This script:
1. Opens the live website in a headless browser.
2. Extracts and downloads all referenced assets (stylesheets, scripts, images).
3. Rewrites relative URLs to point to local copies.
4. Saves everything to playground/frontend/ for offline use.

Usage:
    python -m scripts.download_frontend --url https://jiffy.secondavenue.com --output playground/frontend/

Result:
    playground/
    └── frontend/
        ├── index.html (rewritten with local asset paths)
        ├── css/
        ├── js/
        └── images/
"""

import argparse
import json
from pathlib import Path
from urllib.parse import urljoin, urlparse
from playwright.sync_api import sync_playwright
import logging

logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('FrontendDownloader')


class FrontendDownloader:
    """Download and rewrite frontend assets for local testing."""

    def __init__(self, base_url: str, output_dir: str = 'playground/frontend'):
        self.base_url = base_url
        self.output_dir = Path(output_dir)
        self.downloaded_urls = set()
        self.asset_map = {}  # Maps live URL -> local path

    def download(self, headless: bool = True):
        """Download all frontend assets."""
        self.output_dir.mkdir(parents=True, exist_ok=True)

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=headless)
            page = browser.new_page()
            
            logger.info(f"Loading {self.base_url}")
            page.goto(self.base_url, timeout=30000)
            
            # Extract asset URLs from the page
            assets = self._extract_assets(page)
            logger.info(f"Found {len(assets)} assets to download")
            
            # Download each asset
            for asset_type, urls in assets.items():
                for url in urls:
                    self._download_asset(url, asset_type)
            
            # Save the main HTML
            html = page.content()
            html_rewritten = self._rewrite_html(html)
            main_html_path = self.output_dir / 'index.html'
            with open(main_html_path, 'w', encoding='utf-8') as f:
                f.write(html_rewritten)
            logger.info(f"Saved rewritten HTML to {main_html_path}")
            
            browser.close()
        
        logger.info(f"Download complete. Files saved to {self.output_dir}")

    def _extract_assets(self, page) -> dict:
        """Extract all asset URLs from the page."""
        assets = {
            'stylesheets': [],
            'scripts': [],
            'images': []
        }

        try:
            # Get stylesheet links
            stylesheets = page.evaluate('''() => {
                return Array.from(document.querySelectorAll('link[rel="stylesheet"]'))
                    .map(el => el.href)
                    .filter(href => href && href.includes('http'));
            }''')
            assets['stylesheets'] = stylesheets or []
        except Exception as e:
            logger.warning(f"Failed to extract stylesheets: {e}")

        try:
            # Get script sources
            scripts = page.evaluate('''() => {
                return Array.from(document.querySelectorAll('script[src]'))
                    .map(el => el.src)
                    .filter(src => src && src.includes('http'));
            }''')
            assets['scripts'] = scripts or []
        except Exception as e:
            logger.warning(f"Failed to extract scripts: {e}")

        try:
            # Get image sources
            images = page.evaluate('''() => {
                return Array.from(document.querySelectorAll('img[src]'))
                    .map(el => el.src)
                    .filter(src => src && src.includes('http'));
            }''')
            assets['images'] = images or []
        except Exception as e:
            logger.warning(f"Failed to extract images: {e}")

        return assets

    def _download_asset(self, url: str, asset_type: str):
        """Download a single asset and save locally."""
        if url in self.downloaded_urls:
            return
        
        self.downloaded_urls.add(url)

        try:
            # Determine local path based on asset type
            parsed = urlparse(url)
            path_parts = parsed.path.strip('/').split('/')
            
            if asset_type == 'stylesheets':
                local_path = self.output_dir / 'css' / path_parts[-1]
            elif asset_type == 'scripts':
                local_path = self.output_dir / 'js' / path_parts[-1]
            elif asset_type == 'images':
                local_path = self.output_dir / 'images' / path_parts[-1]
            else:
                local_path = self.output_dir / 'assets' / path_parts[-1]

            local_path.parent.mkdir(parents=True, exist_ok=True)

            # Download using Playwright (handles authentication, redirects, etc.)
            from urllib.request import urlopen
            try:
                with urlopen(url, timeout=10) as response:
                    content = response.read()
                    with open(local_path, 'wb') as f:
                        f.write(content)
                    self.asset_map[url] = str(local_path.relative_to(self.output_dir))
                    logger.info(f"Downloaded {asset_type}: {url} -> {local_path.relative_to(self.output_dir)}")
            except Exception as e:
                logger.warning(f"Failed to download {url}: {e}")
        except Exception as e:
            logger.error(f"Error downloading asset {url}: {e}")

    def _rewrite_html(self, html: str) -> str:
        """Rewrite HTML to point asset URLs to local copies."""
        rewritten = html
        
        for live_url, local_path in self.asset_map.items():
            rewritten = rewritten.replace(live_url, local_path)
        
        return rewritten


def main():
    parser = argparse.ArgumentParser(description='Download frontend assets from a website for local testing.')
    parser.add_argument('--url', required=True, help='Base URL to download from')
    parser.add_argument('--output', default='playground/frontend', help='Output directory for downloaded assets')
    parser.add_argument('--headless', action='store_true', default=True, help='Run headless')
    args = parser.parse_args()

    downloader = FrontendDownloader(args.url, args.output)
    downloader.download(headless=args.headless)


if __name__ == '__main__':
    main()
