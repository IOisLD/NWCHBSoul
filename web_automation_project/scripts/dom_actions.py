# scripts/dom_actions.py

from playwright.sync_api import Page

class DOMActions:
    def __init__(self, page: Page):
        self.page = page

    def fill_input(self, selector: str, value: str):
        try:
            self.page.fill(selector, str(value))
        except Exception as e:
            print(f"[WARN] Could not fill {selector}: {e}")

    def click_button(self, selector: str):
        try:
            self.page.click(selector)
        except Exception as e:
            print(f"[WARN] Could not click {selector}: {e}")

    def read_inputs(self, container_selector="form"):
        """Automatically read all input fields within a form"""
        input_elements = self.page.query_selector_all(f"{container_selector} input, {container_selector} select")
        fields = {}
        for el in input_elements:
            name = el.get_attribute("name") or el.get_attribute("id")
            if name:
                fields[name] = el
        return fields
