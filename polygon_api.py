# polygon_api.py
import requests
import time
import csv
import os
from datetime import datetime

class PolygonOptionsAPI:
    """Client for Polygon.io Options API with rate limiting and caching."""
    
    def __init__(self, cache_dir="options_cache"):
        self.api_key = "V4S4iIdpsDCXnfvCa28xscIrrzpjcPeE"
        self.base_url = "https://api.polygon.io/v3"
        self.rate_limit = 5  # 5 requests per minute
        self.last_request_times = []
        self.cache_dir = cache_dir
        os.makedirs(self.cache_dir, exist_ok=True)

    def _make_request(self, endpoint, params=None):
        """Make API request with rate limiting."""
        self._wait_for_rate_limit()
        url = f"{self.base_url}{endpoint}"
        params = params or {}
        params["apiKey"] = self.api_key
        
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            self.last_request_times.append(time.time())
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"API request failed: {str(e)}")
            return None

    def _wait_for_rate_limit(self):
        """Enforce 5 requests per minute limit."""
        now = time.time()
        self.last_request_times = [t for t in self.last_request_times if now - t < 60]
        if len(self.last_request_times) >= self.rate_limit:
            oldest = self.last_request_times[0]
            time.sleep(60 - (now - oldest) + 0.1)

    def get_options_chain(self, ticker, expiry_date=None, cache=True):
        """Get options chain for a ticker."""
        cache_file = os.path.join(self.cache_dir, f"{ticker}_{expiry_date or 'all'}.csv")
        
        if cache and os.path.exists(cache_file):
            return self._load_from_cache(cache_file)
        
        params = {"underlying_ticker": ticker}
        if expiry_date:
            params["expiration_date"] = expiry_date
        
        data = self._make_request("/reference/options/contracts", params)
        if not data or "results" not in data:
            return []
            
        results = data["results"]
        parsed_results = []
        
        for contract in results:
            parsed_results.append({
                "ticker": contract.get("ticker"),
                "underlying": ticker,
                "expiry": contract.get("expiration_date"),
                "strike": contract.get("strike_price"),
                "iv": contract.get("implied_volatility", 0),
                "option_type": contract.get("contract_type"),
                "last_updated": datetime.now().isoformat()
            })
        
        if cache and parsed_results:
            self._save_to_cache(cache_file, parsed_results)
        return parsed_results

    def _save_to_cache(self, filename, data):
        """Save data to CSV cache."""
        if not data:
            return
        try:
            with open(filename, mode="w", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=data[0].keys())
                writer.writeheader()
                writer.writerows(data)
        except IOError as e:
            print(f"Failed to save cache: {e}")

    def _load_from_cache(self, filename):
        """Load data from CSV cache."""
        try:
            with open(filename, mode="r") as f:
                return list(csv.DictReader(f))
        except IOError as e:
            print(f"Failed to load cache: {e}")
            return []

if __name__ == "__main__":
    # Test the class directly
    api = PolygonOptionsAPI()
    print("Testing PolygonOptionsAPI...")
    test_data = api.get_options_chain("SPY")
    print(f"Retrieved {len(test_data)} contracts")