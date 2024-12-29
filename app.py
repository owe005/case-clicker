from flask import Flask, render_template, jsonify, session, redirect, url_for, request
from dataclasses import dataclass, asdict
from enum import Enum
import random
from typing import List, Dict, Tuple, Union
import time

app = Flask(__name__)

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
    
    # Add price lookup method
    def get_price(self) -> float:
        base_price = SKIN_PRICES.get(f"{self.weapon}|{self.name}", {})
        wear_price = base_price.get(self.wear.name, 0)
        
        if self.stattrak:
            stattrak_price = base_price.get(f"ST_{self.wear.name}", wear_price * 2)
            return stattrak_price
        return wear_price

# Add price dictionary after the Rarity and Wear enums
SKIN_PRICES = {
    "AWP|Lightning Strike": {
        "FN": 495.00,
        "MW": 547.00,
        "ST_FN": 919.00,
        "ST_MW": 900.00
    },
    "AK-47|Case Hardened": {
        "FN": 324.41,
        "MW": 237.90,
        "FT": 211.26,
        "WW": 169.45,
        "BS": 163.70,
        "ST_FN": 680.80,
        "ST_MW": 478.39,
        "ST_FT": 364.98,
        "ST_WW": 315.49,
        "ST_BS": 291.58
    },
    "Desert Eagle|Hypnotic": {
        "FN": 84.06,
        "MW": 85.17,
        "ST_FN": 121.19,
        "ST_MW": 180.99
    },
    "USP-S|Dark Water": {
        "MW": 78.00,
        "FT": 71.80,
        "ST_MW": 122.00,
        "ST_FT": 106.45
    },
    "Glock-18|Dragon Tattoo": {
        "FN": 85.98,
        "MW": 85.00,
        "ST_FN": 347.49,
        "ST_MW": 242.00
    },
    "M4A1-S|Dark Water": {
        "MW": 76.28,
        "FT": 72.00,
        "ST_MW": 135.56,
        "ST_FT": 101.56
    },
    "AUG|Wings": {
        "FN": 22.95,
        "MW": 23.55,
        "ST_FN": 23.64,
        "ST_MW": 23.88
    },
    "MP7|Skulls": {
        "MW": 23.36,
        "FT": 22.52,
        "ST_MW": 22.63,
        "ST_FT": 21.24
    },
    "SG 553|Ultraviolet": {
        "FN": 33.89,
        "MW": 23.40,
        "FT": 22.81,
        "WW": 22.36,
        "BS": 22.03,
        "ST_FN": 87.24,
        "ST_MW": 24.40,
        "ST_FT": 21.80,
        "ST_WW": 21.16,
        "ST_BS": 18.91
    },
    "★ Karambit|Urban Masked": {
        "FN": 744.37,
        "MW": 613.80,
        "FT": 561.00,
        "WW": 527.49,
        "BS": 520.00,
        "ST_FN": 987.20,
        "ST_MW": 613.80,
        "ST_FT": 523.98,
        "ST_WW": 561.74,
        "ST_BS": 534.34
    },
    "★ Karambit|Blue Steel": {
        "FN": 1145.27,
        "MW": 960.00,
        "FT": 902.18,
        "WW": 830.00,
        "BS": 834.80,
        "ST_FN": 2740.21,
        "ST_MW": 986.47,
        "ST_FT": 854.94,
        "ST_WW": 808.36,
        "ST_BS": 817.26
    },
    "★ Bayonet|Blue Steel": {
        "FN": 437.88,
        "MW": 322.58,
        "FT": 299.00,
        "WW": 273.07,
        "BS": 251.68,
        "ST_FN": 640.39,
        "ST_MW": 337.45,
        "ST_FT": 304.00,
        "ST_WW": 287.51,
        "ST_BS": 265.25
    },
    "★ M9 Bayonet|Urban Masked": {
        "FN": 657.65,
        "MW": 480.00,
        "FT": 453.99,
        "WW": 443.91,
        "BS": 471.99,
        "ST_FN": 3912.20,
        "ST_MW": 465.99,
        "ST_FT": 445.28,
        "ST_WW": 438.29,
        "ST_BS": 451.45
    },
    "★ M9 Bayonet|Safari Mesh": {
        "FN": 749.99,
        "MW": 451.92,
        "FT": 432.83,
        "WW": 438.16,
        "BS": 445.76,
        "ST_FN": 3275.24,
        "ST_MW": 476.43,
        "ST_FT": 432.54,
        "ST_WW": 430.32,
        "ST_BS": 438.29
    },
    "★ M9 Bayonet|Stained": {
        "FN": 691.90,
        "MW": 610.31,
        "FT": 579.99,
        "WW": 532.28,
        "BS": 539.95,
        "ST_FN": 684.36,
        "ST_MW": 616.54,
        "ST_FT": 566.08,
        "ST_WW": 530.23,
        "ST_BS": 527.49
    },
    "★ M9 Bayonet|Blue Steel": {
        "FN": 893.24,
        "MW": 748.59,
        "FT": 719.49,
        "WW": 697.06,
        "BS": 688.61,
        "ST_FN": 860.84,
        "ST_MW": 705.00,
        "ST_FT": 684.91,
        "ST_WW": 657.79,
        "ST_BS": 705.74
    },
    "★ Bayonet|Urban Masked": {
        "FN": 328.82,
        "MW": 212.79,
        "FT": 178.47,
        "WW": 177.29,
        "BS": 175.23,
        "ST_FN": 839.39,
        "ST_MW": 239.76,
        "ST_FT": 177.08,
        "ST_WW": 220.00,
        "ST_BS": 177.97
    },
    "★ Bayonet|Stained": {
        "FN": 311.01,
        "MW": 250.30,
        "FT": 234.70,
        "WW": 209.51,
        "BS": 206.88,
        "ST_FN": 548.04,
        "ST_MW": 247.99,
        "ST_FT": 229.33,
        "ST_WW": 262.12,
        "ST_BS": 210.57
    },
    "★ Flip Knife|Urban Masked": {
        "FN": 270.00,
        "MW": 166.00,
        "FT": 145.79,
        "WW": 138.18,
        "BS": 134.95,
        "ST_FN": 5000.00,
        "ST_MW": 164.41,
        "ST_FT": 143.69,
        "ST_WW": 150.71,
        "ST_BS": 135.50
    },
    "★ Flip Knife|Safari Mesh": {
        "FN": 211.93,
        "MW": 142.97,
        "FT": 134.27,
        "WW": 134.25,
        "BS": 129.88,
        "ST_FN": 520.00,
        "ST_MW": 145.09,
        "ST_FT": 135.96,
        "ST_WW": 135.23,
        "ST_BS": 134.20
    },
    "★ Flip Knife|Stained": {
        "FN": 215.89,
        "MW": 184.96,
        "FT": 171.49,
        "WW": 163.04,
        "BS": 156.19,
        "ST_FN": 233.24,
        "ST_MW": 182.15,
        "ST_FT": 173.47,
        "ST_WW": 164.41,
        "ST_BS": 157.56
    },
    "★ Gut Knife|Urban Masked": {
        "FN": 132.62,
        "MW": 95.13,
        "FT": 94.00,
        "WW": 110.00,
        "BS": 91.29,
        "ST_FN": 590.20,
        "ST_MW": 97.69,
        "ST_FT": 95.90,
        "ST_WW": 145.90,
        "ST_BS": 107.43
    },
    "★ Gut Knife|Safari Mesh": {
        "FN": 393.48,
        "MW": 96.52,
        "FT": 92.75,
        "WW": 98.95,
        "BS": 90.57,
        "ST_FN": 1590.14,
        "ST_MW": 99.88,
        "ST_FT": 90.42,
        "ST_WW": 145.62,
        "ST_BS": 306.10
    },
    "★ Gut Knife|Stained": {
        "FN": 113.03,
        "MW": 94.38,
        "FT": 97.96,
        "WW": 93.90,
        "BS": 95.83,
        "ST_FN": 199.90,
        "ST_MW": 123.30,
        "ST_FT": 126.81,
        "ST_WW": 105.53,
        "ST_BS": 97.00
    },
    "★ Gut Knife|Blue Steel": {
        "FN": 164.13,
        "MW": 106.10,
        "FT": 101.02,
        "WW": 95.94,
        "BS": 102.13,
        "ST_FN": 1096.08,
        "ST_MW": 133.90,
        "ST_FT": 126.10,
        "ST_WW": 98.64,
        "ST_BS": 118.00
    },
    "★ Karambit|Slaughter": {
        "FN": 1272.21,
        "MW": 1149.18,
        "FT": 1035.00,
        "ST_FN": 1279.99,
        "ST_MW": 1094.01,
        "ST_FT": 986.46
    },
    "★ Karambit|Fade": {
        "FN": 2397.95,
        "MW": 2327.23,
        "ST_FN": 19294.89,
        "ST_MW": 18272.21
    }
}

