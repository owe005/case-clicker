from config import RANK_EXP


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