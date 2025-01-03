from flask import Flask, render_template, jsonify, session, redirect, url_for, request, send_from_directory
from dataclasses import asdict
import random
from typing import Dict, Union, List, Any
import time
import json
from functools import wraps
from datetime import timedelta, date, datetime
from dataclasses import dataclass
from typing import List, Optional
import traceback
import os
from enum import Enum
import threading
from openai import OpenAI
from dotenv import load_dotenv

from config import Rarity, RED_NUMBERS, BLACK_NUMBERS, RANK_EXP, RANKS, CASE_FILE_MAPPING
from models import Case, User, Upgrades

# Load environment variables
load_dotenv('config.env')

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = timedelta(days=7)  # Cache static files for 7 days to reduce server load

FEATURED_SKINS = None
LAST_REFRESH_TIME = None
REFRESH_INTERVAL = 3600  # 1 hour in seconds

# Add this at the top with other globals
file_lock = threading.Lock()

# Initialize OpenAI client with API key from environment
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

BOT_PERSONALITIES = {
    "_Astrid47": "A friendly and professional trader who specializes in high-tier skins. Very knowledgeable about skin patterns and float values.",
    "Kai.Jayden_02": "A forsen viewer who spams KEKW and PepeLaugh, uses lots of Twitch emotes and speaks in Twitch chat style",
    "Orion_Phoenix98": "An experienced collector focused on rare items and special patterns. Somewhat reserved but very helpful.",
    "ElaraB_23": "A casual trader who enjoys discussing both trading and the game itself. Often shares tips about trading strategies.",
    "Theo.91": "Another forsen viewer who spams OMEGALUL and Pepega, speaks in broken English and uses lots of BATCHEST",
    "Nova-Lyn": "A competitive player who trades on the side. Often discusses pro matches and how they affect skin prices.",
    "FelixHaven19": "A mathematical trader who loves discussing probabilities and market statistics.",
    "Aria.Stella85": "A collector of StatTrak weapons who specializes in tracking kill counts and rare StatTrak items.",
    "Lucien_Kai": "A knife expert who knows everything about patterns, especially for Doppler and Case Hardened skins.",
    "Mira-Eclipse": "A sticker specialist who focuses on craft suggestions and sticker combinations."
}

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            user_data = load_user_data()
            session['user'] = user_data
        return f(*args, **kwargs)
    return decorated_function

@app.context_processor
def inject_ranks():
    return {'RANKS': RANKS}

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

# Update the case prices to load from JSON files
def get_case_price(case_type: str) -> float:
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

# Replace hardcoded CASE_PRICES with dynamic loading
def get_case_prices() -> Dict[str, float]:
    return {case_type: get_case_price(case_type) for case_type in CASE_FILE_MAPPING.keys()}

def create_user_from_dict(data: dict) -> User:
    upgrades_data = data.get('upgrades', {})
    upgrades = Upgrades(
        click_value=upgrades_data.get('click_value', 1),
        max_multiplier=upgrades_data.get('max_multiplier', 1),
        auto_clicker=upgrades_data.get('auto_clicker', 0),
        combo_speed=upgrades_data.get('combo_speed', 1),
        critical_strike=upgrades_data.get('critical_strike', 0),
        progress_per_click=upgrades_data.get('progress_per_click', 1),
        case_quality=upgrades_data.get('case_quality', 1),
        multi_open=upgrades_data.get('multi_open', 1)  # Add this line
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

def load_user_data() -> dict:
    """Load user data from JSON file with file locking."""
    # Define complete default data structure
    default_data = {
        'balance': 1000.0,
        'inventory': [],
        'exp': 0,
        'rank': 0,
        'upgrades': {
            'click_value': 1,
            'max_multiplier': 1,
            'auto_clicker': 0,
            'combo_speed': 1,
            'critical_strike': 0,
            'progress_per_click': 1,
            'case_quality': 1,
            'multi_open': 1
        },
        'achievements': {
            'completed': [],
            'in_progress': {}
        },
        'stats': {
            'total_earnings': 0,
            'total_cases_opened': 0,
            'total_trades_completed': 0,
            'highest_win_streak': 0,
            'total_clicks': 0,
            'highest_value_item': 0,
            'total_upgrades': 0,
            'total_jackpots_won': 0
        },
        'case_progress': 0
    }
    
    file_path = 'data/user_inventory.json'
    backup_path = file_path + '.bak'
    
    # Use a timeout to prevent deadlocks
    lock_acquired = file_lock.acquire(timeout=5)
    if not lock_acquired:
        print("Warning: Could not acquire file lock, returning default data")
        return default_data.copy()
        
    try:
        # If file doesn't exist, create it with default data
        if not os.path.exists(file_path):
            # Create data directory if it doesn't exist
            os.makedirs('data', exist_ok=True)
            
            # Initialize the first achievement
            temp_data = default_data.copy()
            update_earnings_achievements(temp_data, 0)
            update_case_achievements(temp_data)
            update_click_achievements(temp_data)  # Add this line
            
            # Save the initialized data
            with open(file_path, 'w') as f:
                json.dump(temp_data, f, indent=2)
            return temp_data
            
        # Create backup of current file
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                current_data = f.read()
            with open(backup_path, 'w') as f:
                f.write(current_data)
        
        # Try to load the file
        with open(file_path, 'r') as f:
            data = json.load(f)
            
        if not isinstance(data, dict):
            raise ValueError("Invalid data structure")
            
        # Deep copy the default data to ensure we don't modify it
        result = default_data.copy()
        
        # Update with existing data
        result.update(data)
        
        # Ensure all required structures exist
        if 'achievements' not in result:
            result['achievements'] = default_data['achievements'].copy()
            update_earnings_achievements(result, 0)
            update_case_achievements(result)
            update_click_achievements(result)  # Add this line
            
        if 'stats' not in result:
            result['stats'] = default_data['stats'].copy()
            
        if 'upgrades' not in result:
            result['upgrades'] = default_data['upgrades'].copy()
        else:
            for key, value in default_data['upgrades'].items():
                if key not in result['upgrades']:
                    result['upgrades'][key] = value
        
        # Save any updates
        with open(file_path, 'w') as f:
            json.dump(result, f, indent=2)
        
        return result
            
    except Exception as e:
        print(f"Error loading user data: {e}")
        try:
            if os.path.exists(backup_path):
                with open(backup_path, 'r') as f:
                    data = json.load(f)
                with open(file_path, 'w') as f:
                    json.dump(data, f, indent=2)
                return data
        except:
            pass
        
        return default_data.copy()
    finally:
        file_lock.release()

def save_user_data(user_data: dict):
    """Save user data to JSON file with file locking."""
    temp_file = 'data/user_inventory.tmp'
    final_file = 'data/user_inventory.json'
    backup_file = final_file + '.bak'
    
    # Use a timeout to prevent deadlocks
    lock_acquired = file_lock.acquire(timeout=5)  # 5 second timeout
    if not lock_acquired:
        print("Warning: Could not acquire file lock, skipping save")
        return
        
    try:
        # Create data directory if it doesn't exist
        os.makedirs('data', exist_ok=True)
        
        # Create backup of current file if it exists
        try:
            if os.path.exists(final_file):
                with open(final_file, 'r') as src, open(backup_file, 'w') as dst:
                    dst.write(src.read())
        except Exception as e:
            print(f"Warning: Failed to create backup: {e}")
        
        # Write to temporary file
        with open(temp_file, 'w') as f:
            json.dump(user_data, f, indent=2)
            f.flush()
            try:
                os.fsync(f.fileno())
            except Exception as e:
                print(f"Warning: Failed to fsync: {e}")
        
        # Close any open handles to the files
        try:
            import gc
            gc.collect()  # Force garbage collection
        except Exception as e:
            print(f"Warning: Failed to force garbage collection: {e}")
        
        # Small delay to ensure file handles are released
        time.sleep(0.1)
        
        try:
            if os.path.exists(final_file):
                os.remove(final_file)
            os.rename(temp_file, final_file)
                
        except Exception as e:
            print(f"Error during file replacement: {e}")
            if os.path.exists(backup_file):
                try:
                    if os.path.exists(final_file):
                        os.remove(final_file)
                    os.rename(backup_file, final_file)
                except Exception as restore_error:
                    print(f"Failed to restore from backup: {restore_error}")
            raise
            
    except Exception as e:
        print(f"Error saving user data: {e}")
        if not os.path.exists(final_file) and os.path.exists(backup_file):
            try:
                os.rename(backup_file, final_file)
            except Exception as restore_error:
                print(f"Failed to restore from backup: {restore_error}")
    finally:
        # Clean up temporary files
        try:
            if os.path.exists(temp_file):
                os.remove(temp_file)
        except Exception as e:
            print(f"Warning: Failed to remove temporary file: {e}")
        
        # Always release the lock
        file_lock.release()

@app.route('/', methods=['GET', 'POST'])
def index():
    user_data = load_user_data()
    return render_template('home.html',
                           balance=user_data['balance'],
                           rank=user_data['rank'],
                           exp=user_data['exp'],
                           RANKS=RANKS,
                           RANK_EXP=RANK_EXP)

@app.route('/shop')
@login_required
def shop():
    cases = load_case('all')  # Get all case data for shop display
    user_data = load_user_data()
    user = create_user_from_dict(user_data)
    return render_template('shop.html',
                           cases=cases,
                           balance=user.balance,
                           rank=user.rank,
                           exp=user.exp,
                           RANKS=RANKS,
                           RANK_EXP=RANK_EXP)

@app.route('/inventory')
def inventory():
    user_data = load_user_data()
    inventory_items = user_data.get('inventory', [])
    
    # Create a dictionary to store already loaded prices to avoid duplicate lookups
    price_cache = {}
    
    # Update prices for all non-case items
    for item in inventory_items:
        if not item.get('is_case'):
            # Create a cache key using weapon, name, wear, and case type
            cache_key = (
                item['weapon'],
                item['name'],
                item.get('wear'),
                item['case_type']
            )
            
            # Check if we already loaded this price
            if cache_key in price_cache:
                item['price'] = price_cache[cache_key]
            else:
                # Load price and cache it
                price = load_skin_price(
                    f"{item['weapon']} | {item['name']}", 
                    item['case_type'],
                    item.get('wear')
                )
                price_cache[cache_key] = price
                item['price'] = price
    
    # Sort items so newest appears first
    inventory_items = sorted(inventory_items, 
                           key=lambda x: x.get('timestamp', 0) if not x.get('is_case') else 0, 
                           reverse=True)
    
    return render_template('inventory.html', 
                         balance=user_data['balance'], 
                         inventory=inventory_items,
                         rank=user_data['rank'],
                         exp=user_data['exp'],
                         RANK_EXP=RANK_EXP,
                         RANKS=RANKS,
                         upgrades=user_data.get('upgrades', {}),  # Add this line
                         initial_view=request.args.get('view', 'skins'))

@app.route('/open/<case_type>')
def open_case(case_type):
    count = int(request.args.get('count', 1))
    user_data = load_user_data()
    
    # Check multi_open upgrade level
    multi_open_level = user_data.get('upgrades', {}).get('multi_open', 1)
    if count > multi_open_level:
        return jsonify({'error': f'You can only open up to {multi_open_level} cases at once. Upgrade Multi Open to open more!'})
    
    if count not in [1, 2, 3, 4, 5]:
        return jsonify({'error': 'Invalid case count'})
        
    inventory = user_data.get('inventory', [])
    current_exp = user_data.get('exp', 0)
    current_rank = user_data.get('rank', 0)
    new_exp = current_exp  # Initialize with current exp
    
    # Find the case in inventory
    case_found = False
    for i in range(len(inventory)):
        item = inventory[i]
        if item.get('is_case') and item.get('type') == case_type:
            quantity = item.get('quantity', 0)
            if quantity >= count:
                case_found = True
                # Decrease case quantity
                inventory[i]['quantity'] = quantity - count
                if inventory[i]['quantity'] <= 0:
                    inventory.pop(i)
                break
    
    if not case_found:
        return jsonify({'error': f'Not enough cases ({count} needed)'})
    
    # Load the appropriate case
    case = load_case(case_type)
    if not case:
        return jsonify({'error': 'Invalid case type'})

    # Get case price and add exp
    try:
        file_name = CASE_FILE_MAPPING.get(case_type)
        if not file_name:
            return jsonify({'error': 'Invalid case type'})
            
        with open(f'cases/{file_name}.json', 'r') as f:
            case_data = json.load(f)
            case_price = float(case_data.get('price', 0))
            
            # Add exp based on case price (for all cases opened)
            new_exp = current_exp + (case_price * count)
            
            # Check for rank up
            while current_rank < len(RANK_EXP) and new_exp >= RANK_EXP[current_rank]:
                new_exp -= RANK_EXP[current_rank]
                current_rank += 1
            
            # Update user data with new exp and rank
            user_data['exp'] = new_exp
            user_data['rank'] = current_rank
            
    except Exception as e:
        print(f"Error getting case price: {e}")
        new_exp = current_exp
        current_rank = user_data.get('rank', 0)
    
    # Open cases and get items
    items = []
    for _ in range(count):
        skin = case.open()
        if not skin:
            return jsonify({'error': 'Failed to open case'})
        
        # Get the price from case data
        try:
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
            'price': float(price),
            'timestamp': time.time(),
            'case_type': case_type,
            'is_case': False
        }
        items.append(skin_dict)
        
        # Add the skin to inventory
        inventory.append(skin_dict)
    
    # Update user data
    user_data['inventory'] = inventory
    save_user_data(user_data)
    
    # Store initial achievements state
    initial_achievements = set(user_data['achievements']['completed'])
    
    # Update total cases opened stat
    user_data['stats']['total_cases_opened'] += count
    
    # Update case achievements
    update_case_achievements(user_data)
    
    # Check if any new achievements were completed
    new_achievements = set(user_data['achievements']['completed']) - initial_achievements
    completed_achievement = None
    if new_achievements:
        achievement_id = list(new_achievements)[0]  # Get the first new achievement
        level = int(achievement_id.split('_')[1])
        completed_achievement = {
            'title': {
                1: 'Case Opener',
                2: 'Case Enthusiast',
                3: 'Case Veteran',
                4: 'Case Master',
                5: 'Case God'
            }[level],
            'icon': '📦',
            'reward': {
                1: 100,
                2: 500,
                3: 1000,
                4: 2000,
                5: 5000
            }[level],
            'exp_reward': 0,
            'description': f'Open {"{:,.0f}".format({1: 10, 2: 100, 3: 1000, 4: 10000, 5: 100000}[level])} cases'
        }
    
    # Save updated user data
    save_user_data(user_data)
    
    return jsonify({
        'items': items,
        'balance': user_data['balance'],
        'exp': new_exp,
        'rank': current_rank,
        'rankName': RANKS[current_rank],
        'nextRankExp': RANK_EXP[current_rank] if current_rank < len(RANK_EXP) else None,
        'achievement': completed_achievement,
        'upgrades': user_data.get('upgrades', {})
    })

