#!/usr/bin/env python3
"""
Endpoint Discovery Tool
Author: Security Engineer
Purpose: Discover accessible endpoints (routes, URLs, API paths) of a target application.

Usage:
    python endpoint_discovery.py -u https://target.com -w wordlist.txt

Requirements:
    pip install requests beautifulsoup4 argparse
"""

import requests
import argparse
import logging
from bs4 import BeautifulSoup
from urllib.parse import urljoin

# Configure logging
logging.basicConfig(
    filename="endpoint_discovery.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

discovered_endpoints = {}

def log_endpoint(url, method, status):
    """Log and store endpoint details."""
    discovered_endpoints[url] = {"method": method, "status": status}
    logging.info(f"{method} | {url} | {status}")

def crawl_site(base_url, depth=2):
    """Recursively crawl site and extract href/src/action attributes."""
    visited = set()
    to_visit = [base_url]

    for _ in range(depth):
        new_links = []
        for url in to_visit:
            if url in visited:
                continue
            visited.add(url)
            try:
                r = requests.get(url, timeout=5)
                log_endpoint(url, "crawl", r.status_code)
                soup = BeautifulSoup(r.text, "html.parser")
                for tag in soup.find_all(["a", "form", "script", "link"]):
                    attr = tag.get("href") or tag.get("src") or tag.get("action")
                    if attr:
                        full_url = urljoin(base_url, attr)
                        if base_url in full_url:
                            new_links.append(full_url)
            except Exception as e:
                logging.error(f"Error crawling {url}: {e}")
        to_visit = new_links

def extract_js_endpoints(js_url, base_url):
    """Extract endpoints from JavaScript files (basic regex)."""
    try:
        r = requests.get(js_url, timeout=5)
        log_endpoint(js_url, "js-parse", r.status_code)
        endpoints = []
        for line in r.text.splitlines():
            if base_url in line or line.strip().startswith("/"):
                endpoints.append(line.strip())
        return endpoints
    except Exception as e:
        logging.error(f"Error parsing JS {js_url}: {e}")
        return []

def bruteforce_endpoints(base_url, wordlist):
    """Brute-force directories/files using a wordlist."""
    with open(wordlist, "r") as f:
        for word in f:
            word = word.strip()
            test_url = urljoin(base_url, word)
            try:
                r = requests.get(test_url, timeout=5)
                if r.status_code in [200, 302, 403]:
                    log_endpoint(test_url, "bruteforce", r.status_code)
            except Exception as e:
                logging.error(f"Error brute-forcing {test_url}: {e}")

def check_api_docs(base_url):
    """Check for Swagger/OpenAPI and GraphQL endpoints."""
    candidates = ["/swagger.json", "/api-docs", "/graphql"]
    for path in candidates:
        test_url = urljoin(base_url, path)
        try:
            r = requests.get(test_url, timeout=5)
            log_endpoint(test_url, "api-check", r.status_code)
            if "graphql" in path and r.status_code == 200:
                logging.info("GraphQL introspection may be possible.")
        except Exception as e:
            logging.error(f"Error checking {test_url}: {e}")

def export_report(filename="endpoints_report.md"):
    """Export findings to Markdown file."""
    with open(filename, "w") as f:
        f.write("# Endpoint Discovery Report\n\n")
        for url, data in discovered_endpoints.items():
            f.write(f"- **{url}**\n")
            f.write(f"  - Method: {data['method']}\n")
            f.write(f"  - Status: {data['status']}\n\n")
        f.write(f"## Summary\n")
        f.write(f"- Total endpoints: {len(discovered_endpoints)}\n")
        f.write(f"- Unique endpoints: {len(set(discovered_endpoints.keys()))}\n")

def export_plain(filename="endpoints_plain.txt"):
    """Export findings to plain text file."""
    with open(filename, "w") as f:
        for url in discovered_endpoints.keys():
            f.write(f"{url}\n")
        f.write("\n## Summary\n")
        f.write(f"- Total endpoints: {len(discovered_endpoints)}\n")
        f.write(f"- Unique endpoints: {len(set(discovered_endpoints.keys()))}\n")

def main():
    parser = argparse.ArgumentParser(description="Endpoint Discovery Tool")
    parser.add_argument("-u", "--url", required=True, help="Target base URL")
    parser.add_argument("-w", "--wordlist", help="Wordlist for brute-force")
    args = parser.parse_args()

    base_url = args.url

    crawl_site(base_url)
    check_api_docs(base_url)
    if args.wordlist:
        bruteforce_endpoints(base_url, args.wordlist)

    export_report()       # Markdown report
    export_plain()        # Plain text report

if __name__ == "__main__":
    main()
