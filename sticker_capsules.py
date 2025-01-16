import json
import random
from typing import Dict, Union, Tuple
from dataclasses import dataclass
from config import STICKER_CAPSULE_FILE_MAPPING, Rarity, STICKER_DROP_CHANCES

@dataclass
class StickerCapsule:
    name: str
    contents: Dict[Rarity, list]
    file_name: str

def load_sticker_capsule(capsule_type: str) -> Union[StickerCapsule, Dict, None]:
    """
    Load sticker capsule data from JSON file. Returns either a StickerCapsule object for opening capsules,
    or a dictionary with basic capsule info for the shop display.
    """
    try:
        # If we just need basic capsule info for the shop
        if capsule_type == 'all':
            capsules = {}
            for capsule_key, file_name in STICKER_CAPSULE_FILE_MAPPING.items():
                try:
                    with open(f'stickers/{file_name}.json', 'r') as f:
                        capsule_data = json.load(f)
                        capsules[capsule_key] = {
                            'name': capsule_data['name'],
                            'image': capsule_data['image'],
                            'price': capsule_data['price'],
                            'type': capsule_key
                        }
                except Exception as e:
                    print(f"Error loading {file_name}: {e}")
            return capsules
            
        # For opening specific capsules
        file_name = STICKER_CAPSULE_FILE_MAPPING.get(capsule_type)
        if not file_name:
            print(f"Invalid capsule type: {capsule_type}")
            return None
            
        with open(f'stickers/{file_name}.json', 'r') as f:
            data = json.load(f)
            
        # For opening capsules, create a StickerCapsule object with full sticker data
        contents = {
            Rarity.PINK: [],
            Rarity.PURPLE: [],
            Rarity.BLUE: []
        }
        
        grade_map = {
            'pink': Rarity.PINK,
            'purple': Rarity.PURPLE,
            'blue': Rarity.BLUE
        }
        
        for grade, items in data['stickers'].items():
            rarity = grade_map[grade]
            for item in items:
                contents[rarity].append((item['team'], item['tournament']))
        
        return StickerCapsule(data['name'], contents, file_name)
        
    except Exception as e:
        print(f"Error loading capsule {capsule_type}: {e}")
        return None

def get_sticker_capsule_prices(capsule_type: str = None) -> Union[float, Dict[str, float]]:
    """Get price for a single capsule or all capsule prices if no capsule_type provided"""
    if capsule_type is not None:
        try:
            file_name = STICKER_CAPSULE_FILE_MAPPING.get(capsule_type)
            if not file_name:
                print(f"Unknown capsule type: {capsule_type}")
                return 0
                
            with open(f'stickers/{file_name}.json', 'r') as f:
                data = json.load(f)
                return data.get('price', 0)
        except Exception:
            return 0
    else:
        return {capsule_type: get_sticker_capsule_prices(capsule_type) 
                for capsule_type in STICKER_CAPSULE_FILE_MAPPING.keys()} 

def open_sticker_capsule(capsule: StickerCapsule) -> Tuple[str, str, Rarity]:
    """
    Opens a sticker capsule and returns a tuple of (team, tournament, rarity)
    Uses the defined drop chances from config.py
    """
    # Generate a random number between 0 and 100
    roll = random.uniform(0, 100)
    
    # Determine rarity based on roll
    if roll < STICKER_DROP_CHANCES['pink']:
        rarity = Rarity.PINK
    elif roll < STICKER_DROP_CHANCES['pink'] + STICKER_DROP_CHANCES['purple']:
        rarity = Rarity.PURPLE
    else:
        rarity = Rarity.BLUE
        
    # If there are no stickers of the rolled rarity, fall back to blue
    if not capsule.contents[rarity]:
        rarity = Rarity.BLUE
        
    # Select a random sticker from the chosen rarity
    if capsule.contents[rarity]:
        team, tournament = random.choice(capsule.contents[rarity])
        return team, tournament, rarity
    
    # If somehow we have no stickers at all (shouldn't happen), return None
    return None, None, None 