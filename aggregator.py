import os
import sys
import json
import time
import hashlib
import requests
import tldextract
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import urlparse

# --- Configuration ---
SOURCES_FILE = "sources.txt"
OUTPUT_FILE = "hosts"
CACHE_DIR = "cache"
STATE_FILE = os.path.join(CACHE_DIR, "state.json")
HEADERS = {"User-Agent": "Mozilla/5.0 (Hosts Aggregator Script)"}
TIMEOUT = 30
MAX_RETRIES = 3
THREADS = 5  # Number of concurrent downloads


class HostsAggregator:
    def __init__(self):
        self.domains = set()
        self.state = self.load_state()
        self.extractor = tldextract.TLDExtract()

        # Ensure cache directory exists
        if not os.path.exists(CACHE_DIR):
            os.makedirs(CACHE_DIR)

    def load_state(self):
        """Loads the progress state to allow resuming."""
        if os.path.exists(STATE_FILE):
            try:
                with open(STATE_FILE, "r") as f:
                    return json.load(f)
            except:
                return {"completed": [], "failed": []}
        return {"completed": [], "failed": []}

    def save_state(self):
        """Saves progress immediately after each successful source."""
        self.state["last_run"] = time.strftime("%Y-%m-%d %H:%M:%S")
        with open(STATE_FILE, "w") as f:
            json.dump(self.state, f, indent=2)

    def check_last_run(self):
        """Check if the script was run within the last day."""
        last_run = self.state.get("last_run")
        if not last_run:
            return True

        try:
            last_run_time = time.strptime(last_run, "%Y-%m-%d %H:%M:%S")
            last_run_epoch = time.mktime(last_run_time)
            current_epoch = time.time()
            hours_diff = (current_epoch - last_run_epoch) / 3600

            if hours_diff < 24:
                print(f"\nLast run: {last_run}")
                response = (
                    input("Script was run less than 24 hours ago. Run again? (y/n): ")
                    .strip()
                    .lower()
                )
                if response != "y":
                    print("Exiting.")
                    return False
            return True
        except ValueError:
            return True

    def get_url_hash(self, url):
        """Creates a safe filename based on the URL."""
        return hashlib.md5(url.encode("utf-8")).hexdigest()

    def download_source(self, url):
        """Downloads content with retry logic and caching."""
        url_hash = self.get_url_hash(url)
        cache_path = os.path.join(CACHE_DIR, f"{url_hash}.txt")

        # Check if we already have this downloaded in cache from a previous run
        if os.path.exists(cache_path):
            print(f"[CACHE] {url}")
            with open(cache_path, "r", encoding="utf-8", errors="ignore") as f:
                return f.read()

        # Download from network
        for attempt in range(MAX_RETRIES):
            try:
                print(f"[DOWNLOAD] {url} (Attempt {attempt + 1})")
                response = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
                response.raise_for_status()

                # Save to cache immediately upon success
                with open(cache_path, "w", encoding="utf-8") as f:
                    f.write(response.text)

                return response.text

            except Exception as e:
                print(f"[ERROR] {url}: {e}")
                if attempt < MAX_RETRIES - 1:
                    time.sleep(2**attempt)  # Exponential backoff
                else:
                    raise Exception(
                        f"Failed to download {url} after {MAX_RETRIES} attempts"
                    )

    def parse_line(self, line):
        """Extracts a clean domain from various formats."""
        line = line.strip().lower()

        # Ignore empty lines and comments
        if not line or line.startswith("#"):
            return None

        # Handle hosts file format: "0.0.0.0 example.com" or "127.0.0.1 example.com"
        parts = line.split()
        if len(parts) >= 2 and "." in parts[0]:
            # Likely an IP address at the start
            candidate = parts[1]
        else:
            # Likely a raw domain or URL
            candidate = parts[0]

        # Remove http/https/www and extract actual domain
        extracted = self.extractor(candidate)

        if extracted.domain and extracted.suffix:
            # Reconstruct: subdomain.domain.tld
            domain = (
                f"{extracted.subdomain}.{extracted.domain}.{extracted.suffix}".lstrip(
                    "."
                )
            )
            return domain
        return None

    def process_source(self, url):
        """Downloads and parses a single source URL."""
        try:
            content = self.download_source(url)
            if not content:
                return False
            local_count = 0

            for line in content.splitlines():
                domain = self.parse_line(line)
                if domain:
                    self.domains.add(domain)
                    local_count += 1

            print(f"[SUCCESS] {url} -> Found {local_count} domains")
            return True

        except Exception as e:
            print(f"[FATAL] {url} -> {e}")
            return False

    def run(self):
        if not self.check_last_run():
            return

        if not os.path.exists(SOURCES_FILE):
            print(
                f"Error: {SOURCES_FILE} not found. Please create it with your list URLs."
            )
            sys.exit(1)

        with open(SOURCES_FILE, "r") as f:
            urls = [
                line.strip() for line in f if line.strip() and not line.startswith("#")
            ]

        print(f"Loaded {len(urls)} source URLs.")

        # Filter out already completed URLs (Resume Logic)
        pending_urls = [u for u in urls if u not in self.state["completed"]]
        print(
            f"Resuming: {len(pending_urls)} sources pending, {len(self.state['completed'])} skipped."
        )

        if not pending_urls:
            print("All sources already processed. Generating final file...")
        else:
            # Use ThreadPoolExecutor for parallel downloads
            with ThreadPoolExecutor(max_workers=THREADS) as executor:
                future_to_url = {
                    executor.submit(self.process_source, url): url
                    for url in pending_urls
                }

                for future in as_completed(future_to_url):
                    url = future_to_url[future]
                    try:
                        success = future.result()
                        if success:
                            self.state["completed"].append(url)
                            # Remove from failed if it was there previously
                            if url in self.state["failed"]:
                                self.state["failed"].remove(url)
                        else:
                            self.state["failed"].append(url)
                    except Exception as exc:
                        print(f"{url} generated an exception: {exc}")
                        self.state["failed"].append(url)
                    finally:
                        # Save state after every completion to ensure resume capability
                        self.save_state()

        # Final Generation
        print(f"\nProcessing complete. Total unique domains: {len(self.domains)}")
        print("Sorting and writing to hosts file...")

        sorted_domains = sorted(self.domains)

        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            f.write("# Aggregated Hosts File\n")
            f.write(f"# Generated by Python Aggregator\n")
            f.write(f"# Total Entries: {len(sorted_domains)}\n")
            f.write(f"# Date: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("127.0.0.1 localhost\n")
            f.write("127.0.0.1 localhost.localdomain\n")

            for domain in sorted_domains:
                f.write(f"0.0.0.0 {domain}\n")


if __name__ == "__main__":
    aggregator = HostsAggregator()
    aggregator.run()
