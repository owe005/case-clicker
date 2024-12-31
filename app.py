from flask import Flask, render_template, jsonify, session, redirect, url_for, request, send_from_directory
from dataclasses import asdict
import random
from typing import Dict, Union, List, Any
import time
import json
from functools import wraps
from datetime import timedelta
from dataclasses import dataclass
from typing import List, Optional
import traceback

from config import Rarity, RED_NUMBERS, BLACK_NUMBERS, RANK_EXP, RANKS
from models import Case, User, Upgrades

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = timedelta(days=7)  # Cache static files for 7 days to reduce server load

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
                    'critical_strike': 0   # Start at level 0 (not unlocked)
                }
            }
        return f(*args, **kwargs)
    return decorated_function

def load_case(case_type: str) -> Union[Case, Dict, None]:
    """
    Load case data from JSON file. Returns either a Case object for opening cases,
    or a dictionary with basic case info for the shop display.
    """
    case_file_mapping = {
        'csgo': 'weapon_case_1',
        'esports': 'esports_2013',
        'bravo': 'operation_bravo',
        'csgo2': 'weapon_case_2',
        'esports_winter': 'esports_2013_winter',
        'winter_offensive': 'winter_offensive_case'
    }
    
    try:
        # If we just need basic case info for the shop
        if case_type == 'all':
            cases = {}
            for case_key, file_name in case_file_mapping.items():
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
        file_name = case_file_mapping.get(case_type)
        if not file_name:
            print(f"Invalid case type: {case_type}")
            return None
            
        with open(f'cases/{file_name}.json', 'r') as f:
            data = json.load(f)
            
        # For opening cases, create a Case object with full skin data
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
        
        return Case(data['name'], contents, file_name)
        
    except Exception as e:
        print(f"Error loading case {case_type}: {e}")
        return None

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
                    'case_type': item.get('case_type', 'csgo')
                }
                user.inventory.append(skin_dict)
    return user

CASE_PRICES = {
    'csgo': 125.00,  # CS:GO Weapon Case
    'esports': 55.00,   # eSports 2013 Case
    'bravo': 150.00,  # Operation Bravo Case price
    'csgo2': 13.00,   # CS:GO Weapon Case 2 price
    'esports_winter': 11.00,  # eSports 2013 Winter Case price
    'winter_offensive': 10.00  # Winter Offensive Case price
}

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
                'critical_strike': 0   # Add critical strike
            }
        }
    return render_template('home.html',
                         balance=session['user']['balance'],
                         RANKS=RANKS,
                         RANK_EXP=RANK_EXP)

@app.route('/shop')
@login_required
def shop():
    cases = load_case('all')  # Get all case data for shop display
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
        
        # Find the most recently added skin by timestamp
        last_skin_index = max(
            range(len(inventory)),
            key=lambda i: inventory[i].get('timestamp', 0) if not inventory[i].get('is_case') else 0
        )
        
        # Get the item before removing it
        item = inventory[last_skin_index]
        if item.get('is_case'):
            return jsonify({'error': 'Cannot sell cases'})
            
        # Verify the item has a price
        if 'price' not in item:
            return jsonify({'error': 'Item has no price'})
            
        sale_price = float(item.get('price', 0))
        
        # Remove the item and update user's balance
        inventory.pop(last_skin_index)
        session['user']['balance'] = float(session['user']['balance']) + sale_price
        
        # Ensure the session is marked as modified
        session.modified = True
        
        # Log the successful sale
        print(f"Successfully sold item: {item.get('weapon')} | {item.get('name')} for ${sale_price}")
        
        return jsonify({
            'success': True,
            'balance': session['user']['balance'],
            'sold_price': sale_price
        })
        
    except Exception as e:
        print(f"Error in sell_last_item: {e}")
        # Return more detailed error information
        return jsonify({
            'error': 'Failed to sell item',
            'details': str(e)
        })

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
app.secret_key = 'GHJy79fuRYt79UyfF68YGIftR6+90iUOHtdR68ohHIOpjU+9gRD68r'

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
        'inventory': user.inventory,  
        'exp': user.exp,
        'rank': user.rank,
        'upgrades': asdict(user.upgrades)
    }
    
    return jsonify({
        'success': True,
        'balance': user.balance,
        'upgrades': asdict(user.upgrades),
        'nextCost': next_cost 
    })

