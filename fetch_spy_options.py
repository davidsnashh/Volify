import csv
from src.polygon_api import PolygonOptionsAPI

def fetch_spy_options():
    """Fetch and display SPY options chain."""
    try:
        api = PolygonOptionsAPI()
        
        print("Fetching SPY options chain...")
        spy_options = api.get_options_chain("SPY")
        
        if not spy_options:
            print("No options data received")
            return
        
        print("\nFirst 5 SPY options contracts:")
        for i, contract in enumerate(spy_options[:5]):
            print(f"{i+1}. Ticker: {contract['ticker']}")
            print(f"   Expiry: {contract['expiry']}")
            print(f"   Strike: {contract['strike']}")
            print(f"   IV: {contract['iv']}")
            print(f"   Type: {contract['option_type']}\n")
        
        output_file = "SPY_options_chain.csv"
        with open(output_file, mode="w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=spy_options[0].keys())
            writer.writeheader()
            writer.writerows(spy_options)
        print(f"Full options chain saved to {output_file}")
        
    except Exception as e:
        print(f"Error occurred: {str(e)}")

if __name__ == "__main__":
    fetch_spy_options()