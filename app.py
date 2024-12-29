from flask import Flask, render_template, jsonify, session, redirect, url_for, request, send_from_directory
from dataclasses import dataclass, asdict
from enum import Enum
import random
from typing import List, Dict, Tuple, Union
import time
import json
from functools import wraps
from datetime import timedelta

app = Flask(__name__)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = timedelta(days=7)  # Cache static files for 7 days

# Add login_required decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            session['user'] = {
                'balance': 1000.0,
                'inventory': [],
                'exp': 0,
                'rank': 0,
                'upgrades': {
                    'click_value': 1,      # Start at level 1
                    'max_multiplier': 1,   # Start at level 1
                    'auto_clicker': 0,     # Start at level 0 (not unlocked)
                    'combo_speed': 1,      # Start at level 1
                    'critical_strike': 0    # Add critical strike
                }
            }
        return f(*args, **kwargs)
    return decorated_function

class Rarity(Enum):
    BLUE = "Mil-Spec"
    PURPLE = "Restricted"
    PINK = "Classified"
    RED = "Covert"
    GOLD = "Rare Special"

class Wear(Enum):
    BS = "Battle-Scarred"
    WW = "Well-Worn"
    FT = "Field-Tested"
    MW = "Minimal Wear"
    FN = "Factory New"

@dataclass
class Skin:
    weapon: str
    name: str
    rarity: Rarity
    wear: Wear
    stattrak: bool = False
    case_type: str = 'weapon_case_1'  # Add default case type
    
    def get_price(self) -> float:
        try:
            # Get the correct case file based on case_type
            case_file = {
                'csgo': 'weapon_case_1',
                'esports': 'esports_2013',
                'bravo': 'operation_bravo'
            }.get(self.case_type, 'weapon_case_1')
            
            with open(f'cases/{case_file}.json', 'r') as f:
                case_data = json.load(f)
                
            # Search through all rarity categories
            for grade, skins in case_data['skins'].items():
                for skin in skins:
                    if skin['weapon'] == self.weapon and skin['name'] == self.name:
                        prices = skin['prices']
                        wear_key = 'NO' if 'NO' in prices else self.wear.name
                        if self.stattrak:
                            return prices.get(f"ST_{wear_key}", 0)
                        return prices.get(wear_key, 0)
            return 0
        except Exception as e:
            print(f"Error getting price: {e}")
            return 0

class Case:
    def __init__(self, name: str, skins: dict, case_type: str = 'weapon_case_1'):
        self.name = name
        self.skins = skins
        self.case_type = case_type
    
    def open(self) -> Skin:
        # Roll for rarity based on percentages
        roll = random.random() * 100
        
        if roll < 0.26:  # 0.26% chance for Gold/Knives
            chosen_rarity = Rarity.GOLD
        elif roll < 0.26 + 0.90:  # 0.90% chance for Red
            chosen_rarity = Rarity.RED
        elif roll < 0.26 + 0.90 + 4.10:  # 4.10% chance for Pink
            chosen_rarity = Rarity.PINK
        elif roll < 0.26 + 0.90 + 4.10 + 20.08:  # 20.08% chance for Purple
            chosen_rarity = Rarity.PURPLE
        else:  # Remaining ~74.66% chance for Blue
            chosen_rarity = Rarity.BLUE
        
        # Select random skin from chosen rarity
        possible_skins = self.skins.get(chosen_rarity, [])
        if not possible_skins:
            return None
        
        chosen_skin = random.choice(possible_skins)
        
        try:
            # Load case data to get valid wears
            with open(f'cases/{self.case_type}.json', 'r') as f:
                case_data = json.load(f)
                
            # Find the skin in the case data
            skin_data = None
            for rarity in case_data['skins'].values():
                for skin in rarity:
                    if skin['weapon'] == chosen_skin[0] and skin['name'] == chosen_skin[1]:
                        skin_data = skin
                        break
                if skin_data:
                    break
            
            if skin_data:
                valid_wears = skin_data['valid_wears']
                chosen_wear = Wear[random.choice(valid_wears)]
                
                # StatTrak™ chance (10% for all rarities)
                stattrak = random.random() < 0.10
                
                return Skin(
                    chosen_skin[0], 
                    chosen_skin[1], 
                    chosen_rarity, 
                    chosen_wear, 
                    stattrak,
                    self.case_type
                )
        except Exception as e:
            print(f"Error in Case.open(): {e}")
        
        # Fallback to FT wear if something goes wrong
        return Skin(
            chosen_skin[0],
            chosen_skin[1],
            chosen_rarity,
            Wear.FT,
            False,
            self.case_type
        )

