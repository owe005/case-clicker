# Standard library imports
import json
import os
import random
import time
import traceback
from dataclasses import asdict
from datetime import datetime, timedelta
from functools import wraps
from threading import Thread, Lock, Timer
import atexit
from typing import Optional
from werkzeug.utils import safe_join
from pathlib import Path

# Third-party imports
from dotenv import load_dotenv
from flask import (Flask, jsonify, redirect, render_template, request, send_from_directory,
                  session, url_for)

# Local imports
from achievements import (update_case_achievements, update_click_achievements,
                        update_earnings_achievements)
from bots import (client, create_system_message, format_bot_selection_history,
                 format_bot_selection_system_message, format_conversation_history,
                 generate_bot_players, get_trades_context, select_bot_with_ai)

from casino import find_best_skin_combination, handle_blackjack_end
from cases_prices_and_floats import (adjust_price_by_float, generate_float_for_wear,
                                   get_case_prices, load_case, load_skin_price)
from config import (BLACK_NUMBERS, BOT_PERSONALITIES, CASE_DATA, CASE_FILE_MAPPING,
                   CASE_TYPES, CASE_SKINS_FOLDER_NAMES, RANK_EXP, RANKS, RED_NUMBERS, REFRESH_INTERVAL, STICKER_CAPSULE_DATA, STICKER_CAPSULE_FILE_MAPPING)
from daily_trades import generate_daily_trades, load_daily_trades, save_daily_trades
from user_data import create_user_from_dict, load_user_data, save_user_data
from blackjack import BlackjackGame
from sticker_capsules import load_sticker_capsule, get_sticker_capsule_prices, open_sticker_capsule
from auction import load_auction_data, save_auction_data

# Load environment variables
load_dotenv('config.env')

# Initialize Flask app
app = Flask(__name__, 
    static_folder='frontend/dist',  # Point to the Vue build directory
    static_url_path='',            # Serve static files from root URL
    template_folder='frontend/dist'
)

app.secret_key = 'your-secret-key-here'
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = timedelta(days=7)

# Auction-related globals
FEATURED_SKINS = None
LAST_REFRESH_TIME = None
CURRENT_AUCTION = None
AUCTION_BIDS = []
AUCTION_END_TIME = None
AUCTION_BOT_BUDGETS = {}
AUCTION_FILE = 'data/auction_data.json'
LAST_BID_TIME = None
LAST_BIDDER = None
MIN_BID_INCREMENT = 10  # Minimum bid increment in dollars

auction_timer = None
last_auction_check = None

# Add these globals
auction_lock = Lock()
auction_thread = None

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

# Serve Vue App
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_vue_app(path):
    if path.startswith('api/'):
        return {'error': 'Not Found'}, 404
        
    # First try to serve as a static file
    static_file = safe_join(app.static_folder, path)
    if os.path.isfile(static_file):
        return send_from_directory(app.static_folder, path)
        
    # Otherwise return index.html
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/shop')
@login_required
def shop():
    # Since we're using Vue, we'll serve the main app template
    return serve_vue_app('')