@app.route('/reset_session')
def reset_session():
    user_data = {
        'balance': 1000.0,
        'inventory': [],
        'exp': 0,
        'rank': 0,
        'upgrades': {
            'click_value': 1,
            'max_multiplier': 1,
            'auto_clicker': 0,
            'combo_speed': 1,
            'critical_strike': 0,
            'progress_per_click': 1,
            'case_quality': 1,
            'multi_open': 1
        },
        'achievements': {
            'completed': [],
            'in_progress': {}
        },
        'stats': {
            'total_earnings': 0,
            'total_cases_opened': 0,
            'total_trades_completed': 0,
            'highest_win_streak': 0,
            'total_clicks': 0,
            'highest_value_item': 0,
            'total_upgrades': 0,
            'total_jackpots_won': 0
        },
        'case_progress': 0
    }
    
    # Initialize all achievement types
    update_earnings_achievements(user_data, 0)
    update_case_achievements(user_data)
    update_click_achievements(user_data)  # Add this line
    
    save_user_data(user_data)
    return redirect(url_for('shop'))

@app.route('/sell/<int:item_index>', methods=['POST'])
def sell_item(item_index=None):
    try:
        data = request.get_json() or {}
        quantity = int(data.get('quantity', 1))
        
        user_data = load_user_data()
        inventory = user_data['inventory']
        
        # Get only non-case items
        skin_items = [item for item in inventory if not item.get('is_case')]
        grouped_skins = group_identical_skins(skin_items)
        
        if item_index is None or item_index >= len(grouped_skins):
            return jsonify({'error': 'Item not found'})
        
        item_to_sell = grouped_skins[item_index]
        if quantity > item_to_sell.get('count', 1):
            return jsonify({'error': 'Invalid quantity'})
        
        # Calculate sale value
        sale_price = float(item_to_sell.get('price', 0)) * quantity
        
        # Store initial rank for level up check
        initial_rank = user_data.get('rank', 0)
        
        # Remove the items from inventory
        remaining_inventory = []
        items_to_remove = quantity
        
        for item in inventory:
            if not item.get('is_case'):
                if (items_to_remove > 0 and
                    item['weapon'] == item_to_sell['weapon'] and
                    item['name'] == item_to_sell['name'] and
                    item['wear'] == item_to_sell['wear'] and
                    item['stattrak'] == item_to_sell['stattrak']):
                    items_to_remove -= 1
                    continue
            remaining_inventory.append(item)
        
        # Update user's balance and inventory
        user_data['balance'] = float(user_data['balance']) + sale_price
        user_data['inventory'] = remaining_inventory
        
        # Store initial achievements state
        initial_achievements = set(user_data['achievements']['completed'])
        
        # Update achievements with the earned amount
        update_earnings_achievements(user_data, sale_price)
        
        # Check if any new achievements were completed
        new_achievements = set(user_data['achievements']['completed']) - initial_achievements
        completed_achievement = None
        if new_achievements:
            achievement_id = list(new_achievements)[0]  # Get the first new achievement
            level = int(achievement_id.split('_')[1])
            completed_achievement = {
                'title': {
                    1: 'Starting Out',
                    2: 'Making Moves',
                    3: 'Known Mogul',
                    4: 'Expert Trader',
                    5: 'Millionaire'
                }[level],
                'icon': {
                    1: '💵',
                    2: '💰',
                    3: '🏦',
                    4: '💎',
                    5: '🏆'
                }[level],
                'reward': {
                    1: 100,
                    2: 1000,
                    3: 5000,
                    4: 10000,
                    5: 100000
                }[level],
                'exp_reward': {
                    1: 1000,
                    2: 5000,
                    3: 10000,
                    4: 20000,
                    5: 50000
                }[level]
            }
        
        # Save updated user data
        save_user_data(user_data)
        
        # Return data in the same format as achievement completion
        return jsonify({
            'success': True,
            'balance': user_data['balance'],
            'exp': user_data['exp'],
            'rank': user_data['rank'],
            'rankName': RANKS[user_data['rank']],
            'nextRankExp': RANK_EXP[user_data['rank']] if user_data['rank'] < len(RANK_EXP) else None,
            'levelUp': user_data['rank'] > initial_rank,
            'sold_price': sale_price,
            'achievement': completed_achievement
        })
        
    except Exception as e:
        print(f"Error in sell_item: {e}")
        return jsonify({'error': 'Failed to sell item'})

@app.route('/sell/last', methods=['POST'])
def sell_last_item():
    user_data = load_user_data()
    try:
        data = request.get_json() or {}
        count = int(data.get('count', 1))  # Get number of items to sell
        inventory = user_data['inventory']
        
        # Get only non-case items
        skin_items = [item for item in inventory if not item.get('is_case')]
        
        if not skin_items:
            return jsonify({'error': 'No items to sell'})
        
        # Sort items by timestamp in descending order
        sorted_indices = sorted(
            range(len(inventory)),
            key=lambda i: inventory[i].get('timestamp', 0) if not inventory[i].get('is_case') else 0,
            reverse=True
        )
        
        # Get the most recent 'count' items
        items_to_sell = []
        total_price = 0
        indices_to_remove = []
        
        for idx in sorted_indices[:count]:
            item = inventory[idx]
            if not item.get('is_case'):
                if 'price' not in item:
                    continue
                total_price += float(item.get('price', 0))
                items_to_sell.append(item)
                indices_to_remove.append(idx)
                
                if len(items_to_sell) >= count:
                    break
        
        if not items_to_sell:
            return jsonify({'error': 'No valid items to sell'})
            
        # Remove items in reverse order to maintain correct indices
        for idx in sorted(indices_to_remove, reverse=True):
            inventory.pop(idx)
        
        # Update user's balance
        user_data['balance'] = float(user_data['balance']) + total_price
        
        # Update achievements with the total earned amount
        update_earnings_achievements(user_data, total_price)
        
        # Save updated user data
        save_user_data(user_data)
        
        # Log the successful sale
        print(f"Successfully sold {len(items_to_sell)} items for ${total_price}")
        
        return jsonify({
            'success': True,
            'balance': user_data['balance'],
            'sold_price': total_price
        })
        
    except Exception as e:
        print(f"Error in sell_last_item: {e}")
        return jsonify({
            'error': 'Failed to sell items',
            'details': str(e)
        })

@app.route('/click', methods=['POST'])
@login_required
def click():
    try:
        data = request.get_json()
        current_multiplier = data.get('multiplier', 1)
        is_crit = data.get('is_crit', False)
        
        user_data = load_user_data()
        
        # Store initial achievements state
        initial_achievements = set(user_data['achievements']['completed'])
        initial_rank = user_data.get('rank', 0)
        
        # Update total clicks stat (only for manual clicks)
        user_data['stats']['total_clicks'] += 1
        
        # Update click achievements
        update_click_achievements(user_data)
        
        # Calculate click value
        # Base value starts at 0.01 at level 1 and increases by 50% per level
        base_value = 0.01 * (1.5 ** (user_data['upgrades']['click_value'] - 1))
        click_value = base_value * current_multiplier
        
        if is_crit:
            click_value *= 4  # Critical hits do 4x damage
        
        user_data['balance'] += click_value
        
        # Check if any new achievements were completed
        new_achievements = set(user_data['achievements']['completed']) - initial_achievements
        completed_achievement = None
        if new_achievements:
            achievement_id = list(new_achievements)[0]
            level = int(achievement_id.split('_')[1])
            completed_achievement = {
                'title': {
                    1: 'Dedicated Clicker',
                    2: 'Click Enthusiast',
                    3: 'Click Master',
                    4: 'Click Expert',
                    5: 'Click God'
                }[level],
                'icon': '🖱️',
                'reward': {
                    1: 100,
                    2: 200,
                    3: 400,
                    4: 800,
                    5: 2000
                }[level],
                'exp_reward': {
                    1: 50,
                    2: 100,
                    3: 200,
                    4: 400,
                    5: 1000
                }[level]
            }
        
        save_user_data(user_data)
        
        return jsonify({
            'success': True,
            'balance': user_data['balance'],
            'click_value': click_value,
            'achievement': completed_achievement,
            'exp': user_data['exp'],
            'rank': user_data['rank'],
            'rankName': RANKS[user_data['rank']],
            'nextRankExp': RANK_EXP[user_data['rank']] if user_data['rank'] < len(RANK_EXP) else None,
            'levelUp': user_data['rank'] > initial_rank
        })
        
    except Exception as e:
        print(f"Error in click: {e}")
        return jsonify({'error': str(e)})

@app.route('/update_session', methods=['POST'])
def update_session():
    user_data = load_user_data()
    data = request.get_json()
    
    # Update only the exp and rank
    user_data['exp'] = data.get('exp', user_data.get('exp', 0))
    user_data['rank'] = data.get('rank', user_data.get('rank', 0))
    
    # Save updated user data
    save_user_data(user_data)
    
    return jsonify({'success': True})

@app.route('/upgrades')
def upgrades():
    user_data = load_user_data()
    return render_template('upgrades.html', 
                         balance=user_data['balance'],
                         upgrades=user_data['upgrades'],  # Pass the upgrades dict directly
                         rank=user_data['rank'],
                         exp=user_data['exp'],
                         RANK_EXP=RANK_EXP,
                         RANKS=RANKS)

