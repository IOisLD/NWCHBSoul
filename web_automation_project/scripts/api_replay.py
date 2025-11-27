import pandas as pd
import requests
from typing import Dict, Optional
import json
import os


class APIReplay:
    """API replay helper with configurable endpoints and auth.

    This provides a compatible `update_payment(record)` method. Configuration
    can be provided via a config dict, environment variables, or defaults.
    
    Config structure:
    {
        "endpoint": "https://api.example.com/update",
        "auth_type": "bearer",  # or "apikey", "basic"
        "auth_token": "your_token_or_key",
        "timeout": 30,
        "retry_count": 3
    }
    """

    def __init__(self, dry_run: bool = True, config: Optional[Dict] = None):
        self.dry_run = dry_run
        self.config = config or self._load_config()
        self.session = requests.Session()
        self._setup_auth()

    def _load_config(self) -> Dict:
        """Load config from env vars or use defaults."""
        return {
            'endpoint': os.getenv('API_ENDPOINT', 'https://api.example.com/update'),
            'auth_type': os.getenv('API_AUTH_TYPE', 'bearer'),  # 'bearer', 'apikey', 'basic'
            'auth_token': os.getenv('API_AUTH_TOKEN', ''),
            'timeout': int(os.getenv('API_TIMEOUT', '30')),
            'retry_count': int(os.getenv('API_RETRY_COUNT', '3'))
        }

    def _setup_auth(self):
        """Configure session authentication based on config."""
        auth_type = self.config.get('auth_type', '').lower()
        token = self.config.get('auth_token', '')
        
        if auth_type == 'bearer' and token:
            self.session.headers.update({'Authorization': f'Bearer {token}'})
        elif auth_type == 'apikey' and token:
            self.session.headers.update({'X-API-Key': token})
        elif auth_type == 'basic' and token:
            # token should be 'username:password' or base64-encoded
            self.session.headers.update({'Authorization': f'Basic {token}'})
        
        self.session.headers.update({'Content-Type': 'application/json'})

    def update_payment(self, record: Dict) -> Dict:
        """Update a payment record via API.
        
        Returns a dict with keys: 'success', 'status_code', 'response', 'error'.
        """
        if self.dry_run:
            return {
                'success': True,
                'status_code': 200,
                'response': f'[DRY-RUN] Would POST: {record}',
                'error': None
            }
        
        # Prepare the payload (customize mapping as needed)
        payload = {
            'resident_name': record.get('name', ''),
            'resident_href': record.get('resident_href', ''),
            'amount': record.get('amount'),
            'reference': record.get('reference', ''),
            'metadata': {
                'processed_timestamp': record.get('processed_timestamp'),
                'source_row': record.get('row_index')
            }
        }
        
        retry_count = self.config.get('retry_count', 3)
        for attempt in range(retry_count):
            try:
                response = self.session.post(
                    self.config['endpoint'],
                    json=payload,
                    timeout=self.config.get('timeout', 30)
                )
                return {
                    'success': response.status_code in [200, 201, 204],
                    'status_code': response.status_code,
                    'response': response.text,
                    'error': None
                }
            except requests.exceptions.RequestException as e:
                if attempt == retry_count - 1:
                    return {
                        'success': False,
                        'status_code': None,
                        'response': None,
                        'error': str(e)
                    }
                # retry silently


def replay_post_excel(filepath: str = "results/api_post_logs.xlsx", config: Optional[Dict] = None):
    """Replay POST requests from an Excel log file.
    
    Args:
        filepath: path to Excel file with columns: url, headers, post_data
        config: optional APIReplay config dict
    """
    df = pd.read_excel(filepath)
    api = APIReplay(dry_run=False, config=config)
    
    for idx, row in df.iterrows():
        url = row["url"]
        try:
            headers = json.loads(row["headers"]) if isinstance(row["headers"], str) else row["headers"]
        except Exception:
            headers = {}
        payload = row["post_data"]
        try:
            response = requests.post(url, json=payload, headers=headers, timeout=30)
            print(f"POST to {url} -> {response.status_code}")
        except Exception as e:
            print(f"POST to {url} -> ERROR: {e}")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--filepath', default='results/api_post_logs.xlsx')
    parser.add_argument('--endpoint', help='Override API endpoint')
    parser.add_argument('--token', help='Override API token')
    parser.add_argument('--auth-type', default='bearer')
    args = parser.parse_args()
    
    cfg = None
    if args.endpoint or args.token:
        cfg = {
            'endpoint': args.endpoint or 'https://api.example.com/update',
            'auth_token': args.token or '',
            'auth_type': args.auth_type
        }
    
    replay_post_excel(args.filepath, config=cfg)