def load_case(case_type: str) -> Case:
    try:
        case_file_mapping = {
            'csgo': 'weapon_case_1',
            'esports': 'esports_2013',
            'bravo': 'operation_bravo',
            'csgo2': 'weapon_case_2',
            'esports_winter': 'esports_2013_winter',
            'winter_offensive': 'winter_offensive_case'  # Add Winter Offensive Case
        }
        
        file_name = case_file_mapping.get(case_type)
        if not file_name:
            print(f"Invalid case type: {case_type}")
            return None
            
        with open(f'cases/{file_name}.json', 'r') as f:
            data = json.load(f)
            
        contents = {
            Rarity.GOLD: [],
            Rarity.RED: [],
            Rarity.PINK: [],
            Rarity.PURPLE: [],
            Rarity.BLUE: []
        }
        
        grade_map = {
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
        
        return Case(data['name'], contents, file_name)  # Pass the correct file name
    except Exception as e:
        print(f"Error loading case {case_type}: {e}")
        return None

# Replace hardcoded case definitions with loaded ones
CSGO_WEAPON_CASE = load_case('weapon_case_1')
ESPORTS_2013_CASE = load_case('esports_2013')  # You'll need to create this JSON file

# Update the case prices to load from JSON files
def get_case_price(case_type: str) -> float:
    try:
        with open(f'cases/{case_type}.json', 'r') as f:
            data = json.load(f)
            return data.get('price', 0)
    except Exception:
        return 0

# Replace hardcoded CASE_PRICES with dynamic loading
def get_case_prices() -> Dict[str, float]:
    return {
        'csgo': get_case_price('weapon_case_1'),
        'esports': get_case_price('esports_2013'),
        'bravo': get_case_price('operation_bravo'),
        'csgo2': get_case_price('weapon_case_2'),
        'esports_winter': get_case_price('esports_2013_winter'),
        'winter_offensive': get_case_price('winter_offensive_case')  # Add Winter Offensive Case
    }

RANKS = {
    0: "Silver I",
    1: "Silver II", 
    2: "Silver III",
    3: "Silver IV",
    4: "Silver Elite",
    5: "Silver Elite Master",
    6: "Gold Nova I",
    7: "Gold Nova II",
    8: "Gold Nova III",
    9: "Gold Nova Master",
    10: "Master Guardian I",
    11: "Master Guardian II",
    12: "Master Guardian Elite",
    13: "Distinguished Master Guardian",
    14: "Legendary Eagle",
    15: "Legendary Eagle Master",
    16: "Supreme Master First Class",
    17: "The Global Elite"
}

RANK_EXP = {
    0: 10,     # Silver I to Silver II
    1: 50,     # Silver II to Silver III  
    2: 100,    # Silver III to Silver IV
    3: 200,    # Silver IV to Silver Elite
    4: 500,    # Silver Elite to Silver Elite Master
    5: 1000,   # Silver Elite Master to Gold Nova I
    6: 2000,   # Gold Nova I to Gold Nova II
    7: 5000,   # Gold Nova II to Gold Nova III
    8: 10000,  # Gold Nova III to Gold Nova Master
    9: 20000,  # Gold Nova Master to Master Guardian I
    10: 50000, # Master Guardian I to Master Guardian II
    11: 75000, # Master Guardian II to Master Guardian Elite
    12: 100000,# Master Guardian Elite to Distinguished Master Guardian
    13: 150000,# Distinguished Master Guardian to Legendary Eagle
    14: 250000,# Legendary Eagle to Legendary Eagle Master
    15: 500000,# Legendary Eagle Master to Supreme Master First Class
    16: 1000000 # Supreme Master First Class to The Global Elite
}

@dataclass
class Upgrades:
    click_value: int = 1  # Start at level 1
    max_multiplier: int = 1  # Start at level 1
    auto_clicker: int = 0  # Start at level 0 (not unlocked)
    combo_speed: int = 1  # Start at level 1
    critical_strike: int = 0  # Start at level 0 (not unlocked)

@dataclass
class User:
    balance: float = 1000.0
    inventory: List[Union[Skin, dict]] = None  # Can contain both Skin objects and case dictionaries
    exp: float = 0.0
    rank: int = 0
    upgrades: Upgrades = None

    def __post_init__(self):
        if self.inventory is None:
            self.inventory = []
        if self.upgrades is None:
            self.upgrades = Upgrades()

    def can_afford(self, amount: float) -> bool:
        return self.balance >= amount

    def add_skin(self, skin: Skin):
        self.inventory.append(skin)

    def subtract_balance(self, amount: float):
        self.balance -= amount
        self.add_exp(amount)
    
    def add_exp(self, amount: float):
        self.exp += amount
        while self.rank < len(RANK_EXP) and int(self.exp) >= RANK_EXP[self.rank]:
            self.exp -= RANK_EXP[self.rank]
            self.rank += 1

def create_user_from_dict(data: dict) -> User:
    upgrades_data = data.get('upgrades', {})
    upgrades = Upgrades(
        click_value=upgrades_data.get('click_value', 1),
        max_multiplier=upgrades_data.get('max_multiplier', 1),
        auto_clicker=upgrades_data.get('auto_clicker', 0),
        combo_speed=upgrades_data.get('combo_speed', 1),
        critical_strike=upgrades_data.get('critical_strike', 0)
    )
    
    user = User(
        balance=data.get('balance', 1000.0),
        exp=data.get('exp', 0),
        rank=data.get('rank', 0),
        upgrades=upgrades
    )
    
    if data.get('inventory'):
        for item in data['inventory']:
            # Check if item is a case
            if item.get('is_case'):
                # Just append the case data directly to inventory
                user.inventory.append(item)
            else:
                # Create Skin object for weapon skins and preserve case_type
                skin_dict = {
                    'weapon': item['weapon'],
                    'name': item['name'],
                    'rarity': item['rarity'],
                    'wear': item.get('wear', 'FT'),
                    'stattrak': item.get('stattrak', False),
                    'price': item.get('price', 0),
                    'timestamp': item.get('timestamp', 0),
                    'case_type': item.get('case_type', 'csgo')  # Default to 'csgo' if not present
                }
                user.inventory.append(skin_dict)
    return user

# Update the case prices
CASE_PRICES = {
    'csgo': 125.00,  # CS:GO Weapon Case
    'esports': 55.00,   # eSports 2013 Case
    'bravo': 150.00,  # Operation Bravo Case price
    'csgo2': 13.00,   # CS:GO Weapon Case 2 price
    'esports_winter': 11.00,  # eSports 2013 Winter Case price
    'winter_offensive': 10.00  # Winter Offensive Case price
}

VALID_WEARS = {
    "AK-47|Fire Serpent": ["FN", "MW", "FT", "WW", "BS"],
    "Desert Eagle|Golden Koi": ["FN", "MW"],
    "AWP|Graphite": ["FN", "MW"],
    "P90|Emerald Dragon": ["FN", "MW", "FT", "WW", "BS"],
    "P2000|Ocean Foam": ["FN", "MW"],
    "USP-S|Overgrowth": ["FN", "MW", "FT", "WW", "BS"],
    "MAC-10|Graven": ["FN", "MW", "FT", "WW", "BS"],
    "M4A1-S|Bright Water": ["MW", "FT"],
    "M4A4|Zirka": ["FN", "MW", "FT", "WW", "BS"],
    "Dual Berettas|Black Limba": ["FN", "MW", "FT", "WW", "BS"],
    "SG 553|Wave Spray": ["FN", "MW", "FT", "WW", "BS"],
    "Nova|Tempest": ["FN", "MW", "FT", "WW", "BS"],
    "Galil AR|Shattered": ["FN", "MW", "FT", "WW", "BS"],
    "UMP-45|Bone Pile": ["FN", "MW", "FT", "WW", "BS"]
}

# Add this function to load case data
def load_case_data():
    cases = {}
    case_files = {
        'csgo': 'cases/weapon_case_1.json',
        'esports': 'cases/esports_2013.json',
        'bravo': 'cases/operation_bravo.json',
        'csgo2': 'cases/weapon_case_2.json',
        'esports_winter': 'cases/esports_2013_winter.json',
        'winter_offensive': 'cases/winter_offensive_case.json'  # Add Winter Offensive Case
    }
    
    for case_type, file_path in case_files.items():
        try:
            with open(file_path, 'r') as f:
                case_data = json.load(f)
                cases[case_type] = {
                    'name': case_data['name'],
                    'image': case_data['image'],
                    'price': case_data['price']
                }
        except Exception as e:
            print(f"Error loading {file_path}: {e}")
            
    return cases

@app.route('/', methods=['GET', 'POST'])
def index():
    if 'user' not in session:
        session['user'] = {
            'balance': 1000.0,
            'inventory': [],
            'exp': 0,
            'rank': 0,
            'upgrades': {
                'click_value': 1,      # Start at level 1
                'max_multiplier': 1,   # Start at level 1
                'auto_clicker': 0,     # Start at level 0 (not unlocked)
                'combo_speed': 1,      # Start at level 1
                'critical_strike': 0    # Add critical strike
            }
        }
    return redirect(url_for('shop'))

@app.route('/shop')
@login_required
def shop():
    cases = load_case_data()
    user = create_user_from_dict(session['user'])
    return render_template('shop.html',
        cases=cases,
        balance=user.balance,
        RANKS=RANKS,
        RANK_EXP=RANK_EXP
    )

@app.route('/inventory')
def inventory():
    if 'user' not in session:
        session['user'] = {
            'balance': 1000.0,
            'inventory': [],
            'exp': 0,
            'rank': 0,
            'upgrades': {
                'click_value': 1,
                'max_multiplier': 1,
                'auto_clicker': 0,
                'combo_speed': 1,
                'critical_strike': 0
            }
        }
    
    # Get the current inventory from session
    inventory_items = session['user'].get('inventory', [])
    
    # Update prices for all non-case items
    for item in inventory_items:
        if not item.get('is_case'):
            try:
                # Get the case file path
                case_type = item.get('case_type', 'csgo')
                case_file_mapping = {
                    'csgo': 'weapon_case_1',
                    'esports': 'esports_2013',
                    'bravo': 'operation_bravo',
                    'csgo2': 'weapon_case_2',
                    'esports_winter': 'esports_2013_winter',
                    'winter_offensive': 'winter_offensive_case'
                }
                case_file = case_file_mapping.get(case_type, 'weapon_case_1')
                
                # Load case data
                with open(f'cases/{case_file}.json', 'r') as f:
                    case_data = json.load(f)
                
                # Find the item's price in the case data
                for grade, skins in case_data['skins'].items():
                    for skin in skins:
                        if skin['weapon'] == item['weapon'] and skin['name'] == item['name']:
                            prices = skin['prices']
                            wear_key = 'NO' if 'NO' in prices else item['wear']
                            price = prices[f"ST_{wear_key}"] if item.get('stattrak') else prices[wear_key]
                            item['price'] = price
                            break
            except Exception as e:
                print(f"Error loading price for {item['weapon']} | {item['name']}: {e}")
                continue
    
    # Update session with new prices
    session['user']['inventory'] = inventory_items
    
    # Sort items so newest appears first
    inventory_items = sorted(inventory_items, 
                           key=lambda x: x.get('timestamp', 0) if not x.get('is_case') else 0, 
                           reverse=True)
    
    return render_template('inventory.html', 
                         balance=session['user']['balance'], 
                         inventory=inventory_items,
                         RANK_EXP=RANK_EXP,
                         RANKS=RANKS,
                         initial_view=request.args.get('view', 'skins'))

@app.route('/open/<case_type>')
def open_case(case_type):
    if 'user' not in session:
        return jsonify({'error': 'User not found'})
    
    inventory = session['user'].get('inventory', [])
    
    # Find the case in inventory
    case_found = False
    for i in range(len(inventory)):
        item = inventory[i]
        if item.get('is_case') and item.get('type') == case_type:
            quantity = item.get('quantity', 0)
            if quantity > 0:
                case_found = True
                # Decrease case quantity
                inventory[i]['quantity'] = quantity - 1
                # If quantity is 0, remove the case
                if inventory[i]['quantity'] <= 0:
                    inventory.pop(i)
                break
    
    if not case_found:
        return jsonify({'error': 'No cases of this type in inventory'})
    
    # Load the appropriate case
    case = load_case(case_type)
    if not case:
        return jsonify({'error': 'Invalid case type'})

    # Get case price and add exp
    try:
        case_file_mapping = {
            'csgo': 'weapon_case_1',
            'esports': 'esports_2013',
            'bravo': 'operation_bravo',
            'csgo2': 'weapon_case_2',
            'esports_winter': 'esports_2013_winter',
            'winter_offensive': 'winter_offensive_case'
        }
        
        with open(f'cases/{case_file_mapping[case_type]}.json', 'r') as f:
            case_data = json.load(f)
            case_price = float(case_data.get('price', 0))
            
            # Add exp based on case price
            current_exp = session['user'].get('exp', 0)
            current_rank = session['user'].get('rank', 0)
            
            # Add exp equal to case price
            new_exp = current_exp + case_price
            
            # Check for rank up
            while current_rank < len(RANK_EXP) and new_exp >= RANK_EXP[current_rank]:
                new_exp -= RANK_EXP[current_rank]
                current_rank += 1
            
            # Update session with new exp and rank
            session['user']['exp'] = new_exp
            session['user']['rank'] = current_rank
            
    except Exception as e:
        print(f"Error getting case price: {e}")
    
    skin = case.open()
    if not skin:
        return jsonify({'error': 'Failed to open case'})
    
    # Get the price from case data
    try:
        case_file_mapping = {
            'csgo': 'weapon_case_1',
            'esports': 'esports_2013',
            'bravo': 'operation_bravo',
            'csgo2': 'weapon_case_2',
            'esports_winter': 'esports_2013_winter',
            'winter_offensive': 'winter_offensive_case'
        }
        
        with open(f'cases/{case_file_mapping[case_type]}.json', 'r') as f:
            case_data = json.load(f)
            
        # Find the item's price in the case data
        price = 0
        for grade, skins in case_data['skins'].items():
            for case_skin in skins:
                if case_skin['weapon'] == skin.weapon and case_skin['name'] == skin.name:
                    prices = case_skin['prices']
                    wear_key = 'NO' if 'NO' in prices else skin.wear.name
                    price = prices[f"ST_{wear_key}"] if skin.stattrak else prices[wear_key]
                    break
            if price > 0:
                break
    except Exception as e:
        print(f"Error getting price: {e}")
        price = 0
    
    # Convert skin to dictionary format
    skin_dict = {
        'weapon': skin.weapon,
        'name': skin.name,
        'rarity': skin.rarity.name,
        'wear': skin.wear.name,
        'stattrak': skin.stattrak,
        'price': float(price),  # Ensure price is float
        'timestamp': time.time(),
        'case_type': case_type,
        'is_case': False
    }
    
    # Add the skin to inventory
    inventory.append(skin_dict)
    
    # Update session
    session['user']['inventory'] = inventory
    session.modified = True
    
    return jsonify({
        'item': skin_dict,
        'balance': session['user']['balance'],
        'exp': new_exp,
        'rank': current_rank,
        'rankName': RANKS[current_rank],
        'nextRankExp': RANK_EXP[current_rank] if current_rank < len(RANK_EXP) else None
    })

@app.route('/reset_session')
def reset_session():
    session['user'] = {
        'balance': 1000.0,
        'inventory': [],
        'exp': 0,
        'rank': 0,
        'upgrades': {
            'click_value': 1,  # Start at level 1
            'max_multiplier': 1,  # Start at level 1
            'auto_clicker': 0,  # Start at level 0
            'combo_speed': 1,  # Start at level 1
            'critical_strike': 0  # Start at level 0 (not unlocked)
        }
    }
    return redirect(url_for('shop'))

@app.route('/sell/<int:item_index>', methods=['POST'])
def sell_item(item_index=None):
    if 'user' not in session:
        return jsonify({'error': 'User not found'})
    
    try:
        inventory = session['user']['inventory']
        
        # Get only non-case items
        skin_items = [item for item in inventory if not item.get('is_case')]
        
        if item_index is None or item_index >= len(skin_items):
            return jsonify({'error': 'Item not found'})
        
        # Find the actual inventory index of the skin
        skin_indices = [i for i, item in enumerate(inventory) if not item.get('is_case')]
        actual_index = skin_indices[item_index]
        
        # Get the item before removing it
        item = inventory[actual_index]
        if item.get('is_case'):
            return jsonify({'error': 'Cannot sell cases'})
            
        sale_price = float(item.get('price', 0))
        
        # Remove the item and update user's balance
        inventory.pop(actual_index)
        session['user']['balance'] = float(session['user']['balance']) + sale_price
        
        # Ensure the session is updated
        session.modified = True
        
        return jsonify({
            'success': True,
            'balance': session['user']['balance'],
            'sold_price': sale_price
        })
        
    except Exception as e:
        print(f"Error in sell_item: {e}")
        return jsonify({'error': 'Failed to sell item'})

@app.route('/sell/last', methods=['POST'])
def sell_last_item():
    if 'user' not in session:
        return jsonify({'error': 'User not found'})
    
    try:
        inventory = session['user']['inventory']
        
        # Get only non-case items
        skin_items = [item for item in inventory if not item.get('is_case')]
        
        if not skin_items:
            return jsonify({'error': 'No items to sell'})
        
        # Get the most recently added skin (last item in the list)
        last_skin_index = max(
            range(len(inventory)),
            key=lambda i: inventory[i].get('timestamp', 0) if not inventory[i].get('is_case') else 0
        )
        
        # Get the item before removing it
        item = inventory[last_skin_index]
        if item.get('is_case'):
            return jsonify({'error': 'Cannot sell cases'})
            
        sale_price = float(item.get('price', 0))
        
        # Remove the item and update user's balance
        inventory.pop(last_skin_index)
        session['user']['balance'] = float(session['user']['balance']) + sale_price
        
        # Ensure the session is updated
        session.modified = True
        
        return jsonify({
            'success': True,
            'balance': session['user']['balance'],
            'sold_price': sale_price
        })
        
    except Exception as e:
        print(f"Error in sell_last_item: {e}")
        return jsonify({'error': 'Failed to sell item'})

@app.route('/clicker')
def clicker():
    if 'user' not in session:
        session['user'] = {
            'balance': 1000.0,
            'inventory': [],
            'exp': 0,
            'rank': 0,
            'upgrades': {
                'click_value': 1,      # Start at level 1
                'max_multiplier': 1,   # Start at level 1
                'auto_clicker': 0,     # Start at level 0 (not unlocked)
                'combo_speed': 1,      # Start at level 1
                'critical_strike': 0   # Start at level 0 (not unlocked)
            }
        }
    user = create_user_from_dict(session['user'])
    return render_template('clicker.html', 
                         balance=user.balance,
                         RANK_EXP=RANK_EXP,
                         RANKS=RANKS)

@app.route('/click', methods=['POST'])
def click():
    if 'user' not in session:
        return jsonify({'error': 'User not found'})
    
    data = request.get_json()
    multiplier = data.get('amount', 0)
    critical = data.get('critical', False)
    is_auto = data.get('auto', False)  # New flag for auto clicks
    
    user = create_user_from_dict(session['user'])
    
    # For auto clicks, use base value without combo multiplier
    if is_auto:
        base_click = 0.01 * (1.5 ** user.upgrades.click_value)
        earned = base_click
    else:
        base_click = 0.01 * (1.5 ** user.upgrades.click_value)
        earned = base_click * multiplier
    
    # Apply critical multiplier if it was a critical hit
    if critical:
        earned *= 4
    
    user.balance += earned
    
    # Update session
    session['user'] = {
        'balance': user.balance,
        'inventory': user.inventory,
        'exp': user.exp,
        'rank': user.rank,
        'upgrades': asdict(user.upgrades)
    }
    
    return jsonify({
        'success': True,
        'balance': user.balance,
        'earned': earned,
        'exp': int(user.exp),
        'rank': user.rank,
        'rankName': RANKS[user.rank],
        'nextRankExp': RANK_EXP[user.rank] if user.rank < len(RANK_EXP) else None
    })

@app.route('/update_session', methods=['POST'])
def update_session():
    if 'user' not in session:
        return jsonify({'error': 'User not found'})
    
    data = request.get_json()
    
    # Keep all existing user data
    current_user = session['user']
    
    # Update only the exp and rank
    current_user['exp'] = data.get('exp', current_user.get('exp', 0))
    current_user['rank'] = data.get('rank', current_user.get('rank', 0))
    
    # Save back to session
    session['user'] = current_user
    
    return jsonify({'success': True})

# Required for session handling
app.secret_key = 'your-secret-key-here'  # Change this to a secure key in production

@app.route('/upgrades')
def upgrades():
    if 'user' not in session:
        session['user'] = {
            'balance': 1000.0,
            'inventory': [],
            'exp': 0,
            'rank': 0,
            'upgrades': {
                'click_value': 0,
                'max_multiplier': 0,
                'auto_clicker': 0
            }
        }
    user = create_user_from_dict(session['user'])
    return render_template('upgrades.html', 
                         balance=user.balance,
                         upgrades=user.upgrades,
                         RANK_EXP=RANK_EXP,
                         RANKS=RANKS)

@app.route('/purchase_upgrade', methods=['POST'])
def purchase_upgrade():
    if 'user' not in session:
        return jsonify({'error': 'User not found'})
    
    user = create_user_from_dict(session['user'])
    data = request.get_json()
    upgrade_type = data.get('upgrade_type')
    
    # Update the costs dictionary to include critical strike
    costs = {
        'click_value': lambda level: 100 * (2 ** (level - 1)),  # Starts at 100
        'max_multiplier': lambda level: 250 * (2 ** (level - 1)),  # Starts at 250
        'auto_clicker': lambda level: 500 if level == 0 else 50 * (1.8 ** (level - 1)),  # Starts at 500, then 50
        'combo_speed': lambda level: 150 * (2 ** (level - 1)),  # Starts at 150
        'critical_strike': lambda level: 1000 if level == 0 else 200 * (2 ** (level - 1))  # Starts at 1000, then 200
    }
    
    if upgrade_type not in costs:
        return jsonify({'error': 'Invalid upgrade type'})
    
    current_level = getattr(user.upgrades, upgrade_type)
    cost = costs[upgrade_type](current_level)
    
    if user.balance < cost:
        return jsonify({'error': 'Insufficient funds'})
    
    # Purchase the upgrade
    user.balance -= cost
    setattr(user.upgrades, upgrade_type, current_level + 1)
    
    # Calculate next cost after level increase
    next_cost = costs[upgrade_type](current_level + 1)
    
    # Update session
    session['user'] = {
        'balance': user.balance,
        'inventory': user.inventory,  # The inventory already contains dictionaries
        'exp': user.exp,
        'rank': user.rank,
        'upgrades': asdict(user.upgrades)
    }
    
    return jsonify({
        'success': True,
        'balance': user.balance,
        'upgrades': asdict(user.upgrades),
        'nextCost': next_cost  # Send the next cost to the frontend
    })

@app.route('/get_upgrades')
def get_upgrades():
    if 'user' not in session:
        return jsonify({
            'click_value': 0,
            'max_multiplier': 0,
            'auto_clicker': 0,
            'combo_speed': 0,
            'critical_strike': 0  # Add critical strike
        })
    
    user = create_user_from_dict(session['user'])
    return jsonify({
        'click_value': user.upgrades.click_value,
        'max_multiplier': user.upgrades.max_multiplier,
        'auto_clicker': user.upgrades.auto_clicker,
        'combo_speed': user.upgrades.combo_speed,
        'critical_strike': user.upgrades.critical_strike  # Add critical strike
    })

@app.route('/cheat')
def cheat():
    if 'user' not in session:
        session['user'] = {
            'balance': 1000.0,
            'inventory': [],
            'exp': 0,
            'rank': 0,
            'upgrades': {
                'click_value': 1,
                'max_multiplier': 1,
                'auto_clicker': 0,
                'combo_speed': 1,
                'critical_strike': 0    # Add critical strike
            }
        }
    
    user = create_user_from_dict(session['user'])
    user.balance += 10000.0
    
    # Update session - just pass the inventory directly since items are already dictionaries
    session['user'] = {
        'balance': user.balance,
        'inventory': user.inventory,  # The inventory already contains dictionaries
        'exp': user.exp,
        'rank': user.rank,
        'upgrades': asdict(user.upgrades)
    }
    
    return redirect(url_for('shop'))

@app.route('/chest_reward', methods=['POST'])
def chest_reward():
    if 'user' not in session:
        return jsonify({'error': 'User not found'})
    
    data = request.get_json()
    reward = data.get('amount', 0)
    
    user = create_user_from_dict(session['user'])
    user.balance += reward
    
    # Get current inventory and preserve cases
    inventory = session['user'].get('inventory', [])
    
    # Update session while preserving cases
    session['user'] = {
        'balance': user.balance,
        'inventory': inventory,  # Keep the entire inventory including cases
        'exp': user.exp,
        'rank': user.rank,
        'upgrades': asdict(user.upgrades)
    }
    
    return jsonify({
        'success': True,
        'balance': user.balance
    })

# Add this new route to handle case purchases
@app.route('/buy_case', methods=['POST'])
def buy_case():
    if 'user' not in session:
        return jsonify({'error': 'User not found'})
    
    data = request.get_json()
    case_type = data.get('case_type')
    quantity = data.get('quantity', 1)
    
    case_prices = get_case_prices()
    if case_type not in case_prices:
        return jsonify({'error': 'Invalid case type'})
    
    total_cost = case_prices[case_type] * quantity
    user = create_user_from_dict(session['user'])
    
    if not user.can_afford(total_cost):
        return jsonify({'error': 'Insufficient funds'})
    
    user.balance -= total_cost
    
    # Add cases to inventory
    case_data = {
        'csgo': {
            'name': 'CS:GO Weapon Case',
            'image': 'weapon_case_1.png',
            'is_case': True,
            'type': 'csgo'
        },
        'esports': {
            'name': 'eSports 2013 Case',
            'image': 'esports_2013_case.png',
            'is_case': True,
            'type': 'esports'
        },
        'bravo': {
            'name': 'Operation Bravo Case',
            'image': 'operation_bravo_case.png',
            'is_case': True,
            'type': 'bravo'
        },
        'csgo2': {
            'name': 'CS:GO Weapon Case 2',
            'image': 'weapon_case_2.png',
            'is_case': True,
            'type': 'csgo2'
        },
        'esports_winter': {
            'name': 'eSports 2013 Winter Case',
            'image': 'esports_2013_winter_case.png',
            'is_case': True,
            'type': 'esports_winter'
        },
        'winter_offensive': {
            'name': 'Winter Offensive Case',
            'image': 'winter_offensive_case.png',
            'is_case': True,
            'type': 'winter_offensive'
        }
    }
    
    # Get current inventory
    inventory = session['user'].get('inventory', [])
    
    # Update or add case to inventory
    case_found = False
    for item in inventory:
        if item.get('is_case') and item.get('type') == case_type:
            item['quantity'] = item.get('quantity', 0) + quantity
            case_found = True
            break
    
    if not case_found:
        case_info = case_data[case_type].copy()
        case_info['quantity'] = quantity
        inventory.append(case_info)
    
    # Update session with complete user data
    session['user'] = {
        'balance': user.balance,
        'inventory': inventory,
        'exp': user.exp,
        'rank': user.rank,
        'upgrades': asdict(user.upgrades)
    }
    
    print("Updated inventory:", inventory)  # Debug print
    
    return jsonify({
        'success': True,
        'balance': user.balance
    })

@app.route('/get_inventory')
def get_inventory():
    if 'user' not in session:
        return jsonify({'error': 'User not found'})
    
    inventory_items = session['user'].get('inventory', [])
    
    # Update prices for non-case items
    for item in inventory_items:
        if not item.get('is_case'):
            try:
                case_type = item.get('case_type', 'csgo')
                case_file_mapping = {
                    'csgo': 'weapon_case_1',
                    'esports': 'esports_2013',
                    'bravo': 'operation_bravo',
                    'csgo2': 'weapon_case_2',
                    'esports_winter': 'esports_2013_winter',
                    'winter_offensive': 'winter_offensive_case'
                }
                
                with open(f'cases/{case_file_mapping[case_type]}.json', 'r') as f:
                    case_data = json.load(f)
                
                # Find the item's price in the case data
                for grade, skins in case_data['skins'].items():
                    for skin in skins:
                        if skin['weapon'] == item['weapon'] and skin['name'] == item['name']:
                            prices = skin['prices']
                            wear_key = 'NO' if 'NO' in prices else item['wear']
                            price = prices[f"ST_{wear_key}"] if item.get('stattrak') else prices[wear_key]
                            item['price'] = float(price)  # Ensure price is float
                            break
                    if item['price'] > 0:
                        break
                        
            except Exception as e:
                print(f"Error loading price for {item['weapon']} | {item['name']}: {e}")
                continue
    
    # Update session with new prices
    session['user']['inventory'] = inventory_items
    session.modified = True
    
    return jsonify({
        'inventory': inventory_items
    })

@app.route('/get_user_data')
def get_user_data():
    if 'user' not in session:
        return jsonify({'error': 'User not found'})
    
    user = create_user_from_dict(session['user'])
    return jsonify({
        'exp': int(user.exp),
        'rank': user.rank,
        'rankName': RANKS[user.rank],
        'nextRankExp': RANK_EXP[user.rank] if user.rank < len(RANK_EXP) else None
    })

@app.route('/data/case_contents/<case_type>')
def get_case_contents(case_type):
    case_file_mapping = {
        'csgo': 'weapon_case_1',
        'esports': 'esports_2013',
        'bravo': 'operation_bravo',
        'csgo2': 'weapon_case_2',
        'esports_winter': 'esports_2013_winter',
        'winter_offensive': 'winter_offensive_case'  # Add Winter Offensive Case
    }
    
    if case_type not in case_file_mapping:
        return jsonify({'error': 'Invalid case type'}), 404
        
    try:
        with open(f'cases/{case_file_mapping[case_type]}.json', 'r') as f:
            return jsonify(json.load(f))
    except FileNotFoundError:
        return jsonify({'error': 'Case data not found'}), 404

@app.route('/static/<path:filename>')
def custom_static(filename):
    cache_timeout = app.config['SEND_FILE_MAX_AGE_DEFAULT'].total_seconds()
    response = send_from_directory('static', filename)
    response.cache_control.max_age = int(cache_timeout)
    response.cache_control.public = True
    return response

@app.route('/casino')
@login_required
def casino():
    return render_template('casino.html',
                         balance=session['user']['balance'],
                         RANKS=RANKS,
                         RANK_EXP=RANK_EXP)

@app.route('/coinflip')
@login_required
def coinflip():
    return render_template('coinflip.html',
                         balance=session['user']['balance'],
                         RANKS=RANKS,
                         RANK_EXP=RANK_EXP)

@app.route('/play_coinflip', methods=['POST'])
@login_required
def play_coinflip():
    try:
        data = request.get_json()
        bet_amount = float(data.get('amount', 0))
        chosen_side = data.get('side')
        
        if not chosen_side or chosen_side not in ['ct', 't']:
            return jsonify({'error': 'Invalid side selection'})
        
        if bet_amount <= 0:
            return jsonify({'error': 'Invalid bet amount'})
        
        user = create_user_from_dict(session['user'])
        
        if bet_amount > user.balance:
            return jsonify({'error': 'Insufficient funds'})
        
        # Determine result (50/50 chance)
        result = random.choice(['ct', 't'])
        won = result == chosen_side
        
        # Calculate new balance but don't update session yet
        new_balance = user.balance + bet_amount if won else user.balance - bet_amount
        
        return jsonify({
            'success': True,
            'won': won,
            'result': result,
            'balance': new_balance,
            'currentBalance': user.balance
        })
        
    except Exception as e:
        print(f"Error in play_coinflip: {e}")
        return jsonify({'error': 'Failed to play coinflip'})

# Add new route to update balance after animation
@app.route('/update_coinflip_balance', methods=['POST'])
@login_required
def update_coinflip_balance():
    try:
        data = request.get_json()
        new_balance = float(data.get('balance', 0))
        
        user = create_user_from_dict(session['user'])
        user.balance = new_balance
        
        # Update session
        session['user'] = {
            'balance': user.balance,
            'inventory': user.inventory,
            'exp': user.exp,
            'rank': user.rank,
            'upgrades': asdict(user.upgrades)
        }
        
        return jsonify({'success': True})
    except Exception as e:
        print(f"Error updating balance: {e}")
        return jsonify({'error': 'Failed to update balance'})

@app.route('/roulette')
@login_required
def roulette():
    return render_template('roulette.html',
                         balance=session['user']['balance'],
                         RANKS=RANKS,
                         RANK_EXP=RANK_EXP)

@app.route('/play_roulette', methods=['POST'])
@login_required
def play_roulette():
    try:
        data = request.get_json()
        bets = data.get('bets', {})  # Dictionary of bets {bet_type: amount}
        total_bet = sum(bets.values())
        
        user = create_user_from_dict(session['user'])
        
        if total_bet > user.balance:
            return jsonify({'error': 'Insufficient funds'})
        
        # Determine result
        result = random.randint(0, 36)
        
        # Calculate winnings
        winnings = 0
        for bet_type, amount in bets.items():
            if bet_type.isdigit():  # Single number bet
                if int(bet_type) == result:
                    winnings += amount * 36
            elif bet_type in ['red', 'black']:
                if (bet_type == 'red' and result in RED_NUMBERS) or \
                   (bet_type == 'black' and result in BLACK_NUMBERS):
                    winnings += amount * 2
            elif bet_type in ['even', 'odd']:
                if result != 0 and \
                   ((bet_type == 'even' and result % 2 == 0) or \
                    (bet_type == 'odd' and result % 2 == 1)):
                    winnings += amount * 2
            elif bet_type in ['1-18', '19-36']:
                if (bet_type == '1-18' and 1 <= result <= 18) or \
                   (bet_type == '19-36' and 19 <= result <= 36):
                    winnings += amount * 2
            elif bet_type in ['1st12', '2nd12', '3rd12']:
                if (bet_type == '1st12' and 1 <= result <= 12) or \
                   (bet_type == '2nd12' and 13 <= result <= 24) or \
                   (bet_type == '3rd12' and 25 <= result <= 36):
                    winnings += amount * 3
        
        # Calculate new balance only if there were bets
        new_balance = user.balance - total_bet + winnings if total_bet > 0 else user.balance
        
        return jsonify({
            'success': True,
            'result': result,
            'winnings': winnings,
            'balance': new_balance,
            'currentBalance': user.balance
        })
        
    except Exception as e:
        print(f"Error in play_roulette: {e}")
        return jsonify({'error': 'Failed to play roulette'})

@app.route('/update_roulette_balance', methods=['POST'])
@login_required
def update_roulette_balance():
    try:
        data = request.get_json()
        new_balance = float(data.get('balance', 0))
        
        user = create_user_from_dict(session['user'])
        user.balance = new_balance
        
        # Update session
        session['user'] = {
            'balance': user.balance,
            'inventory': user.inventory,
            'exp': user.exp,
            'rank': user.rank,
            'upgrades': asdict(user.upgrades)
        }
        
        return jsonify({'success': True})
    except Exception as e:
        print(f"Error updating balance: {e}")
        return jsonify({'error': 'Failed to update balance'})

# Add these constants at the top of the file with other constants
RED_NUMBERS = {1, 3, 5, 7, 9, 12, 14, 16, 18, 19, 21, 23, 25, 27, 30, 32, 34, 36}
BLACK_NUMBERS = {2, 4, 6, 8, 10, 11, 13, 15, 17, 20, 22, 24, 26, 28, 29, 31, 33, 35}

if __name__ == '__main__':
    app.run(debug=True)
