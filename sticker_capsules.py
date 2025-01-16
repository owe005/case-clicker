import json
import random
from typing import Dict, Union, Tuple
from dataclasses import dataclass
from config import STICKER_CAPSULE_FILE_MAPPING, Rarity, STICKER_DROP_CHANCES
import traceback

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
            
        # Calculate adjusted probabilities
        available_rarities = {}
        for rarity_name in data['stickers'].keys():
            if rarity_name in STICKER_DROP_CHANCES:
                available_rarities[rarity_name] = STICKER_DROP_CHANCES[rarity_name]
        
        if available_rarities:
            total_chance = sum(available_rarities.values())
            adjusted_chances = {
                rarity: (chance / total_chance * 100)
                for rarity, chance in available_rarities.items()
            }
        else:
            adjusted_chances = {}
            
        # Return the full capsule data for display
        return {
            'name': data['name'],
            'image': data['image'],
            'price': data['price'],
            'type': capsule_type,
            'stickers': data['stickers'],
            'probabilities': adjusted_chances
        }
        
    except Exception as e:
        print(f"Error loading capsule {capsule_type}: {e}")
        traceback.print_exc()  # Add traceback for better debugging
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

def open_sticker_capsule(capsule_type: str) -> Tuple[str, float, str, str]:
    """
    Opens a sticker capsule and returns a tuple of (name, price, rarity, image)
    Uses the defined drop chances from config.py but adjusts them if rarities are missing
    """
    try:
        print(f"\nDEBUG: Opening capsule type: {capsule_type}")
        file_name = STICKER_CAPSULE_FILE_MAPPING.get(capsule_type)
        if not file_name:
            print("DEBUG: Invalid capsule type")
            return None, 0, None, None
            
        print(f"DEBUG: Loading file: stickers/{file_name}.json")
        with open(f'stickers/{file_name}.json', 'r') as f:
            data = json.load(f)

        print(f"DEBUG: STICKER_DROP_CHANCES = {STICKER_DROP_CHANCES}")
        print(f"DEBUG: Available rarities in capsule = {list(data['stickers'].keys())}")

        # Get available rarities and their probabilities
        available_rarities = {}
        for rarity_name, stickers in data['stickers'].items():
            print(f"DEBUG: Processing rarity: {rarity_name}, has stickers: {bool(stickers)}")
            print(f"DEBUG: Type of STICKER_DROP_CHANCES[{rarity_name}] = {type(STICKER_DROP_CHANCES.get(rarity_name))}")
            if rarity_name in STICKER_DROP_CHANCES and stickers:
                available_rarities[rarity_name] = float(STICKER_DROP_CHANCES[rarity_name])
                print(f"DEBUG: Added {rarity_name} with chance {available_rarities[rarity_name]}")

        print(f"DEBUG: Final available_rarities = {available_rarities}")

        if not available_rarities:
            print("DEBUG: No available rarities found")
            return None, 0, None, None

        # Calculate total probability and normalize
        total_prob = sum(available_rarities.values())
        print(f"DEBUG: Total probability = {total_prob}")
        
        normalized_chances = {k: v/total_prob for k, v in available_rarities.items()}
        print(f"DEBUG: Normalized chances = {normalized_chances}")
        
        # Roll for rarity
        roll = random.random()
        print(f"DEBUG: Random roll = {roll}")
        
        cumulative = 0.0
        chosen_rarity = None
        
        print("DEBUG: Starting cumulative roll:")
        for rarity, chance in normalized_chances.items():
            cumulative += chance
            print(f"DEBUG: Rarity {rarity}, Chance {chance}, Cumulative {cumulative}")
            if roll <= cumulative:
                chosen_rarity = rarity
                print(f"DEBUG: Selected rarity {chosen_rarity}")
                break
        
        if not chosen_rarity:
            chosen_rarity = list(available_rarities.keys())[-1]
            print(f"DEBUG: Using fallback rarity {chosen_rarity}")

        # Select a random sticker from the chosen rarity
        stickers = data['stickers'][chosen_rarity]
        print(f"DEBUG: Found {len(stickers)} stickers for rarity {chosen_rarity}")
        
        if not stickers:
            print(f"DEBUG: No stickers found for rarity {chosen_rarity}")
            return None, 0, None, None
            
        sticker = random.choice(stickers)
        print(f"DEBUG: Selected sticker: {sticker['name']}")
        
        # Return the sticker data with rarity as a string
        return (
            sticker['name'],
            float(sticker['price']),
            chosen_rarity.upper(),  # Ensure rarity is uppercase string
            sticker['image']
        )
            
    except Exception as e:
        print(f"Error opening capsule: {e}")
        traceback.print_exc()
        return None, 0, None, None 