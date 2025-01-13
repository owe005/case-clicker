from datetime import date, datetime
import json
import random

from config import CASE_FILE_MAPPING, CASE_TYPES

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
        # Load all case data for available skins
        all_skins = []
        
        # Load skins from each case
        for case_type in CASE_TYPES:
            try:
                file_name = CASE_FILE_MAPPING.get(case_type)
                if not file_name:
                    continue
                with open(f'cases/{file_name}.json', 'r') as f:
                    case_data = json.load(f)
                    
                    for grade, items in case_data['skins'].items():
                        for item in items:
                            skin_info = {
                                'weapon': item['weapon'],
                                'name': item['name'],
                                'prices': item['prices'],
                                'case_type': case_type,
                                'case_file': file_name,
                                'rarity': grade.upper(),
                                'image': item['image']
                            }
                            all_skins.append(skin_info)
            except Exception as e:
                print(f"Error loading case {case_type}: {e}")
                continue

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
            
            # Generate trade items
            if trade_type == 'buy':
                # Bot offers money for skins
                num_requested = random.randint(1, 3)
                requested_skins = []
                
                for _ in range(num_requested):
                    skin = random.choice(all_skins)
                    wear = random.choice(['FN', 'MW', 'FT', 'WW', 'BS'])
                    stattrak = random.random() < 0.1
                    
                    price_key = f"ST_{wear}" if stattrak else wear
                    if price_key in skin['prices']:
                        price = float(skin['prices'][price_key])
                        requested_skins.append({
                            'type': 'skin',
                            'weapon': skin['weapon'],
                            'name': skin['name'],
                            'wear': wear,
                            'stattrak': stattrak,
                            'price': price,
                            'case_type': skin['case_type'],
                            'case_file': skin['case_file'],
                            'rarity': skin['rarity'],
                            'image': skin['image']
                        })
                
                if not requested_skins:  # Skip if no valid skins were found
                    continue
                    
                # Bot offers slightly more than market value to buy specific skins
                total_value = sum(skin['price'] for skin in requested_skins)
                variance = random.uniform(1.05, 1.15)  # Bot pays 5-15% more than market
                money_amount = total_value * variance
                
                trade = {
                    'type': 'buy',
                    'botName': bot['name'],
                    'botAvatar': bot['avatar'],
                    'offering': [{'type': 'money', 'amount': money_amount}],
                    'requesting': requested_skins
                }
                
            elif trade_type == 'sell':
                # Bot offers skins for money
                num_offered = random.randint(1, 3)
                offered_skins = []
                total_value = 0
                
                for _ in range(num_offered):
                    skin = random.choice(all_skins)
                    wear = random.choice(['FN', 'MW', 'FT', 'WW', 'BS'])
                    stattrak = random.random() < 0.1
                    
                    price_key = f"ST_{wear}" if stattrak else wear
                    if price_key in skin['prices']:
                        price = float(skin['prices'][price_key])
                        total_value += price
                        offered_skins.append({
                            'type': 'skin',
                            'weapon': skin['weapon'],
                            'name': skin['name'],
                            'wear': wear,
                            'stattrak': stattrak,
                            'price': price,
                            'case_type': skin['case_type'],
                            'case_file': skin['case_file'],
                            'rarity': skin['rarity'],
                            'image': skin['image']
                        })
                
                if not offered_skins:  # Skip if no valid skins were found
                    continue
                
                # Bot sells at a premium - users pay more for specific skins
                markup = random.uniform(1.15, 1.35)  # 15-35% markup for desired skins
                money_requested = total_value * markup
                
                trade = {
                    'type': 'sell',
                    'botName': bot['name'],
                    'botAvatar': bot['avatar'],
                    'offering': offered_skins,
                    'requesting': [{'type': 'money', 'amount': money_requested}]
                }
                
            else:  # swap
                # Bot offers skins for other skins
                num_each = random.randint(1, 2)
                offered_skins = []
                requested_skins = []
                offered_value = 0
                
                for _ in range(num_each):
                    # Offered skins
                    skin = random.choice(all_skins)
                    wear = random.choice(['FN', 'MW', 'FT', 'WW', 'BS'])
                    stattrak = random.random() < 0.1
                    
                    price_key = f"ST_{wear}" if stattrak else wear
                    if price_key in skin['prices']:
                        price = float(skin['prices'][price_key])
                        offered_value += price
                        offered_skins.append({
                            'type': 'skin',
                            'weapon': skin['weapon'],
                            'name': skin['name'],
                            'wear': wear,
                            'stattrak': stattrak,
                            'price': price,
                            'case_type': skin['case_type'],
                            'case_file': skin['case_file'],
                            'rarity': skin['rarity'],
                            'image': skin['image']
                        })
                
                if not offered_skins:  # Skip if no valid skins were found
                    continue
                    
                # Bot offers fair-ish trades but still wants a small premium
                target_value = offered_value * random.uniform(1.05, 1.15)  # 5-15% premium
                current_value = 0
                
                while current_value < target_value and len(requested_skins) < 3:
                    skin = random.choice(all_skins)
                    wear = random.choice(['FN', 'MW', 'FT', 'WW', 'BS'])
                    stattrak = random.random() < 0.1
                    
                    price_key = f"ST_{wear}" if stattrak else wear
                    if price_key in skin['prices']:
                        price = float(skin['prices'][price_key])
                        if current_value + price <= target_value * 1.1:  # Keep it close to target
                            current_value += price
                            requested_skins.append({
                                'type': 'skin',
                                'weapon': skin['weapon'],
                                'name': skin['name'],
                                'wear': wear,
                                'stattrak': stattrak,
                                'price': price,
                                'case_type': skin['case_type'],
                                'case_file': skin['case_file'],
                                'rarity': skin['rarity'],
                                'image': skin['image']
                            })
                
                if not requested_skins:  # Skip if no valid skins were found
                    continue
                
                trade = {
                    'type': 'swap',
                    'botName': bot['name'],
                    'botAvatar': bot['avatar'],
                    'offering': offered_skins,
                    'requesting': requested_skins
                }
            
            # Only add valid trades until we have 10
            if ((trade['offering'] and trade['requesting']) and
                (len(trade['offering']) > 0 and len(trade['requesting']) > 0)):
                trades.append(trade)
        
        return trades
        
    except Exception as e:
        print(f"Error generating daily trades: {e}")
        return []