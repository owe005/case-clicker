import json
import os
import threading
import time

from achievements import update_case_achievements, update_click_achievements, update_earnings_achievements
from models import Upgrades, User

# Add this at the top with other globals
file_lock = threading.Lock()

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
        balance=data.get('balance', 100.0),
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
            update_click_achievements(result)
            
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