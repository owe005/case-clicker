import json
import traceback

from flask import jsonify, session
from config import CASE_FILE_MAPPING
from user_data import load_user_data, save_user_data

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
        
        # Skip StatTrak for stickers
        if skin.get('is_sticker'):
            continue
            
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

def handle_blackjack_end(game_state):
    try:
        user_data = load_user_data()
        total_payout = 0
        
        # Calculate total payout from all hands
        for hand in game_state['player_hands']:
            if 'payout' in hand:
                total_payout += hand['payout']
                
        # Update user balance with winnings/losses
        if total_payout > 0:
            user_data['balance'] = float(user_data['balance']) + total_payout
            
        save_user_data(user_data)
        
        # Clear game from session
        session.pop('blackjack_state', None)
        
        return jsonify({
            'success': True,
            'state': game_state,
            'balance': user_data['balance'],
            'payout': total_payout
        })
        
    except Exception as e:
        print(f"Error handling blackjack end: {e}")
        traceback.print_exc()  # Add traceback for better debugging
        return jsonify({'error': 'Failed to process game end'})