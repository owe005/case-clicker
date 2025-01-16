import json
from typing import Union
from config import STICKER_CAPSULE_FILE_MAPPING

def load_sticker_price(team: str, tournament: str, capsule_type: str) -> float:
    """Load price for a sticker based on capsule data"""
    try:
        # Get capsule file name
        file_name = STICKER_CAPSULE_FILE_MAPPING.get(capsule_type)
        if not file_name:
            return 0
            
        # Load capsule data
        with open(f'stickers/{file_name}.json', 'r') as f:
            capsule_data = json.load(f)
            
        # Find the sticker in capsule data
        for grade, stickers in capsule_data['stickers'].items():
            for sticker in stickers:
                if sticker['team'] == team and sticker['tournament'] == tournament:
                    return float(sticker['price'])
                    
        return 0
    except Exception as e:
        print(f"Error loading sticker price: {e}")
        return 0 