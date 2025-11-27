"""
Mock API Server — A Flask-based testing playground that replays captured API responses.

This server:
- Serves mock API responses from JSON fixtures (captured from the live site).
- Accepts GET, POST, PUT, DELETE requests matching real endpoints.
- Logs all requests for debugging and introspection.
- Allows easy manipulation of responses for testing edge cases.

Setup:
    pip install flask python-dotenv

Usage:
    python -m scripts.mock_api_server --port 5000 --fixtures-dir api_fixtures/

Or from Python:
    from scripts.mock_api_server import create_app
    app = create_app(fixtures_dir='api_fixtures/')
    app.run(debug=True, port=5000)

Fixture Structure:
    api_fixtures/
    ├── login.json          (POST /login response)
    ├── residents.json      (GET /api/residents response)
    ├── residents_1.json    (GET /api/residents/1 response)
    └── update_payment.json (PUT /api/residents/1/payment response)

Each JSON file contains:
    {
        "status": 200,
        "headers": {"Content-Type": "application/json"},
        "body": { ... actual response data ... }
    }
"""

import json
import argparse
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional
from flask import Flask, request, jsonify, Response
from flask_cors import CORS

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('MockAPI')


class MockAPIServer:
    """Flask app wrapper for serving mock API responses."""

    def __init__(self, fixtures_dir: str = 'api_fixtures'):
        self.fixtures_dir = Path(fixtures_dir)
        self.fixtures = {}
        self.request_log = []
        self.app = Flask(__name__)
        CORS(self.app)
        self._setup_routes()
        self._load_fixtures()

    def _setup_routes(self):
        """Register Flask routes to catch all incoming requests."""

        @self.app.route('/', defaults={'path': ''}, methods=['GET', 'POST', 'PUT', 'DELETE', 'PATCH'])
        @self.app.route('/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE', 'PATCH'])
        def catch_all(path):
            """Catch all requests and log them."""
            return self._handle_request(request)

        @self.app.route('/mock-api/health', methods=['GET'])
        def health():
            return jsonify({
                'status': 'ok',
                'timestamp': datetime.utcnow().isoformat(),
                'fixtures_loaded': len(self.fixtures),
                'requests_logged': len(self.request_log)
            })

        @self.app.route('/mock-api/request-log', methods=['GET'])
        def get_request_log():
            """Return all logged requests."""
            return jsonify({
                'total': len(self.request_log),
                'requests': self.request_log[-100:]  # Last 100
            })

        @self.app.route('/mock-api/fixtures', methods=['GET'])
        def get_fixtures():
            """Return list of loaded fixture files."""
            return jsonify({
                'total': len(self.fixtures),
                'fixtures': list(self.fixtures.keys())
            })

    def _load_fixtures(self):
        """Load all JSON fixture files from the fixtures directory."""
        if not self.fixtures_dir.exists():
            logger.warning(f"Fixtures directory not found: {self.fixtures_dir}")
            return

        for json_file in self.fixtures_dir.glob('*.json'):
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                self.fixtures[json_file.stem] = data
                logger.info(f"Loaded fixture: {json_file.stem}")
            except Exception as e:
                logger.error(f"Failed to load fixture {json_file.stem}: {e}")

    def _handle_request(self, req: Any) -> Response:
        """Handle incoming request and return mock response."""
        method = req.method
        path = req.path
        query_string = req.query_string.decode('utf-8') if req.query_string else ''
        body = req.get_data(as_text=True)
        headers = dict(req.headers)

        # Log request
        log_entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'method': method,
            'path': path,
            'query': query_string,
            'body_preview': body[:200] if body else None,
            'headers': {k: v for k, v in headers.items() if k.lower() not in ['cookie', 'authorization']}
        }
        self.request_log.append(log_entry)

        logger.info(f"{method} {path} {query_string}")

        # Try to find matching fixture
        fixture_key = self._find_matching_fixture(method, path)
        
        if fixture_key and fixture_key in self.fixtures:
            fixture = self.fixtures[fixture_key]
            status = fixture.get('status', 200)
            response_headers = fixture.get('headers', {'Content-Type': 'application/json'})
            response_body = fixture.get('body', {})

            logger.info(f"  -> Returning fixture '{fixture_key}' with status {status}")
            return Response(
                json.dumps(response_body),
                status=status,
                headers=response_headers,
                mimetype='application/json'
            )
        else:
            # No fixture found; return 404
            logger.warning(f"  -> No fixture found; returning 404")
            return Response(
                json.dumps({'error': 'Not found', 'path': path}),
                status=404,
                headers={'Content-Type': 'application/json'},
                mimetype='application/json'
            )

    def _find_matching_fixture(self, method: str, path: str) -> Optional[str]:
        """
        Find a matching fixture for the given method and path.
        
        Strategy:
        1. Normalize path (remove query string, trailing slashes).
        2. Try exact key match (e.g., "login", "api_residents_1").
        3. Try partial matches (e.g., "residents" for path="/api/residents").
        """
        # Clean path
        path_clean = path.strip('/').split('?')[0]
        
        # Convert path to fixture key (e.g., "/api/residents" -> "api_residents")
        key_parts = [p for p in path_clean.split('/') if p]
        candidate_key = '_'.join(key_parts) if key_parts else 'index'
        
        # Try exact match first
        if candidate_key in self.fixtures:
            return candidate_key
        
        # Try method + key
        method_key = f"{method.lower()}_{candidate_key}"
        if method_key in self.fixtures:
            return method_key
        
        # Try partial matches (e.g., "residents" for "/api/residents/1")
        for fixture_key in self.fixtures.keys():
            if fixture_key in candidate_key or candidate_key in fixture_key:
                return fixture_key
        
        return None

    def run(self, debug=False, port=5000, host='127.0.0.1'):
        """Start the Flask development server."""
        logger.info(f"Starting Mock API Server on {host}:{port}")
        self.app.run(debug=debug, port=port, host=host)


def create_app(fixtures_dir: str = 'api_fixtures') -> Flask:
    """Factory function to create the Flask app."""
    server = MockAPIServer(fixtures_dir=fixtures_dir)
    return server.app


def main():
    parser = argparse.ArgumentParser(description='Mock API Server for testing automation.')
    parser.add_argument('--port', type=int, default=5000, help='Port to run the server on')
    parser.add_argument('--host', default='127.0.0.1', help='Host to bind to')
    parser.add_argument('--fixtures-dir', default='api_fixtures', help='Path to fixtures directory')
    parser.add_argument('--debug', action='store_true', help='Run in debug mode')
    args = parser.parse_args()

    server = MockAPIServer(fixtures_dir=args.fixtures_dir)
    server.run(debug=args.debug, port=args.port, host=args.host)


if __name__ == '__main__':
    main()