# Add valid wear ranges for each skin after SKIN_PRICES
VALID_WEARS = {
    "AWP|Lightning Strike": ["FN", "MW"],
    "AK-47|Case Hardened": ["FN", "MW", "FT", "WW", "BS"],
    "Desert Eagle|Hypnotic": ["FN", "MW"],
    "USP-S|Dark Water": ["MW", "FT"],
    "Glock-18|Dragon Tattoo": ["FN", "MW"],
    "M4A1-S|Dark Water": ["MW", "FT"],
    "AUG|Wings": ["FN", "MW"],
    "MP7|Skulls": ["MW", "FT"],
    "SG 553|Ultraviolet": ["FN", "MW", "FT", "WW", "BS"],
    "★ Karambit|Urban Masked": ["FN", "MW", "FT", "WW", "BS"],
    "★ Karambit|Blue Steel": ["FN", "MW", "FT", "WW", "BS"],
    "★ Bayonet|Blue Steel": ["FN", "MW", "FT", "WW", "BS"],
    "★ M9 Bayonet|Urban Masked": ["FN", "MW", "FT", "WW", "BS"],
    "★ M9 Bayonet|Safari Mesh": ["FN", "MW", "FT", "WW", "BS"],
    "★ M9 Bayonet|Stained": ["FN", "MW", "FT", "WW", "BS"],
    "★ M9 Bayonet|Blue Steel": ["FN", "MW", "FT", "WW", "BS"],
    "★ Bayonet|Urban Masked": ["FN", "MW", "FT", "WW", "BS"],
    "★ Bayonet|Stained": ["FN", "MW", "FT", "WW", "BS"],
    "★ Flip Knife|Urban Masked": ["FN", "MW", "FT", "WW", "BS"],
    "★ Flip Knife|Safari Mesh": ["FN", "MW", "FT", "WW", "BS"],
    "★ Flip Knife|Stained": ["FN", "MW", "FT", "WW", "BS"],
    "★ Gut Knife|Urban Masked": ["FN", "MW", "FT", "WW", "BS"],
    "★ Gut Knife|Safari Mesh": ["FN", "MW", "FT", "WW", "BS"],
    "★ Gut Knife|Stained": ["FN", "MW", "FT", "WW", "BS"],
    "★ Gut Knife|Blue Steel": ["FN", "MW", "FT", "WW", "BS"],
    "★ Karambit|Slaughter": ["FN", "MW", "FT"],
    "★ Karambit|Fade": ["FN", "MW"]
}

