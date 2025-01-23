from dataclasses import dataclass
import random
from typing import List, Union
import json
import time
from config import Rarity, Wear

@dataclass
class Skin:
    weapon: str
    name: str
    rarity: Rarity
    wear: Wear
    stattrak: bool = False
    case_type: str = 'weapon_case_1'
    
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

@dataclass
class Upgrades:
    click_value: int = 1
    max_multiplier: int = 1
    auto_clicker: int = 0
    combo_speed: int = 1
    critical_strike: int = 0
    progress_per_click: int = 1
    case_quality: int = 1
    multi_open: int = 1

@dataclass
class User:
    balance: float = 100.0
    inventory: List[Union[Skin, dict]] = None
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
        from config import RANK_EXP
        self.exp += amount
        while self.rank < len(RANK_EXP) and int(self.exp) >= RANK_EXP[self.rank]:
            self.exp -= RANK_EXP[self.rank]
            self.rank += 1

class Case:
    def __init__(self, name: str, contents: dict, file_name: str, is_souvenir: bool = False):
        self.name = name
        self.contents = contents
        self.file_name = file_name
        self.is_souvenir = is_souvenir

    def get_drop_chances(self) -> dict:
        """Get the drop chances based on case type"""
        if self.is_souvenir:
            from config import SOUVENIR_DROP_CHANCES
            return SOUVENIR_DROP_CHANCES
        else:
            return {
                'gold': 0.26,
                'red': 0.90,
                'pink': 4.10,
                'purple': 20.08,
                'blue': 74.66
            }

    def get_special_chance(self) -> float:
        """Get chance for StatTrak or Souvenir based on case type"""
        if self.is_souvenir:
            from config import SOUVENIR_CHANCE
            return SOUVENIR_CHANCE
        else:
            return 10  # 10% chance for StatTrak

    def get_special_prefix(self) -> str:
        """Get the prefix for special items (StatTrak™ or Souvenir)"""
        return "Souvenir" if self.is_souvenir else "StatTrak™"

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
        possible_skins = self.contents.get(chosen_rarity, [])
        if not possible_skins:
            return None
        
        chosen_skin = random.choice(possible_skins)
        
        try:
            # Load case data to get valid wears
            with open(f'cases/{self.file_name}.json', 'r') as f:
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
                
                # On top of the normal roll there is a 10% chance to get a StatTrak™ skin
                stattrak = random.random() < 0.10
                
                return Skin(
                    chosen_skin[0], 
                    chosen_skin[1], 
                    chosen_rarity, 
                    chosen_wear, 
                    stattrak,
                    self.file_name
                )
        except Exception as e:
            print(f"Error in Case.open(): {e}")
        
        # Fallback to FT wear if something goes wrong as FT is the most common wear
        return Skin(
            chosen_skin[0],
            chosen_skin[1],
            chosen_rarity,
            Wear.FT,
            False,
            self.file_name
        ) 