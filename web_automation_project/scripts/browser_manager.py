# scripts/browser_manager.py

from playwright.sync_api import sync_playwright
import json
import os

class BrowserManager:
    def __init__(self, headless=True, cookie_file="cookies.json"):
        self.headless = headless
        self.cookie_file = cookie_file
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None

    def __enter__(self):
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(headless=self.headless)
        self.context = self.browser.new_context()

        # Inject cookies if file exists
        if os.path.exists(self.cookie_file):
            with open(self.cookie_file) as f:
                cookies = json.load(f)
                self.context.add_cookies(cookies)

        self.page = self.context.new_page()
        return self.page

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.browser.close()
        self.playwright.stop()