class Case:
    def __init__(self, name: str, skins: dict):
        self.name = name
        self.skins = skins
    
    def open(self) -> Skin:
        # Determine rarity first
        rarity_roll = random.random() * 100  # Roll between 0 and 100
        
        # Define rarity thresholds based on given percentages
        if rarity_roll < 0.26:  # 0.26% chance for Gold
            chosen_rarity = Rarity.GOLD
        elif rarity_roll < 0.90 + 0.26:  # 0.90% chance for Red
            chosen_rarity = Rarity.RED
        elif rarity_roll < 4.10 + 0.90 + 0.26:  # 4.10% chance for Pink
            chosen_rarity = Rarity.PINK
        elif rarity_roll < 20.08 + 4.10 + 0.90 + 0.26:  # 20.08% chance for Purple
            chosen_rarity = Rarity.PURPLE
        else:  # Remaining ~74.66% chance for Blue
            chosen_rarity = Rarity.BLUE
        
        # Select random skin from chosen rarity
        possible_skins = self.skins.get(chosen_rarity, [])
        if not possible_skins:
            return None
        
        chosen_skin = random.choice(possible_skins)
        
        # For gold items, we still generate the actual knife but it's hidden in the animation
        skin_key = f"{chosen_skin[0]}|{chosen_skin[1]}"
        valid_wears = VALID_WEARS.get(skin_key, ["FT"])
        chosen_wear = Wear[random.choice(valid_wears)]
        
        # StatTrak™ chance (10% for all rarities)
        stattrak = random.random() < 0.10
        
        return Skin(chosen_skin[0], chosen_skin[1], chosen_rarity, chosen_wear, stattrak)

