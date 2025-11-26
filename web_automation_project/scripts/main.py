from scripts.smart_matcher import SmartMatcher

matcher = SmartMatcher(threshold=75)

# Example: map Excel row to DOM
dom_field_candidates = ["Property Address", "Tenant Name", "Receipt Amount", "Status"]
for idx, row in df.iterrows():
    mapped = matcher.map_excel_to_dom(row.to_dict(), dom_field_candidates)
    if DRY_RUN:
        print(f"[DRY RUN] Mapped row {idx}: {mapped}")
    else:
        # Use mapped dict to fill inputs dynamically
        for dom_field, value in mapped.items():
            selector = f"#{dom_field.replace(' ', '-').lower()}"
            dom.fill_input(selector, value)
        dom.click_button("#submit-btn")
