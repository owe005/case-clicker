import json
import random
from typing import Any, Dict, List

from config import CASE_FILE_MAPPING, CASE_TYPES, client, STICKER_CAPSULE_FILE_MAPPING
from cases_prices_and_floats import generate_float_for_wear

images_bots_avatars = {
    'Astrid47': 'bot1.png',
    'Kai.Jayden_02': 'bot2.png',
    'Orion_Phoenix98': 'bot3.png',
    'ElaraB_23': 'bot4.png',
    'Theo.91': 'bot5.png',
    'Nova-Lyn': 'bot6.png',
    'FelixHaven19': 'bot7.png',
    'Aria.Stella85': 'bot8.png',
    'Lucien_Kai': 'bot9.png',
    'Mira-Eclipse': 'bot10.png'
}

def generate_bot_players(num_bots: int, mode_limits: dict) -> List[Dict[str, Any]]:
    bot_names = [
        "_Astrid47", "Kai.Jayden_02", "Orion_Phoenix98", "ElaraB_23", "Theo.91", 
        "Nova-Lyn", "FelixHaven19", "Aria.Stella85", "Lucien_Kai", "Mira-Eclipse"
    ]
    
    # Load all case data and sticker data
    all_items = []  # Combined list for both skins and stickers
    
    # Load skins from each case
    for case_type in CASE_TYPES:
        try:
            file_name = CASE_FILE_MAPPING.get(case_type)
            if not file_name:
                continue
            with open(f'cases/{file_name}.json', 'r') as f:
                case_data = json.load(f)
                # Add all skins to the pool
                for grade, items in case_data['skins'].items():
                    for item in items:
                        all_items.append({
                            'weapon': item['weapon'],
                            'name': item['name'],
                            'prices': item['prices'],
                            'case_type': case_type,
                            'case_file': file_name,
                            'image': item.get('image', f"{item['weapon'].lower().replace(' ', '')}_{item['name'].lower().replace(' ', '_')}.png"),
                            'rarity': grade.upper(),
                            'is_sticker': False
                        })
        except Exception as e:
            print(f"Error loading case {case_type}: {e}")
            continue
    
    # Load stickers from each capsule
    for capsule_type, file_name in STICKER_CAPSULE_FILE_MAPPING.items():
        try:
            with open(f'stickers/{file_name}.json', 'r') as f:
                capsule_data = json.load(f)
                # Add all stickers to the pool
                for grade, stickers in capsule_data['stickers'].items():
                    for sticker in stickers:
                        all_items.append({
                            'name': sticker['name'],
                            'price': float(sticker['price']),
                            'case_type': capsule_type,
                            'image': sticker['image'],
                            'rarity': grade.upper(),
                            'is_sticker': True
                        })
        except Exception as e:
            print(f"Error loading sticker capsule {capsule_type}: {e}")
            continue
    
    bots = []
    used_names = set()
    
    for _ in range(num_bots):
        available_names = [name for name in bot_names if name not in used_names]
        if not available_names:
            break
        bot_name = random.choice(available_names)
        used_names.add(bot_name)
        
        # Generate 1-10 items for the bot within price range
        num_items = random.randint(1, 10)
        bot_items = []
        attempts = 0
        max_attempts = 100
        
        while len(bot_items) < num_items and attempts < max_attempts:
            attempts += 1
            if not all_items:
                break
                
            item = random.choice(all_items)
            
            if item['is_sticker']:
                # Sticker items already have a direct price
                price = item['price']
                if mode_limits['min'] <= price <= mode_limits['max']:
                    bot_items.append({
                        'name': item['name'],
                        'price': price,
                        'case_type': item['case_type'],
                        'image': item['image'],
                        'rarity': item['rarity'],
                        'is_sticker': True
                    })
            else:
                # Handle weapon skins
                wear_options = [w for w in item['prices'].keys() 
                              if not w.startswith('ST_') and w != 'NO']
                if not wear_options:
                    continue
                    
                wear = random.choice(wear_options)
                stattrak = random.random() < 0.1  # 10% chance
                
                price_key = f"ST_{wear}" if stattrak else wear
                try:
                    price = float(item['prices'].get(price_key, 0))
                    
                    # Only add if price is within mode range
                    if mode_limits['min'] <= price <= mode_limits['max']:
                        bot_items.append({
                            'weapon': item['weapon'],
                            'name': item['name'],
                            'wear': wear,
                            'rarity': item['rarity'],
                            'stattrak': stattrak,
                            'price': price,
                            'case_type': item['case_type'],
                            'case_file': item['case_file'],
                            'image': item.get('image', f"{item['weapon'].lower().replace(' ', '')}_{item['name'].lower().replace(' ', '_')}.png"),
                            'float_value': generate_float_for_wear(wear),
                            'is_sticker': False
                        })
                except (ValueError, TypeError):
                    continue
        
        if bot_items:
            bots.append({
                'name': bot_name,
                'items': bot_items
            })
    
    return bots