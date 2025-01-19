from datetime import datetime
import json
import random
import traceback

from config import CASE_FILE_MAPPING, STICKER_CAPSULE_FILE_MAPPING

# Define wear ranges for float value generation
WEAR_RANGES = {
    'FN': (0.00, 0.07),
    'MW': (0.07, 0.15),
    'FT': (0.15, 0.38),
    'WW': (0.38, 0.45),
    'BS': (0.45, 1.00)
}

def generate_float_value(wear):
    """Generate a float value based on wear condition"""
    if wear not in WEAR_RANGES:
        return None
    min_float, max_float = WEAR_RANGES[wear]
    return round(random.uniform(min_float, max_float), 8)

def load_daily_trades():
    """Load daily trades from JSON file"""
    try:
        with open('data/daily_trades.json', 'r') as f:
            data = json.load(f)
            if 'completed_trades' not in data:
                data['completed_trades'] = []
            return data
    except FileNotFoundError:
        return {'date': datetime.now().strftime('%Y-%m-%d'), 'trades': [], 'completed_trades': []}

def save_daily_trades(trades_data):
    """Save daily trades to JSON file"""
    with open('data/daily_trades.json', 'w') as f:
        json.dump(trades_data, f, indent=2)

def generate_daily_trades():
    """Generate 10 random trades for the day"""
    try:
        # Load all skins from case files
        all_skins = []
        for case_type, file_name in CASE_FILE_MAPPING.items():
            try:
                with open(f'cases/{file_name}.json', 'r') as f:
                    case_data = json.load(f)
                    for grade, skins in case_data['skins'].items():
                        for skin in skins:
                            skin['case_type'] = case_type
                            skin['case_file'] = file_name
                            skin['rarity'] = grade.upper()
                            all_skins.append(skin)
            except Exception as e:
                print(f"Error loading case {case_type}: {e}")
                continue
            
        # Load sticker data
        sticker_data = {}
        for capsule_type, file_name in STICKER_CAPSULE_FILE_MAPPING.items():
            try:
                with open(f'stickers/{file_name}.json', 'r') as f:
                    capsule_data = json.load(f)
                    for rarity, stickers in capsule_data['stickers'].items():
                        for sticker in stickers:
                            sticker['case_type'] = capsule_type
                            sticker['rarity'] = rarity.upper()
                            sticker_data[f"{sticker['name']}_{capsule_type}"] = sticker
            except Exception as e:
                print(f"Error loading sticker capsule {capsule_type}: {e}")
                continue

        # Convert sticker data to list
        all_stickers = list(sticker_data.values())

        bot_names = [
            {"name": "_Astrid47", "avatar": "bot1.png"},
            {"name": "Kai.Jayden_02", "avatar": "bot2.png"},
            {"name": "Orion_Phoenix98", "avatar": "bot3.png"},
            {"name": "ElaraB_23", "avatar": "bot4.png"},
            {"name": "Theo.91", "avatar": "bot5.png"},
            {"name": "Nova-Lyn", "avatar": "bot6.png"},
            {"name": "FelixHaven19", "avatar": "bot7.png"},
            {"name": "Aria.Stella85", "avatar": "bot8.png"},
            {"name": "Lucien_Kai", "avatar": "bot9.png"},
            {"name": "Mira-Eclipse", "avatar": "bot10.png"}
        ]

        trades = []
        
        # Generate exactly 10 trades
        while len(trades) < 10:
            trade_type = random.choice(['buy', 'sell', 'swap'])
            bot = random.choice(bot_names)
            
            # Decide if this trade will involve stickers (20% chance)
            is_sticker_trade = random.random() < 0.2
            
            # Generate trade items
            if trade_type == 'buy':
                # Bot offers money for items
                num_requested = random.randint(1, 3)
                requested_items = []
                
                for _ in range(num_requested):
                    if is_sticker_trade:
                        sticker = random.choice(all_stickers)
                        requested_items.append({
                            'type': 'skin',
                            'is_sticker': True,
                            'name': sticker['name'],
                            'price': float(sticker['price']),
                            'case_type': sticker['case_type'],
                            'rarity': sticker['rarity'],
                            'image': sticker['image']
                        })
                    else:
                        skin = random.choice(all_skins)
                        wear = random.choice(['FN', 'MW', 'FT', 'WW', 'BS'])
                        stattrak = random.random() < 0.1
                        
                        price_key = f"ST_{wear}" if stattrak else wear
                        if price_key in skin['prices']:
                            price = float(skin['prices'][price_key])
                            requested_items.append({
                                'type': 'skin',
                                'is_sticker': False,
                                'weapon': skin['weapon'],
                                'name': skin['name'],
                                'wear': wear,
                                'stattrak': stattrak,
                                'price': price,
                                'case_type': skin['case_type'],
                                'case_file': skin['case_file'],
                                'rarity': skin['rarity'],
                                'image': skin['image'],
                                'float_value': generate_float_value(wear)
                            })
                    
                if not requested_items:  # Skip if no valid items were found
                    continue
                    
                # Bot offers slightly more than market value
                total_value = sum(item['price'] for item in requested_items)
                variance = random.uniform(1.05, 1.15)  # Bot pays 5-15% more than market
                money_amount = total_value * variance
                
                trade = {
                    'type': 'buy',
                    'botName': bot['name'],
                    'botAvatar': bot['avatar'],
                    'offering': [{'type': 'money', 'amount': money_amount}],
                    'requesting': requested_items
                }
                
            elif trade_type == 'sell':
                # Bot offers items for money
                num_offered = random.randint(1, 3)
                offered_items = []
                total_value = 0
                
                for _ in range(num_offered):
                    if is_sticker_trade:
                        sticker = random.choice(all_stickers)
                        price = float(sticker['price'])
                        total_value += price
                        offered_items.append({
                            'type': 'skin',
                            'is_sticker': True,
                            'name': sticker['name'],
                            'price': price,
                            'case_type': sticker['case_type'],
                            'rarity': sticker['rarity'],
                            'image': sticker['image']
                        })
                    else:
                        skin = random.choice(all_skins)
                        wear = random.choice(['FN', 'MW', 'FT', 'WW', 'BS'])
                        stattrak = random.random() < 0.1
                        
                        price_key = f"ST_{wear}" if stattrak else wear
                        if price_key in skin['prices']:
                            price = float(skin['prices'][price_key])
                            total_value += price
                            offered_items.append({
                                'type': 'skin',
                                'is_sticker': False,
                                'weapon': skin['weapon'],
                                'name': skin['name'],
                                'wear': wear,
                                'stattrak': stattrak,
                                'price': price,
                                'case_type': skin['case_type'],
                                'case_file': skin['case_file'],
                                'rarity': skin['rarity'],
                                'image': skin['image'],
                                'float_value': generate_float_value(wear)
                            })
                
                if not offered_items:  # Skip if no valid items were found
                    continue
                
                # Bot sells at a premium
                markup = random.uniform(1.15, 1.35)  # 15-35% markup
                money_requested = total_value * markup
                
                trade = {
                    'type': 'sell',
                    'botName': bot['name'],
                    'botAvatar': bot['avatar'],
                    'offering': offered_items,
                    'requesting': [{'type': 'money', 'amount': money_requested}]
                }
                
            else:  # swap
                # Bot offers items for other items
                num_each = random.randint(1, 2)
                offered_items = []
                requested_items = []
                offered_value = 0
                
                for _ in range(num_each):
                    if is_sticker_trade:
                        sticker = random.choice(all_stickers)
                        price = float(sticker['price'])
                        offered_value += price
                        offered_items.append({
                            'type': 'skin',
                            'is_sticker': True,
                            'name': sticker['name'],
                            'price': price,
                            'case_type': sticker['case_type'],
                            'rarity': sticker['rarity'],
                            'image': sticker['image']
                        })
                    else:
                        skin = random.choice(all_skins)
                        wear = random.choice(['FN', 'MW', 'FT', 'WW', 'BS'])
                        stattrak = random.random() < 0.1
                        
                        price_key = f"ST_{wear}" if stattrak else wear
                        if price_key in skin['prices']:
                            price = float(skin['prices'][price_key])
                            offered_value += price
                            offered_items.append({
                                'type': 'skin',
                                'is_sticker': False,
                                'weapon': skin['weapon'],
                                'name': skin['name'],
                                'wear': wear,
                                'stattrak': stattrak,
                                'price': price,
                                'case_type': skin['case_type'],
                                'case_file': skin['case_file'],
                                'rarity': skin['rarity'],
                                'image': skin['image'],
                                'float_value': generate_float_value(wear)
                            })
                
                if not offered_items:  # Skip if no valid items were found
                    continue
                    
                # Bot offers fair-ish trades but still wants a small premium
                target_value = offered_value * random.uniform(1.05, 1.15)  # 5-15% premium
                current_value = 0
                
                while current_value < target_value and len(requested_items) < 3:
                    if is_sticker_trade:
                        sticker = random.choice(all_stickers)
                        price = float(sticker['price'])
                        if current_value + price <= target_value * 1.1:
                            current_value += price
                            requested_items.append({
                                'type': 'skin',
                                'is_sticker': True,
                                'name': sticker['name'],
                                'price': price,
                                'case_type': sticker['case_type'],
                                'rarity': sticker['rarity'],
                                'image': sticker['image']
                            })
                    else:
                        skin = random.choice(all_skins)
                        wear = random.choice(['FN', 'MW', 'FT', 'WW', 'BS'])
                        stattrak = random.random() < 0.1
                        
                        price_key = f"ST_{wear}" if stattrak else wear
                        if price_key in skin['prices']:
                            price = float(skin['prices'][price_key])
                            if current_value + price <= target_value * 1.1:
                                current_value += price
                                requested_items.append({
                                    'type': 'skin',
                                    'is_sticker': False,
                                    'weapon': skin['weapon'],
                                    'name': skin['name'],
                                    'wear': wear,
                                    'stattrak': stattrak,
                                    'price': price,
                                    'case_type': skin['case_type'],
                                    'case_file': skin['case_file'],
                                    'rarity': skin['rarity'],
                                    'image': skin['image'],
                                    'float_value': generate_float_value(wear)
                                })
                
                if not requested_items:  # Skip if no valid items were found
                    continue
                
                trade = {
                    'type': 'swap',
                    'botName': bot['name'],
                    'botAvatar': bot['avatar'],
                    'offering': offered_items,
                    'requesting': requested_items
                }
            
            # Only add valid trades until we have 10
            if ((trade['offering'] and trade['requesting']) and
                (len(trade['offering']) > 0 and len(trade['requesting']) > 0)):
                trades.append(trade)
        
        return trades
        
    except Exception as e:
        print(f"Error generating daily trades: {e}")
        traceback.print_exc()
        return []