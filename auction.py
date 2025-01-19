from datetime import datetime
import json
from pathlib import Path
from threading import Timer
import traceback
from cases_prices_and_floats import adjust_price_by_float
from config import AUCTION_FILE, CASE_FILE_MAPPING, CASE_SKINS_FOLDER_NAMES, CASE_TYPES, STICKER_CAPSULE_FILE_MAPPING
import random
import os


def save_auction_data(auction_data):
    """Save auction data to JSON file using atomic write to prevent corruption"""
    temp_file = AUCTION_FILE + '.tmp'
    try:
        # Write to temporary file first
        with open(temp_file, 'w') as f:
            # Write data and ensure it's flushed to disk
            json.dump(auction_data, f, indent=2, default=str)
            f.flush()
            os.fsync(f.fileno())
            # Close the file explicitly before rename
            f.close()
            
        # Now that file is closed, perform the atomic rename
        os.replace(temp_file, AUCTION_FILE)
            
    except Exception as e:
        print(f"Error saving auction data: {e}")
        # Clean up temp file if it exists
        if os.path.exists(temp_file):
            try:
                os.remove(temp_file)
            except Exception as cleanup_err:
                print(f"Error cleaning up temp file: {cleanup_err}")
                
    # Final cleanup check
    if os.path.exists(temp_file):
        try:
            os.remove(temp_file)
        except Exception:
            pass  # Already logged any important errors above

def load_auction_data():
    """Load auction data from JSON file"""
    try:
        if not Path(AUCTION_FILE).exists():
            return None
        with open(AUCTION_FILE, 'r') as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        print(f"Error decoding auction data: {e}")
        # Backup corrupted file for debugging
        backup_file = AUCTION_FILE + '.corrupted'
        try:
            import shutil
            shutil.copy2(AUCTION_FILE, backup_file)
            print(f"Corrupted file backed up to: {backup_file}")
        except Exception as backup_err:
            print(f"Failed to backup corrupted file: {backup_err}")
        return None
    except Exception as e:
        print(f"Error loading auction data: {e}")
        return None

def generate_bot_budgets(base_price):
    """Generate random budgets for bots based on item value"""
    budgets = {}
    
    # List of all possible bot names
    all_bot_names = [
        "_Astrid47", "Kai.Jayden_02", "Orion_Phoenix98", "ElaraB_23",
        "Theo.91", "Nova-Lyn", "FelixHaven19", "Aria.Stella85",
        "Lucien_Kai", "Mira-Eclipse"
    ]
    
    # Randomly select 3-10 bots to participate
    num_bots = random.randint(3, 10)
    active_bots = random.sample(all_bot_names, num_bots)
    
    # Set all bots as offline initially
    for bot_name in all_bot_names:
        budgets[bot_name] = {
            "budget": 0,
            "status": "offline"
        }
    
    # Set budgets for active bots
    for bot_name in active_bots:
        # Determine budget strategy (5% chance for high/low, 90% for normal)
        strategy = random.choices(
            ['normal', 'high', 'low'],
            weights=[90, 5, 5]
        )[0]
        
        if strategy == 'normal':
            # Normal budget: ±10% of base price
            budgets[bot_name]["budget"] = base_price * random.uniform(0.9, 1.1)
        elif strategy == 'high':
            # High budget: 150% of base price
            budgets[bot_name]["budget"] = base_price * 1.5
        elif strategy == 'low':
            # Low budget: 50% of base price
            budgets[bot_name]["budget"] = base_price * 0.5
        
        # Set bot status to online
        budgets[bot_name]["status"] = "online"
    
    return budgets