# Define the cases
CSGO_WEAPON_CASE = Case("CS:GO Weapon Case", {
    Rarity.RED: [
        ("AWP", "Lightning Strike")
    ],
    Rarity.PINK: [
        ("AK-47", "Case Hardened"),
        ("Desert Eagle", "Hypnotic")
    ],
    Rarity.PURPLE: [
        ("Glock-18", "Dragon Tattoo"),
        ("M4A1-S", "Dark Water"),
        ("USP-S", "Dark Water")
    ],
    Rarity.BLUE: [
        ("SG 553", "Ultraviolet"),
        ("MP7", "Skulls"),
        ("AUG", "Wings")
    ],
    Rarity.GOLD: [
        ("★ Karambit", "Fade"),
        ("★ Karambit", "Slaughter"),
        ("★ Karambit", "Urban Masked"),
        ("★ Karambit", "Blue Steel"),
        ("★ Karambit", "Stained"),
        ("★ Karambit", "Safari Mesh"),
        ("★ M9 Bayonet", "Urban Masked"),
        ("★ M9 Bayonet", "Safari Mesh"),
        ("★ M9 Bayonet", "Stained"),
        ("★ M9 Bayonet", "Blue Steel"),
        ("★ Bayonet", "Urban Masked"),
        ("★ Bayonet", "Stained"),
        ("★ Bayonet", "Blue Steel"),
        ("★ Flip Knife", "Urban Masked"),
        ("★ Flip Knife", "Safari Mesh"),
        ("★ Flip Knife", "Stained"),
        ("★ Gut Knife", "Urban Masked"),
        ("★ Gut Knife", "Safari Mesh"),
        ("★ Gut Knife", "Stained"),
        ("★ Gut Knife", "Blue Steel")
    ]
})

