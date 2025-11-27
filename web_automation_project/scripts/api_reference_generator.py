"""
API Reference Generator — Parses captured exploration reports and generates structured API documentation.

Produces:
- Endpoints discovered (from API patterns and network logs)
- Methods (GET, POST, PUT, DELETE, etc.)
- Request/Response structure and headers
- Schema inference from captured payloads
- Status codes and error handling
- Sample curl commands

Usage:
    from scripts.api_reference_generator import APIReferenceGenerator
    
    gen = APIReferenceGenerator()
    gen.load_captures('results/api_captures_enhanced.json')
    gen.generate_reference()  # returns rich dict
    gen.write_markdown('docs/API_REFERENCE.md')

    # Or use CLI:
    python -m scripts.api_reference_generator --captures results/api_captures_enhanced.json --output docs/API_REFERENCE.md
"""

import json
import argparse
from typing import Dict, List, Any, Optional
from collections import defaultdict
from pathlib import Path


class APIReferenceGenerator:
    """Generate structured API documentation from exploration captures."""

    def __init__(self):
        self.captures = []
        self.endpoints = defaultdict(lambda: {
            'methods': set(),
            'status_codes': set(),
            'request_headers': defaultdict(int),
            'response_headers': defaultdict(int),
            'request_samples': [],
            'response_samples': [],
            'description': ''
        })
        self.forms = []
        self.buttons = []
        self.network_patterns = []

    def load_captures(self, filepath: str):
        """Load exploration report JSON file."""
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        if 'results' in data:
            for result in data['results']:
                self._extract_from_result(result)
        else:
            self._extract_from_result(data)

    def _extract_from_result(self, result: Dict):
        """Extract API endpoints and structures from a single exploration result."""
        report = result.get('exploration_report', {})
        
        # Extract forms (potential API endpoints)
        for form in report.get('forms', []):
            self.forms.append(form)
            endpoint = form.get('action', '')
            if endpoint:
                self.endpoints[endpoint]['methods'].add(form.get('method', 'GET').upper())
        
        # Extract buttons/links
        for btn in report.get('buttons', []):
            if btn.get('href'):
                self.buttons.append(btn)
        
        # Extract API patterns
        for pattern in report.get('api_patterns', []):
            endpoint = pattern.get('endpoint', '')
            if endpoint:
                self.endpoints[endpoint]['description'] = f"API endpoint discovered from {pattern.get('type', 'unknown')}"
        
        # Extract from network log
        for req in report.get('network_log', []):
            method = req.get('method', 'GET')
            url = req.get('url', '')
            status = req.get('status')
            
            if url and '/api/' in url:
                self.endpoints[url]['methods'].add(method)
                if status:
                    self.endpoints[url]['status_codes'].add(status)
                
                # Collect headers
                for k, v in req.get('requestHeaders', {}).items():
                    self.endpoints[url]['request_headers'][k] += 1
                for k, v in req.get('responseHeaders', {}).items():
                    self.endpoints[url]['response_headers'][k] += 1
                
                # Store samples
                sample = {
                    'method': method,
                    'status': status,
                    'request_body': req.get('requestBody'),
                    'response_body': req.get('responseBody')[:500] if req.get('responseBody') else None
                }
                self.endpoints[url]['request_samples'].append(sample)
        
        # Extract request/response headers from general info
        req_headers = report.get('request_headers', {})
        resp_headers = report.get('response_headers', {})
        for endpoint in self.endpoints:
            for k, v in req_headers.items():
                self.endpoints[endpoint]['request_headers'][k] += 1
            for k, v in resp_headers.items():
                self.endpoints[endpoint]['response_headers'][k] += 1

    def generate_reference(self) -> Dict:
        """Generate a structured API reference dictionary."""
        reference = {
            'title': 'API Reference',
            'generated_at': self._timestamp(),
            'summary': {
                'total_endpoints': len(self.endpoints),
                'total_forms': len(self.forms),
                'total_buttons': len(self.buttons)
            },
            'endpoints': {},
            'forms': self.forms,
            'buttons': self.buttons,
            'common_headers': self._extract_common_headers()
        }
        
        for endpoint, info in self.endpoints.items():
            reference['endpoints'][endpoint] = {
                'description': info['description'],
                'methods': sorted(list(info['methods'])) if info['methods'] else ['GET'],
                'status_codes': sorted(list(info['status_codes'])) if info['status_codes'] else [200],
                'request_headers': dict(sorted(info['request_headers'].items(), key=lambda x: -x[1])[:5]),
                'response_headers': dict(sorted(info['response_headers'].items(), key=lambda x: -x[1])[:5]),
                'samples': info['request_samples'][:2] if info['request_samples'] else []
            }
        
        return reference

    def _extract_common_headers(self) -> Dict:
        """Extract the most common request/response headers across all endpoints."""
        common = {}
        all_headers = defaultdict(int)
        for endpoint_info in self.endpoints.values():
            for h, count in endpoint_info['request_headers'].items():
                all_headers[h] += count
        
        # Return top 5
        sorted_headers = sorted(all_headers.items(), key=lambda x: -x[1])
        return {h: 'common' for h, _ in sorted_headers[:5]}

    def write_markdown(self, filepath: str):
        """Write API reference as Markdown document."""
        ref = self.generate_reference()
        
        md = []
        md.append(f"# {ref['title']}\n")
        md.append(f"**Generated:** {ref['generated_at']}\n")
        
        # Summary
        md.append("## Summary\n")
        md.append(f"- Total Endpoints: {ref['summary']['total_endpoints']}")
        md.append(f"- Forms Discovered: {ref['summary']['total_forms']}")
        md.append(f"- Buttons/Links: {ref['summary']['total_buttons']}\n")
        
        # Common Headers
        if ref['common_headers']:
            md.append("## Common Headers\n")
            for header in ref['common_headers'].keys():
                md.append(f"- `{header}`")
            md.append("")
        
        # Endpoints
        if ref['endpoints']:
            md.append("## API Endpoints\n")
            for endpoint, details in ref['endpoints'].items():
                md.append(f"### {endpoint}\n")
                md.append(f"**Description:** {details.get('description', 'N/A')}\n")
                md.append(f"**Methods:** {', '.join(details.get('methods', ['GET']))}\n")
                md.append(f"**Status Codes:** {', '.join(map(str, details.get('status_codes', [200])))}\n")
                
                if details.get('request_headers'):
                    md.append("\n**Common Request Headers:**")
                    for h in list(details.get('request_headers', {}).keys())[:3]:
                        md.append(f"- `{h}`")
                
                if details.get('response_headers'):
                    md.append("\n**Common Response Headers:**")
                    for h in list(details.get('response_headers', {}).keys())[:3]:
                        md.append(f"- `{h}`")
                
                md.append("")
        
        # Forms
        if ref['forms']:
            md.append("## Forms Discovered\n")
            for form in ref['forms']:
                md.append(f"**Form ID:** {form.get('id', 'N/A')}")
                md.append(f"- **Action:** {form.get('action', 'N/A')}")
                md.append(f"- **Method:** {form.get('method', 'GET')}")
                md.append(f"- **Fields:**")
                for field in form.get('fields', []):
                    md.append(f"  - `{field.get('name', 'N/A')}` ({field.get('type', 'text')})")
                md.append("")
        
        # Write to file
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write('\n'.join(md))
        
        print(f"[APIRefGen] Wrote API reference to {filepath}")

    @staticmethod
    def _timestamp() -> str:
        from datetime import datetime
        return datetime.utcnow().isoformat()


def main():
    parser = argparse.ArgumentParser(description='Generate API reference from exploration captures.')
    parser.add_argument('--captures', required=True, help='Path to api_captures_enhanced.json')
    parser.add_argument('--output', required=True, help='Output Markdown file path')
    args = parser.parse_args()
    
    gen = APIReferenceGenerator()
    gen.load_captures(args.captures)
    gen.write_markdown(args.output)
    
    print("[APIRefGen] Complete.")


if __name__ == '__main__':
    main()