def generate_auction_item():
    """Generate a rare/valuable item for auction with balanced distribution"""
    try:
        # Load all case data
        weapon_skins = []  # Regular weapons (AK-47, M4A4, etc.)
        knife_skins = []   # All knife skins
        glove_skins = []   # All glove skins
        sticker_items = [] # High value stickers
        
        print("\nGenerating auction item...")
        
        # First load valuable stickers
        for capsule_type, file_name in STICKER_CAPSULE_FILE_MAPPING.items():
            try:
                with open(f'stickers/{file_name}.json', 'r') as f:
                    capsule_data = json.load(f)
                    
                    # Look through all sticker rarities
                    for rarity, stickers in capsule_data['stickers'].items():
                        for sticker in stickers:
                            try:
                                price = float(sticker['price'])
                                # Only include very valuable stickers (over $800)
                                if price >= 800:
                                    print(f"Found valuable sticker: {sticker['name']} - ${price}")
                                    sticker_item = {
                                        'name': sticker['name'],
                                        'image': sticker['image'],
                                        'rarity': rarity.upper(),
                                        'case_type': capsule_type,
                                        'base_price': price,
                                        'adjusted_price': price,  # Stickers don't have float adjustment
                                        'is_sticker': True,
                                        'stattrak': False,  # Stickers don't have StatTrak
                                        'wear': None,  # Stickers don't have wear
                                        'float_value': None,  # Stickers don't have float
                                        'weapon': None  # Stickers don't have weapon type
                                    }
                                    sticker_items.append(sticker_item)
                            except (ValueError, KeyError) as e:
                                print(f"Error processing sticker price: {e}")
                                continue
            except Exception as e:
                print(f"Error loading sticker capsule {file_name}: {e}")
                continue
        
        print(f"\nFound {len(sticker_items)} valuable stickers")
        
        # Get wear ranges from cases_prices_and_floats
        wear_ranges = {
            'FN': (0.00, 0.07),
            'MW': (0.07, 0.15),
            'FT': (0.15, 0.38),
            'WW': (0.38, 0.45),
            'BS': (0.45, 1.00)
        }
        
        # Then load weapon/knife/glove skins
        for case_type in CASE_TYPES:
            file_name = CASE_FILE_MAPPING.get(case_type)
            folder_name = CASE_SKINS_FOLDER_NAMES.get(case_type)
            if not file_name:
                continue
                
            with open(f'cases/{file_name}.json', 'r') as f:
                case_data = json.load(f)
                
                # Look through all skins
                for grade, skins in case_data['skins'].items():
                    for skin in skins:
                        # Just use the image filename without the path
                        image_path = skin['image']
                        
                        # Check prices for valuable items
                        for wear, price in skin['prices'].items():
                            if wear != 'NO' and not wear.startswith('ST_'):
                                try:
                                    price_value = float(price)
                                    
                                    # Categorize items by their rarity grade
                                    is_knife = grade.upper() in ['GOLD', 'GOLD_KNIFE'] and not ('Gloves' in skin['weapon'] or 'Hand Wraps' in skin['weapon'])
                                    is_glove = 'Gloves' in skin['weapon'] or 'Hand Wraps' in skin['weapon']
                                    
                                    # Adjust thresholds to better balance with stickers
                                    if is_knife:
                                        # Knives: Only FN/ST FN over $2500 (increased from $2000)
                                        if wear != 'FN':
                                            continue
                                        threshold = 2500  # Further increased threshold to reduce knife count
                                    elif is_glove:
                                        # Gloves: Include FN/MW/FT over $1000
                                        if wear not in ['FN', 'MW', 'FT']:  # Added FT for gloves
                                            continue
                                        threshold = 1000  # Increased threshold but allowing more wear conditions
                                    else:
                                        # Regular weapons: Only FN/ST FN over $250 (reduced from $300)
                                        if wear != 'FN':
                                            continue
                                        threshold = 250  # Further reduced threshold to include more weapons
                                    
                                    if price_value >= threshold:                                        
                                        # Generate float based on wear range
                                        wear_range = wear_ranges.get(wear)
                                        if not wear_range:
                                            continue
                                        
                                        # Generate a very good float for the wear range
                                        min_float, max_float = wear_range
                                        float_range = max_float - min_float
                                        max_special = min_float + (float_range * 0.2)
                                        float_value = random.uniform(min_float, max_special)
                                        
                                        # Adjust price based on special float
                                        adjusted_price = adjust_price_by_float(
                                            price_value,
                                            wear,
                                            float_value
                                        )
                                        
                                        item_data = {
                                            'weapon': skin['weapon'],
                                            'name': skin['name'],
                                            'wear': wear,
                                            'float_value': float_value,
                                            'rarity': grade.upper(),
                                            'case_type': case_type,
                                            'base_price': price_value,
                                            'adjusted_price': adjusted_price,
                                            'stattrak': False,
                                            'image': image_path,
                                            'is_sticker': False
                                        }
                                        
                                        # Categorize the item based on rarity grade
                                        if is_knife:
                                            knife_skins.append(item_data)
                                        elif is_glove:
                                            glove_skins.append(item_data)
                                        else:
                                            weapon_skins.append(item_data)
                                        
                                        # Also add StatTrak version if available (only for weapons and knives)
                                        st_key = f'ST_{wear}'
                                        if st_key in skin['prices'] and not is_glove:
                                            st_price = float(skin['prices'][st_key])
                                            if st_price >= threshold:  # Use same threshold for StatTrak
                                                print(f"Found StatTrak version: {skin['weapon']} | {skin['name']} ({wear}) - ${st_price}")
                                                # Calculate StatTrak adjusted price
                                                st_adjusted_price = adjust_price_by_float(
                                                    st_price,
                                                    wear,
                                                    float_value
                                                )
                                                
                                                st_item_data = {
                                                    'weapon': skin['weapon'],
                                                    'name': skin['name'],
                                                    'wear': wear,
                                                    'float_value': float_value,
                                                    'rarity': grade.upper(),
                                                    'case_type': case_type,
                                                    'base_price': st_price,
                                                    'adjusted_price': st_adjusted_price,
                                                    'stattrak': True,
                                                    'image': image_path,
                                                    'is_sticker': False
                                                }
                                                
                                                if is_knife:
                                                    knife_skins.append(st_item_data)
                                                else:
                                                    weapon_skins.append(st_item_data)
                                except Exception as e:
                                    print(f"Error processing price: {e}")
                                    continue
        
        print(f"\nFound items:")
        print(f"Weapons: {len(weapon_skins)}")
        print(f"Knives: {len(knife_skins)}")
        print(f"Gloves: {len(glove_skins)}")
        print(f"Stickers: {len(sticker_items)}")
        
        # Ensure we have at least some items
        if not any([weapon_skins, knife_skins, glove_skins, sticker_items]):
            raise ValueError("No valuable items found")
            
        # Select item type with balanced probability
        available_types = []
        if weapon_skins:
            available_types.append(('weapon', weapon_skins))
        if knife_skins:
            available_types.append(('knife', knife_skins))
        if glove_skins:
            available_types.append(('glove', glove_skins))
        if sticker_items:
            available_types.append(('sticker', sticker_items))
            
        # Distribution: 40% weapons, 20% knives, 20% gloves, 20% stickers
        weights = []
        for item_type, items in available_types:
            if item_type == 'weapon':
                weights.append(40)  # Increased from 35%
            elif item_type == 'knife':
                weights.append(20)  # Reduced from 25%
            elif item_type == 'glove':
                weights.append(20)  # Increased from 15%
            else:  # sticker
                weights.append(20)  # Reduced from 25%
                
        # Normalize weights if not all types are available
        if weights:
            total = sum(weights)
            weights = [w/total * 100 for w in weights]
            
        # If weapons are available, force weapon selection 30% of the time (reduced from 40%)
        if any(t[0] == 'weapon' for t in available_types):
            force_weapon = random.random() < 0.30
            if force_weapon:
                weapon_pool = next(pool for type_name, pool in available_types if type_name == 'weapon')
                selected_item = random.choice(weapon_pool)
                print(f"\nForced weapon selection: {selected_item.get('weapon')} | {selected_item.get('name')}")
                return selected_item
            
        # Otherwise use weighted selection
        chosen_type, chosen_pool = random.choices(available_types, weights=weights)[0]
        selected_item = random.choice(chosen_pool)
        
        if selected_item['is_sticker']:
            print(f"\nSelected sticker: {selected_item['name']} - ${selected_item['base_price']}")
        else:
            print(f"\nSelected item: {selected_item.get('weapon')} | {selected_item['name']} - ${selected_item['base_price']}")
            
        return selected_item
        
    except Exception as e:
        print(f"Error generating auction item: {e}")
        traceback.print_exc()  # Add full traceback
        # Return a fallback item if something goes wrong
        return {
            'weapon': 'Karambit',
            'name': 'Fade',
            'wear': 'FN',
            'float_value': 0.0007,
            'rarity': 'GOLD',
            'case_type': 'csgo',
            'base_price': 1500.0,
            'adjusted_price': 2000.0,
            'stattrak': False,
            'image': 'karambit_fade.png',
            'is_sticker': False
        }