ESPORTS_2013_CASE = Case("eSports 2013 Case", {
    Rarity.RED: [
        ("P90", "Death by Kitty")
    ],
    Rarity.PINK: [
        ("AWP", "BOOM"),
        ("AK-47", "Red Laminate")
    ],
    Rarity.PURPLE: [
        ("Galil AR", "Orange DDPAT"),
        ("P250", "Splash"),
        ("Sawed-Off", "Orange DDPAT")
    ],
    Rarity.BLUE: [
        ("M4A4", "Faded Zebra"),
        ("MAG-7", "Memento"),
        ("FAMAS", "Doomkitty")
    ],
    Rarity.GOLD: [
        ("★ Karambit", "Urban Masked"),
        ("★ Karambit", "Blue Steel"), 
        ("★ Karambit", "Stained"),
        ("★ Karambit", "Safari Mesh"),
        ("★ M9 Bayonet", "Urban Masked"),
        ("★ M9 Bayonet", "Safari Mesh"),
        ("★ M9 Bayonet", "Stained"),
        ("★ M9 Bayonet", "Blue Steel"),
        ("★ Bayonet", "Urban Masked"),
        ("★ Bayonet", "Stained"),
        ("★ Bayonet", "Blue Steel"),
        ("★ Flip Knife", "Urban Masked"),
        ("★ Flip Knife", "Safari Mesh"),
        ("★ Flip Knife", "Stained"),
        ("★ Gut Knife", "Urban Masked"),
        ("★ Gut Knife", "Safari Mesh"),
        ("★ Gut Knife", "Stained"),
        ("★ Gut Knife", "Blue Steel")
    ]
})

RANKS = {
    0: "Silver I",
    1: "Silver II", 
    2: "Silver III",
    3: "Silver IV",
    4: "Silver Elite",
    5: "Silver Elite Master"
}

RANK_EXP = {
    0: 10,    # Silver I to Silver II
    1: 50,    # Silver II to Silver III  
    2: 100,   # Silver III to Silver IV
    3: 200,   # Silver IV to Silver Elite
    4: 500    # Silver Elite to Silver Elite Master
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
    'bravo': 150.00  # Add Operation Bravo Case price
}

VALID_WEARS.update({
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
})

SKIN_PRICES.update({
    "AK-47|Fire Serpent": {"FN": 0.00, "MW": 0.00, "FT": 0.00, "WW": 0.00, "BS": 0.00},
    "Desert Eagle|Golden Koi": {"FN": 0.00, "MW": 0.00},
    "AWP|Graphite": {"FN": 0.00, "MW": 0.00},
    "P90|Emerald Dragon": {"FN": 0.00, "MW": 0.00, "FT": 0.00, "WW": 0.00, "BS": 0.00},
    "P2000|Ocean Foam": {"FN": 0.00, "MW": 0.00},
    "USP-S|Overgrowth": {"FN": 0.00, "MW": 0.00, "FT": 0.00, "WW": 0.00, "BS": 0.00},
    "MAC-10|Graven": {"FN": 0.00, "MW": 0.00, "FT": 0.00, "WW": 0.00, "BS": 0.00},
    "M4A1-S|Bright Water": {"MW": 0.00, "FT": 0.00},
    "M4A4|Zirka": {"FN": 0.00, "MW": 0.00, "FT": 0.00, "WW": 0.00, "BS": 0.00},
    "Dual Berettas|Black Limba": {"FN": 0.00, "MW": 0.00, "FT": 0.00, "WW": 0.00, "BS": 0.00},
    "SG 553|Wave Spray": {"FN": 0.00, "MW": 0.00, "FT": 0.00, "WW": 0.00, "BS": 0.00},
    "Nova|Tempest": {"FN": 0.00, "MW": 0.00, "FT": 0.00, "WW": 0.00, "BS": 0.00},
    "Galil AR|Shattered": {"FN": 0.00, "MW": 0.00, "FT": 0.00, "WW": 0.00, "BS": 0.00},
    "UMP-45|Bone Pile": {"FN": 0.00, "MW": 0.00, "FT": 0.00, "WW": 0.00, "BS": 0.00}
})

