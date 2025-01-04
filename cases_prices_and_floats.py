# Add this helper function near the top with other helpers
import json
import random
from typing import Dict, Union

from config import CASE_FILE_MAPPING, Rarity
from models import Case

def generate_float_for_wear(wear: str) -> float:
    """Generate a random float value based on wear condition"""
    wear_ranges = {
        'FN': (0.00, 0.07),
        'MW': (0.07, 0.15),
        'FT': (0.15, 0.38),
        'WW': (0.38, 0.45),
        'BS': (0.45, 1.00)
    }
    
    if wear not in wear_ranges:
        return 0.0
        
    min_float, max_float = wear_ranges[wear]
    return round(random.uniform(min_float, max_float), 8)


# Add this helper function near the top with other helpers
def adjust_price_by_float(price: float, wear: str, float_value: float) -> float:
    """Adjust item price based on float value"""

    if wear == 'FN':
        if float_value < 0.001:
            return price * 1.5
        elif float_value < 0.006:
            return price * 1.2
        elif float_value < 0.015:
            return price * 1.1
        else:
            return price
            
    elif wear == 'BS':
        if float_value > 0.97:
            return price * 0.5
        elif float_value > 0.93:
            return price * 0.7
        elif float_value > 0.90:
            return price * 0.85
        else:
            return price
    
    return price

def load_skin_price(skin_name: str, case_type: str, wear: str, float_value: float, is_stattrak: bool = False) -> float:
    """Load and adjust price for a skin based on case data and float value"""
    try:
        # Get case file name
        file_name = CASE_FILE_MAPPING.get(case_type)
        if not file_name:
            return 0
            
        # Load case data
        with open(f'cases/{file_name}.json', 'r') as f:
            case_data = json.load(f)
            
        # Find the skin in case data
        weapon, name = skin_name.split(' | ')
        for grade, skins in case_data['skins'].items():
            for skin in skins:
                if skin['weapon'] == weapon and skin['name'] == name:
                    # Get the correct price key based on StatTrak
                    price_key = f'ST_{wear}' if is_stattrak else wear
                    if price_key not in skin['prices']:
                        return 0
                        
                    # Get base price
                    base_price = float(skin['prices'][price_key])
                    
                    # Adjust price based on float value
                    adjusted_price = adjust_price_by_float(base_price, wear, float_value)
                    
                    # If it's StatTrak, we need to ensure we're using the StatTrak price as base
                    if is_stattrak:
                        # Calculate the adjustment multiplier from the base adjustment
                        adjustment_multiplier = adjusted_price / base_price
                        # Apply the same multiplier to the StatTrak price
                        return base_price * adjustment_multiplier
                    
                    return adjusted_price
                    
        return 0
    except Exception as e:
        print(f"Error loading skin price: {e}")
        return 0
    

def load_case(case_type: str) -> Union[Case, Dict, None]:
    """
    Load case data from JSON file. Returns either a Case object for opening cases,
    or a dictionary with basic case info for the shop display.
    """
    try:
        # If we just need basic case info for the shop
        if case_type == 'all':
            cases = {}
            for case_key, file_name in CASE_FILE_MAPPING.items():
                try:
                    with open(f'cases/{file_name}.json', 'r') as f:
                        case_data = json.load(f)
                        cases[case_key] = {
                            'name': case_data['name'],
                            'image': case_data['image'],
                            'price': case_data['price']
                        }
                except Exception as e:
                    print(f"Error loading {file_name}: {e}")
            return cases
            
        # For opening specific cases
        file_name = CASE_FILE_MAPPING.get(case_type)
        if not file_name:
            print(f"Invalid case type: {case_type}")
            return None
            
        with open(f'cases/{file_name}.json', 'r') as f:
            data = json.load(f)
            
        # For opening cases, create a Case object with full skin data
        contents = {
            Rarity.CONTRABAND: [],  # Add CONTRABAND rarity
            Rarity.GOLD: [],
            Rarity.RED: [],
            Rarity.PINK: [],
            Rarity.PURPLE: [],
            Rarity.BLUE: []
        }
        
        grade_map = {
            'contraband': Rarity.CONTRABAND,  # Add contraband mapping
            'gold': Rarity.GOLD,
            'red': Rarity.RED,
            'pink': Rarity.PINK,
            'purple': Rarity.PURPLE,
            'blue': Rarity.BLUE
        }
        
        for grade, items in data['skins'].items():
            rarity = grade_map[grade]
            for item in items:
                contents[rarity].append((item['weapon'], item['name']))
        
        return Case(data['name'], contents, file_name)
        
    except Exception as e:
        print(f"Error loading case {case_type}: {e}")
        return None

def get_case_prices(case_type: str = None) -> Union[float, Dict[str, float]]:
    """Get price for a single case or all case prices if no case_type provided"""
    if case_type is not None:
        try:
            file_name = CASE_FILE_MAPPING.get(case_type)
            if not file_name:
                print(f"Unknown case type: {case_type}")
                return 0
                
            with open(f'cases/{file_name}.json', 'r') as f:
                data = json.load(f)
                return data.get('price', 0)
        except Exception:
            return 0
    else:
        return {case_type: get_case_prices(case_type) for case_type in CASE_FILE_MAPPING.keys()}