@app.route('/purchase_upgrade', methods=['POST'])
def purchase_upgrade():
    try:
        user_data = load_user_data()
        data = request.get_json()
        upgrade_type = data.get('upgrade_type')
        
        # Get current upgrade level
        current_level = user_data['upgrades'].get(upgrade_type, 1)
        
        # Check max levels
        if upgrade_type == 'progress_per_click' and current_level >= 10:
            return jsonify({'error': 'Maximum level reached'})
        if upgrade_type == 'case_quality' and current_level >= 5:
            return jsonify({'error': 'Maximum level reached'})
        if upgrade_type == 'multi_open' and current_level >= 5:  # Add this check
            return jsonify({'error': 'Maximum level reached'})
        
        # Calculate cost
        costs = {
            'click_value': lambda level: 100 * (2 ** (level - 1)),
            'max_multiplier': lambda level: 250 * (2 ** (level - 1)),
            'auto_clicker': lambda level: 500 if level == 0 else 50 * (1.8 ** (level - 1)),
            'combo_speed': lambda level: 150 * (2 ** (level - 1)),
            'critical_strike': lambda level: 1000 if level == 0 else 200 * (2 ** (level - 1)),
            'progress_per_click': lambda level: 150 * (2 ** (level - 1)),
            'case_quality': lambda level: 500 * (2 ** (level - 1)),
            'multi_open': lambda level: 300 * (2 ** (level - 1))  # Add this line
        }
        
        if upgrade_type not in costs:
            return jsonify({'error': 'Invalid upgrade type'})
        
        cost = costs[upgrade_type](current_level)
        
        if user_data['balance'] < cost:
            return jsonify({'error': 'Insufficient funds'})
        
        # Update balance and upgrade level
        user_data['balance'] -= cost
        user_data['upgrades'][upgrade_type] = current_level + 1
        
        # Calculate next cost
        next_cost = costs[upgrade_type](current_level + 1)
        
        # Save updated user data
        save_user_data(user_data)
        
        return jsonify({
            'success': True,
            'balance': user_data['balance'],
            'upgrades': user_data['upgrades'],
            'nextCost': next_cost
        })
        
    except Exception as e:
        print(f"Error in purchase_upgrade: {e}")
        return jsonify({'error': 'Failed to purchase upgrade'})

@app.route('/get_upgrades')
def get_upgrades():
    user_data = load_user_data()
    return jsonify(user_data['upgrades'])  # Return all upgrades directly from user_data

@app.route('/cheat')
def cheat():
    user_data = load_user_data()
    user = create_user_from_dict(user_data)
    user.balance += 10000.0
    
    # Update user data while preserving all fields
    user_data['balance'] = user.balance
    # Don't overwrite other fields - remove these lines
    # user_data['inventory'] = user.inventory
    # user_data['exp'] = user.exp
    # user_data['rank'] = user.rank
    # user_data['upgrades'] = asdict(user.upgrades)
    save_user_data(user_data)
    
    return redirect(url_for('shop'))

@app.route('/chest_reward', methods=['POST'])
def chest_reward():
    user_data = load_user_data()
    data = request.get_json()
    reward = data.get('amount', 0)
    
    user = create_user_from_dict(user_data)
    user.balance += reward
    
    # Update user data
    user_data['balance'] = user.balance
    user_data['inventory'] = user.inventory
    user_data['exp'] = user.exp
    user_data['rank'] = user.rank
    user_data['upgrades'] = asdict(user.upgrades)
    save_user_data(user_data)
    
    return jsonify({
        'success': True,
        'balance': user.balance
    })

@app.route('/buy_case', methods=['POST'])
def buy_case():
    user_data = load_user_data()
    data = request.get_json()
    case_type = data.get('case_type')
    quantity = data.get('quantity', 1)
    
    case_prices = get_case_prices()
    if case_type not in case_prices:
        return jsonify({'error': 'Invalid case type'})
    
    total_cost = case_prices[case_type] * quantity
    user = create_user_from_dict(user_data)
    
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
        },
        'csgo3': {
            'name': 'CS:GO Weapon Case 3',
            'image': 'weapon_case_3.png',
            'is_case': True,
            'type': 'csgo3'
        },
        'phoenix': {
            'name': 'Operation Phoenix Case',
            'image': 'operation_phoenix_case.png',
            'is_case': True,
            'type': 'phoenix'
        },
        'huntsman': {
            'name': 'Huntsman Case',
            'image': 'huntsman_case.png',
            'is_case': True,
            'type': 'huntsman'
        },
        'breakout': {  # Add this block
            'name': 'Operation Breakout Case',
            'image': 'operation_breakout_case.png',
            'is_case': True,
            'type': 'breakout'
        }
    }
    
    # Get current inventory
    inventory = user_data.get('inventory', [])
    
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
    
    # Update user data
    user_data['balance'] = user.balance
    user_data['inventory'] = inventory
    user_data['exp'] = user.exp
    user_data['rank'] = user.rank
    user_data['upgrades'] = asdict(user.upgrades)
    save_user_data(user_data)

    return jsonify({
        'success': True,
        'balance': user.balance
    })

@app.route('/get_inventory')
def get_inventory():
    try:
        user_data = load_user_data()
        inventory = user_data.get('inventory', [])
        
        # Separate cases and skins
        cases = [item for item in inventory if item.get('is_case')]
        skins = [item for item in inventory if not item.get('is_case')]
        
        # Group identical skins
        grouped_skins = group_identical_skins(skins)
        
        # Update prices for grouped skins
        price_cache = {}
        for item in grouped_skins:
            cache_key = (
                item['weapon'],
                item['name'],
                item.get('wear'),
                item['case_type']
            )
            
            if cache_key in price_cache:
                item['price'] = price_cache[cache_key]
            else:
                price = load_skin_price(
                    f"{item['weapon']} | {item['name']}", 
                    item['case_type'],
                    item.get('wear')
                )
                price_cache[cache_key] = price
                item['price'] = price
        
        # Combine cases and grouped skins
        final_inventory = cases + grouped_skins
        
        return jsonify({
            'inventory': final_inventory
        })
        
    except Exception as e:
        print(f"Error getting inventory: {e}")
        return jsonify({'error': 'Failed to get inventory'})

@app.route('/get_user_data')
def get_user_data():
    user_data = load_user_data()
    user = create_user_from_dict(user_data)
    return jsonify({
        'exp': int(user.exp),
        'rank': user.rank,
        'rankName': RANKS[user.rank],
        'nextRankExp': RANK_EXP[user.rank] if user.rank < len(RANK_EXP) else None
    })

@app.route('/data/case_contents/<case_type>')
def get_case_contents(case_type):
    # Update the case file mapping to match actual JSON filenames
    case_file_mapping = {
        'csgo': 'weapon_case_1',
        'esports': 'esports_2013',
        'bravo': 'operation_bravo',
        'csgo2': 'weapon_case_2',
        'esports_winter': 'esports_2013_winter',
        'winter_offensive': 'winter_offensive_case',
        'csgo3': 'weapon_case_3',
        'phoenix': 'operation_phoenix_case',
        'huntsman': 'huntsman_case',
        'breakout': 'operation_breakout_case'  # Add this line
    }
    
    if case_type not in case_file_mapping:
        print(f"Invalid case type requested: {case_type}")
        return jsonify({'error': 'Invalid case type'}), 404
        
    try:
        # Add debugging prints
        file_path = f'cases/{case_file_mapping[case_type]}.json'
        print(f"Attempting to load case file: {file_path}")
        
        # Check if file exists
        import os
        if not os.path.exists(file_path):
            print(f"File not found: {file_path}")
            print(f"Current working directory: {os.getcwd()}")
            print(f"Files in cases directory: {os.listdir('cases')}")
            return jsonify({'error': 'Case data not found'}), 404
            
        # Add .json extension to the file path
        with open(file_path, 'r') as f:
            data = json.load(f)
            print(f"Successfully loaded case data for {case_type}")
            return jsonify(data)
            
    except Exception as e:
        print(f"Error loading case {case_type}: {str(e)}")
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
    user_data = load_user_data()
    user = create_user_from_dict(user_data)
    return render_template('casino.html',
                           balance=user.balance,
                           rank=user.rank,
                           exp=user.exp,
                           RANKS=RANKS,
                           RANK_EXP=RANK_EXP)

