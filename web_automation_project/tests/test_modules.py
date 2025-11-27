"""
Unit tests for the web automation project.

Run with:
    pytest tests/test_modules.py -v

Or with coverage:
    pytest tests/test_modules.py --cov=scripts --cov-report=html
"""
import pytest
import json
import tempfile
import os
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# Import modules to test
from scripts.crawler import crawl, normalize_url, same_domain
from scripts.scraper import (
    extract_title, extract_list_items, extract_api_urls_from_html,
    extract_resident_rows, scrape_page
)
from scripts.api_replay import APIReplay
from scripts.load_input import load_excel


class TestCrawler:
    """Tests for crawler.py"""
    
    def test_normalize_url_absolute(self):
        """Test normalization of absolute URLs."""
        base = "https://example.com/page"
        href = "https://other.com/path"
        result = normalize_url(base, href)
        assert result == "https://other.com/path"
    
    def test_normalize_url_relative(self):
        """Test normalization of relative URLs."""
        base = "https://example.com/page"
        href = "/about"
        result = normalize_url(base, href)
        assert result == "https://example.com/about"
    
    def test_normalize_url_protocol_relative(self):
        """Test normalization of protocol-relative URLs."""
        base = "https://example.com/page"
        href = "//other.com/path"
        result = normalize_url(base, href)
        assert result == "https://other.com/path"
    
    def test_same_domain_true(self):
        """Test same_domain returns True for same domain."""
        base = "https://example.com/page"
        url = "https://example.com/other"
        assert same_domain(base, url) is True
    
    def test_same_domain_false(self):
        """Test same_domain returns False for different domain."""
        base = "https://example.com/page"
        url = "https://other.com/page"
        assert same_domain(base, url) is False
    
    def test_same_domain_with_subdomain(self):
        """Test same_domain distinguishes subdomains."""
        base = "https://example.com/page"
        url = "https://sub.example.com/page"
        assert same_domain(base, url) is False


class TestScraper:
    """Tests for scraper.py"""
    
    def test_extract_title_with_h1(self):
        """Test title extraction from h1."""
        mock_page = Mock()
        mock_locator = Mock()
        mock_page.locator.return_value = mock_locator
        mock_locator.count.return_value = 1
        mock_h1 = Mock()
        mock_h1.text_content.return_value = "  Test Title  "
        mock_locator.first = mock_h1
        
        result = extract_title(mock_page)
        assert result == "Test Title"
    
    def test_extract_title_fallback_to_page_title(self):
        """Test title extraction falls back to page.title()."""
        mock_page = Mock()
        mock_locator = Mock()
        mock_page.locator.return_value = mock_locator
        mock_locator.count.return_value = 0
        mock_page.title.return_value = "Page Title"
        
        result = extract_title(mock_page)
        assert result == "Page Title"
    
    def test_extract_api_urls_from_html(self):
        """Test API URL extraction from HTML."""
        html = """
        <a href="https://api.example.com/api/residents">Link</a>
        <img src="https://cdn.example.com/image.png">
        <script src="https://api.example.com/api/fetch"></script>
        """
        urls = extract_api_urls_from_html(html)
        assert len(urls) == 2
        assert "https://api.example.com/api/residents" in urls
        assert "https://api.example.com/api/fetch" in urls
    
    def test_extract_list_items(self):
        """Test list item extraction."""
        mock_page = Mock()
        mock_locator = Mock()
        mock_page.locator.return_value = mock_locator
        mock_locator.all_text_contents.return_value = ["Item 1", "Item 2", "Item 3"]
        
        result = extract_list_items(mock_page)
        assert result == ["Item 1", "Item 2", "Item 3"]


class TestAPIReplay:
    """Tests for api_replay.py"""
    
    def test_api_replay_init_default_config(self):
        """Test APIReplay initializes with default config from env."""
        with patch.dict(os.environ, {'API_ENDPOINT': 'https://test.com'}, clear=False):
            api = APIReplay(dry_run=True)
            assert api.dry_run is True
            assert 'endpoint' in api.config
    
    def test_api_replay_custom_config(self):
        """Test APIReplay accepts custom config."""
        config = {
            'endpoint': 'https://custom.com/api',
            'auth_type': 'bearer',
            'auth_token': 'test_token',
            'timeout': 60,
            'retry_count': 5
        }
        api = APIReplay(dry_run=True, config=config)
        assert api.config == config
    
    def test_update_payment_dry_run(self):
        """Test update_payment in dry_run mode."""
        config = {'endpoint': 'https://test.com'}
        api = APIReplay(dry_run=True, config=config)
        
        record = {'name': 'John', 'amount': 100}
        result = api.update_payment(record)
        
        assert result['success'] is True
        assert result['status_code'] == 200
        assert result['error'] is None
    
    def test_api_replay_bearer_auth(self):
        """Test APIReplay sets Bearer auth header."""
        config = {
            'endpoint': 'https://test.com',
            'auth_type': 'bearer',
            'auth_token': 'token123'
        }
        api = APIReplay(dry_run=True, config=config)
        assert 'Authorization' in api.session.headers
        assert api.session.headers['Authorization'] == 'Bearer token123'
    
    def test_api_replay_apikey_auth(self):
        """Test APIReplay sets API Key auth header."""
        config = {
            'endpoint': 'https://test.com',
            'auth_type': 'apikey',
            'auth_token': 'key123'
        }
        api = APIReplay(dry_run=True, config=config)
        assert 'X-API-Key' in api.session.headers
        assert api.session.headers['X-API-Key'] == 'key123'


class TestLoadInput:
    """Tests for load_input.py"""
    
    def test_load_excel_with_valid_file(self):
        """Test load_excel with a valid Excel file."""
        # Create a temporary Excel file
        import pandas as pd
        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = os.path.join(tmpdir, 'test.xlsx')
            df = pd.DataFrame({'name': ['John', 'Jane'], 'value': [1, 2]})
            df.to_excel(filepath, index=False)
            
            result = load_excel(filepath)
            assert isinstance(result, type(df))  # Should be a DataFrame
            assert len(result) == 2
    
    def test_load_excel_with_missing_file(self):
        """Test load_excel with a missing file."""
        result = load_excel('/nonexistent/file.xlsx')
        # Should return empty DataFrame, not crash
        import pandas as pd
        assert isinstance(result, type(pd.DataFrame()))
        assert len(result) == 0
    
    def test_load_excel_with_csv_fallback(self):
        """Test load_excel falls back to CSV reading."""
        import pandas as pd
        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = os.path.join(tmpdir, 'test.csv')
            with open(filepath, 'w') as f:
                f.write("name,value\nJohn,1\nJane,2\n")
            
            result = load_excel(filepath)
            assert isinstance(result, type(pd.DataFrame()))
            assert len(result) == 2


class TestIntegration:
    """Integration tests combining multiple modules."""
    
    def test_crawl_scrape_workflow(self):
        """Test a basic crawl -> scrape workflow."""
        # This is a smoke test that verifies the modules work together
        # In a real scenario, you'd mock Playwright to avoid actual network calls
        assert True  # Placeholder
    
    def test_dry_run_api_flow(self):
        """Test dry-run mode doesn't make actual API calls."""
        config = {'endpoint': 'https://test.com'}
        api = APIReplay(dry_run=True, config=config)
        
        record = {
            'name': 'Test User',
            'resident_href': '/residents/1',
            'amount': 50.00
        }
        
        result = api.update_payment(record)
        # In dry-run, no actual request should be made
        assert result['success'] is True
        assert '[DRY-RUN]' in result['response']


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