# Add the Operation Bravo Case definition
OPERATION_BRAVO_CASE = Case("Operation Bravo Case", {
    Rarity.RED: [
        ("AK-47", "Fire Serpent"),
        ("Desert Eagle", "Golden Koi")
    ],
    Rarity.PINK: [
        ("AWP", "Graphite"),
        ("P90", "Emerald Dragon"),
        ("P2000", "Ocean Foam")
    ],
    Rarity.PURPLE: [
        ("USP-S", "Overgrowth"),
        ("MAC-10", "Graven"),
        ("M4A1-S", "Bright Water"),
        ("M4A4", "Zirka")
    ],
    Rarity.BLUE: [
        ("Dual Berettas", "Black Limba"),
        ("SG 553", "Wave Spray"),
        ("Nova", "Tempest"),
        ("Galil AR", "Shattered"),
        ("UMP-45", "Bone Pile")
    ],
    Rarity.GOLD: [
        ("★ Karambit", "Urban Masked"),
        ("★ Karambit", "Blue Steel"),
        ("★ Karambit", "Stained"),
        ("★ Karambit", "Safari Mesh"),
        ("★ M9 Bayonet", "Urban Masked"),
        ("★ M9 Bayonet", "Safari Mesh"),
        ("★ M9 Bayonet", "Stained"),
        ("★ M9 Bayonet", "Blue Steel"),
        ("★ Bayonet", "Urban Masked"),
        ("★ Bayonet", "Stained"),
        ("★ Bayonet", "Blue Steel"),
        ("★ Flip Knife", "Urban Masked"),
        ("★ Flip Knife", "Safari Mesh"),
        ("★ Flip Knife", "Stained"),
        ("★ Gut Knife", "Urban Masked"),
        ("★ Gut Knife", "Safari Mesh"),
        ("★ Gut Knife", "Stained"),
        ("★ Gut Knife", "Blue Steel")
    ]
})

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
def shop():
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
    user = create_user_from_dict(session['user'])
    return render_template('shop.html', 
                         balance=user.balance, 
                         RANK_EXP=RANK_EXP,
                         RANKS=RANKS)

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
    
    # Sort items so newest appears first
    inventory_items = sorted(inventory_items, key=lambda x: x.get('timestamp', 0) if not x.get('is_case') else 0, reverse=True)
    
    # Add debug logging
    print("Inventory route - items being sent to template:", inventory_items)
    
    view = request.args.get('view', 'skins')  # Get the view parameter, default to skins
    
    return render_template('inventory.html', 
                         balance=session['user']['balance'], 
                         inventory=inventory_items,  # Pass the inventory directly
                         RANK_EXP=RANK_EXP,
                         RANKS=RANKS,
                         initial_view=view)

@app.route('/open/<case_type>')
def open_case(case_type):
    if 'user' not in session:
        return jsonify({'error': 'User not found'})
    
    user = create_user_from_dict(session['user'])
    inventory = session['user'].get('inventory', [])
    
    print(f"Opening case type: {case_type}")
    print(f"Current inventory before opening: {inventory}")
    
    # Find the case in inventory
    case_found = False
    case_to_remove = None
    for item in inventory:
        if item.get('is_case') and item.get('type') == case_type:
            if item.get('quantity', 0) > 0:
                case_found = True
                item['quantity'] -= 1  # Decrease case quantity
                if item['quantity'] == 0:
                    case_to_remove = item  # Mark for removal
                break
    
    # Remove case if quantity is 0
    if case_to_remove:
        inventory.remove(case_to_remove)
    
    if not case_found:
        print("No cases found in inventory")
        return jsonify({'error': 'No cases of this type in inventory'})
    
    case = CSGO_WEAPON_CASE if case_type == 'csgo' else ESPORTS_2013_CASE
    skin = case.open()
    
    if skin:
        print(f"Successfully opened case. Got skin: {skin.weapon} | {skin.name}")
        
        # Add experience based on case price and log it
        case_price = CASE_PRICES[case_type]
        print(f"Adding {case_price} EXP from case price")
        user.add_exp(case_price)
        print(f"New EXP: {user.exp}, Rank: {user.rank}")
        
        # Convert skin to dictionary format with timestamp and case_type
        skin_dict = {
            'weapon': skin.weapon,
            'name': skin.name,
            'rarity': skin.rarity.name,
            'wear': skin.wear.name,
            'stattrak': skin.stattrak,
            'price': skin.get_price(),
            'timestamp': time.time(),
            'case_type': case_type  # Make sure this is set
        }
        
        print(f"Created skin_dict with case_type: {skin_dict}")  # Debug log
        
        # Add the skin dictionary to inventory
        inventory.append(skin_dict)
        
        print(f"Updated inventory after opening: {inventory}")
        
        # Update session with all user data
        session['user'] = {
            'balance': user.balance,
            'inventory': inventory,
            'exp': user.exp,
            'rank': user.rank,
            'upgrades': asdict(user.upgrades)
        }
        
        # Verify the case_type is still present
        print(f"Verifying case_type in session: {session['user']['inventory'][-1].get('case_type')}")
        
        return jsonify({
            'item': skin_dict,
            'balance': user.balance,
            'exp': int(user.exp),
            'rank': user.rank,
            'rankName': RANKS[user.rank],
            'nextRankExp': RANK_EXP[user.rank] if user.rank < len(RANK_EXP) else None
        })
    
    print("Failed to open case - no skin generated")
    return jsonify({'error': 'Failed to open case'})

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

