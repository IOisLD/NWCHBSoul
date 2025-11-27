# API Configuration Setup

## Overview
This guide helps you set up API credentials and configuration for the web automation project.

## Environment Variables (Recommended for Production)

Set these environment variables before running the automation:

### PowerShell
```powershell
$env:API_ENDPOINT = "https://jiffy.secondavenue.com/api/payments/update"
$env:API_AUTH_TYPE = "bearer"  # Options: bearer, apikey, basic
$env:API_AUTH_TOKEN = "your_actual_token_here"
$env:API_TIMEOUT = "30"
$env:API_RETRY_COUNT = "3"

# Run the automation
python -m scripts.main
```

### Command Prompt (CMD)
```cmd
set API_ENDPOINT=https://jiffy.secondavenue.com/api/payments/update
set API_AUTH_TYPE=bearer
set API_AUTH_TOKEN=your_actual_token_here
set API_TIMEOUT=30
set API_RETRY_COUNT=3

python -m scripts.main
```

### Bash / Linux / Mac
```bash
export API_ENDPOINT="https://jiffy.secondavenue.com/api/payments/update"
export API_AUTH_TYPE="bearer"
export API_AUTH_TOKEN="your_actual_token_here"
export API_TIMEOUT="30"
export API_RETRY_COUNT="3"

python -m scripts.main
```

## Configuration File (Alternative)

### Step 1: Copy the Template
```powershell
Copy-Item config/api_config.template.json config/api_config.json
```

### Step 2: Edit `config/api_config.json`
Replace placeholder values with your actual API details:

```json
{
  "api": {
    "endpoint": "https://jiffy.secondavenue.com/api/payments/update",
    "auth_type": "bearer",
    "auth_token": "YOUR_ACTUAL_TOKEN_HERE",
    "timeout": 30,
    "retry_count": 3
  },
  "selectors": {
    "resident_table_row": "tr",
    "resident_name_cell": 0,
    "resident_href_attr": "data-href"
  }
}
```

### Step 3: Load Config in Python
```python
import json
from scripts.api_replay import APIReplay

# Load config from file
with open('config/api_config.json') as f:
    config = json.load(f)

# Pass to APIReplay
api = APIReplay(dry_run=False, config=config['api'])
result = api.update_payment(record)
```

## Authentication Types

### Bearer Token (Default)
Use for modern APIs with JWT or OAuth tokens.
```json
{
  "auth_type": "bearer",
  "auth_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

### API Key
Use for APIs that accept a simple API key header.
```json
{
  "auth_type": "apikey",
  "auth_token": "sk_live_abc123def456..."
}
```

### Basic Authentication
Use for simple username:password authentication.
```json
{
  "auth_type": "basic",
  "auth_token": "dXNlcm5hbWU6cGFzc3dvcmQ="
}
```
Note: The token should be base64-encoded `username:password`.

## Testing Your Configuration

### 1. Test API Connection (Dry-Run)
```powershell
python -m scripts.main --dry-run
```
This will log the intended API calls without actually making them.

### 2. Test with a Single Row
```python
from scripts.api_replay import APIReplay
import os

api = APIReplay(dry_run=False)

test_record = {
    'name': 'John Doe',
    'resident_href': '/residents/123',
    'amount': 100.00,
    'reference': 'Payment for Oct 2025'
}

result = api.update_payment(test_record)
print(f"Success: {result['success']}")
print(f"Status: {result['status_code']}")
print(f"Error: {result['error']}")
```

### 3. Test API Replay from Log
```powershell
python -m scripts.api_replay --filepath results/api_post_logs.xlsx --endpoint "https://api.example.com/update" --token "your_token"
```

## Securing Credentials

⚠️ **IMPORTANT: Never commit credentials to git!**

### Best Practices:
1. **Use environment variables** in production (recommended).
2. **Use `.env` files** locally with `python-dotenv`:
   ```python
   from dotenv import load_dotenv
   load_dotenv()  # Loads from .env file
   ```

3. **Add `config/api_config.json` to `.gitignore`**:
   ```
   # In .gitignore
   config/api_config.json
   config/*.local.json
   .env
   ```

4. **Use a secrets manager** for enterprise deployments:
   - Azure Key Vault
   - AWS Secrets Manager
   - HashiCorp Vault

## Troubleshooting

### "401 Unauthorized"
- Check that `auth_token` is correct and not expired.
- Verify `auth_type` matches your API's requirement.

### "Connection refused"
- Verify `endpoint` URL is correct and accessible.
- Check firewall and proxy settings.

### "Timeout"
- Increase `timeout` value (in seconds).
- Check your network connection.

### "404 Not Found"
- Verify the `endpoint` URL path is correct.
- Check if the API version has changed.

## Reference: APIReplay Class

```python
class APIReplay:
    def __init__(self, dry_run: bool = True, config: Optional[Dict] = None):
        # config options:
        # - endpoint: str (API URL)
        # - auth_type: str (bearer, apikey, basic)
        # - auth_token: str (token value)
        # - timeout: int (seconds, default: 30)
        # - retry_count: int (default: 3)
        pass
    
    def update_payment(self, record: Dict) -> Dict:
        # Returns: {'success': bool, 'status_code': int, 'response': str, 'error': str}
        pass
```

## Next Steps

1. **Obtain API credentials** from your jiffy.secondavenue.com administrator.
2. **Set environment variables** or create `config/api_config.json`.
3. **Run a dry-run test**: `python -m scripts.main --dry-run`.
4. **Run a single live test** with a test record.
5. **Schedule the automation** once confirmed working (see Windows Task Scheduler setup).