@app.route('/inventory')
def inventory():
    # Since we're using Vue, we'll serve the main app template
    # All data will be fetched through the /get_inventory API endpoint
    return serve_vue_app('inventory')

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
            image = None
            for grade, skins in case_data['skins'].items():
                for case_skin in skins:
                    if case_skin['weapon'] == skin.weapon and case_skin['name'] == skin.name:
                        prices = case_skin['prices']
                        wear_key = 'NO' if 'NO' in prices else skin.wear.name
                        price = prices[f"ST_{wear_key}"] if skin.stattrak else prices[wear_key]
                        image = case_skin['image']
                        break
                if price > 0:
                    break
        except Exception as e:
            print(f"Error getting price: {e}")
            price = 0
            image = None
        
        # Generate float value for the new skin
        float_value = generate_float_for_wear(skin.wear.name)
        adjusted_price = adjust_price_by_float(float(price), skin.wear.name, float_value)
        
        skin_dict = {
            'weapon': skin.weapon,
            'name': skin.name,
            'rarity': skin.rarity.name,
            'wear': skin.wear.name,
            'stattrak': skin.stattrak,
            'price': adjusted_price,
            'timestamp': time.time(),
            'case_type': case_type,
            'float_value': float_value,  # Add float_value here
            'is_case': False,
            'image': image  # Add image field
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
        'balance': 100.0,
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
        
        # Get only visible non-case items in display order
        visible_items = []
        visible_indices = []
        
        # First, group identical items to match frontend display
        item_groups = {}
        for i, item in enumerate(inventory):
            if item.get('is_case'):
                continue
                
            # Create a unique key for each distinct skin
            key = (
                item['weapon'],
                item['name'],
                item.get('wear'),
                item.get('stattrak', False),
                item.get('case_type')
            )
            
            if key not in item_groups:
                item_groups[key] = {
                    'items': [item],
                    'indices': [i],
                    'timestamp': item.get('timestamp', 0)
                }
            else:
                item_groups[key]['items'].append(item)
                item_groups[key]['indices'].append(i)
                item_groups[key]['timestamp'] = max(
                    item_groups[key]['timestamp'],
                    item.get('timestamp', 0)
                )
        
        # Convert groups to sorted list matching frontend display
        sorted_groups = sorted(
            item_groups.values(),
            key=lambda x: x['timestamp'],
            reverse=True
        )
        
        # Flatten groups into visible items list
        for group in sorted_groups:
            visible_items.extend(group['items'])
            visible_indices.extend(group['indices'])
        
        if item_index is None or item_index >= len(visible_items):
            return jsonify({'error': 'Item not found'})
        
        # Get the actual inventory index using our mapping
        actual_index = visible_indices[item_index]
        item_to_sell = inventory[actual_index]
        
        print(f"Selling item at visual index {item_index}, actual index {actual_index}")
        print(f"Item details: {item_to_sell}")
        
        if quantity > item_to_sell.get('count', 1):
            return jsonify({'error': 'Invalid quantity'})
        
        # Calculate sale value
        sale_price = float(item_to_sell.get('price', 0)) * quantity
        
        # Store initial rank for level up check
        initial_rank = user_data.get('rank', 0)
        
        # Remove the item from the actual inventory
        inventory.pop(actual_index)
        
        # Update user's balance
        user_data['balance'] = float(user_data['balance']) + sale_price
        
        # Store initial achievements state
        initial_achievements = set(user_data['achievements']['completed'])
        
        # Update achievements with the earned amount
        update_earnings_achievements(user_data, sale_price)
        
        # Save updated user data
        save_user_data(user_data)
        
        # Check if any new achievements were completed
        new_achievements = set(user_data['achievements']['completed']) - initial_achievements
        completed_achievement = None
        if new_achievements:
            achievement_id = list(new_achievements)[0]
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
        traceback.print_exc()
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
    # For Vue routes, we need to serve the main Vue app
    return send_from_directory('frontend/dist', 'index.html')

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
    user.balance += 100000.0
    
    user_data['balance'] = user.balance
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
    case_data = CASE_DATA
    
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
        # Load user inventory
        with open('data/user_inventory.json', 'r') as f:
            user_data = json.load(f)
        
        # Ensure each item has a favorite field (even if false)
        for item in user_data['inventory']:
            if 'favorite' not in item:
                item['favorite'] = False
        
        return jsonify({
            'inventory': user_data['inventory'],
            'balance': user_data['balance'],
            'exp': user_data['exp'],
            'rank': user_data['rank'],
            'upgrades': user_data.get('upgrades', {})
        })
    except Exception as e:
        print(f"Error in get_inventory: {str(e)}")
        return jsonify({'error': 'Failed to get inventory'}), 500

@app.route('/api/get_user_data')
def get_user_data():
    user_data = load_user_data()
    user = create_user_from_dict(user_data)
    return jsonify({
        'exp': int(user.exp),
        'rank': user.rank,
        'rankName': RANKS[user.rank],
        'nextRankExp': RANK_EXP[user.rank] if user.rank < len(RANK_EXP) else None,
        'balance': user.balance,
        'inventory': user.inventory,
        'upgrades': user_data.get('upgrades', {}),  # Add upgrades to response
        'case_progress': user_data.get('case_progress', 0)  # Add case progress too
    })

@app.route('/api/data/case_contents/<case_type>')
def get_case_contents(case_type):
    # Use CASE_FILE_MAPPING from config.py
    if case_type not in CASE_FILE_MAPPING:
        print(f"Invalid case type requested: {case_type}")
        return jsonify({'error': 'Invalid case type'}), 404
        
    try:
        file_path = f'cases/{CASE_FILE_MAPPING[case_type]}.json'
        print(f"Attempting to load case file: {file_path}")
        
        if not os.path.exists(file_path):
            print(f"File not found: {file_path}")
            return jsonify({'error': 'Case data not found'}), 404
            
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
    return serve_vue_app('casino')

@app.route('/coinflip')
@login_required
def coinflip():
    # For Vue routes, we need to serve the main Vue app
    return serve_vue_app('')

@app.route('/api/coinflip/data')
@login_required
def get_coinflip_data():
    user_data = load_user_data()
    user = create_user_from_dict(user_data)
    return jsonify({
        'balance': user.balance,
        'rank': user.rank,
        'exp': user.exp,
        'ranks': RANKS,
        'rank_exp': RANK_EXP
    })

@app.route('/play_coinflip', methods=['POST'])
@login_required
def play_coinflip():
    try:
        data = request.get_json()
        amount = float(data.get('amount', 0))
        side = data.get('side')

        if not side or side not in ['ct', 't']:
            return jsonify({'error': 'Invalid side selection'})

        user_data = load_user_data()
        current_balance = float(user_data['balance'])

        if amount <= 0:
            return jsonify({'error': 'Invalid bet amount'})

        if amount > current_balance:
            return jsonify({'error': 'Insufficient funds'})

        # Immediately deduct the bet amount
        user_data['balance'] = current_balance - amount
        save_user_data(user_data)

        # Determine game result
        result = random.choice(['ct', 't'])
        won = result == side

        # Calculate final balance but don't save it yet
        final_balance = user_data['balance']
        if won:
            final_balance += (amount * 2)

        # Store the result in session
        session['coinflip_result'] = {
            'result': result,
            'won': won,
            'amount': amount,
            'current_balance': user_data['balance'],
            'final_balance': final_balance
        }

        return jsonify({
            'success': True,
            'result': result,
            'won': won,
            'current_balance': user_data['balance']
        })

    except Exception as e:
        print(f"Error in play_coinflip: {e}")
        return jsonify({'error': 'Failed to play coinflip'})

@app.route('/update_coinflip_balance', methods=['POST'])
@login_required
def update_coinflip_balance():
    try:
        # Get stored game result
        result = session.get('coinflip_result')
        if not result:
            return jsonify({'error': 'No active game found'})

        # If player won, update their balance with winnings now
        if result['won']:
            user_data = load_user_data()
            user_data['balance'] = result['final_balance']
            save_user_data(user_data)

        # Return the final balance
        return jsonify({
            'success': True,
            'balance': result['final_balance']
        })

    except Exception as e:
        print(f"Error updating balance: {e}")
        return jsonify({'error': 'Failed to update balance'})

@app.route('/roulette')
@login_required
def roulette():
    # Since we're using Vue, we'll serve the main app template
    return serve_vue_app('')

@app.route('/play_roulette', methods=['POST'])
@login_required
def play_roulette():
    try:
        data = request.get_json()
        lightning_numbers = set(data.get('lightningNumbers', []))
        clear_previous_bets = data.get('clearPreviousBets', False)
        
        # Load current user data
        user_data = load_user_data()
        current_balance = float(user_data['balance'])
        
        # Determine result
        result = random.randint(0, 36)
        
        # Clear previous bets if requested or if no bets are sent
        if clear_previous_bets or data.get('bets') is None:
            session.pop('roulette_bet', None)
            session.pop('roulette_result', None)
            return jsonify({
                'success': True,
                'result': result,
                'balance': current_balance
            })
        
        # Get the stored bet info from session
        bet_info = session.get('roulette_bet')
        
        # If no bets or spectating, just return the result
        if not bet_info or not bet_info.get('bets'):
            return jsonify({
                'success': True,
                'result': result,
                'balance': current_balance
            })
            
        # Verify bet was properly closed
        if not bet_info.get('balance_deducted'):
            return jsonify({'error': 'Bet not properly closed'})
            
        bets = bet_info['bets']
        total_bet = bet_info['total_bet']
        
        # Calculate winnings for placed bets
        winnings = 0
        
        for bet_type, amount in bets.items():
            amount = float(amount)
            if bet_type.isdigit():  # Single number bet
                if int(bet_type) == result:
                    win_amount = amount * 36
                    winnings += win_amount
                    update_earnings_achievements(user_data, win_amount - amount)
            elif bet_type in ['red', 'black']:
                if (bet_type == 'red' and result in RED_NUMBERS) or \
                   (bet_type == 'black' and result in BLACK_NUMBERS):
                    win_amount = amount * 2
                    winnings += win_amount
                    update_earnings_achievements(user_data, win_amount - amount)
            elif bet_type in ['even', 'odd']:
                if result != 0 and \
                   ((bet_type == 'even' and result % 2 == 0) or \
                    (bet_type == 'odd' and result % 2 == 1)):
                    win_amount = amount * 2
                    winnings += win_amount
                    update_earnings_achievements(user_data, win_amount - amount)
            elif bet_type in ['1-18', '19-36']:
                if (bet_type == '1-18' and 1 <= result <= 18) or \
                   (bet_type == '19-36' and 19 <= result <= 36):
                    win_amount = amount * 2
                    winnings += win_amount
                    update_earnings_achievements(user_data, win_amount - amount)
            elif bet_type in ['1st12', '2nd12', '3rd12']:
                if (bet_type == '1st12' and 1 <= result <= 12) or \
                   (bet_type == '2nd12' and 13 <= result <= 24) or \
                   (bet_type == '3rd12' and 25 <= result <= 36):
                    win_amount = amount * 3
                    winnings += win_amount
                    update_earnings_achievements(user_data, win_amount - amount)
        
        # Update final balance with winnings
        final_balance = float(user_data['balance']) + winnings
        user_data['balance'] = final_balance
        save_user_data(user_data)
        
        # Clear the bet info from session after processing
        session.pop('roulette_bet', None)
        session.pop('roulette_result', None)
        
        return jsonify({
            'success': True,
            'result': result,
            'winnings': winnings,
            'balance': final_balance,
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

@app.route('/crash')
@login_required
def crash():
    # For Vue routes, we need to serve the main Vue app
    return send_from_directory('frontend/dist', 'index.html')

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

@app.route('/sell/all', methods=['POST'])
def sell_all():
    try:
        user_data = load_user_data()
        inventory = user_data.get('inventory', [])
        
        # Get only non-case items
        skins = [item for item in inventory if not item.get('is_case')]
        cases = [item for item in inventory if item.get('is_case')]
        
        if not skins:
            return jsonify({'error': 'No items to sell'})
            
        # Calculate total value
        total_value = sum(float(item.get('price', 0)) for item in skins)
        
        # Store initial rank and achievements state
        initial_rank = user_data.get('rank', 0)
        initial_achievements = set(user_data['achievements']['completed'])
        
        # Update user's balance
        user_data['balance'] = float(user_data['balance']) + total_value
        
        # Keep only cases in inventory
        user_data['inventory'] = cases
        
        # Update achievements with the total earned amount
        update_earnings_achievements(user_data, total_value)
        
        # Check if any new achievements were completed
        new_achievements = set(user_data['achievements']['completed']) - initial_achievements
        completed_achievement = None
        if new_achievements:
            achievement_id = list(new_achievements)[0]
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
        
        return jsonify({
            'success': True,
            'balance': user_data['balance'],
            'sold_price': total_value,
            'remaining_cases': cases,
            'exp': user_data['exp'],
            'rank': user_data['rank'],
            'rankName': RANKS[user_data['rank']],
            'nextRankExp': RANK_EXP[user_data['rank']] if user_data['rank'] < len(RANK_EXP) else None,
            'levelUp': user_data['rank'] > initial_rank,
            'achievement': completed_achievement
        })
        
    except Exception as e:
        print(f"Error in sell_all: {e}")
        return jsonify({'error': 'Failed to sell items'})

@app.route('/jackpot')
@login_required
def jackpot():
    # For Vue routes, we need to serve the main Vue app
    return serve_vue_app('jackpot')

@app.route('/get_jackpot_inventory')
@login_required
def get_jackpot_inventory():
    try:
        user_data = load_user_data()
        inventory = user_data.get('inventory', [])
        
        # Filter out cases and sticker capsules
        eligible_items = [
            item for item in inventory
            if not item.get('is_case') and not item.get('is_capsule')
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
                if selected_item.get('is_sticker'):
                    # Match sticker items
                    if (inv_item.get('is_sticker') and
                        inv_item.get('name') == selected_item['name'] and
                        inv_item.get('case_type') == selected_item['case_type'] and
                        i not in found_items):
                        item_found = True
                        found_items.append(i)
                        break
                else:
                    # Match weapon skin items
                    if (inv_item.get('weapon') == selected_item['weapon'] and 
                        inv_item.get('name') == selected_item['name'] and
                        inv_item.get('wear') == selected_item['wear'] and
                        inv_item.get('stattrak') == selected_item['stattrak'] and
                        i not in found_items):
                        item_found = True
                        found_items.append(i)
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
                    # Add timestamp to each item
                    for item in player['items']:
                        item['timestamp'] = int(time.time())
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
        shop_price = float(data.get('price', 0))  # This is the shop price

        if shop_price > current_balance:
            return jsonify({'error': 'Insufficient funds'})

        # Generate float value if not provided
        if 'float_value' not in data:
            data['float_value'] = generate_float_for_wear(data['wear'])

        # Calculate the adjusted price using the same logic as inventory
        adjusted_price = load_skin_price(
            f"{data['weapon']} | {data['name']}", 
            data['case_type'],
            data['wear'],
            data['float_value'],
            data.get('stattrak', False)
        )

        # Create skin item with adjusted price
        skin_item = {
            'weapon': data['weapon'],
            'name': data['name'],
            'rarity': data['rarity'],
            'wear': data['wear'],
            'stattrak': data['stattrak'],
            'price': adjusted_price,  # Use adjusted price here
            'float_value': data['float_value'],
            'timestamp': time.time(),
            'case_type': data['case_type'],
            'is_case': False,
            'image': data['image']  # Add image field from request data
        }

        # Update user data using shop price for purchase
        user_data['balance'] = current_balance - shop_price
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
    
    if not FEATURED_SKINS or not LAST_REFRESH_TIME or (current_time - LAST_REFRESH_TIME) >= REFRESH_INTERVAL:
        try:
            # Load all case contents
            all_skins = []
            
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
                                wear_options = [w for w in item['prices'].keys() 
                                              if not w.startswith('ST_') and w != 'NO']
                                if wear_options:
                                    wear = random.choice(wear_options)
                                    float_value = generate_float_for_wear(wear)
                                    base_price = float(item['prices'][wear])
                                    adjusted_price = adjust_price_by_float(base_price, wear, float_value)
                                    
                                    # Apply 10% shop markup
                                    shop_price = adjusted_price * 1.1
                                    
                                    all_skins.append({
                                        'weapon': item['weapon'],
                                        'name': item['name'],
                                        'prices': item['prices'],
                                        'case_type': case_type,
                                        'case_file': file_name,
                                        'image': item.get('image', f"{item['weapon'].lower().replace(' ', '')}_{item['name'].lower().replace(' ', '_')}.png"),
                                        'rarity': grade.upper(),
                                        'wear': wear,
                                        'float_value': float_value,
                                        'base_price': base_price,
                                        'adjusted_price': adjusted_price,  # Store original adjusted price
                                        'price': shop_price,  # Display price with markup
                                        'stattrak': random.random() < 0.1  # 10% chance for StatTrak
                                    })
                except Exception as e:
                    print(f"Error loading case {case_type}: {e}")
                    continue
            
            # Select one random skin from each rarity
            FEATURED_SKINS = {}
            rarities = ['GOLD', 'RED', 'PINK', 'PURPLE', 'BLUE']
            
            for rarity in rarities:
                rarity_skins = [skin for skin in all_skins if skin['rarity'] == rarity]
                if rarity_skins:
                    FEATURED_SKINS[rarity] = random.choice(rarity_skins)
            
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
    # For Vue routes, we need to serve the main Vue app
    return send_from_directory('frontend/dist', 'index.html')

@app.route('/play_upgrade', methods=['POST'])
@login_required
def play_upgrade():
    try:
        data = request.get_json()
        items = data.get('items', [])
        multiplier = float(data.get('multiplier', 2))
        
        if not items:
            return jsonify({'error': 'No items selected'})
            
        # Load user data
        user_data = load_user_data()
        inventory = user_data.get('inventory', [])
        
        # Calculate total value of selected items
        total_value = sum(float(item['price']) for item in items)
        target_value = total_value * multiplier
        
        # Load all possible skins first
        available_skins = []
        
        # Load weapon skins
        for case_type, file_name in CASE_FILE_MAPPING.items():
            try:
                with open(f'cases/{file_name}.json', 'r') as f:
                    case_data = json.load(f)
                    for grade, skins in case_data['skins'].items():
                        for skin in skins:
                            # First get the base wear prices
                            for wear, base_price in skin['prices'].items():
                                if wear != 'NO' and not wear.startswith('ST_'):
                                    float_value = generate_float_for_wear(wear)
                                    
                                    # Handle normal version
                                    normal_price = float(base_price)
                                    adjusted_normal_price = adjust_price_by_float(normal_price, wear, float_value)
                                    
                                    # Add normal version
                                    available_skins.append({
                                        'weapon': skin['weapon'],
                                        'name': skin['name'],
                                        'wear': wear,
                                        'price': adjusted_normal_price,
                                        'base_price': normal_price,
                                        'rarity': grade.upper(),
                                        'case_type': case_type,
                                        'case_file': file_name,
                                        'stattrak': False,
                                        'timestamp': time.time(),
                                        'float_value': float_value,
                                        'image': skin['image'],
                                        'is_sticker': False
                                    })
                                    
                                    # Handle StatTrak version if available
                                    st_key = f'ST_{wear}'
                                    if st_key in skin['prices']:
                                        st_base_price = float(skin['prices'][st_key])
                                        # Use StatTrak base price for adjustment
                                        adjusted_st_price = adjust_price_by_float(st_base_price, wear, float_value)
                                        
                                        available_skins.append({
                                            'weapon': skin['weapon'],
                                            'name': skin['name'],
                                            'wear': wear,
                                            'price': adjusted_st_price,
                                            'base_price': st_base_price,
                                            'rarity': grade.upper(),
                                            'case_type': case_type,
                                            'case_file': file_name,
                                            'stattrak': True,
                                            'timestamp': time.time(),
                                            'float_value': float_value,
                                            'image': skin['image'],
                                            'is_sticker': False
                                        })
            except Exception as e:
                print(f"Error loading case {case_type}: {e}")
                continue
                
        # Load stickers
        for capsule_type, file_name in STICKER_CAPSULE_FILE_MAPPING.items():
            try:
                with open(f'stickers/{file_name}.json', 'r') as f:
                    capsule_data = json.load(f)
                    for grade, stickers in capsule_data['stickers'].items():
                        for sticker in stickers:
                            available_skins.append({
                                'name': sticker['name'],
                                'price': float(sticker['price']),
                                'rarity': grade.upper(),
                                'case_type': capsule_type,
                                'case_file': file_name,  # Add case_file field
                                'image': sticker['image'],
                                'is_sticker': True,
                                'timestamp': time.time()
                            })
            except Exception as e:
                print(f"Error loading sticker capsule {capsule_type}: {e}")
                continue
        
        # Find potential winning skins before determining outcome
        won_skins = find_best_skin_combination(available_skins, target_value)
        
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
        
        # Remove selected items from inventory
        selected_indices = []
        for selected_item in items:
            for i, inv_item in enumerate(inventory):
                if i not in selected_indices:
                    if selected_item.get('is_sticker'):
                        # Match stickers by name and case_type
                        if (inv_item.get('is_sticker') and
                            inv_item.get('name') == selected_item['name'] and
                            inv_item.get('case_type') == selected_item['case_type']):
                            selected_indices.append(i)
                            break
                    else:
                        # Match skins by weapon, name, wear and stattrak
                        if (not inv_item.get('is_sticker') and
                            inv_item.get('weapon') == selected_item['weapon'] and
                            inv_item.get('name') == selected_item['name'] and
                            inv_item.get('wear') == selected_item['wear'] and
                            inv_item.get('stattrak') == selected_item['stattrak']):
                            selected_indices.append(i)
                            break
        
        # Create new inventory without selected items
        new_inventory = [item for i, item in enumerate(inventory) 
                       if i not in selected_indices]
        
        if success:
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
            # Update user data with removed items
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

@app.route('/trading')
@login_required
def trading():
    # For Vue routes, we need to serve the main Vue app
    return serve_vue_app('')

@app.route('/get_trades')
@login_required
def get_trades():
    try:
        trades_data = load_daily_trades()
        current_date = datetime.now().strftime('%Y-%m-%d')
        
        # Check if trades need to be regenerated
        if not trades_data.get('trades') or trades_data.get('date') != current_date:
            # Generate new trades for the day
            trades_data['trades'] = generate_daily_trades()
            trades_data['date'] = current_date
            trades_data['completed_trades'] = []  # Reset completed trades
            save_daily_trades(trades_data)
        
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
        
        # Check for required items (skins and stickers)
        if any(item['type'] == 'skin' for item in trade['requesting']):
            required_items = [item for item in trade['requesting'] if item['type'] == 'skin']
            for required_item in required_items:
                item_found = False
                for inv_item in inventory:
                    if required_item.get('is_sticker'):
                        if (inv_item.get('is_sticker') and
                            inv_item['name'] == required_item['name'] and
                            inv_item['case_type'] == required_item['case_type']):
                            item_found = True
                            break
                    else:
                        if (not inv_item.get('is_case') and not inv_item.get('is_sticker') and
                            inv_item['weapon'] == required_item['weapon'] and
                            inv_item['name'] == required_item['name'] and
                            inv_item['wear'] == required_item['wear'] and
                            inv_item['stattrak'] == required_item['stattrak']):
                            item_found = True
                            break
                if not item_found:
                    return jsonify({'error': f"Missing item: {required_item.get('weapon', '')} {required_item['name']}"})
        
        # Process inventory changes
        new_inventory = []
        used_indices = set()
        
        # Remove requested items
        for required_item in (item for item in trade['requesting'] if item['type'] == 'skin'):
            for i, inv_item in enumerate(inventory):
                if i not in used_indices:
                    if required_item.get('is_sticker'):
                        if (inv_item.get('is_sticker') and
                            inv_item['name'] == required_item['name'] and
                            inv_item['case_type'] == required_item['case_type']):
                            used_indices.add(i)
                            break
                    else:
                        if (not inv_item.get('is_case') and not inv_item.get('is_sticker') and
                            inv_item['weapon'] == required_item['weapon'] and
                            inv_item['name'] == required_item['name'] and
                            inv_item['wear'] == required_item['wear'] and
                            inv_item['stattrak'] == required_item['stattrak']):
                            used_indices.add(i)
                            break
        
        # Keep items that weren't traded
        new_inventory = [item for i, item in enumerate(inventory) if i not in used_indices]
        
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
        
        # Add offered items
        for offered_item in trade['offering']:
            if offered_item['type'] == 'skin':
                if offered_item.get('is_sticker'):
                    sticker_item = {
                        'name': offered_item['name'],
                        'price': offered_item['price'],
                        'rarity': offered_item['rarity'],
                        'case_type': offered_item['case_type'],
                        'image': offered_item['image'],
                        'timestamp': time.time(),
                        'is_sticker': True
                    }
                    new_inventory.append(sticker_item)
                else:
                    # Generate float value if not present
                    if 'float_value' not in offered_item:
                        offered_item['float_value'] = generate_float_for_wear(offered_item['wear'])
                    
                    skin_item = {
                        'weapon': offered_item['weapon'],
                        'name': offered_item['name'],
                        'wear': offered_item['wear'],
                        'stattrak': offered_item['stattrak'],
                        'price': offered_item['price'],
                        'rarity': offered_item['rarity'],
                        'case_type': offered_item['case_type'],
                        'case_file': offered_item.get('case_file'),
                        'float_value': offered_item['float_value'],
                        'image': offered_item['image'],
                        'timestamp': time.time(),
                        'is_case': False,
                        'is_sticker': False
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
            
        personality = BOT_PERSONALITIES.get(bot_name, "A friendly CS:GO skin trader")
        trades_context = get_trades_context()
        system_message = create_system_message(bot_name, personality, trades_context)

        # Add example responses
        EXAMPLE_RESPONSES = [
            "kys noob", "trash inv fr fr", "ratio + didn't ask",
            "nice pattern KEKW", "ur poor lmao", "actual silver trader xD",
            "cope harder kid", "nice lowball kekw", "imagine being this broke",
            "skill issue + L"
        ]
        system_message += f"\n\nExample responses: {', '.join(EXAMPLE_RESPONSES)}"

        conversation_history = format_conversation_history(chat_history, message)

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
        
        system_message = format_bot_selection_system_message(chat_history, message)
        conversation_history = format_bot_selection_history(chat_history, message)
        selected_bot = select_bot_with_ai(system_message, conversation_history)
            
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

@app.route('/clicker')
@login_required
def clicker():
    # For Vue routes, we need to serve the main Vue app
    return send_from_directory('frontend/dist', 'index.html')

# Add a catch-all route for Vue router
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def catch_all(path):
    if path and (path.startswith('api/') or path.startswith('static/')):
        return app.send_static_file('404.html'), 404
    return send_from_directory('frontend/dist', 'index.html')

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

@app.route('/sell/item', methods=['POST'])
def sell_specific_item():
    try:
        data = request.get_json() or {}
        item_data = data.get('item')
        quantity = int(data.get('quantity', 1))
        
        if not item_data:
            return jsonify({'error': 'No item data provided'})
            
        user_data = load_user_data()
        inventory = user_data['inventory']
        
        # Find the specific item in inventory
        item_index = None
        for i, inv_item in enumerate(inventory):
            if inv_item.get('is_case') or inv_item.get('is_capsule'):
                continue
                
            # First check if either item is a sticker
            is_sticker_inv = inv_item.get('is_sticker', False)
            is_sticker_data = item_data.get('is_sticker', False)
            
            # If one is a sticker and the other isn't, skip
            if is_sticker_inv != is_sticker_data:
                continue
                
            if is_sticker_inv:
                # For sticker items, compare name and case_type
                if (inv_item['name'] == item_data['name'] and
                    inv_item['case_type'] == item_data['case_type']):
                    item_index = i
                    break
            else:
                # For weapon skins, compare all attributes
                if (inv_item['weapon'] == item_data['weapon'] and
                    inv_item['name'] == item_data['name'] and
                    inv_item['wear'] == item_data['wear'] and
                    inv_item.get('stattrak', False) == item_data.get('stattrak', False) and
                    abs(float(inv_item['float_value']) - float(item_data['float_value'])) < 0.0001):
                    item_index = i
                    break
        
        if item_index is None:
            return jsonify({'error': 'Item not found in inventory'})
            
        item_to_sell = inventory[item_index]
        
        # Calculate sale value
        sale_price = float(item_to_sell.get('price', 0)) * quantity
        
        # Store initial rank for level up check
        initial_rank = user_data.get('rank', 0)
        
        # Remove the item from inventory
        inventory.pop(item_index)

        # Update user's balance
        user_data['balance'] = float(user_data['balance']) + sale_price
        
        # Update achievements
        initial_achievements = set(user_data['achievements']['completed'])
        update_earnings_achievements(user_data, sale_price)
        
        # Save updated user data
        save_user_data(user_data)
                
        return jsonify({
            'success': True,
            'balance': user_data['balance'],
            'exp': user_data['exp'],
            'rank': user_data['rank'],
            'rankName': RANKS[user_data['rank']],
            'nextRankExp': RANK_EXP[user_data['rank']] if user_data['rank'] < len(RANK_EXP) else None,
            'levelUp': user_data['rank'] > initial_rank,
            'sold_price': sale_price
        })
        
    except Exception as e:
        print(f"Error in sell_specific_item: {e}")
        traceback.print_exc()
        return jsonify({'error': 'Failed to sell item'})

def start_auction_thread():
    """Start the background thread for auction processing"""
    global auction_thread
    if auction_thread is None or not auction_thread.is_alive():
        auction_thread = Thread(target=process_auction_background, daemon=True)
        auction_thread.start()

def process_auction_background():
    """Background thread to process bot bids"""
    global CURRENT_AUCTION, AUCTION_END_TIME, AUCTION_BIDS, last_auction_check
    
    while True:
        try:
            current_time = datetime.now()
            
            with auction_lock:
                # Check if auction has ended
                if CURRENT_AUCTION and current_time >= AUCTION_END_TIME:
                    complete_auction()
                    break
                
                # Only process bids if auction is active
                if CURRENT_AUCTION and current_time < AUCTION_END_TIME:
                    # Update last check time
                    last_auction_check = current_time
                    process_bot_bids()
            
            # Sleep for a random interval
            time_remaining = (AUCTION_END_TIME - current_time).total_seconds()
            if time_remaining < 60:  # Last minute
                sleep_time = random.uniform(1, 3)
            elif time_remaining < 300:  # Last 5 minutes
                sleep_time = random.uniform(3, 8)
            elif time_remaining < 600:  # Last 10 minutes
                sleep_time = random.uniform(5, 15)
            else:  # Earlier in auction
                sleep_time = random.uniform(15, 30)
            
            time.sleep(sleep_time)
            
        except Exception as e:
            print(f"Error in auction background thread: {e}")
            time.sleep(5)  # Sleep on error to prevent rapid retries

@app.route('/auction')
@login_required
def auction():
    # For Vue routes, we need to serve the main Vue app
    return render_template('index.html')

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
            budget = base_price * random.uniform(0.9, 1.1)
        elif strategy == 'high':
            # High budget: +10% to +100% of base price
            budget = base_price * random.uniform(1.1, 2.0)
        else:  # low
            # Low budget: 50% to 90% of base price
            budget = base_price * random.uniform(0.5, 0.9)
        
        budgets[bot_name] = {
            "budget": budget,
            "status": "online"
        }
    
    return budgets

def get_current_bid():
    """Get the current highest bid"""
    if not AUCTION_BIDS:
        return CURRENT_AUCTION['base_price'] * 0.1  # Start at 10% of base price
    return AUCTION_BIDS[-1]['amount']

@app.route('/place_bid', methods=['POST'])
@login_required
def place_bid():
    try:
        data = request.get_json()
        bid_amount = float(data.get('amount', 0))
        
        user_data = load_user_data()
        current_balance = float(user_data['balance'])
        
        if bid_amount > current_balance:
            return jsonify({'error': 'Insufficient funds'})
        
        with auction_lock:
            # Load current auction state from file
            auction_data = load_auction_data()
            if not auction_data:
                return jsonify({'error': 'No active auction'})
            
            current_bid = auction_data.get('current_bid', 0)
            if bid_amount <= current_bid:
                return jsonify({'error': f'Bid must be higher than ${current_bid:.2f}'})
            
            # If user had a previous bid, refund it
            if auction_data['bids'] and auction_data['bids'][-1]['bidder'] == 'You':
                previous_bid = auction_data['bids'][-1]['amount']
                current_balance += previous_bid
            
            # Deduct new bid amount
            current_balance -= bid_amount
            
            # Update user's balance
            user_data['balance'] = current_balance
            save_user_data(user_data)
            
            # Add bid to auction data
            new_bid = {
                'bidder': 'You',
                'amount': bid_amount,
                'timestamp': datetime.now().isoformat()
            }
            auction_data['bids'].append(new_bid)
            auction_data['current_bid'] = bid_amount
            
            # Extend timer by 15 seconds only if time remaining is less than 1 minute
            current_end_time = datetime.fromisoformat(auction_data['end_time'])
            time_remaining = (current_end_time - datetime.now()).total_seconds()
            if time_remaining < 60:
                new_end_time = current_end_time + timedelta(seconds=15)
                auction_data['end_time'] = new_end_time.isoformat()
                print(f"Timer extended by 15s. New end time: {new_end_time}")
            
            # Save updated auction data
            save_auction_data(auction_data)
            
            # Update global state to match file
            global CURRENT_AUCTION, AUCTION_BIDS, AUCTION_END_TIME, LAST_BIDDER
            AUCTION_BIDS = auction_data['bids']
            AUCTION_END_TIME = datetime.fromisoformat(auction_data['end_time'])
            LAST_BIDDER = 'You'
        
        return jsonify({
            'success': True,
            'current_bid': bid_amount,
            'end_time': auction_data['end_time'],
            'bids': auction_data['bids'],
            'balance': current_balance
        })
        
    except Exception as e:
        print(f"Error placing bid: {e}")
        return jsonify({'error': 'Failed to place bid'})

def process_bot_bids(trigger_bid=None):
    """Process automatic bot bidding responses"""
    global LAST_BIDDER, AUCTION_END_TIME
    
    # Load current auction state from file
    auction_data = load_auction_data()
    if not auction_data:
        return
        
    time_remaining = (datetime.fromisoformat(auction_data['end_time']) - datetime.now()).total_seconds()
    
    # Calculate base response chance based on time remaining
    if time_remaining < 60:  # Last minute
        base_chance = 0.4
    elif time_remaining < 300:  # Last 5 minutes
        base_chance = 0.25
    elif time_remaining < 600:  # Last 10 minutes
        base_chance = 0.15
    elif time_remaining < 1800:  # Last 30 minutes
        base_chance = 0.08
    
    # Increase chance if there was a recent bid
    if trigger_bid:
        base_chance *= 1.2
    
    # Process bot responses - only consider online bots with budgets
    active_bots = [(name, data['budget']) 
                   for name, data in auction_data['bot_budgets'].items() 
                   if data['status'] == 'online' and name != LAST_BIDDER]
    
    random.shuffle(active_bots)  # Randomize bot order
    
    for bot_name, max_budget in active_bots:
        if random.random() < base_chance:
            current_bid = auction_data['current_bid']
            if current_bid < max_budget:
                # Calculate bid increment (larger near end)
                if time_remaining < 600:
                    increment = random.uniform(MIN_BID_INCREMENT * 1.5, MIN_BID_INCREMENT * 3)
                else:
                    increment = random.uniform(MIN_BID_INCREMENT, MIN_BID_INCREMENT * 1.5)
                
                # Add some randomness to bid amounts
                increment *= random.uniform(1.0, 1.2)
                
                new_bid = min(current_bid + increment, max_budget)
                if new_bid > current_bid:
                    # If player was outbid, refund their bid
                    if auction_data['bids'] and auction_data['bids'][-1]['bidder'] == 'You':
                        try:
                            user_data = load_user_data()
                            user_data['balance'] += auction_data['bids'][-1]['amount']
                            save_user_data(user_data)
                        except Exception as e:
                            print(f"Error refunding outbid: {e}")
                    
                    # Update auction data
                    auction_data['bids'].append({
                        'bidder': bot_name,
                        'amount': new_bid,
                        'timestamp': datetime.now().isoformat()
                    })
                    auction_data['current_bid'] = new_bid
                    
                    # Extend timer by 15 seconds only if time remaining is less than 1 minute
                    current_end_time = datetime.fromisoformat(auction_data['end_time'])
                    time_remaining = (current_end_time - datetime.now()).total_seconds()
                    if time_remaining < 60:
                        new_end_time = current_end_time + timedelta(seconds=15)
                        auction_data['end_time'] = new_end_time.isoformat()
                        print(f"Timer extended by 15s (bot bid). New end time: {new_end_time}")
                    
                    # Save updated auction data
                    save_auction_data(auction_data)
                    
                    # Update global state
                    global AUCTION_BIDS
                    AUCTION_BIDS = auction_data['bids']
                    LAST_BIDDER = bot_name
                    
                    # Small chance for immediate response from another bot
                    if random.random() < 0.3:
                        process_bot_bids(trigger_bid=True)
                    return  # Only one bot bids at a time

# Add new debug route
@app.route('/debug/decrease_timer', methods=['POST'])
@login_required
def decrease_timer():
    if not app.debug:
        return jsonify({'error': 'Debug mode not enabled'})
    
    with auction_lock:
        # Load current auction data
        auction_data = load_auction_data()
        if not auction_data:
            return jsonify({'error': 'No active auction'})
        
        data = request.get_json()
        minutes = int(data.get('minutes', 30))  # Default to 30 if not specified
        
        # Update end time in auction data
        current_end_time = datetime.fromisoformat(auction_data['end_time'])
        new_end_time = current_end_time - timedelta(minutes=minutes)
        auction_data['end_time'] = new_end_time.isoformat()
        
        # Save updated auction data
        save_auction_data(auction_data)
        
        # Update global state
        global AUCTION_END_TIME
        AUCTION_END_TIME = new_end_time
        
        return jsonify({
            'success': True,
            'new_end_time': new_end_time.isoformat()
        })

# Add this function to handle auction completion
def complete_auction():
    """Handle auction completion and award item to winner"""
    global CURRENT_AUCTION, AUCTION_BIDS, AUCTION_END_TIME
    
    if not AUCTION_BIDS:
        return
        
    # Get winning bid
    winning_bid = AUCTION_BIDS[-1]
    print(f"\nAuction completed! Winner: {winning_bid['bidder']} with ${winning_bid['amount']:,.2f}")
    
    # Load current auction data
    auction_data = load_auction_data()
    
    # Create history entry
    print("\nCreating history entry from current auction:", CURRENT_AUCTION)
    history_entry = {
        "weapon": CURRENT_AUCTION['weapon'],
        "name": CURRENT_AUCTION['name'],
        "wear": CURRENT_AUCTION['wear'],
        "rarity": CURRENT_AUCTION['rarity'],
        "stattrak": CURRENT_AUCTION.get('stattrak', False),
        "image": CURRENT_AUCTION.get('image', ''),
        "case_type": CURRENT_AUCTION.get('case_type', ''),
        "final_price": winning_bid['amount'],
        "winner": winning_bid['bidder'],
        "timestamp": datetime.now().isoformat(),
        "is_sticker": CURRENT_AUCTION.get('is_sticker', False)  # Add this line
    }
    print("Created history entry:", history_entry)
    
    # Add to history, keeping only last 10 entries
    if 'history' not in auction_data:
        auction_data['history'] = []
    auction_data['history'].insert(0, history_entry)  # Insert at beginning
    auction_data['history'] = auction_data['history'][:10]  # Keep only last 10
    
    # If player won
    if winning_bid['bidder'] == 'You':
        try:
            user_data = load_user_data()
            
            # Add item to inventory immediately
            won_item = CURRENT_AUCTION.copy()
            won_item['price'] = won_item['adjusted_price']
            won_item['timestamp'] = time.time()
            won_item['is_case'] = False
            if won_item.get('image') and won_item['image'].startswith('media/skins/'):
                won_item['image'] = won_item['image'].split('/')[-1]
            
            user_data['inventory'].append(won_item)
            save_user_data(user_data)
            
        except Exception as e:
            print(f"Error completing auction: {e}")
            traceback.print_exc()
            
    # Generate and save new auction data
    new_auction = generate_auction_item()
    auction_data.update({
        'item': new_auction,
        'end_time': (datetime.now() + timedelta(minutes=30)).isoformat(),
        'current_bid': float(new_auction['base_price']) * 0.1,
        'bids': [],
        'bot_budgets': generate_bot_budgets(new_auction['base_price'])
    })
    save_auction_data(auction_data)
    
    # Update current auction state
    CURRENT_AUCTION = new_auction
    AUCTION_BIDS = []
    AUCTION_END_TIME = datetime.fromisoformat(auction_data['end_time'])
    global AUCTION_BOT_BUDGETS
    AUCTION_BOT_BUDGETS = auction_data['bot_budgets']

@app.route('/get_auction_status')
@login_required
def get_auction_status():
    with auction_lock:
        # Load auction data from file
        auction_data = load_auction_data()
        
        # If no auction data exists at all, start new one
        if not auction_data:
            complete_auction()
            auction_data = load_auction_data()
            if not auction_data:
                return jsonify({'error': 'Failed to start auction'})
            
        # Update global state from file
        global CURRENT_AUCTION, AUCTION_BIDS, AUCTION_END_TIME, AUCTION_BOT_BUDGETS
        CURRENT_AUCTION = auction_data['item']
        AUCTION_BIDS = auction_data.get('bids', [])
        AUCTION_END_TIME = datetime.fromisoformat(auction_data['end_time'])
        AUCTION_BOT_BUDGETS = auction_data.get('bot_budgets', {})
        
        current_bid = auction_data.get('current_bid', 0)
        
        # Get active/inactive status for each bot
        bot_statuses = []
        for bot_name, data in AUCTION_BOT_BUDGETS.items():
            bot_statuses.append({
                'name': bot_name,
                'active': data['budget'] > current_bid,
                'status': data['status']
            })
        
        # Check if auction has ended
        auction_ended = datetime.now() >= AUCTION_END_TIME
        winner = None
        won_item = None
        final_price = None
        
        if auction_ended and AUCTION_BIDS:
            winner = 'You' if AUCTION_BIDS[-1]['bidder'] == 'You' else AUCTION_BIDS[-1]['bidder']
            if winner == 'You':
                won_item = CURRENT_AUCTION
                final_price = AUCTION_BIDS[-1]['amount']
                
            # Start new auction if current one ended
            complete_auction()
            auction_data = load_auction_data()
            CURRENT_AUCTION = auction_data['item']
            AUCTION_BIDS = auction_data['bids']
            AUCTION_END_TIME = datetime.fromisoformat(auction_data['end_time'])
            AUCTION_BOT_BUDGETS = auction_data['bot_budgets']
            current_bid = auction_data['current_bid']
        
        # Include history in response
        history = auction_data.get('history', [])
        
        return jsonify({
            'auction_item': CURRENT_AUCTION,
            'current_bid': current_bid,
            'end_time': AUCTION_END_TIME.isoformat(),
            'bids': AUCTION_BIDS,
            'bot_statuses': bot_statuses,
            'ended': auction_ended,
            'winner': winner,
            'won_item': won_item,
            'final_price': final_price,
            'history': history
        })

@app.route('/close_roulette_bets', methods=['POST'])
@login_required
def close_roulette_bets():
    try:
        data = request.get_json()
        bets = data.get('bets', {})
        
        # If no bets, just return success
        if not bets:
            return jsonify({'success': True})
            
        # Load current user data
        user_data = load_user_data()
        current_balance = float(user_data['balance'])
        
        # Calculate total bet amount
        total_bet = sum(float(amount) for amount in bets.values())
        
        # Immediately deduct the bet amount and save
        user_data['balance'] -= total_bet
        save_user_data(user_data)
        
        # Store the bet state in session
        session['roulette_bet'] = {
            'bets': bets,
            'total_bet': total_bet,
            'in_progress': True,
            'balance_deducted': True
        }
        
        return jsonify({
            'success': True,
            'balance': user_data['balance']
        })
        
    except Exception as e:
        print(f"Error closing roulette bets: {e}")
        return jsonify({'error': 'Failed to close bets'})

# Add this function to start a new auction
def start_new_auction():
    global CURRENT_AUCTION, AUCTION_END_TIME, AUCTION_BIDS, AUCTION_BOT_BUDGETS, LAST_BIDDER, last_auction_check
    
    with auction_lock:
        CURRENT_AUCTION = generate_auction_item()
        AUCTION_END_TIME = datetime.now() + timedelta(minutes=30)
        AUCTION_BIDS = []
        AUCTION_BOT_BUDGETS = generate_bot_budgets(CURRENT_AUCTION['base_price'])
        LAST_BIDDER = None
        last_auction_check = datetime.now()
        
        # Save the initial auction data
        auction_data = {
            'item': CURRENT_AUCTION,
            'end_time': AUCTION_END_TIME.isoformat(),
            'current_bid': 0,
            'bids': [],
            'bot_budgets': AUCTION_BOT_BUDGETS
        }
        save_auction_data(auction_data)
    
    # Start the auction processing thread
    start_auction_thread()
    
    # Schedule the next auction
    schedule_next_auction()

# Add this function to schedule the next auction
def schedule_next_auction():
    global auction_timer
    
    # Cancel any existing timer
    if auction_timer:
        auction_timer.cancel()
    
    # Schedule new auction to start when current one ends
    time_until_next = (AUCTION_END_TIME - datetime.now()).total_seconds()
    auction_timer = Timer(time_until_next, start_new_auction)
    auction_timer.daemon = True  # Make sure the timer doesn't prevent app shutdown
    auction_timer.start()

# Add this function to clean up on shutdown
def cleanup_auction():
    global auction_timer
    if auction_timer:
        auction_timer.cancel()

# Add this initialization code after app = Flask(__name__)
def init_auction_system():
    global CURRENT_AUCTION, last_auction_check
    
    # Load existing auction data if available
    auction_data = load_auction_data()
    
    if auction_data:
        # Update global state from existing data
        global AUCTION_BIDS, AUCTION_END_TIME, AUCTION_BOT_BUDGETS
        CURRENT_AUCTION = auction_data['item']
        AUCTION_BIDS = auction_data.get('bids', [])
        AUCTION_END_TIME = datetime.fromisoformat(auction_data['end_time'])
        AUCTION_BOT_BUDGETS = auction_data.get('bot_budgets', {})
        
        # Check if the existing auction has ended
        if datetime.now() >= AUCTION_END_TIME:
            start_new_auction()
        else:
            # Existing auction is still valid, just schedule the next one
            schedule_next_auction()
            start_auction_thread()
    else:
        # No existing auction, start a new one
        start_new_auction()

# Register the cleanup function
atexit.register(cleanup_auction)

# Initialize auction system when app starts
with app.app_context():
    init_auction_system()

@app.route('/api/data/case_contents/all')
def get_all_case_contents():
    try:
        # Use load_case from cases_prices_and_floats.py
        cases = load_case('all')
        if not cases:
            return jsonify({'error': 'Failed to load cases'}), 500
        return jsonify(cases)
    except Exception as e:
        print(f"Error loading all cases: {str(e)}")
        return jsonify({'error': 'Failed to load cases'}), 500

def calculate_rank(exp):
    """Calculate rank based on experience points"""
    for rank, required_exp in RANK_EXP.items():
        if exp < required_exp:
            return {
                'rank': rank,
                'name': RANKS[rank],
                'next_rank_exp': required_exp
            }
    
    # If exp is higher than all ranks, return max rank
    max_rank = max(RANKS.keys())
    return {
        'rank': max_rank,
        'name': RANKS[max_rank],
        'next_rank_exp': None
    }

@app.route('/api/batch_click', methods=['POST'])
@login_required
def batch_click():
    try:
        data = request.get_json()
        normal_clicks = data.get('normal_clicks', 0)
        critical_clicks = data.get('critical_clicks', 0)
        auto_normal_clicks = data.get('auto_normal_clicks', 0)
        auto_critical_clicks = data.get('auto_critical_clicks', 0)

        total_clicks = normal_clicks + critical_clicks + auto_normal_clicks + auto_critical_clicks
        if total_clicks <= 0:
            return jsonify({'error': 'No clicks provided'}), 400

        # Load user data from file
        user_data = load_user_data()
        current_balance = float(user_data.get('balance', 0))
        
        # Get base click value from upgrades
        upgrades = user_data.get('upgrades', {})
        click_value_level = upgrades.get('click_value', 1)
        base_click_value = 0.01 * (1.5 ** (click_value_level - 1))
        
        # Get current multiplier from session or default to 1
        current_multiplier = session.get('multiplier', 1.0)
        
        # Calculate values for different click types
        normal_value = base_click_value * current_multiplier * normal_clicks
        critical_value = base_click_value * current_multiplier * 4 * critical_clicks  # 4x for critical hits
        auto_normal_value = base_click_value * auto_normal_clicks  # Auto clicks don't use multiplier
        auto_critical_value = base_click_value * 4 * auto_critical_clicks  # 4x for critical auto hits

        # Calculate total value
        total_value = round(normal_value + critical_value + auto_normal_value + auto_critical_value, 3)

        # Update balance
        new_balance = round(current_balance + total_value, 3)
        
        # Update user data
        user_data['balance'] = new_balance
        
        # Update stats
        if 'stats' not in user_data:
            user_data['stats'] = {}
        if 'total_clicks' not in user_data['stats']:
            user_data['stats']['total_clicks'] = 0
        if 'total_earnings' not in user_data['stats']:
            user_data['stats']['total_earnings'] = 0
            
        user_data['stats']['total_clicks'] += total_clicks
        user_data['stats']['total_earnings'] = round(user_data['stats'].get('total_earnings', 0) + total_value, 3)
        
        # Save to file
        save_user_data(user_data)
        
        # Update session
        session['user_data'] = user_data
        session.modified = True

        return jsonify({
            'balance': new_balance,
            'value_earned': total_value
        })
    except Exception as e:
        print('Error in batch_click:', str(e))
        return jsonify({'error': str(e)}), 500

@app.route('/api/batch_case_click', methods=['POST'])
@login_required
def batch_case_click():
    try:
        data = request.get_json()
        click_count = data.get('click_count', 0)
        current_progress = float(data.get('current_progress', 0))
        
        user_data = load_user_data()
        upgrades = user_data.get('upgrades', {})
        progress_per_click = upgrades.get('progress_per_click', 1)
        case_quality = upgrades.get('case_quality', 1)
        
        # Calculate total progress
        total_progress = current_progress + (progress_per_click * click_count)
        earned_cases = []
        
        # Process complete cases (100% progress)
        while total_progress >= 100:
            # Reset progress
            total_progress -= 100
            
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
                earned_cases.append(earned_case_data)
                
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
        
        # Save final progress
        user_data['case_progress'] = total_progress
        save_user_data(user_data)
        
        return jsonify({
            'success': True,
            'progress': total_progress,
            'earned_cases': earned_cases,
            'progress_per_click': progress_per_click
        })
        
    except Exception as e:
        print(f"Error in batch case click: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/get_balance')
@login_required
def get_balance():
    try:
        user_data = load_user_data()
        return jsonify({
            'balance': float(user_data['balance'])
        })
    except Exception as e:
        print(f"Error getting balance: {e}")
        return jsonify({'error': 'Failed to get balance'}), 500

# Add after other casino routes
@app.route('/api/blackjack/start', methods=['POST'])
@login_required
def start_blackjack():
    try:
        data = request.get_json()
        bet_amount = float(data.get('bet', 0))
        
        user_data = load_user_data()
        current_balance = float(user_data['balance'])
        
        if bet_amount <= 0:
            return jsonify({'error': 'Invalid bet amount'})
            
        if bet_amount > current_balance:
            return jsonify({'error': 'Insufficient funds'})
            
        # Deduct bet amount
        user_data['balance'] = current_balance - bet_amount
        save_user_data(user_data)
        
        # Start new game
        game = BlackjackGame()
        game_states = game.start_game(bet_amount)  # Returns both display and internal states
        
        # Store internal game state in session
        session['blackjack_state'] = game_states['internal_state']
        
        return jsonify({
            'success': True,
            'state': game_states['display_state'],  # Send display state to frontend
            'balance': user_data['balance']
        })
        
    except Exception as e:
        print(f"Error starting blackjack: {e}")
        traceback.print_exc()  # Add traceback for debugging
        return jsonify({'error': 'Failed to start game'})

@app.route('/api/blackjack/hit', methods=['POST'])
@login_required
def blackjack_hit():
    try:
        # Get internal state from session
        state_data = session.get('blackjack_state')
        if not state_data:
            return jsonify({'error': 'No active game'})
            
        game = BlackjackGame.from_state(state_data)
        game_states = game.hit()  # Returns both display and internal states
        
        # Store updated internal state
        session['blackjack_state'] = game_states['internal_state']
        
        if game_states['display_state']['game_over']:
            return handle_blackjack_end(game_states['display_state'])
            
        return jsonify({
            'success': True,
            'state': game_states['display_state']  # Send display state to frontend
        })
        
    except Exception as e:
        print(f"Error in blackjack hit: {e}")
        traceback.print_exc()
        return jsonify({'error': 'Failed to hit'})

@app.route('/api/blackjack/stand', methods=['POST'])
@login_required
def blackjack_stand():
    try:
        # Get internal state from session
        state_data = session.get('blackjack_state')
        if not state_data:
            return jsonify({'error': 'No active game'})
            
        game = BlackjackGame.from_state(state_data)
        game_states = game.stand()  # Returns both display and internal states
        
        # Store updated internal state
        session['blackjack_state'] = game_states['internal_state']
        
        if game_states['display_state']['game_over']:
            return handle_blackjack_end(game_states['display_state'])
            
        return jsonify({
            'success': True,
            'state': game_states['display_state']  # Send display state to frontend
        })
        
    except Exception as e:
        print(f"Error in blackjack stand: {e}")
        traceback.print_exc()
        return jsonify({'error': 'Failed to stand'})

@app.route('/api/blackjack/double', methods=['POST'])
@login_required
def blackjack_double():
    try:
        # Get internal state from session
        state_data = session.get('blackjack_state')
        if not state_data:
            return jsonify({'error': 'No active game'})
            
        game = BlackjackGame.from_state(state_data)
        
        # Check if player can afford double down
        user_data = load_user_data()
        current_hand = game.player_hands[game.current_hand_index]
        if current_hand.bet > float(user_data['balance']):
            return jsonify({'error': 'Insufficient funds for double down'})
            
        # Deduct additional bet
        user_data['balance'] -= current_hand.bet
        save_user_data(user_data)
        
        game_states = game.double_down()  # Returns both display and internal states
        
        # Store updated internal state
        session['blackjack_state'] = game_states['internal_state']
        
        if game_states['display_state']['game_over']:
            return handle_blackjack_end(game_states['display_state'])
            
        return jsonify({
            'success': True,
            'state': game_states['display_state'],  # Send display state to frontend
            'balance': user_data['balance']
        })
        
    except Exception as e:
        print(f"Error in blackjack double: {e}")
        traceback.print_exc()
        return jsonify({'error': 'Failed to double down'})

@app.route('/api/blackjack/split', methods=['POST'])
@login_required
def blackjack_split():
    try:
        # Get internal state from session
        state_data = session.get('blackjack_state')
        if not state_data:
            return jsonify({'error': 'No active game'})
            
        game = BlackjackGame.from_state(state_data)
        
        # Check if player can afford split
        user_data = load_user_data()
        current_hand = game.player_hands[game.current_hand_index]
        if current_hand.bet > float(user_data['balance']):
            return jsonify({'error': 'Insufficient funds for split'})
            
        # Deduct additional bet
        user_data['balance'] -= current_hand.bet
        save_user_data(user_data)
        
        game_states = game.split()  # Returns both display and internal states
        
        # Store updated internal state
        session['blackjack_state'] = game_states['internal_state']
        
        return jsonify({
            'success': True,
            'state': game_states['display_state'],  # Send display state to frontend
            'balance': user_data['balance']
        })
        
    except Exception as e:
        print(f"Error in blackjack split: {e}")
        traceback.print_exc()
        return jsonify({'error': 'Failed to split'})

@app.route('/api/blackjack/insurance', methods=['POST'])
@login_required
def blackjack_insurance():
    try:
        # Get internal state from session
        state_data = session.get('blackjack_state')
        if not state_data:
            return jsonify({'error': 'No active game'})
            
        game = BlackjackGame.from_state(state_data)
        
        # Check if player can afford insurance
        user_data = load_user_data()
        current_hand = game.player_hands[game.current_hand_index]
        insurance_cost = current_hand.bet / 2
        
        if insurance_cost > float(user_data['balance']):
            return jsonify({'error': 'Insufficient funds for insurance'})
            
        # Deduct insurance cost
        user_data['balance'] -= insurance_cost
        save_user_data(user_data)
        
        game_states = game.insurance()  # Returns both display and internal states
        
        # Store updated internal state
        session['blackjack_state'] = game_states['internal_state']
        
        return jsonify({
            'success': True,
            'state': game_states['display_state'],  # Send display state to frontend
            'balance': user_data['balance']
        })
        
    except Exception as e:
        print(f"Error in blackjack insurance: {e}")
        traceback.print_exc()
        return jsonify({'error': 'Failed to take insurance'})

@app.route('/blackjack')
@login_required
def blackjack():
    # For Vue routes, we need to serve the main Vue app
    return serve_vue_app('')

@app.route('/api/data/sticker_capsule_contents/<capsule_type>')
def get_sticker_capsule_contents(capsule_type):
    try:
        capsule_data = load_sticker_capsule(capsule_type)
        if not capsule_data:
            return jsonify({'error': 'Invalid capsule type'})
        return jsonify(capsule_data)
    except Exception as e:
        print(f"Error loading sticker capsule {capsule_type}: {e}")
        return jsonify({'error': 'Failed to load sticker capsule data'})

@app.route('/api/data/sticker_capsule_contents/all')
def get_all_sticker_capsules():
    try:
        capsules = load_sticker_capsule('all')
        if not capsules:
            return jsonify({'error': 'Failed to load sticker capsules'})
        return jsonify(capsules)
    except Exception as e:
        print(f"Error loading all sticker capsules: {e}")
        return jsonify({'error': 'Failed to load sticker capsules'})

@app.route('/buy_sticker_capsule', methods=['POST'])
@login_required
def buy_sticker_capsule():
    try:
        data = request.get_json()
        capsule_type = data.get('capsule_type')
        quantity = int(data.get('quantity', 1))

        # Load user data
        user_data = load_user_data()
        current_balance = float(user_data['balance'])

        # Get capsule price
        capsule_price = get_sticker_capsule_prices(capsule_type)
        if not capsule_price:
            return jsonify({'error': 'Invalid capsule type'})

        total_cost = capsule_price * quantity
        if total_cost > current_balance:
            return jsonify({'error': 'Insufficient funds'})

        # Update user's balance
        user_data['balance'] = current_balance - total_cost

        # Add capsule to inventory
        inventory = user_data.get('inventory', [])
        capsule_found = False

        for item in inventory:
            if item.get('is_capsule') and item.get('type') == capsule_type:
                item['quantity'] = item.get('quantity', 0) + quantity
                # Make sure price is set
                if 'price' not in item:
                    item['price'] = capsule_price
                capsule_found = True
                break

        if not capsule_found:
            capsule_info = STICKER_CAPSULE_DATA[capsule_type].copy()
            capsule_info.update({
                'quantity': quantity,
                'price': capsule_price,
                'is_capsule': True,
                'type': capsule_type
            })
            inventory.append(capsule_info)

        # Save user data
        user_data['inventory'] = inventory
        save_user_data(user_data)

        return jsonify({
            'success': True,
            'balance': user_data['balance']
        })

    except Exception as e:
        print(f"Error buying sticker capsule: {e}")
        return jsonify({'error': 'Failed to purchase sticker capsule'})

@app.route('/open_capsule/<capsule_type>')
@login_required
def open_capsule(capsule_type):
    """Open a sticker capsule and get a sticker"""
    try:
        # Get count parameter (default to 1)
        count = int(request.args.get('count', 1))
        if count < 1:
            return jsonify({'error': 'Invalid count'})

        # Load user data
        user_data = load_user_data()
        inventory = user_data.get('inventory', [])

        # Find the capsule in inventory
        capsule_found = False
        capsule_price = 0
        for item in inventory:
            if item.get('is_capsule') and item.get('type') == capsule_type:
                if item.get('quantity', 0) < count:
                    return jsonify({'error': 'Not enough capsules'})
                # Get capsule price for EXP calculation
                capsule_price = float(item.get('price', 0))
                # Decrease quantity instead of removing
                item['quantity'] = item.get('quantity', 0) - count
                if item['quantity'] <= 0:
                    inventory.remove(item)
                capsule_found = True
                break

        if not capsule_found:
            return jsonify({'error': 'Not enough capsules'})

        # Open capsules and get stickers
        items = []
        for _ in range(count):
            # Open capsule
            sticker_name, sticker_price, rarity, image = open_sticker_capsule(capsule_type)
            if not sticker_name:
                continue

            # Create sticker item
            sticker_item = {
                'name': sticker_name,
                'price': sticker_price,
                'rarity': rarity.upper(),  # Ensure rarity is uppercase
                'case_type': capsule_type,
                'timestamp': time.time(),
                'is_sticker': True,
                'image': image
            }
            
            # Add to inventory and items list
            inventory.append(sticker_item)
            items.append(sticker_item)

        # Save updated inventory
        user_data['inventory'] = inventory

        # Update exp and calculate rank - EXP gain is equal to capsule price
        current_exp = float(user_data.get('exp', 0))
        current_rank = int(user_data.get('rank', 0))
        new_exp = current_exp + (capsule_price * count)
        
        # Calculate if level up occurred
        while current_rank < len(RANK_EXP) and new_exp >= RANK_EXP[current_rank]:
            new_exp -= RANK_EXP[current_rank]
            current_rank += 1
        
        # Update user data with new exp and rank
        user_data['exp'] = new_exp
        user_data['rank'] = current_rank
        
        # Save all changes
        save_user_data(user_data)

        return jsonify({
            'items': items,
            'balance': user_data.get('balance', 0),
            'exp': new_exp,
            'rank': current_rank,
            'levelUp': current_rank > int(user_data.get('rank', 0))
        })

    except Exception as e:
        print(f"Error in open_capsule: {e}")
        traceback.print_exc()
        return jsonify({'error': 'Failed to open capsule'})

@app.route('/reset_trades', methods=['GET', 'POST'])
@login_required
def reset_trades():
    try:
        # Generate new trades
        new_trades = generate_daily_trades()
        
        # Save the new trades
        trades_data = {
            'date': datetime.now().strftime('%Y-%m-%d'),
            'trades': new_trades,
            'completed_trades': []
        }
        save_daily_trades(trades_data)
        
        return jsonify({
            'success': True,
            'message': 'Daily trades have been reset',
            'trades': new_trades
        })
        
    except Exception as e:
        print(f"Error resetting trades: {e}")
        traceback.print_exc()
        return jsonify({'error': 'Failed to reset trades'}), 500

@app.route('/toggle_favorite', methods=['POST'])
@login_required
def toggle_favorite():
    try:
        data = request.get_json()
        if not data or 'timestamp' not in data:
            return jsonify({'error': 'Invalid request data'}), 400

        timestamp = data['timestamp']
        
        # Load user inventory
        with open('data/user_inventory.json', 'r') as f:
            user_data = json.load(f)
        
        # Find the item with matching timestamp and other properties
        target_item = None
        for item in user_data['inventory']:
            if item.get('timestamp') == timestamp:
                # For weapon skins, match weapon, name, wear, and stattrak
                if (not item.get('is_sticker') and not item.get('is_case') and 
                    item.get('weapon') and item.get('name')):
                    if (item.get('weapon') == data.get('weapon') and 
                        item.get('name') == data.get('name') and 
                        item.get('wear') == data.get('wear') and 
                        item.get('stattrak') == data.get('stattrak')):
                        target_item = item
                        break
                # For stickers, match name and case_type
                elif item.get('is_sticker'):
                    if (item.get('name') == data.get('name') and 
                        item.get('case_type') == data.get('case_type')):
                        target_item = item
                        break
                # For cases, match type
                elif item.get('is_case'):
                    if item.get('type') == data.get('type'):
                        target_item = item
                        break

        if target_item:
            # Toggle favorite status
            if target_item.get('favorite'):
                del target_item['favorite']
            else:
                target_item['favorite'] = True

            # Save updated inventory
            with open('data/user_inventory.json', 'w') as f:
                json.dump(user_data, f, indent=2)
            
            # Return the updated inventory data
            return jsonify({
                'success': True,
                'inventory': user_data['inventory']
            })
        else:
            return jsonify({'error': 'Item not found'}), 404
            
    except Exception as e:
        print(f"Error in toggle_favorite: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    init_auction_system()  # Keep this line
    app.run(debug=True)