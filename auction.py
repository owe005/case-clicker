import json
from pathlib import Path
from config import AUCTION_FILE


def save_auction_data(auction_data):
    """Save auction data to JSON file"""
    try:
        with open(AUCTION_FILE, 'w') as f:
            json.dump(auction_data, f, indent=2, default=str)
    except Exception as e:
        print(f"Error saving auction data: {e}")

def load_auction_data():
    """Load auction data from JSON file"""
    try:
        if not Path(AUCTION_FILE).exists():
            return None
        with open(AUCTION_FILE, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading auction data: {e}")
        return None