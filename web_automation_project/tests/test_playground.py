"""
Playground Test Suite — Integration tests that run against the local mock API server
instead of the live site. Safe for rapid iteration and edge-case testing.

Usage:
    # Start the mock server first (in another terminal)
    python -m scripts.mock_api_server --port 5000 --fixtures-dir playground/api_fixtures

    # Then run tests
    python -m pytest tests/test_playground.py -v
"""

import pytest
import requests
import json
from pathlib import Path


@pytest.fixture
def api_base_url():
    """Mock API server base URL."""
    return 'http://localhost:5000'


@pytest.fixture
def sample_resident_id():
    """Sample resident ID from fixtures."""
    return 1


class TestMockAPIServer:
    """Tests for the mock API server itself."""

    def test_server_health(self, api_base_url):
        """Verify mock server is running and healthy."""
        response = requests.get(f'{api_base_url}/mock-api/health')
        assert response.status_code == 200
        data = response.json()
        assert data['status'] == 'ok'
        assert data['fixtures_loaded'] >= 2

    def test_fixtures_listed(self, api_base_url):
        """Verify fixtures are loaded."""
        response = requests.get(f'{api_base_url}/mock-api/fixtures')
        assert response.status_code == 200
        data = response.json()
        assert data['total'] >= 2
        assert 'fixtures' in data

    def test_request_log_accessible(self, api_base_url):
        """Verify request log is accessible."""
        response = requests.get(f'{api_base_url}/mock-api/request-log')
        assert response.status_code == 200
        data = response.json()
        assert 'total' in data
        assert 'requests' in data


class TestLoginEndpoint:
    """Tests for the login endpoint."""

    def test_login_success(self, api_base_url):
        """Verify login endpoint returns mock response."""
        response = requests.post(f'{api_base_url}/login', json={
            'email': 'admin@jiffy.local',
            'password': 'test'
        })
        assert response.status_code == 200
        data = response.json()
        assert data['success'] is True
        assert 'token' in data
        assert 'user' in data

    def test_login_returns_user_info(self, api_base_url):
        """Verify login response includes user information."""
        response = requests.post(f'{api_base_url}/login', json={
            'email': 'admin@jiffy.local',
            'password': 'test'
        })
        data = response.json()
        user = data['user']
        assert user['email'] == 'admin@jiffy.local'
        assert user['name'] == 'Test Admin'
        assert user['role'] == 'admin'


class TestResidentsEndpoint:
    """Tests for residents API endpoints."""

    def test_get_residents_list(self, api_base_url):
        """Verify GET /api/residents returns list of residents."""
        response = requests.get(f'{api_base_url}/api/residents')
        assert response.status_code == 200
        data = response.json()
        assert data['success'] is True
        assert 'residents' in data
        assert len(data['residents']) >= 1

    def test_residents_list_structure(self, api_base_url):
        """Verify resident objects have expected fields."""
        response = requests.get(f'{api_base_url}/api/residents')
        data = response.json()
        resident = data['residents'][0]
        
        required_fields = ['id', 'name', 'email', 'unit', 'balance', 'status']
        for field in required_fields:
            assert field in resident, f"Missing field: {field}"

    def test_get_resident_by_id(self, api_base_url, sample_resident_id):
        """Verify GET /api/residents/:id returns single resident."""
        response = requests.get(f'{api_base_url}/api/residents/{sample_resident_id}')
        assert response.status_code == 200
        data = response.json()
        assert data['success'] is True
        assert data['id'] == sample_resident_id
        assert 'name' in data
        assert 'payment_history' in data

    def test_resident_has_payment_history(self, api_base_url, sample_resident_id):
        """Verify resident includes payment history."""
        response = requests.get(f'{api_base_url}/api/residents/{sample_resident_id}')
        data = response.json()
        assert 'payment_history' in data
        assert len(data['payment_history']) >= 1
        
        payment = data['payment_history'][0]
        assert 'date' in payment
        assert 'amount' in payment
        assert 'status' in payment


class TestPaymentEndpoint:
    """Tests for payment processing endpoints."""

    def test_update_resident_payment(self, api_base_url, sample_resident_id):
        """Verify PUT /api/residents/:id/payment processes payment."""
        response = requests.put(f'{api_base_url}/api/residents/{sample_resident_id}/payment', json={
            'amount': 500
        })
        assert response.status_code == 200
        data = response.json()
        assert data['success'] is True
        assert 'transaction_id' in data
        assert data['amount'] == 500

    def test_payment_updates_balance(self, api_base_url, sample_resident_id):
        """Verify payment updates resident balance."""
        response = requests.put(f'{api_base_url}/api/residents/{sample_resident_id}/payment', json={
            'amount': 500
        })
        data = response.json()
        
        # Original balance: 1200.50, payment: 500, new balance should be 700.50
        assert data['new_balance'] == 700.50

    def test_payment_includes_timestamp(self, api_base_url, sample_resident_id):
        """Verify payment response includes timestamp."""
        response = requests.put(f'{api_base_url}/api/residents/{sample_resident_id}/payment', json={
            'amount': 500
        })
        data = response.json()
        assert 'timestamp' in data


class TestErrorHandling:
    """Tests for error handling and edge cases."""

    def test_not_found_returns_404(self, api_base_url):
        """Verify non-existent endpoints return 404."""
        response = requests.get(f'{api_base_url}/api/non-existent-endpoint')
        assert response.status_code == 404
        data = response.json()
        assert 'error' in data

    def test_mock_server_handles_missing_body(self, api_base_url):
        """Verify mock server gracefully handles requests with no body."""
        response = requests.post(f'{api_base_url}/login')
        # Should either return 404 or process with defaults
        assert response.status_code in [200, 404]

    def test_request_logging_works(self, api_base_url):
        """Verify request logging captures incoming requests."""
        # Make a request
        requests.get(f'{api_base_url}/api/residents')
        
        # Check request log
        response = requests.get(f'{api_base_url}/mock-api/request-log')
        data = response.json()
        assert data['total'] >= 1


class TestPlaygroundScenarios:
    """High-level scenarios that test real use cases."""

    def test_full_login_and_resident_retrieval(self, api_base_url):
        """Scenario: Login, then retrieve resident list."""
        # Step 1: Login
        login_response = requests.post(f'{api_base_url}/login', json={
            'email': 'admin@jiffy.local',
            'password': 'test'
        })
        assert login_response.status_code == 200
        token = login_response.json()['token']
        
        # Step 2: Get residents with token
        headers = {'Authorization': f'Bearer {token}'}
        residents_response = requests.get(f'{api_base_url}/api/residents', headers=headers)
        assert residents_response.status_code == 200
        residents = residents_response.json()['residents']
        assert len(residents) >= 1

    def test_select_resident_and_process_payment(self, api_base_url, sample_resident_id):
        """Scenario: Select a resident and process a payment."""
        # Step 1: Get resident details
        resident_response = requests.get(f'{api_base_url}/api/residents/{sample_resident_id}')
        assert resident_response.status_code == 200
        resident = resident_response.json()
        initial_balance = resident['balance']
        
        # Step 2: Process payment
        payment_response = requests.put(f'{api_base_url}/api/residents/{sample_resident_id}/payment', json={
            'amount': 100
        })
        assert payment_response.status_code == 200
        payment_data = payment_response.json()
        
        # Step 3: Verify balance changed
        assert payment_data['new_balance'] == initial_balance - 100


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