@app.route('/get_upgrades')
def get_upgrades():
    if 'user' not in session:
        return jsonify({
            'click_value': 0,
            'max_multiplier': 0,
            'auto_clicker': 0,
            'combo_speed': 0,
            'critical_strike': 0  
        })
    
    user = create_user_from_dict(session['user'])
    return jsonify({
        'click_value': user.upgrades.click_value,
        'max_multiplier': user.upgrades.max_multiplier,
        'auto_clicker': user.upgrades.auto_clicker,
        'combo_speed': user.upgrades.combo_speed,
        'critical_strike': user.upgrades.critical_strike 
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
                'critical_strike': 0 
            }
        }
    
    user = create_user_from_dict(session['user'])
    user.balance += 10000.0
    
    
    session['user'] = {
        'balance': user.balance,
        'inventory': user.inventory,  
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
        'inventory': inventory,  
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
        'winter_offensive': 'winter_offensive_case' 
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

@dataclass
class Card:
    rank: str
    suit: str
    value: int

class BlackjackGame:
    def __init__(self):
        self.deck = []
        self.dealer_cards = []
        self.player_hands = [[]]  # List of hands (each hand is a list of cards)
        self.current_hand = 0     # Index of the current hand being played
        self.bet_amount = 0
        self.split_bet_amount = 0  # Additional bet for split hand
        self.insurance_bet = 0  # Add this line
        self.game_over = False
        self._create_deck()
        self._shuffle()
    
    def _create_deck(self):
        suits = ['♠', '♥', '♣', '♦']
        ranks = {
            'A': 11, '2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7,
            '8': 8, '9': 9, '10': 10, 'J': 10, 'Q': 10, 'K': 10
        }
        self.deck = [Card(rank, suit, value) for suit in suits 
                    for rank, value in ranks.items()]
    
    def _shuffle(self):
        random.shuffle(self.deck)
    
    def deal(self, bet_amount: float):
        self.bet_amount = bet_amount
        self.split_bet_amount = 0
        self.dealer_cards = [self.deck.pop(), self.deck.pop()]
        self.player_hands = [[self.deck.pop(), self.deck.pop()]]
        self.current_hand = 0
        self.game_over = False
        
        # Check for dealer blackjack
        dealer_score = self.get_score(self.dealer_cards)
        player_score = self.get_score(self.player_hands[0])
        
        # End game immediately if dealer has blackjack
        if dealer_score == 21 and len(self.dealer_cards) == 2:
            self.game_over = True
        # Also end game if player has blackjack (either push or win)
        elif player_score == 21 and len(self.player_hands[0]) == 2:
            self.game_over = True
    
    def hit(self):
        current_hand = self.player_hands[self.current_hand]
        current_hand.append(self.deck.pop())
        
        if self.get_score(current_hand) > 21:
            if self.current_hand < len(self.player_hands) - 1:
                # Move to next split hand if available
                self.current_hand += 1
            else:
                self.game_over = True
    
    def stand(self):
        if self.current_hand < len(self.player_hands) - 1:
            # Move to next split hand
            self.current_hand += 1
        else:
            # All hands complete, dealer's turn
            while self.get_score(self.dealer_cards) < 17:
                self.dealer_cards.append(self.deck.pop())
            self.game_over = True
    
    def double_down(self):
        self.bet_amount *= 2
        self.player_hands[self.current_hand].append(self.deck.pop())
        self.game_over = True
        self.stand()
    
    def can_split(self) -> bool:
        current_hand = self.player_hands[self.current_hand]
        return (len(current_hand) == 2 and 
                current_hand[0].rank == current_hand[1].rank and 
                len(self.player_hands) == 1)  # Can only split once
    
    def split(self):
        if not self.can_split():
            raise ValueError("Cannot split current hand")
        
        # Create new hand with second card
        current_hand = self.player_hands[self.current_hand]
        new_hand = [current_hand.pop()]
        
        # Deal one new card to each hand
        current_hand.append(self.deck.pop())
        new_hand.append(self.deck.pop())
        
        # Add new hand to player_hands
        self.player_hands.append(new_hand)
        self.split_bet_amount = self.bet_amount  # Match original bet
    
    @staticmethod
    def get_score(cards: List[Card]) -> int:
        score = sum(card.value for card in cards)
        num_aces = sum(1 for card in cards if card.rank == 'A')
        
        # Adjust for aces
        while score > 21 and num_aces:
            score -= 10
            num_aces -= 1
            
        return score
    
    def get_game_state(self) -> dict:
        dealer_score = self.get_score(self.dealer_cards)
        player_scores = [self.get_score(hand) for hand in self.player_hands]
        current_hand_score = player_scores[self.current_hand]
        
        # Determine winner if game is over
        message = ""
        won = [False] * len(self.player_hands)
        if self.game_over:
            dealer_blackjack = dealer_score == 21 and len(self.dealer_cards) == 2
            
            for i, score in enumerate(player_scores):
                if score > 21:
                    won[i] = False
                # Check for natural blackjack (21 with first two cards)
                elif score == 21 and len(self.player_hands[i]) == 2:
                    if dealer_blackjack:
                        won[i] = None  # Push if both have blackjack
                        message = "Push! Both have blackjack"
                    else:
                        won[i] = 'blackjack'  # Player wins with blackjack
                elif dealer_blackjack:
                    won[i] = False  # Dealer wins with blackjack
                    message = "Dealer Blackjack!"
                elif dealer_score > 21:
                    won[i] = True
                elif score > dealer_score:
                    won[i] = True
                elif score == dealer_score:
                    won[i] = None
                else:
                    won[i] = False
            
            # Set appropriate message if not already set
            if not message:
                if all(w is False for w in won):
                    message = "You lost!"
                elif all(w == 'blackjack' for w in won):
                    message = "Blackjack!"
                elif all(w in [True, 'blackjack'] for w in won):
                    message = "You won!"
                elif len(won) > 1:
                    wins = sum(1 for w in won if w in [True, 'blackjack'])
                    message = f"Won {wins} hand{'s' if wins != 1 else ''}!"
                else:
                    if won[0] == 'blackjack':
                        message = "Blackjack!"
                    elif won[0] is True:
                        message = "You win!"
                    elif won[0] is None:
                        message = "Push! It's a tie"
                    else:
                        message = "Dealer wins!"
        
        return {
            'dealer': {
                'cards': [{'rank': c.rank, 'suit': c.suit} for c in self.dealer_cards],
                'score': dealer_score
            },
            'player': {
                'hands': [[{'rank': c.rank, 'suit': c.suit} for c in hand] 
                         for hand in self.player_hands],
                'scores': player_scores,
                'currentHand': self.current_hand
            },
            'gameOver': self.game_over,
            'message': message,
            'won': won,
            'betAmount': self.bet_amount,
            'splitBetAmount': self.split_bet_amount,
            'insuranceBet': self.insurance_bet,
            'canInsure': self.can_offer_insurance(),
            'canHit': not self.game_over and current_hand_score < 21,
            'canStand': not self.game_over and current_hand_score <= 21,
            'canDouble': not self.game_over and len(self.player_hands[self.current_hand]) == 2,
            'canSplit': not self.game_over and self.can_split()
        }
    
    def serialize(self) -> dict:
        """Convert game state to a dictionary for session storage"""
        return {
            'deck': [{'rank': c.rank, 'suit': c.suit, 'value': c.value} for c in self.deck],
            'dealer_cards': [{'rank': c.rank, 'suit': c.suit, 'value': c.value} for c in self.dealer_cards],
            'player_hands': [[{'rank': c.rank, 'suit': c.suit, 'value': c.value} for c in hand] 
                           for hand in self.player_hands],
            'current_hand': self.current_hand,
            'bet_amount': self.bet_amount,
            'split_bet_amount': self.split_bet_amount,
            'insurance_bet': self.insurance_bet,
            'game_over': self.game_over
        }
    
    @classmethod
    def deserialize(cls, data: dict) -> 'BlackjackGame':
        """Create a game instance from serialized data"""
        game = cls()
        if data:
            game.deck = [Card(**card) for card in data['deck']]
            game.dealer_cards = [Card(**card) for card in data['dealer_cards']]
            game.player_hands = [[Card(**card) for card in hand] 
                               for hand in data['player_hands']]
            game.current_hand = data['current_hand']
            game.bet_amount = data['bet_amount']
            game.split_bet_amount = data['split_bet_amount']
            game.insurance_bet = data.get('insurance_bet', 0)
            game.game_over = data['game_over']
        return game

    def can_offer_insurance(self) -> bool:
        """Check if insurance can be offered (dealer's up card is Ace)"""
        return len(self.dealer_cards) == 2 and self.dealer_cards[0].rank == 'A'

    def take_insurance(self, amount: float):
        """Process insurance bet"""
        self.insurance_bet = amount
        # Check if dealer has blackjack immediately
        dealer_score = self.get_score(self.dealer_cards)
        if dealer_score == 21:
            return True  # Insurance bet wins
        return False  # Insurance bet loses

@app.route('/blackjack')
@login_required
def blackjack():
    return render_template('blackjack.html',
                         balance=session['user']['balance'],
                         RANKS=RANKS,
                         RANK_EXP=RANK_EXP)

@app.route('/play_blackjack', methods=['POST'])
@login_required
def play_blackjack():
    try:
        data = request.get_json()
        action = data.get('action')
        
        # Initialize game if not exists
        if 'blackjack_game' not in session:
            session['blackjack_game'] = None
        
        # Deserialize game from session
        game = BlackjackGame.deserialize(session.get('blackjack_game')) if session.get('blackjack_game') else None
        
        if not game and action != 'deal':
            return jsonify({'error': 'No game in progress'})
        
        if action == 'deal':
            bet_amount = round(float(data.get('amount', 0)), 2)  # Round to 2 decimal places
            current_balance = round(float(session['user']['balance']), 2)  # Round to 2 decimal places
            
            # Add debug logging
            print(f"Bet amount: {bet_amount}, Current balance: {current_balance}")
            
            if bet_amount <= 0:
                return jsonify({'error': 'Bet amount must be greater than 0'})
            if bet_amount > current_balance:
                return jsonify({'error': f'Insufficient funds (bet: ${bet_amount:.2f}, balance: ${current_balance:.2f})'})
            
            # Create new game
            game = BlackjackGame()
            game.deal(bet_amount)
            
            # Store initial bet
            session['user']['balance'] = round(current_balance - bet_amount, 2)  # Round result
            session.modified = True
            
        elif action == 'split':
            if not game:
                return jsonify({'error': 'No game in progress'})
            
            # Check if player can afford split
            current_balance = float(session['user']['balance'])
            if game.bet_amount > current_balance:
                return jsonify({'error': 'Insufficient funds to split'})
            
            # Deduct split bet amount
            session['user']['balance'] = current_balance - game.bet_amount
            game.split()
            
        elif action == 'hit':
            if not game:
                return jsonify({'error': 'No game in progress'})
            game.hit()
            
        elif action == 'stand':
            if not game:
                return jsonify({'error': 'No game in progress'})
            game.stand()
            
        elif action == 'double':
            # Check if player can afford double down
            current_balance = float(session['user']['balance'])
            if game.bet_amount > current_balance:
                # Return current game state along with error
                state = game.get_game_state()
                state['error'] = 'Insufficient funds to double down'
                return jsonify(state)
            
            # Deduct additional bet amount
            session['user']['balance'] = current_balance - game.bet_amount
            game.double_down()
        
        # Get game state
        state = game.get_game_state()
        
        # Update balance if game is over
        if state['gameOver']:
            current_balance = float(session['user']['balance'])
            total_won = 0
            
            for i, won in enumerate(state['won']):
                bet = game.bet_amount if i == 0 else game.split_bet_amount
                if won == 'blackjack':
                    total_won += bet * 2.5  # 3:2 payout for blackjack
                elif won is True:
                    total_won += bet * 2
                elif won is None:  # Push
                    total_won += bet
            
            session['user']['balance'] = current_balance + total_won
            
            # Clear game
            session['blackjack_game'] = None
        else:
            # Store serialized game state in session
            session['blackjack_game'] = game.serialize()
        
        # Add balance to response
        state['balance'] = session['user']['balance']
        
        return jsonify(state)
        
    except Exception as e:
        print(f"Error in play_blackjack: {e}")
        if game:
            # If we have a game state, return it along with the error
            state = game.get_game_state()
            state['error'] = 'Failed to process game action'
            return jsonify(state)
        return jsonify({'error': 'Failed to process game action'})

@app.route('/crash')
@login_required
def crash():
    return render_template('crash.html',
                         balance=session['user']['balance'],
                         RANKS=RANKS,
                         RANK_EXP=RANK_EXP)

@app.route('/play_crash', methods=['POST'])
@login_required
def play_crash():
    try:
        data = request.get_json()
        bet_amount = float(data.get('amount', 0))
        auto_cashout = data.get('auto_cashout')
        if auto_cashout is not None:
            auto_cashout = float(auto_cashout)
        
        if bet_amount <= 0:
            return jsonify({'error': 'Invalid bet amount'})
        
        user = create_user_from_dict(session['user'])
        
        if bet_amount > user.balance:
            return jsonify({'error': 'Insufficient funds'})
        
        # Deduct bet amount immediately
        user.balance -= bet_amount
        
        # Store the bet amount in session
        session['crash_bet'] = bet_amount
        
        # Update session with new balance
        session['user'] = {
            'balance': user.balance,
            'inventory': user.inventory,
            'exp': user.exp,
            'rank': user.rank,
            'upgrades': asdict(user.upgrades)
        }
        
        # Return the new balance so we can update the UI
        return jsonify({
            'success': True,
            'balance': user.balance
        })
        
    except Exception as e:
        print(f"Error in play_crash: {e}")
        return jsonify({'error': 'Failed to place bet'})

@app.route('/crash_cashout', methods=['POST'])
@login_required
def crash_cashout():
    try:
        data = request.get_json()
        multiplier = float(data.get('multiplier', 1))
        
        # Get the current bet amount from session
        current_game_bet = session.get('crash_bet')
        
        if current_game_bet is None:  # Changed condition
            return jsonify({'error': 'No active bet found'})
        
        # Calculate winnings
        winnings = current_game_bet * multiplier
        
        # Update user balance
        user = create_user_from_dict(session['user'])
        user.balance += winnings
        
        # Update session
        session['user'] = {
            'balance': user.balance,
            'inventory': user.inventory,
            'exp': user.exp,
            'rank': user.rank,
            'upgrades': asdict(user.upgrades)
        }
        session['crash_bet'] = None  # Changed to None instead of 0
        
        return jsonify({
            'success': True,
            'balance': user.balance
        })
        
    except Exception as e:
        print(f"Error in crash_cashout: {e}")
        return jsonify({'error': 'Failed to process cashout'})

@app.route('/crash_end', methods=['POST'])
@login_required
def crash_end():
    try:
        data = request.get_json()
        crashed = data.get('crashed', False)
        
        if crashed:
            # Reset current bet
            session['crash_bet'] = None  # Changed to None instead of 0
        
        return jsonify({'success': True})
        
    except Exception as e:
        print(f"Error in crash_end: {e}")
        return jsonify({'error': 'Failed to process game end'})

@app.route('/take_insurance', methods=['POST'])
@login_required
def take_insurance():
    try:
        data = request.get_json()
        insurance_amount = float(data.get('amount', 0))
        
        # Get current game
        game = BlackjackGame.deserialize(session.get('blackjack_game'))
        if not game:
            return jsonify({'error': 'No game in progress'})
            
        # Validate insurance amount (should be half the original bet)
        max_insurance = game.bet_amount / 2
        if insurance_amount > max_insurance:
            return jsonify({'error': f'Maximum insurance bet is ${max_insurance:.2f}'})
            
        # Check if player can afford insurance
        current_balance = float(session['user']['balance'])
        if insurance_amount > current_balance:
            return jsonify({'error': 'Insufficient funds for insurance'})
            
        # Process insurance bet
        insurance_wins = game.take_insurance(insurance_amount)
        
        # Update player's balance
        if insurance_wins:
            # Insurance pays 2:1
            session['user']['balance'] = current_balance + insurance_amount * 2
        else:
            session['user']['balance'] = current_balance - insurance_amount
            
        # Store updated game state
        session['blackjack_game'] = game.serialize()
        
        # Get full game state
        state = game.get_game_state()
        state['balance'] = session['user']['balance']
        state['insuranceResult'] = insurance_wins
        
        return jsonify(state)
        
    except Exception as e:
        print(f"Error in take_insurance: {e}")
        return jsonify({'error': 'Failed to process insurance bet'})

@app.route('/sell/all', methods=['POST'])
@login_required
def sell_all():
    try:
        inventory = session['user'].get('inventory', [])
        
        # Calculate total value of all skins
        total_value = 0
        new_inventory = []
        
        for item in inventory:
            if item.get('is_case'):
                new_inventory.append(item)
            else:
                total_value += float(item.get('price', 0))
        
        # Update user's balance and inventory
        session['user']['balance'] = float(session['user']['balance']) + total_value
        session['user']['inventory'] = new_inventory
        
        # Ensure the session is marked as modified
        session.modified = True
        
        return jsonify({
            'success': True,
            'balance': session['user']['balance'],
            'sold_value': total_value
        })
        
    except Exception as e:
        print(f"Error in sell_all: {e}")
        return jsonify({'error': 'Failed to sell all items'})

@app.route('/jackpot')
@login_required
def jackpot():
    return render_template('jackpot.html',
                         balance=session['user']['balance'],
                         RANKS=RANKS,
                         RANK_EXP=RANK_EXP)

@app.route('/get_jackpot_inventory')
@login_required
def get_jackpot_inventory():
    try:
        inventory = session['user'].get('inventory', [])
        
        # Filter for eligible items (non-case items worth $0-30)
        eligible_items = [
            item for item in inventory
            if not item.get('is_case') and 0 <= float(item.get('price', 0)) <= 30
        ]
        
        return jsonify({
            'inventory': eligible_items
        })
        
    except Exception as e:
        print(f"Error getting jackpot inventory: {e}")
        return jsonify({'error': 'Failed to get inventory'})

@app.route('/start_jackpot', methods=['POST'])
def start_jackpot():
    try:
        data = request.get_json()
        print("Received data:", data)
        
        user_items = data.get('items', [])
        
        # Validate and sum user items with detailed logging
        user_value = 0
        print("\nCalculating user value:")
        for item in user_items:
            item_price = float(item['price'])
            user_value += item_price
            print(f"Added item: {item['weapon']} | {item['name']} (${item_price:.2f})")
        print(f"Total user value: ${user_value:.2f}")
        
        if not user_items:
            return jsonify({'error': 'No items selected'})
            
        # Validate user items
        inventory = session['user'].get('inventory', [])
        
        # Create a copy of inventory to remove items as we find them
        remaining_inventory = inventory.copy()
        found_items = []  # Keep track of found items
        
        # For each selected item
        for selected_item in user_items:
            item_found = False
            
            # Look through remaining inventory
            for i, inv_item in enumerate(remaining_inventory):
                if (inv_item.get('weapon') == selected_item['weapon'] and 
                    inv_item.get('name') == selected_item['name'] and
                    inv_item.get('wear') == selected_item['wear'] and
                    inv_item.get('stattrak') == selected_item['stattrak'] and
                    i not in found_items):  # Make sure we haven't used this item already
                    item_found = True
                    found_items.append(i)  # Mark this item as used
                    break
            
            if not item_found:
                return jsonify({'error': f'Item not found in inventory or already selected: {selected_item["weapon"]} | {selected_item["name"]}'})
        
        # Remove the selected items from inventory
        new_inventory = [item for i, item in enumerate(inventory) if i not in found_items]
        session['user']['inventory'] = new_inventory
        session.modified = True
        
        # Generate bot players
        print("\nGenerating bot players...")
        num_bots = random.randint(1, 10)
        bot_players = generate_bot_players(num_bots)
        
        # Calculate total bot value with detailed logging
        bot_total = 0
        print("\nCalculating bot values:")
        for bot in bot_players:
            bot_value = sum(float(item['price']) for item in bot['items'])
            bot_total += bot_value
            print(f"{bot['name']}: ${bot_value:.2f}")
        print(f"Total bot value: ${bot_total:.2f}")
        
        # Calculate final total
        total_value = user_value + bot_total
        print(f"\nFinal totals:")
        print(f"User value: ${user_value:.2f}")
        print(f"Bot value: ${bot_total:.2f}")
        print(f"Total pot: ${total_value:.2f}")
        
        # Prepare players list
        players = [
            {
                'name': 'You',
                'items': user_items,
                'value': round(user_value, 2),
                'winChance': round((user_value / total_value * 100), 2) if total_value > 0 else 0
            }
        ]
        
        # Add bot players
        for bot in bot_players:
            bot_value = sum(float(item['price']) for item in bot['items'])
            players.append({
                'name': bot['name'],
                'items': bot['items'],
                'value': round(bot_value, 2),
                'winChance': round((bot_value / total_value * 100), 2) if total_value > 0 else 0
            })
        
        # Verify total percentages add up to 100%
        total_percentage = sum(player['winChance'] for player in players)
        print(f"\nTotal win percentage: {total_percentage}%")
        
        # Determine winner
        winner = random.choices(
            players,
            weights=[float(player['value']) for player in players],
            k=1
        )[0]
        
        # If user won, add all other players' items to their inventory
        if winner['name'] == 'You':
            # Get current inventory (which has the user's wagered items removed)
            current_inventory = session['user'].get('inventory', [])
            
            # Add back the user's wagered items since they won
            current_inventory.extend(user_items)
            
            # Add items from all other players
            for player in players:
                if player['name'] != 'You':
                    # Add to user's inventory
                    current_inventory.extend(player['items'])
            
            # Update session with new inventory
            session['user']['inventory'] = current_inventory
            session.modified = True
            
            # Add won items to winner data for display
            winner['items'] = user_items + [item for player in players 
                                          if player['name'] != 'You' 
                                          for item in player['items']]
            
            print(f"Added back {len(user_items)} user items and {len(winner['items']) - len(user_items)} won items")
        
        return jsonify({
            'players': players,
            'totalPotValue': total_value,
            'winChance': (user_value / total_value * 100) if total_value > 0 else 0,
            'winner': {
                'name': winner['name'],
                'items': winner['items'],
                'totalValue': total_value,
                'isUser': winner['name'] == 'You'
            }
        })
        
    except Exception as e:
        print(f"Error in start_jackpot: {str(e)}")
        print(f"Error traceback: {traceback.format_exc()}")
        return jsonify({'error': 'Failed to start game'})

def generate_bot_players(num_bots: int) -> List[Dict[str, Any]]:
    bot_names = [
        "skibidi toilet", "ohio rizz", "sigma grindset", "gyatt enthusiast", 
        "backrooms entity", "no cap fr fr", "megamind rizz", "skill issue", 
        "brainrot gaming", "based department", "gigachad", "npc moment",
        "ratio + L", "sheeeesh", "sus imposter", "copium addict",
        "peak fiction", "rizz master", "skull emoji", "real and true"
    ]
    
    # Load all case data
    case_types = ['csgo', 'esports', 'bravo', 'csgo2', 'esports_winter', 'winter_offensive']
    all_skins = []
    
    case_file_mapping = {
        'csgo': 'weapon_case_1',
        'esports': 'esports_2013',
        'bravo': 'operation_bravo_case',
        'csgo2': 'weapon_case_2',
        'esports_winter': 'esports_2013_winter',
        'winter_offensive': 'winter_offensive_case'
    }
    
    # Load skins directly from case files instead of using Case object
    for case_type in case_types:
        try:
            with open(f'cases/{case_file_mapping[case_type]}.json', 'r') as f:
                case_data = json.load(f)
                
                # Process each rarity grade
                for grade, items in case_data['skins'].items():
                    rarity = grade.upper()  # Convert grade to rarity name
                    for item in items:
                        # Add skin with its case type and prices
                        all_skins.append({
                            'weapon': item['weapon'],
                            'name': item['name'],
                            'rarity': rarity,
                            'case_type': case_type,
                            'prices': item['prices']
                        })
        except Exception as e:
            print(f"Error loading case {case_type}: {e}")
            continue
    
    print(f"Loaded {len(all_skins)} potential skins for bots")  # Debug log
    
    bots = []
    used_names = set()
    
    for _ in range(num_bots):
        # Select random unique bot name
        available_names = [name for name in bot_names if name not in used_names]
        if not available_names:
            break
        bot_name = random.choice(available_names)
        used_names.add(bot_name)
        
        # Generate 1-10 items for the bot
        num_items = random.randint(1, 10)
        bot_items = []
        attempts = 0
        max_attempts = 100  # Prevent infinite loops
        
        while len(bot_items) < num_items and attempts < max_attempts:
            attempts += 1
            if not all_skins:  # Safety check
                break
                
            skin = random.choice(all_skins)
            
            # Randomly decide wear and StatTrak
            wear_options = [w for w in skin['prices'].keys() 
                          if not w.startswith('ST_') and w != 'NO']
            if not wear_options:
                continue
                
            wear = random.choice(wear_options)
            stattrak = random.random() < 0.1  # 10% chance for StatTrak
            
            # Get price
            price_key = f"ST_{wear}" if stattrak else wear
            try:
                price = float(skin['prices'].get(price_key, 0))
            except (ValueError, TypeError):
                continue
            
            # Only add if price is within range (0-30)
            if 0 < price <= 30:
                bot_items.append({
                    'weapon': skin['weapon'],
                    'name': skin['name'],
                    'wear': wear,
                    'rarity': skin['rarity'],
                    'stattrak': stattrak,
                    'price': price,
                    'case_type': skin['case_type']
                })
        
        if bot_items:  # Only add bot if they have items
            bots.append({
                'name': bot_name,
                'items': bot_items
            })
            print(f"Added bot {bot_name} with {len(bot_items)} items")  # Debug log
    
    return bots

if __name__ == '__main__':
    app.run(debug=True)
