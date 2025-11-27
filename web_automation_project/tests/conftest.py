"""
Pytest configuration and fixtures for test suite.
"""
import pytest
import sys
from pathlib import Path

# Add project root to path so imports work
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


@pytest.fixture
def mock_page():
    """Provide a mock Playwright page object."""
    from unittest.mock import Mock
    page = Mock()
    page.url = "https://example.com/page"
    page.title.return_value = "Test Page"
    return page


@pytest.fixture
def temp_excel_file(tmp_path):
    """Create a temporary Excel file for testing."""
    import pandas as pd
    
    df = pd.DataFrame({
        'name': ['John Doe', 'Jane Smith'],
        'email': ['john@example.com', 'jane@example.com'],
        'amount': [100.0, 200.0]
    })
    
    filepath = tmp_path / "test_data.xlsx"
    df.to_excel(filepath, index=False)
    return filepath


@pytest.fixture
def api_config():
    """Provide a test API configuration."""
    return {
        'endpoint': 'https://test-api.example.com/update',
        'auth_type': 'bearer',
        'auth_token': 'test_token_123',
        'timeout': 30,
        'retry_count': 3
    }


@pytest.fixture
def sample_record():
    """Provide a sample record for testing."""
    return {
        'name': 'John Doe',
        'resident_href': '/residents/123',
        'amount': 150.00,
        'reference': 'Test Payment',
        'processed_timestamp': '2025-11-27T10:00:00',
        'row_index': 1
    }