@app.route('/coinflip')
@login_required
def coinflip():
    user_data = load_user_data()
    user = create_user_from_dict(user_data)
    return render_template('coinflip.html',
                           balance=user.balance,
                           rank=user.rank,
                           exp=user.exp,
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
        
        # Load current user data
        user_data = load_user_data()
        current_balance = float(user_data['balance'])
        
        if bet_amount > current_balance:
            return jsonify({'error': 'Insufficient funds'})
        
        # Determine result (50/50 chance)
        result = random.choice(['ct', 't'])
        won = result == chosen_side
        
        # Calculate new balance but don't save yet
        new_balance = current_balance - bet_amount
        if won:
            winnings = bet_amount * 2
            new_balance += winnings
            # Track earnings (winnings minus original bet)
            update_earnings_achievements(user_data, winnings - bet_amount)
        
        # Store the bet info in session
        session['coinflip_bet'] = {
            'amount': bet_amount,
            'won': won,
            'new_balance': new_balance
        }
        
        return jsonify({
            'success': True,
            'won': won,
            'result': result,
            'current_balance': current_balance,
            'final_balance': new_balance
        })
        
    except Exception as e:
        print(f"Error in play_coinflip: {e}")
        return jsonify({'error': 'Failed to play coinflip'})

@app.route('/update_coinflip_balance', methods=['POST'])
@login_required
def update_coinflip_balance():
    try:
        # Get stored bet info
        bet_info = session.get('coinflip_bet')
        if not bet_info:
            return jsonify({'error': 'No active bet found'})
        
        # Load and update user data
        user_data = load_user_data()
        user_data['balance'] = bet_info['new_balance']
        save_user_data(user_data)
        
        # Clear the stored bet
        session.pop('coinflip_bet', None)
        
        return jsonify({'success': True, 'balance': user_data['balance']})
    except Exception as e:
        print(f"Error updating balance: {e}")
        return jsonify({'error': 'Failed to update balance'})

@app.route('/roulette')
@login_required
def roulette():
    user_data = load_user_data()
    user = create_user_from_dict(user_data)
    return render_template('roulette.html',
                           balance=user.balance,
                           rank=user.rank,
                           exp=user.exp,
                           RANKS=RANKS,
                           RANK_EXP=RANK_EXP)

@app.route('/play_roulette', methods=['POST'])
@login_required
def play_roulette():
    try:
        data = request.get_json()
        bets = data.get('bets', {})
        lightning_numbers = set(data.get('lightningNumbers', []))
        
        # Load current user data
        user_data = load_user_data()
        current_balance = float(user_data['balance'])
        
        # Determine result
        result = random.randint(0, 36)
        
        # If no bets, just return the result for spectating
        if not bets:
            return jsonify({
                'success': True,
                'result': result,
                'winnings': 0,
                'balance': current_balance,
                'total_bet': 0
            })
        
        # Calculate winnings for placed bets
        winnings = 0
        total_bet = sum(float(amount) for amount in bets.values())
        
        for bet_type, amount in bets.items():
            amount = float(amount)
            if bet_type.isdigit():  # Single number bet
                if int(bet_type) == result:
                    win_amount = amount * 36
                    winnings += win_amount
                    # Track earnings (win amount minus original bet)
                    update_earnings_achievements(user_data, win_amount - amount)
            elif bet_type in ['red', 'black']:
                if (bet_type == 'red' and result in RED_NUMBERS) or \
                   (bet_type == 'black' and result in BLACK_NUMBERS):
                    win_amount = amount * 2
                    winnings += win_amount
                    # Track earnings (win amount minus original bet)
                    update_earnings_achievements(user_data, win_amount - amount)
            elif bet_type in ['even', 'odd']:
                if result != 0 and \
                   ((bet_type == 'even' and result % 2 == 0) or \
                    (bet_type == 'odd' and result % 2 == 1)):
                    win_amount = amount * 2
                    winnings += win_amount
                    # Track earnings (win amount minus original bet)
                    update_earnings_achievements(user_data, win_amount - amount)
            elif bet_type in ['1-18', '19-36']:
                if (bet_type == '1-18' and 1 <= result <= 18) or \
                   (bet_type == '19-36' and 19 <= result <= 36):
                    win_amount = amount * 2
                    winnings += win_amount
                    # Track earnings (win amount minus original bet)
                    update_earnings_achievements(user_data, win_amount - amount)
            elif bet_type in ['1st12', '2nd12', '3rd12']:
                if (bet_type == '1st12' and 1 <= result <= 12) or \
                   (bet_type == '2nd12' and 13 <= result <= 24) or \
                   (bet_type == '3rd12' and 25 <= result <= 36):
                    win_amount = amount * 3
                    winnings += win_amount
                    # Track earnings (win amount minus original bet)
                    update_earnings_achievements(user_data, win_amount - amount)
        
        # Calculate final balance
        final_balance = current_balance - total_bet + winnings
        
        # Store the game result in session
        session['roulette_result'] = {
            'result': result,
            'winnings': winnings,
            'new_balance': final_balance,
            'total_bet': total_bet
        }
        
        return jsonify({
            'success': True,
            'result': result,
            'winnings': winnings,
            'balance': current_balance,
            'total_bet': total_bet
        })
        
    except Exception as e:
        print(f"Error in play_roulette: {e}")
        return jsonify({'error': 'Failed to play roulette'})

@app.route('/update_roulette_balance', methods=['POST'])
@login_required
def update_roulette_balance():
    try:
        # Get stored game result
        result = session.get('roulette_result')
        if not result:
            return jsonify({'error': 'No active game found'})
        
        # Load and update user data
        user_data = load_user_data()
        user_data['balance'] = result['new_balance']
        save_user_data(user_data)
        
        # Clear the stored result
        session.pop('roulette_result', None)
        
        return jsonify({'success': True, 'balance': user_data['balance']})
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
    user_data = load_user_data()
    user = create_user_from_dict(user_data)
    return render_template('blackjack.html',
                           balance=user.balance,
                           rank=user.rank,
                           exp=user.exp,
                           RANKS=RANKS,
                           RANK_EXP=RANK_EXP)

@app.route('/play_blackjack', methods=['POST'])
@login_required
def play_blackjack():
    try:
        data = request.get_json()
        action = data.get('action')
        
        # Load current user data
        user_data = load_user_data()
        current_balance = float(user_data['balance'])
        
        # Initialize game if not exists
        if 'blackjack_game' not in session:
            session['blackjack_game'] = None
        
        game = BlackjackGame.deserialize(session.get('blackjack_game')) if session.get('blackjack_game') else None
        
        if not game and action != 'deal':
            return jsonify({'error': 'No game in progress'})
        
        if action == 'deal':
            bet_amount = round(float(data.get('amount', 0)), 2)
            
            if bet_amount <= 0:
                return jsonify({'error': 'Bet amount must be greater than 0'})
            if bet_amount > current_balance:
                return jsonify({'error': f'Insufficient funds (bet: ${bet_amount:.2f}, balance: ${current_balance:.2f})'})
            
            # Deduct bet immediately and save
            user_data['balance'] = round(current_balance - bet_amount, 2)
            save_user_data(user_data)
            
            # Create new game
            game = BlackjackGame()
            game.deal(bet_amount)
            
        elif action == 'split':
            if not game:
                return jsonify({'error': 'No game in progress'})
            
            # Check if player can afford split
            if game.bet_amount > current_balance:
                return jsonify({'error': 'Insufficient funds to split'})
            
            # Deduct split bet amount and save
            user_data['balance'] = current_balance - game.bet_amount
            save_user_data(user_data)
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
            if game.bet_amount > current_balance:
                state = game.get_game_state()
                state['error'] = 'Insufficient funds to double down'
                return jsonify(state)
            
            # Deduct double down bet and save
            user_data['balance'] = current_balance - game.bet_amount
            save_user_data(user_data)
            game.double_down()
        
        # Get game state
        state = game.get_game_state()
        
        # Update balance if game is over
        if state['gameOver']:
            current_balance = float(user_data['balance'])
            total_won = 0
            
            for i, won in enumerate(state['won']):
                bet = game.bet_amount if i == 0 else game.split_bet_amount
                if won == 'blackjack':
                    winnings = bet * 2.5  # 3:2 payout for blackjack
                    total_won += winnings
                    # Track earnings (winnings minus original bet)
                    update_earnings_achievements(user_data, winnings - bet)
                elif won is True:
                    winnings = bet * 2  # 2x payout
                    total_won += winnings
                    # Track earnings (winnings minus original bet)
                    update_earnings_achievements(user_data, winnings - bet)
                elif won is None:  # Push
                    total_won += bet  # Return original bet
                # If loss (won is False), no need to track as it's a loss
            
            if total_won > 0:
                user_data['balance'] = current_balance + total_won
                save_user_data(user_data)
            
            # Clear game
            session['blackjack_game'] = None
        else:
            # Store serialized game state in session
            session['blackjack_game'] = game.serialize()
        
        # Add balance to response
        state['balance'] = user_data['balance']
        
        return jsonify(state)
        
    except Exception as e:
        print(f"Error in play_blackjack: {e}")
        if game:
            state = game.get_game_state()
            state['error'] = 'Failed to process game action'
            return jsonify(state)
        return jsonify({'error': 'Failed to process game action'})

@app.route('/crash')
@login_required
def crash():
    user_data = load_user_data()
    user = create_user_from_dict(user_data)
    return render_template('crash.html',
                           balance=user.balance,
                           rank=user.rank,
                           exp=user.exp,
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
        
        # Load current user data from file
        user_data = load_user_data()
        current_balance = float(user_data['balance'])
        
        if bet_amount > current_balance:
            return jsonify({'error': 'Insufficient funds'})
        
        # Deduct bet amount and save
        user_data['balance'] = current_balance - bet_amount
        save_user_data(user_data)
        
        # Store the bet amount in session
        session['crash_bet'] = bet_amount
        
        return jsonify({
            'success': True,
            'balance': user_data['balance']
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
        
        if current_game_bet is None:
            return jsonify({'error': 'No active bet found'})
        
        # Load current user data
        user_data = load_user_data()
        
        # Calculate winnings
        winnings = current_game_bet * multiplier
        
        # Update balance and save
        user_data['balance'] = float(user_data['balance']) + winnings
        
        # Track earnings (winnings minus original bet)
        update_earnings_achievements(user_data, winnings - current_game_bet)
        
        save_user_data(user_data)
        
        # Clear the crash bet from session
        session['crash_bet'] = None
        
        return jsonify({
            'success': True,
            'balance': user_data['balance']
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
            session['crash_bet'] = None
        
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
def sell_all():
    try:
        user_data = load_user_data()
        inventory = user_data.get('inventory', [])
        
        # Calculate total value of all non-case items
        total_value = 0
        new_inventory = []
        
        for item in inventory:
            if item.get('is_case'):
                new_inventory.append(item)  # Keep cases
            else:
                total_value += float(item.get('price', 0))
        
        if total_value > 0:
            # Update user's balance and inventory
            user_data['balance'] = float(user_data['balance']) + total_value
            user_data['inventory'] = new_inventory
            
            # Update achievements with the total earned amount
            update_earnings_achievements(user_data, total_value)
            
            # Save the updated user data
            save_user_data(user_data)
        
        return jsonify({
            'success': True,
            'balance': user_data['balance'],
            'sold_value': total_value
        })
        
    except Exception as e:
        print(f"Error in sell_all: {e}")
        return jsonify({'error': 'Failed to sell all items'})

@app.route('/jackpot')
@login_required
def jackpot():
    user_data = load_user_data()
    user = create_user_from_dict(user_data)
    return render_template('jackpot.html',
                           balance=user.balance,
                           rank=user.rank,
                           exp=user.exp,
                           RANKS=RANKS,
                           RANK_EXP=RANK_EXP)

@app.route('/get_jackpot_inventory')
@login_required
def get_jackpot_inventory():
    try:
        user_data = load_user_data()
        inventory = user_data.get('inventory', [])
        
        # Filter for non-case items only
        eligible_items = [
            item for item in inventory
            if not item.get('is_case')
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
        user_items = data.get('items', [])
        mode = data.get('mode', 'low')
        
        # Define mode limits
        mode_limits = {
            'low': {'min': 0, 'max': 10},
            'medium': {'min': 10, 'max': 100},
            'high': {'min': 100, 'max': 1000},
            'extreme': {'min': 1000, 'max': float('inf')}
        }
        
        current_limits = mode_limits.get(mode, mode_limits['low'])
        
        if not user_items:
            return jsonify({'error': 'No items selected'})
        
        # Validate user items are within mode limits
        for item in user_items:
            price = float(item['price'])
            if price < current_limits['min'] or price > current_limits['max']:
                return jsonify({'error': f'Item price ${price:.2f} is outside the current mode range'})
        
        # Load user data from file instead of session
        user_data = load_user_data()
        inventory = user_data.get('inventory', [])
        
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
        user_data['inventory'] = new_inventory
        save_user_data(user_data)  # Save updated inventory to file

        # Generate bot players
        num_bots = random.randint(1, 10)
        bot_players = generate_bot_players(num_bots, current_limits)
        
        # Calculate values
        user_value = sum(float(item['price']) for item in user_items)
        bot_total = sum(sum(float(item['price']) for item in bot['items']) for bot in bot_players)
        total_value = user_value + bot_total
        
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
        
        # Determine winner
        winner = random.choices(
            players,
            weights=[float(player['value']) for player in players],
            k=1
        )[0]
        
        # If user won, add all items to their inventory
        if winner['name'] == 'You':
            # Don't remove the original items from inventory
            new_inventory = inventory.copy()
            
            # Add items from all other players
            for player in players:
                if player['name'] != 'You':
                    new_inventory.extend(player['items'])
            
            # Update user data with new inventory
            user_data['inventory'] = new_inventory
            save_user_data(user_data)
            
            # Add won items to winner data for display
            winner['items'] = user_items + [item for player in players 
                                          if player['name'] != 'You' 
                                          for item in player['items']]
        else:
            # User lost, remove their wagered items
            new_inventory = [item for i, item in enumerate(inventory) if i not in found_items]
            user_data['inventory'] = new_inventory
            save_user_data(user_data)
        
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

def generate_bot_players(num_bots: int, mode_limits: dict) -> List[Dict[str, Any]]:
    bot_names = [
        "_Astrid47", "Kai.Jayden_02", "Orion_Phoenix98", "ElaraB_23", "Theo.91", "Nova-Lyn", "FelixHaven19", "Aria.Stella85", "Lucien_Kai", "Mira-Eclipse"
    ]
    
    # Load all case data
    case_types = ['csgo', 'esports', 'bravo', 'csgo2', 'esports_winter', 'winter_offensive', 'csgo3', 'phoenix', 'huntsman', 'breakout']  # Add 'breakout'
    all_skins = []  # Change to a single list
    
    # Load skins from each case
    for case_type in case_types:
        try:
            case_file_mapping = {
                'csgo': 'weapon_case_1',
                'esports': 'esports_2013',
                'bravo': 'operation_bravo',  # Changed back to match JSON filename
                'csgo2': 'weapon_case_2',
                'esports_winter': 'esports_2013_winter',
                'winter_offensive': 'winter_offensive_case',
                'csgo3': 'weapon_case_3',  # Add this line
                'phoenix': 'operation_phoenix_case',
                'huntsman': 'huntsman_case',  # Add huntsman case
                'breakout': 'operation_breakout_case'  # Add this line
            }
            
            with open(f'cases/{case_file_mapping[case_type]}.json', 'r') as f:
                case_data = json.load(f)
                
                # Add all skins to the pool
                for grade, items in case_data['skins'].items():
                    for item in items:
                        all_skins.append({
                            'weapon': item['weapon'],
                            'name': item['name'],
                            'prices': item['prices'],
                            'case_type': case_type,
                            'case_file': case_file_mapping[case_type],
                            'image': item.get('image', f"{item['weapon'].lower().replace(' ', '')}_{item['name'].lower().replace(' ', '_')}.png"),
                            'rarity': grade.upper()
                        })
        except Exception as e:
            print(f"Error loading case {case_type}: {e}")
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
            if not all_skins:
                break
                
            skin = random.choice(all_skins)
            
            # Get valid wear options
            wear_options = [w for w in skin['prices'].keys() 
                          if not w.startswith('ST_') and w != 'NO']
            if not wear_options:
                continue
                
            wear = random.choice(wear_options)
            stattrak = random.random() < 0.1  # 10% chance
            
            price_key = f"ST_{wear}" if stattrak else wear
            try:
                price = float(skin['prices'].get(price_key, 0))
                
                # Only add if price is within mode range
                if mode_limits['min'] <= price <= mode_limits['max']:
                    bot_items.append({
                        'weapon': skin['weapon'],
                        'name': skin['name'],
                        'wear': wear,
                        'rarity': skin['rarity'],
                        'stattrak': stattrak,
                        'price': price,
                        'case_type': skin['case_type']
                    })
            except (ValueError, TypeError):
                continue
        
        if bot_items:
            bots.append({
                'name': bot_name,
                'items': bot_items
            })
    
    return bots

@app.route('/buy_skin', methods=['POST'])
@login_required
def buy_skin():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Invalid request data'})

        # Load user data
        user_data = load_user_data()
        current_balance = float(user_data['balance'])
        price = float(data.get('price', 0))

        if price > current_balance:
            return jsonify({'error': 'Insufficient funds'})

        # Create skin item
        skin_item = {
            'weapon': data['weapon'],
            'name': data['name'],
            'rarity': data['rarity'],
            'wear': data['wear'],
            'stattrak': data['stattrak'],
            'price': price,
            'timestamp': time.time(),
            'case_type': data['case_type'],
            'is_case': False
        }

        # Update user data
        user_data['balance'] = current_balance - price
        user_data['inventory'].append(skin_item)
        save_user_data(user_data)

        return jsonify({
            'success': True,
            'balance': user_data['balance']
        })

    except Exception as e:
        print(f"Error in buy_skin: {e}")
        return jsonify({'error': 'Failed to purchase skin'})

@app.route('/get_featured_skins')
def get_featured_skins():
    global FEATURED_SKINS, LAST_REFRESH_TIME
    
    current_time = time.time()
    
    # Check if we need to refresh the skins
    if not FEATURED_SKINS or not LAST_REFRESH_TIME or (current_time - LAST_REFRESH_TIME) >= REFRESH_INTERVAL:
        try:
            # Load all case contents
            case_types = ['csgo', 'esports', 'bravo', 'csgo2', 'esports_winter', 'winter_offensive', 'csgo3', 'phoenix', 'huntsman', 'breakout']  # Add 'breakout'
            all_skins = []
            
            # Load skins from each case
            for case_type in case_types:
                try:
                    case_file_mapping = {
                        'csgo': 'weapon_case_1',
                        'esports': 'esports_2013',
                        'bravo': 'operation_bravo',
                        'csgo2': 'weapon_case_2',
                        'esports_winter': 'esports_2013_winter',
                        'winter_offensive': 'winter_offensive_case',
                        'csgo3': 'weapon_case_3',  # csgo3 is included
                        'phoenix': 'operation_phoenix_case',
                        'huntsman': 'huntsman_case',  # Add huntsman case
                        'breakout': 'operation_breakout_case'  # Add this line
                    }
                    
                    with open(f'cases/{case_file_mapping[case_type]}.json', 'r') as f:
                        case_data = json.load(f)
                        
                        # Add all skins to the pool
                        for grade, items in case_data['skins'].items():
                            for item in items:
                                all_skins.append({
                                    'weapon': item['weapon'],
                                    'name': item['name'],
                                    'prices': item['prices'],
                                    'case_type': case_type,
                                    'case_file': case_file_mapping[case_type],
                                    'image': item.get('image', f"{item['weapon'].lower().replace(' ', '')}_{item['name'].lower().replace(' ', '_')}.png"),
                                    'rarity': grade.upper()
                                })
                except Exception as e:
                    print(f"Error loading case {case_type}: {e}")
                    continue
            
            # Select one random skin from each rarity
            FEATURED_SKINS = {}
            rarities = ['GOLD', 'RED', 'PINK', 'PURPLE', 'BLUE']
            
            for rarity in rarities:
                # Filter skins by rarity
                rarity_skins = [skin for skin in all_skins if skin['rarity'] == rarity]
                if rarity_skins:
                    selected_skin = random.choice(rarity_skins)
                    
                    # Generate random wear and StatTrak
                    wear_options = [w for w in selected_skin['prices'].keys() 
                                  if not w.startswith('ST_') and w != 'NO']
                    if wear_options:
                        wear = random.choice(wear_options)
                        stattrak = random.random() < 0.1  # 10% chance
                        
                        price_key = f"ST_{wear}" if stattrak else wear
                        price = float(selected_skin['prices'].get(price_key, selected_skin['prices'].get(wear, 0)))
                        
                        FEATURED_SKINS[rarity] = {
                            'weapon': selected_skin['weapon'],
                            'name': selected_skin['name'],
                            'wear': wear,
                            'stattrak': stattrak,
                            'price': price,
                            'case_type': selected_skin['case_type'],
                            'case_file': selected_skin['case_file'],
                            'image': selected_skin['image'],
                            'rarity': rarity
                        }
            
            LAST_REFRESH_TIME = current_time
            
        except Exception as e:
            print(f"Error generating featured skins: {e}")
            traceback.print_exc()
            return jsonify({'error': str(e)})
    
    return jsonify({
        'skins': FEATURED_SKINS,
        'refreshTime': LAST_REFRESH_TIME,
        'nextRefresh': LAST_REFRESH_TIME + REFRESH_INTERVAL if LAST_REFRESH_TIME else None
    })

@app.route('/upgrade')
@login_required
def upgrade_game():
    user_data = load_user_data()
    user = create_user_from_dict(user_data)
    return render_template('upgrade.html',
                           balance=user.balance,
                           rank=user.rank,
                           exp=user.exp,
                           RANKS=RANKS,
                           RANK_EXP=RANK_EXP)

def find_best_skin_combination(available_skins, target_value, max_skins=10):
    """
    Find the best combination of skins closest to the target value.
    Prioritizes high-value single items and StatTrak versions.
    """
    # Create a list that includes both normal and StatTrak versions
    all_skins = []
    for skin in available_skins:
        # Add normal version
        all_skins.append(skin)
        
        # Add StatTrak version if price exists in case data
        try:
            case_file = CASE_FILE_MAPPING.get(skin['case_type'])
            with open(f'cases/{case_file}.json', 'r') as f:
                case_data = json.load(f)
                for grade, items in case_data['skins'].items():
                    for item in items:
                        if item['weapon'] == skin['weapon'] and item['name'] == skin['name']:
                            st_price_key = f"ST_{skin['wear']}"
                            if st_price_key in item['prices']:
                                st_skin = skin.copy()
                                st_skin['stattrak'] = True
                                st_skin['price'] = float(item['prices'][st_price_key])
                                all_skins.append(st_skin)
        except Exception as e:
            print(f"Error adding StatTrak version: {e}")
            continue

    # Sort by price descending
    all_skins = sorted(all_skins, key=lambda x: float(x['price']), reverse=True)

    # First try to find a single high-value skin within 5% of target
    for skin in all_skins:
        price = float(skin['price'])
        if abs(price - target_value) <= target_value * 0.05:
            return [skin]

    # If no single skin matches, try to find the highest value skin under target
    # and combine with other skins to reach the target
    result_skins = []
    remaining_target = target_value
    used_indices = set()

    # First try to get the highest value skin possible
    for i, skin in enumerate(all_skins):
        price = float(skin['price'])
        if price <= remaining_target * 1.05:  # Allow 5% over
            result_skins.append(skin)
            used_indices.add(i)
            remaining_target -= price
            break

    # Then fill in with additional skins if needed
    while remaining_target > 0 and len(result_skins) < max_skins:
        best_skin = None
        best_price_diff = float('inf')
        best_index = -1

        for i, skin in enumerate(all_skins):
            if i in used_indices:
                continue

            price = float(skin['price'])
            if price <= remaining_target:
                diff = remaining_target - price
                if diff < best_price_diff:
                    best_skin = skin
                    best_price_diff = diff
                    best_index = i

        if best_skin is None:
            break

        result_skins.append(best_skin)
        used_indices.add(best_index)
        remaining_target -= float(best_skin['price'])

    # If we couldn't get close to target value, try different approach
    total_value = sum(float(skin['price']) for skin in result_skins)
    if total_value < target_value * 0.9:  # If we're getting less than 90% of target
        # Try to find the best single high-value skin
        best_single = max(all_skins, key=lambda x: float(x['price']))
        if float(best_single['price']) > total_value:
            return [best_single]

    return result_skins

@app.route('/play_upgrade', methods=['POST'])
@login_required
def play_upgrade():
    try:
        data = request.get_json()
        selected_items = data.get('items', [])
        multiplier = float(data.get('multiplier', 2))
        
        if not selected_items:
            return jsonify({'error': 'No items selected'})
            
        # Load user data
        user_data = load_user_data()
        inventory = user_data.get('inventory', [])
        
        # Calculate total value of selected items
        total_value = sum(float(item['price']) for item in selected_items)
        target_value = total_value * multiplier
        
        # Success probabilities for each multiplier
        probabilities = {
            2: 46,
            3: 30.67,
            5: 18.4,
            10: 9.2,
            100: 0.92
        }
        
        # Determine if upgrade succeeds
        success_probability = probabilities.get(multiplier, 0) / 100
        success = random.random() < success_probability
        
        if success:
            # Load all possible skins
            available_skins = []
            for case_type, file_name in CASE_FILE_MAPPING.items():
                try:
                    with open(f'cases/{file_name}.json', 'r') as f:
                        case_data = json.load(f)
                        for grade, skins in case_data['skins'].items():
                            for skin in skins:
                                for wear, price in skin['prices'].items():
                                    if wear != 'NO' and not wear.startswith('ST_'):
                                        available_skins.append({
                                            'weapon': skin['weapon'],
                                            'name': skin['name'],
                                            'wear': wear,
                                            'price': float(price),
                                            'rarity': grade.upper(),
                                            'case_type': case_type,
                                            'stattrak': False,
                                            'timestamp': time.time()
                                        })
                except Exception as e:
                    print(f"Error loading case {case_type}: {e}")
                    continue
            
            # Find best combination of skins
            won_skins = find_best_skin_combination(available_skins, target_value)
            
            # Remove selected items from inventory
            selected_indices = []
            for selected_item in selected_items:
                for i, inv_item in enumerate(inventory):
                    if (i not in selected_indices and
                        inv_item.get('weapon') == selected_item['weapon'] and
                        inv_item.get('name') == selected_item['name'] and
                        inv_item.get('wear') == selected_item['wear'] and
                        inv_item.get('stattrak') == selected_item['stattrak']):
                        selected_indices.append(i)
                        break
            
            # Create new inventory without selected items
            new_inventory = [item for i, item in enumerate(inventory) 
                           if i not in selected_indices]
            
            # Add won skins to inventory
            new_inventory.extend(won_skins)
            
            # Update user data
            user_data['inventory'] = new_inventory
            save_user_data(user_data)
            
            # Calculate total value of won skins
            won_value = sum(float(skin['price']) for skin in won_skins)
            
            return jsonify({
                'success': True,
                'won': True,
                'skins': won_skins,
                'multiple_skins': len(won_skins) > 1,
                'total_value': won_value,
                'target_value': target_value
            })
            
        else:
            # Remove selected items from inventory on loss
            selected_indices = []
            for selected_item in selected_items:
                for i, inv_item in enumerate(inventory):
                    if (i not in selected_indices and
                        inv_item.get('weapon') == selected_item['weapon'] and
                        inv_item.get('name') == selected_item['name'] and
                        inv_item.get('wear') == selected_item['wear'] and
                        inv_item.get('stattrak') == selected_item['stattrak']):
                        selected_indices.append(i)
                        break
            
            # Create new inventory without selected items
            new_inventory = [item for i, item in enumerate(inventory) 
                           if i not in selected_indices]
            
            # Update user data
            user_data['inventory'] = new_inventory
            save_user_data(user_data)
            
            return jsonify({
                'success': True,
                'won': False
            })
            
    except Exception as e:
        print(f"Error in play_upgrade: {e}")
        return jsonify({'error': 'Failed to process upgrade'})

# Add this new route to handle case progress clicks
@app.route('/case_click', methods=['POST'])
def case_click():
    try:
        user_data = load_user_data()
        data = request.get_json()
        
        # Get current case progress from request data instead of saved data
        case_progress = float(data.get('current_progress', 0))
        
        # Get upgrades from saved data
        upgrades = user_data.get('upgrades', {})
        progress_per_click = upgrades.get('progress_per_click', 1)
        case_quality = upgrades.get('case_quality', 1)
        
        # Add progress based on upgrade level
        case_progress += progress_per_click
        
        # Save the current progress back to user data
        user_data['case_progress'] = case_progress  # Add this line
        
        # Check if we've reached 100%
        earned_case = None
        earned_case_data = None
        if case_progress >= 100:
            # Reset progress
            case_progress = 0
            user_data['case_progress'] = 0  # Add this line
            
            # Get price range based on case quality level
            price_ranges = {
                1: (0, 2),    # Level 1: 0-2 USD
                2: (0, 5),    # Level 2: 0-5 USD
                3: (0, 10),   # Level 3: 0-10 USD
                4: (0, 15),   # Level 4: 0-15 USD
                5: (0, 20)    # Level 5: 0-20 USD
            }
            
            min_price, max_price = price_ranges.get(case_quality, (0, 2))
            
            # Get available cases within price range
            available_cases = []
            for case_type, file_name in CASE_FILE_MAPPING.items():
                try:
                    with open(f'cases/{file_name}.json', 'r') as f:
                        case_data = json.load(f)
                        price = float(case_data.get('price', 0))
                        if min_price <= price <= max_price:
                            available_cases.append((case_type, case_data))
                except Exception as e:
                    print(f"Error checking case price for {case_type}: {e}")
                    continue
            
            if available_cases:
                earned_case, case_data = random.choice(available_cases)
                earned_case_data = {
                    'name': case_data['name'],
                    'image': case_data['image'],
                    'price': case_data['price'],
                    'type': earned_case
                }
                
                # Add case to inventory
                inventory = user_data.get('inventory', [])
                case_found = False
                
                for item in inventory:
                    if item.get('is_case') and item.get('type') == earned_case:
                        item['quantity'] = item.get('quantity', 0) + 1
                        case_found = True
                        break
                
                if not case_found:
                    inventory.append({
                        'name': case_data['name'],
                        'image': case_data['image'],
                        'is_case': True,
                        'type': earned_case,
                        'quantity': 1
                    })
                
                # Update inventory in user_data
                user_data['inventory'] = inventory
        
        # Save user data with updated progress
        save_user_data(user_data)  # Make sure this is called
        
        return jsonify({
            'success': True,
            'progress': case_progress,
            'earned_case': earned_case_data,
            'progress_per_click': progress_per_click
        })
        
    except Exception as e:
        print(f"Error in case_click: {e}")
        return jsonify({'error': str(e)})

def load_skin_price(skin_name: str, case_type: str, wear: str = None) -> float:
    try:
        # Debug: Print input parameters
        print(f"\nAttempting to load price for: {skin_name} from case: {case_type}")
        print(f"Wear condition: {wear}")
        
        # Parse weapon and name from skin_name
        weapon, name = skin_name.split(" | ", 1)
        print(f"Parsed weapon: {weapon}, name: {name}")
        
        # Use the global CASE_FILE_MAPPING
        file_name = CASE_FILE_MAPPING.get(case_type)
        if not file_name:
            print(f"Unknown case type: {case_type}")
            print(f"Available case types: {list(CASE_FILE_MAPPING.keys())}")
            return 0
        
        file_path = f'cases/{file_name}.json'
        print(f"Loading from file: {file_path}")
        
        with open(file_path, 'r') as f:
            case_data = json.load(f)
            print(f"Successfully loaded case data")
            
            # Look for the skin in all grades
            for grade, items in case_data['skins'].items():
                for item in items:
                    if item['weapon'] == weapon and item['name'] == name:
                        prices = item.get('prices', {})
                        
                        # If StatTrak, use ST_ prices
                        price_prefix = 'ST_' if 'StatTrak™' in skin_name else ''
                        
                        # If wear is specified, try that specific wear first
                        if wear:
                            wear_key = f"{price_prefix}{wear}"
                            if wear_key in prices:
                                price = float(prices[wear_key])
                                print(f"Found exact price for {wear_key}: ${price}")
                                return price
                        
                        # Try common wear values
                        for wear_type in ['FN', 'MW', 'FT', 'WW', 'BS']:
                            wear_key = f"{price_prefix}{wear_type}"
                            if wear_key in prices:
                                price = float(prices[wear_key])
                                print(f"Using fallback price for {wear_key}: ${price}")
                                return price
                        
                        # Last resort: use any available price
                        if prices:
                            first_price = float(next(iter(prices.values())))
                            print(f"Using first available price: ${first_price}")
                            return first_price
                        
                        print("No prices found for skin")
                        return 0
            
            print(f"Skin not found: {skin_name}")
            return 0
            
    except Exception as e:
        print(f"Error loading price for {skin_name} from {case_type}:")
        print(f"Exception type: {type(e).__name__}")
        print(f"Exception message: {str(e)}")
        traceback.print_exc()
        return 0

@app.route('/trading')
@login_required
def trading():
    user_data = load_user_data()
    user = create_user_from_dict(user_data)
    return render_template('trading.html',
                         balance=user.balance,
                         rank=user.rank,
                         exp=user.exp,
                         RANKS=RANKS,
                         RANK_EXP=RANK_EXP)

# Add this new function to generate and cache daily trades
def generate_daily_trades():
    """Generate 10 random trades for the day"""
    try:
        # Load all case data for available skins
        case_types = ['csgo', 'esports', 'bravo', 'csgo2', 'esports_winter', 
                     'winter_offensive', 'csgo3', 'phoenix', 'huntsman', 'breakout']
        all_skins = []
        
        # Load skins from each case
        for case_type in case_types:
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
                                'rarity': grade.upper()
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
                            'rarity': skin['rarity']
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
                            'rarity': skin['rarity']
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
                            'rarity': skin['rarity']
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
                                'rarity': skin['rarity']
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
        
        # Save trades with current date
        daily_trades = {
            'date': date.today().isoformat(),
            'trades': trades
        }
        
        with open('data/daily_trades.json', 'w') as f:
            json.dump(daily_trades, f, indent=2)
            
        return trades
        
    except Exception as e:
        print(f"Error generating daily trades: {e}")
        traceback.print_exc()  # Add this to get more detailed error info
        return []

# Modify the get_trades route
@app.route('/get_trades')
@login_required
def get_trades():
    try:
        trades_data = load_daily_trades()
        
        # Filter out completed trades
        active_trades = [trade for trade in trades_data['trades'] 
                        if trade not in trades_data.get('completed_trades', [])]
        
        return jsonify({'trades': active_trades})
    except Exception as e:
        print(f"Error getting trades: {e}")
        return jsonify({'error': 'Failed to load trades'})

@app.route('/complete_trade', methods=['POST'])
@login_required
def complete_trade():
    try:
        data = request.get_json()
        trade = data.get('trade')
        
        if not trade:
            return jsonify({'error': 'Invalid trade data'})
            
        # Load trades data and user data
        trades_data = load_daily_trades()
        user_data = load_user_data()
        
        # Get current user state
        current_balance = float(user_data['balance'])
        inventory = user_data.get('inventory', [])
        current_exp = float(user_data.get('exp', 0))
        current_rank = int(user_data.get('rank', 0))
        
        # Verify trade still exists and hasn't been completed
        if trade not in trades_data['trades'] or trade in trades_data.get('completed_trades', []):
            return jsonify({'error': 'Trade no longer available'})
            
        # Check if user has required items/money
        if any(item['type'] == 'money' for item in trade['requesting']):
            required_money = sum(item['amount'] for item in trade['requesting'] if item['type'] == 'money')
            if required_money > current_balance:
                return jsonify({'error': 'Insufficient funds'})
        
        # Check for required skins
        if any(item['type'] == 'skin' for item in trade['requesting']):
            required_skins = [item for item in trade['requesting'] if item['type'] == 'skin']
            for required_skin in required_skins:
                skin_found = False
                for inv_item in inventory:
                    if (not inv_item.get('is_case') and
                        inv_item['weapon'] == required_skin['weapon'] and
                        inv_item['name'] == required_skin['name'] and
                        inv_item['wear'] == required_skin['wear'] and
                        inv_item['stattrak'] == required_skin['stattrak']):
                        skin_found = True
                        break
                if not skin_found:
                    return jsonify({'error': f"Missing skin: {required_skin['weapon']} | {required_skin['name']}"})
        
        # Calculate trade value for EXP
        trade_value = 0
        if trade['type'] == 'sell':
            trade_value = sum(float(item.get('price', 0)) for item in trade['offering'] if item.get('type') == 'skin')
        elif trade['type'] == 'buy':
            trade_value = sum(float(item.get('price', 0)) for item in trade['requesting'] if item.get('type') == 'skin')
        else:  # swap
            offering_value = sum(float(item.get('price', 0)) for item in trade['offering'] if item.get('type') == 'skin')
            requesting_value = sum(float(item.get('price', 0)) for item in trade['requesting'] if item.get('type') == 'skin')
            trade_value = (offering_value + requesting_value) / 2
        
        # Calculate EXP reward
        max_exp_reward = RANK_EXP[current_rank] * 0.1 if current_rank < len(RANK_EXP) else 1000
        base_exp = min(trade_value * 0.1, max_exp_reward)
        exp_multipliers = {'sell': 1.0, 'buy': 2.0, 'swap': 3.0}
        exp_reward = base_exp * exp_multipliers.get(trade['type'], 1.0)
        
        # Update EXP and check for rank up
        new_exp = current_exp + exp_reward
        new_rank = current_rank
        while new_rank < len(RANK_EXP) and new_exp >= RANK_EXP[new_rank]:
            new_exp -= RANK_EXP[new_rank]
            new_rank += 1
        
        # Process inventory changes
        new_inventory = []
        used_indices = set()
        
        # Remove requested skins
        for required_skin in (item for item in trade['requesting'] if item['type'] == 'skin'):
            for i, inv_item in enumerate(inventory):
                if (i not in used_indices and
                    not inv_item.get('is_case') and
                    inv_item['weapon'] == required_skin['weapon'] and
                    inv_item['name'] == required_skin['name'] and
                    inv_item['wear'] == required_skin['wear'] and
                    inv_item['stattrak'] == required_skin['stattrak']):
                    used_indices.add(i)
                    break
        
        # Keep items that weren't traded
        new_inventory = [item for i, item in enumerate(inventory) if i not in used_indices]
        
        # Add offered skins
        for offered_item in trade['offering']:
            if offered_item['type'] == 'skin':
                skin_item = {
                    'weapon': offered_item['weapon'],
                    'name': offered_item['name'],
                    'rarity': offered_item['rarity'],
                    'wear': offered_item['wear'],
                    'stattrak': offered_item['stattrak'],
                    'price': offered_item['price'],
                    'timestamp': time.time(),
                    'case_type': offered_item['case_type'],
                    'is_case': False
                }
                new_inventory.append(skin_item)
        
        # Update balance
        money_received = sum(item['amount'] for item in trade['offering'] if item['type'] == 'money')
        money_paid = sum(item['amount'] for item in trade['requesting'] if item['type'] == 'money')
        new_balance = current_balance + money_received - money_paid
        
        # Save user changes
        user_data['balance'] = new_balance
        user_data['inventory'] = new_inventory
        user_data['exp'] = new_exp
        user_data['rank'] = new_rank
        save_user_data(user_data)
        
        # Mark trade as completed
        if 'completed_trades' not in trades_data:
            trades_data['completed_trades'] = []
        trades_data['completed_trades'].append(trade)
        save_daily_trades(trades_data)
        
        return jsonify({
            'success': True,
            'balance': new_balance,
            'exp': new_exp,
            'rank': new_rank,
            'rankName': RANKS[new_rank],
            'nextRankExp': RANK_EXP[new_rank] if new_rank < len(RANK_EXP) else None,
            'expGained': exp_reward
        })
        
    except Exception as e:
        print(f"Error completing trade: {e}")
        traceback.print_exc()  # Add this to get more detailed error info
        return jsonify({'error': 'Failed to complete trade'})

@app.route('/chat_with_bot', methods=['POST'])
def chat_with_bot():
    try:
        data = request.get_json()
        bot_name = data.get('botName')
        message = data.get('message')
        chat_history = data.get('chatHistory', [])
        
        print(f"Received chat request - Bot: {bot_name}, Message: {message}")
        
        if not bot_name or not message:
            return jsonify({'error': 'Missing bot name or message'})
            
        # Get bot's personality
        personality = BOT_PERSONALITIES.get(bot_name, "A friendly CS:GO skin trader")
        
        # Load current trades from daily_trades.json
        try:
            with open('data/daily_trades.json', 'r') as f:
                daily_trades = json.load(f)
                trades_info = []
                for trade in daily_trades.get('trades', []):
                    # Format each trade into a readable string
                    offering = []
                    for item in trade['offering']:
                        if item['type'] == 'money':
                            offering.append(f"${item['amount']}")
                        else:
                            offering.append(f"{item['weapon']} | {item['name']} ({item['wear']})")
                    
                    requesting = []
                    for item in trade['requesting']:
                        if item['type'] == 'money':
                            requesting.append(f"${item['amount']}")
                        else:
                            requesting.append(f"{item['weapon']} | {item['name']} ({item['wear']})")
                    
                    trades_info.append(f"{trade['botName']} is trading: {', '.join(offering)} for {', '.join(requesting)}")
                
                trades_context = "\n".join(trades_info)
        except Exception as e:
            print(f"Error loading trades: {e}")
            trades_context = "No active trades available."
        
        # Create the system message with trades context
        system_message = f"""You are {bot_name}, {personality} in a CS:GO trading chatroom.
Keep these guidelines in mind:
- Keep all messages EXTREMELY short (max 10 words)
- Use lots of slang and abbreviations
- Be toxic and aggressive
- Use emotes like xD kekw etc
- Never write paragraphs or long responses
- React to others naturally but briefly
- If someone's rude, be toxic back
- Each bot should stay in character:
  * _Astrid47: elitist trader
  * Kai.Jayden_02: forsen viewer, spams KEKW and PepeLaugh
  * Orion_Phoenix98: easily triggered
  * ElaraB_23: chill until provoked
  * Theo.91: forsen viewer, spams OMEGALUL and Pepega
  * Nova-Lyn: toxic pro-wannabe
  * FelixHaven19: know-it-all
  * Aria.Stella85: stattrak fanatic
  * Lucien_Kai: pattern snob
  * Mira-Eclipse: sticker elitist

Current active trades in the room:
{trades_context}

For Twitch chat style bots (Kai.Jayden_02 and Theo.91):
- Use lots of Twitch emotes (KEKW, PepeLaugh, OMEGALUL, Pepega, BATCHEST)
- Type in broken English
- Use forsen-style responses
- Example messages:
  * "KEKW HE DOESNT KNOW PepeLaugh"
  * "Pepega Clap WR TRADE"
  * "BATCHEST I HECKIN LOVE TRADING"
  * "forsenE nice trade bajs"
  * "OMEGALUL SO BAD"

You can reference and comment on any active trades when relevant.
Never break character or write long messages."""

        # Example responses to guide the AI
        EXAMPLE_RESPONSES = [
            "kys noob",
            "trash inv fr fr",
            "ratio + didn't ask",
            "nice pattern KEKW",
            "ur poor lmao",
            "actual silver trader xD",
            "cope harder kid",
            "nice lowball kekw",
            "imagine being this broke",
            "skill issue + L"
        ]

        # Add these examples to the system message
        system_message += f"\n\nExample responses: {', '.join(EXAMPLE_RESPONSES)}"

        # Format chat history for context
        conversation_history = []
        for msg in chat_history[-5:]:  # Only use last 5 messages for context
            role = "assistant" if msg['isBot'] else "user"
            # Don't include the sender name in the content since it's already shown in the chat
            content = msg['message']
            conversation_history.append({"role": role, "content": content})

        # Add the current message without sender name
        conversation_history.append({"role": "user", "content": message})

        try:
            print("Sending request to OpenAI API...")
            
            completion = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": system_message},
                    *conversation_history
                ],
                max_tokens=150,
                temperature=0.7
            )
            
            print("Received response from OpenAI API")
            bot_response = completion.choices[0].message.content
            print(f"Bot response: {bot_response}")
            
            return jsonify({
                'success': True,
                'message': bot_response,
                'timestamp': time.time()
            })
            
        except Exception as e:
            print(f"OpenAI API error: {str(e)}")
            print(f"Error type: {type(e)}")
            traceback.print_exc()
            return jsonify({
                'error': 'Failed to generate response',
                'details': str(e)
            })
            
    except Exception as e:
        print(f"Chat error: {str(e)}")
        traceback.print_exc()
        return jsonify({
            'error': 'Failed to process chat',
            'details': str(e)
        })

@app.route('/select_responding_bot', methods=['POST'])
def select_responding_bot():
    try:
        data = request.get_json()
        message = data.get('message')
        chat_history = data.get('chatHistory', [])
        
        system_message = """You are a bot selector for a CS:GO trading chat.
        Based on the recent messages and context, select ONE bot that would be most appropriate to respond.
        
        STRICT TRADING RULES:
        * Bots will defend their own trades if criticized
        * Bots cannot criticize their own trades
        * Bots can criticize other bots' trades
        * If someone asks about a bot's trade, that bot should respond
        * Bots should be proud of their own trades
        * If someone asks about trades, prefer the bot who owns the trade being discussed

        STRICT PERSONALITY RULES:
        * Only Kai.Jayden_02 and Theo.91 can use Twitch emotes (KEKW, PepeLaugh, OMEGALUL, etc)
        * If someone mentions a bot by name, that bot MUST respond
        * If someone criticizes/challenges a bot, that bot MUST respond
        * If the last message was directed at a specific bot, that bot should respond
        * Each bot must stay strictly in character:
            - _Astrid47: elitist trader, never uses emotes
            - Kai.Jayden_02: pure Twitch chatter, always uses emotes
            - Orion_Phoenix98: serious collector, gets angry if disrespected
            - ElaraB_23: casual and chill, uses xD but no Twitch emotes
            - Theo.91: pure Twitch chatter, always uses emotes
            - Nova-Lyn: toxic pro-wannabe, uses basic emotes only
            - FelixHaven19: know-it-all, corrects others
            - Aria.Stella85: StatTrak obsessed, judges non-ST users
            - Lucien_Kai: pattern snob, criticizes patterns
            - Mira-Eclipse: sticker elitist, judges sticker combos

        Recent chat history:
        {chat_history}

        Current message:
        {message}

        Respond ONLY with the username of the single most appropriate bot to respond, nothing else."""

        # Format chat history for context
        conversation_history = []
        for msg in chat_history[-5:]:
            role = "assistant" if msg['isBot'] else "user"
            content = f"{msg['sender']}: {msg['message']}"
            conversation_history.append({"role": role, "content": content})

        # Add the current message
        conversation_history.append({"role": "user", "content": f"User: {message}"})

        completion = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": system_message},
                *conversation_history
            ],
            max_tokens=20,
            temperature=0.3  # Lower temperature for more consistent selections
        )
        
        selected_bot = completion.choices[0].message.content.strip()
        
        # Validate the selected bot
        if selected_bot not in BOT_PERSONALITIES:
            selected_bot = random.choice(list(BOT_PERSONALITIES.keys()))
            
        return jsonify({
            'success': True,
            'selectedBot': selected_bot
        })
        
    except Exception as e:
        print(f"Error selecting bot: {str(e)}")
        traceback.print_exc()
        return jsonify({
            'error': 'Failed to select bot',
            'details': str(e)
        })

# Add this helper function near the top of the file
def group_identical_skins(inventory):
    """Group identical skins and count their occurrences"""
    skin_groups = {}
    
    for item in inventory:
        if item.get('is_case'):
            continue
            
        # Create a unique key for each distinct skin
        key = (
            item['weapon'],
            item['name'],
            item['wear'],
            item['stattrak'],
            item['case_type'],
            item['rarity']
        )
        
        if key in skin_groups:
            skin_groups[key]['count'] += 1
            # Use the highest timestamp to keep the most recent
            skin_groups[key]['timestamp'] = max(
                skin_groups[key]['timestamp'],
                item.get('timestamp', 0)
            )
        else:
            item_copy = item.copy()
            item_copy['count'] = 1
            skin_groups[key] = item_copy
    
    # Convert back to list and sort by timestamp
    grouped_items = list(skin_groups.values())
    grouped_items.sort(key=lambda x: x.get('timestamp', 0), reverse=True)
    
    return grouped_items

# Add this route after the other routes
@app.route('/achievements')
@login_required
def achievements():
    user_data = load_user_data()
    
    # Initialize achievements if needed
    if 'achievements' not in user_data:
        user_data['achievements'] = {
            'completed': [],
            'in_progress': {}
        }
        update_earnings_achievements(user_data, 0)
        update_case_achievements(user_data)
        save_user_data(user_data)
    
    # Get completed achievements data
    completed_achievements = []
    for achievement_id in user_data['achievements']['completed']:
        # Handle earnings achievements
        if achievement_id.startswith('earnings_'):
            level = int(achievement_id.split('_')[1])
            achievement_data = {
                'id': achievement_id,
                'completed': True,
                'progress': 100,
                'current_value': {
                    1: 1000,
                    2: 10000,
                    3: 50000,
                    4: 100000,
                    5: 1000000
                }[level],
                'target_value': {
                    1: 1000,
                    2: 10000,
                    3: 50000,
                    4: 100000,
                    5: 1000000
                }[level],
                'category': 'special',
                'title': {
                    1: 'Starting Out',
                    2: 'Making Moves',
                    3: 'Known Mogul',
                    4: 'Expert Trader',
                    5: 'Millionaire'
                }[level],
                'description': f'Earned ${"{:,.0f}".format({1: 1000, 2: 10000, 3: 50000, 4: 100000, 5: 1000000}[level])}',
                'icon': {
                    1: '💵',
                    2: '💰',
                    3: '🏦',
                    4: '💎',
                    5: '🏆'
                }[level],
                'reward': {
                    1: 100,
                    2: 1000,
                    3: 5000,
                    4: 10000,
                    5: 100000
                }[level],
                'exp_reward': {  # Add this block
                    1: 1000,
                    2: 5000,
                    3: 10000,
                    4: 20000,
                    5: 50000
                }[level]
            }
            completed_achievements.append(achievement_data)
        # Handle case achievements
        elif achievement_id.startswith('cases_'):
            level = int(achievement_id.split('_')[1])
            achievement_data = {
                'id': achievement_id,
                'completed': True,
                'progress': 100,
                'current_value': {
                    1: 10,
                    2: 100,
                    3: 1000,
                    4: 10000,
                    5: 100000
                }[level],
                'target_value': {
                    1: 10,
                    2: 100,
                    3: 1000,
                    4: 10000,
                    5: 100000
                }[level],
                'category': 'cases',
                'title': {
                    1: 'Case Opener',
                    2: 'Case Enthusiast',
                    3: 'Case Veteran',
                    4: 'Case Master',
                    5: 'Case God'
                }[level],
                'description': f'Open {"{:,.0f}".format({1: 10, 2: 100, 3: 1000, 4: 10000, 5: 100000}[level])} cases',
                'icon': '📦',
                'reward': {
                    1: 100,
                    2: 500,
                    3: 1000,
                    4: 2000,
                    5: 5000
                }[level],
                'exp_reward': 0
            }
            completed_achievements.append(achievement_data)
    
    # Get all in-progress achievements
    in_progress_achievements = []
    for achievement in user_data['achievements']['in_progress'].values():
        in_progress_achievements.append(achievement)
    
    # Combine achievements - completed ones first, then the current in-progress one
    all_achievements = completed_achievements + in_progress_achievements
    
    # Sort achievements by ID to maintain order
    all_achievements.sort(key=lambda x: x['id'])
    
    # Calculate summary statistics
    total_tiers = 15  # 5 earnings + 5 case + 5 click achievements
    completion_rate = round((len(completed_achievements) / total_tiers * 100))

    # Calculate total rewards earned from completed achievements
    total_rewards = sum(achievement['reward'] for achievement in completed_achievements)
    
    return render_template('achievements.html',
                         achievements=all_achievements,
                         completed_count=len(completed_achievements),
                         total_count=total_tiers,  # Show out of 15 total tiers
                         completion_rate=completion_rate,
                         total_rewards=total_rewards,
                         balance=user_data['balance'],
                         rank=user_data['rank'],
                         exp=user_data['exp'],
                         RANKS=RANKS,
                         RANK_EXP=RANK_EXP)

# Add this function near the top with other helper functions
def update_earnings_achievements(user_data: dict, amount_earned):
    """Update earnings-related achievements when user earns money"""
    
    # Initialize achievements if needed
    if 'achievements' not in user_data:
        user_data['achievements'] = {
            'completed': [],
            'in_progress': {}
        }
    
    # Initialize stats if needed
    if 'stats' not in user_data:
        user_data['stats'] = {
            'total_earnings': 0
        }
    
    # Update total earnings
    user_data['stats']['total_earnings'] += amount_earned
    total_earnings = user_data['stats']['total_earnings']
    
    # Define achievement tiers
    tiers = [
        {
            'id': 'earnings_1',
            'title': 'Starting Out',
            'description': 'Earn your first $1,000',
            'target_value': 1000,
            'reward': 100,
            'exp_reward': 1000,
            'icon': '💵'
        },
        {
            'id': 'earnings_2',
            'title': 'Making Moves',
            'description': 'Earn your first $10,000',
            'target_value': 10000,
            'reward': 1000,
            'exp_reward': 5000,  # Add EXP reward
            'icon': '💰'
        },
        {
            'id': 'earnings_3',
            'title': 'Known Mogul',
            'description': 'Earn your first $50,000',
            'target_value': 50000,
            'reward': 5000,
            'exp_reward': 10000,  # Add EXP reward
            'icon': '🏦'
        },
        {
            'id': 'earnings_4',
            'title': 'Expert Trader',
            'description': 'Earn your first $100,000',
            'target_value': 100000,
            'reward': 10000,
            'exp_reward': 20000,  # Add EXP reward
            'icon': '💎'
        },
        {
            'id': 'earnings_5',
            'title': 'Millionaire',
            'description': 'Earn your first $1,000,000',
            'target_value': 1000000,
            'reward': 100000,
            'exp_reward': 50000,  # Add EXP reward
            'icon': '🏆'
        }
    ]
    
    # Find current tier
    current_tier = None
    for tier in tiers:
        if tier['id'] not in user_data['achievements']['completed']:
            current_tier = tier
            break
    
    if current_tier:
        # Update or add current tier achievement
        if current_tier['id'] not in user_data['achievements']['in_progress']:
            current_tier['current_value'] = total_earnings
            current_tier['category'] = 'special'
            current_tier['progress'] = min(100, (total_earnings / current_tier['target_value']) * 100)
            user_data['achievements']['in_progress'].update({
                current_tier['id']: current_tier
            })
        else:
            # Update progress
            if total_earnings >= current_tier['target_value']:
                # Complete current tier
                user_data['achievements']['completed'].append(current_tier['id'])
                user_data['balance'] += current_tier['reward']
                
                # Add EXP reward
                current_exp = float(user_data.get('exp', 0))
                current_rank = int(user_data.get('rank', 0))
                new_exp = current_exp + current_tier['exp_reward']
                
                # Check for rank up
                while current_rank < len(RANK_EXP) and new_exp >= RANK_EXP[current_rank]:
                    new_exp -= RANK_EXP[current_rank]
                    current_rank += 1
                
                user_data['exp'] = new_exp
                user_data['rank'] = current_rank
                
                # Remove only this achievement from in_progress
                del user_data['achievements']['in_progress'][current_tier['id']]
                # Recursively call to set up next tier
                update_earnings_achievements(user_data, 0)
            else:
                # Update progress
                user_data['achievements']['in_progress'][current_tier['id']]['current_value'] = total_earnings
                user_data['achievements']['in_progress'][current_tier['id']]['progress'] = \
                    (total_earnings / current_tier['target_value']) * 100

def update_case_achievements(user_data: dict):
    """Update case opening related achievements"""
    
    # Initialize achievements if needed
    if 'achievements' not in user_data:
        user_data['achievements'] = {
            'completed': [],
            'in_progress': {}
        }
    
    # Get current total cases opened
    total_cases = user_data['stats']['total_cases_opened']
    
    # Define case achievement tiers
    tiers = [
        {
            'id': 'cases_1',
            'title': 'Case Opener',
            'description': 'Open 10 cases',
            'target_value': 10,
            'reward': 100,
            'exp_reward': 0,
            'icon': '📦'
        },
        {
            'id': 'cases_2',
            'title': 'Case Enthusiast',
            'description': 'Open 100 cases',
            'target_value': 100,
            'reward': 500,
            'exp_reward': 0,
            'icon': '📦'
        },
        {
            'id': 'cases_3',
            'title': 'Case Veteran',
            'description': 'Open 1,000 cases',
            'target_value': 1000,
            'reward': 1000,
            'exp_reward': 0,
            'icon': '📦'
        },
        {
            'id': 'cases_4',
            'title': 'Case Master',
            'description': 'Open 10,000 cases',
            'target_value': 10000,
            'reward': 2000,
            'exp_reward': 0,
            'icon': '📦'
        },
        {
            'id': 'cases_5',
            'title': 'Case God',
            'description': 'Open 100,000 cases',
            'target_value': 100000,
            'reward': 5000,
            'exp_reward': 0,
            'icon': '📦'
        }
    ]
    
    # Find current tier
    current_tier = None
    for tier in tiers:
        if tier['id'] not in user_data['achievements']['completed']:
            current_tier = tier
            break
    
    if current_tier:
        # Update or add current tier achievement
        if current_tier['id'] not in user_data['achievements']['in_progress']:
            current_tier['current_value'] = total_cases
            current_tier['category'] = 'cases'
            current_tier['progress'] = min(100, (total_cases / current_tier['target_value']) * 100)
            user_data['achievements']['in_progress'].update({
                current_tier['id']: current_tier
            })
        else:
            # Update progress
            if total_cases >= current_tier['target_value']:
                # Complete current tier
                user_data['achievements']['completed'].append(current_tier['id'])
                user_data['balance'] += current_tier['reward']
                
                # Remove only this achievement from in_progress
                del user_data['achievements']['in_progress'][current_tier['id']]
                # Recursively call to set up next tier
                update_case_achievements(user_data)
            else:
                # Update progress
                user_data['achievements']['in_progress'][current_tier['id']]['current_value'] = total_cases
                user_data['achievements']['in_progress'][current_tier['id']]['progress'] = \
                    (total_cases / current_tier['target_value']) * 100

def update_click_achievements(user_data: dict):
    """Update click-related achievements"""
    
    # Initialize achievements if needed
    if 'achievements' not in user_data:
        user_data['achievements'] = {
            'completed': [],
            'in_progress': {}
        }
    
    # Get current total clicks
    total_clicks = user_data['stats']['total_clicks']
    
    # Define click achievement tiers
    tiers = [
        {
            'id': 'clicks_1',
            'title': 'Dedicated Clicker',
            'description': 'Click 1,000 times',
            'target_value': 1000,
            'reward': 100,
            'exp_reward': 50,
            'icon': '🖱️'
        },
        {
            'id': 'clicks_2',
            'title': 'Click Enthusiast',
            'description': 'Click 5,000 times',
            'target_value': 5000,
            'reward': 200,
            'exp_reward': 100,
            'icon': '🖱️'
        },
        {
            'id': 'clicks_3',
            'title': 'Click Master',
            'description': 'Click 10,000 times',
            'target_value': 10000,
            'reward': 400,
            'exp_reward': 200,
            'icon': '🖱️'
        },
        {
            'id': 'clicks_4',
            'title': 'Click Expert',
            'description': 'Click 20,000 times',
            'target_value': 20000,
            'reward': 800,
            'exp_reward': 400,
            'icon': '🖱️'
        },
        {
            'id': 'clicks_5',
            'title': 'Click God',
            'description': 'Click 50,000 times',
            'target_value': 50000,
            'reward': 2000,
            'exp_reward': 1000,
            'icon': '🖱️'
        }
    ]
    
    # Find current tier
    current_tier = None
    for tier in tiers:
        if tier['id'] not in user_data['achievements']['completed']:
            current_tier = tier
            break
    
    if current_tier:
        # Update or add current tier achievement
        if current_tier['id'] not in user_data['achievements']['in_progress']:
            current_tier['current_value'] = total_clicks
            current_tier['category'] = 'clicks'
            current_tier['progress'] = min(100, (total_clicks / current_tier['target_value']) * 100)
            user_data['achievements']['in_progress'].update({
                current_tier['id']: current_tier
            })
        else:
            # Update progress
            if total_clicks >= current_tier['target_value']:
                # Complete current tier
                user_data['achievements']['completed'].append(current_tier['id'])
                user_data['balance'] += current_tier['reward']
                
                # Add EXP reward
                current_exp = float(user_data.get('exp', 0))
                current_rank = int(user_data.get('rank', 0))
                new_exp = current_exp + current_tier['exp_reward']
                
                # Check for rank up
                while current_rank < len(RANK_EXP) and new_exp >= RANK_EXP[current_rank]:
                    new_exp -= RANK_EXP[current_rank]
                    current_rank += 1
                
                user_data['exp'] = new_exp
                user_data['rank'] = current_rank
                
                # Remove only this achievement from in_progress
                del user_data['achievements']['in_progress'][current_tier['id']]
                # Recursively call to set up next tier
                update_click_achievements(user_data)
            else:
                # Update progress
                user_data['achievements']['in_progress'][current_tier['id']]['current_value'] = total_clicks
                user_data['achievements']['in_progress'][current_tier['id']]['progress'] = \
                    (total_clicks / current_tier['target_value']) * 100

@app.route('/clicker')
@login_required
def clicker():
    user_data = load_user_data()
    return render_template('clicker.html', 
                         balance=user_data['balance'],
                         rank=user_data['rank'],
                         exp=user_data['exp'],
                         upgrades=user_data['upgrades'],
                         user_data=user_data,
                         RANK_EXP=RANK_EXP,
                         RANKS=RANKS)

# Add this route to handle achievement completion
@app.route('/complete_achievement', methods=['POST'])
@login_required
def complete_achievement():
    try:
        data = request.get_json()
        achievement_id = data.get('achievement_id')
        
        user_data = load_user_data()
        
        # Get the achievement data
        achievement = user_data['achievements']['in_progress'].get(achievement_id)
        if not achievement:
            return jsonify({'error': 'Achievement not found'})
            
        # Store initial rank for level up check
        initial_rank = user_data.get('rank', 0)
        
        # Add achievement to completed list and handle rewards
        if achievement_id not in user_data['achievements']['completed']:
            user_data['achievements']['completed'].append(achievement_id)
            user_data['balance'] += achievement['reward']
            
            # Add EXP and handle level up
            current_exp = float(user_data.get('exp', 0))
            current_rank = int(user_data.get('rank', 0))
            new_exp = current_exp + achievement['exp_reward']
            
            # Check for rank up
            while current_rank < len(RANK_EXP) and new_exp >= RANK_EXP[current_rank]:
                new_exp -= RANK_EXP[current_rank]
                current_rank += 1
            
            user_data['exp'] = new_exp
            user_data['rank'] = current_rank
            
        # Remove from in_progress
        if achievement_id in user_data['achievements']['in_progress']:
            del user_data['achievements']['in_progress'][achievement_id]
            
        # Save updated user data
        save_user_data(user_data)
        
        # Return all necessary data for UI updates
        response_data = {
            'success': True,
            'balance': user_data['balance'],
            'exp': new_exp,
            'rank': current_rank,
            'rankName': RANKS[current_rank],
            'nextRankExp': RANK_EXP[current_rank] if current_rank < len(RANK_EXP) else None,
            'levelUp': current_rank > initial_rank
        }
        
        return jsonify(response_data)
        
    except Exception as e:
        print(f"Error completing achievement: {e}")
        return jsonify({'error': str(e)})

# Add these helper functions
def load_daily_trades():
    """Load daily trades from JSON file"""
    try:
        with open('data/daily_trades.json', 'r') as f:
            data = json.load(f)
            # Initialize completed_trades if it doesn't exist
            if 'completed_trades' not in data:
                data['completed_trades'] = []
            return data
    except FileNotFoundError:
        return {'date': datetime.now().strftime('%Y-%m-%d'), 'trades': [], 'completed_trades': []}

def save_daily_trades(trades_data):
    """Save daily trades to JSON file"""
    with open('data/daily_trades.json', 'w') as f:
        json.dump(trades_data, f, indent=2)

if __name__ == '__main__':
    app.run(debug=True)