@app.route('/sell/last', methods=['POST'])
@app.route('/sell/<int:item_index>', methods=['POST'])
def sell_item(item_index=None):
    if 'user' not in session:
        return jsonify({'error': 'User not found'})
    
    user = create_user_from_dict(session['user'])
    inventory = session['user']['inventory']
    
    try:
        # Get only skin items (not cases) for selling
        skin_items = [item for item in inventory if not item.get('is_case')]
        actual_index = len(skin_items) - 1 if item_index is None else item_index
        
        item = skin_items[actual_index]
        sale_price = item.get('price', 0)
        
        user.balance += sale_price
        
        # Remove the sold item from inventory
        inventory.remove(item)
        
        # Update session with ALL user data, preserving cases and case_type
        session['user'] = {
            'balance': user.balance,
            'inventory': inventory,  # Keep the entire inventory including cases and case_type
            'exp': user.exp,
            'rank': user.rank,
            'upgrades': asdict(user.upgrades)
        }
        
        return jsonify({
            'success': True,
            'balance': user.balance,
            'sold_price': sale_price,
            'exp': int(user.exp),
            'rank': user.rank,
            'rankName': RANKS[user.rank],
            'nextRankExp': RANK_EXP[user.rank] if user.rank < len(RANK_EXP) else None
        })
        
    except IndexError:
        return jsonify({'error': 'Item not found'})

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
    
    user = create_user_from_dict(session['user'])
    
    # Apply click value multiplier
    base_click = 0.01 * (1.5 ** user.upgrades.click_value)
    earned = base_click * multiplier
    
    # Apply critical multiplier if it was a critical hit
    if critical:
        earned *= 4
    
    user.balance += earned
    
    # Update session with ALL user data
    session['user'] = {
        'balance': user.balance,
        'inventory': user.inventory,  # Just pass the inventory directly since it's already in dict format
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
        'inventory': [{
            'weapon': s.weapon,
            'name': s.name,
            'rarity': s.rarity.name,
            'wear': s.wear.name,
            'stattrak': s.stattrak,
            'price': s.get_price()
        } for s in user.inventory],
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
    
    # Update session
    session['user'] = {
        'balance': user.balance,
        'inventory': [{
            'weapon': s.weapon,
            'name': s.name,
            'rarity': s.rarity.name,
            'wear': s.wear.name,
            'stattrak': s.stattrak,
            'price': s.get_price()
        } for s in user.inventory],
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
    
    if case_type not in CASE_PRICES:
        return jsonify({'error': 'Invalid case type'})
    
    total_cost = CASE_PRICES[case_type] * quantity
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
    # Add debug logging
    print("Current inventory items:", inventory_items)
    
    # Sort items so newest appears first
    inventory_items = sorted(inventory_items, 
                           key=lambda x: x.get('timestamp', 0) if not x.get('is_case') else 0, 
                           reverse=True)
    
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

if __name__ == '__main__':
    app.run(debug=True)
