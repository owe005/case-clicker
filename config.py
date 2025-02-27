# Standard library imports
import os
from enum import Enum
from typing import Optional

# Third-party imports
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv()

# Featured skins refresh interval
REFRESH_INTERVAL = 3600 
AUCTION_FILE = 'data/auction_data.json'

# Initialize OpenAI client with API key from environment
api_key = os.getenv('OPENAI_API_KEY')
if not api_key:
    print("Warning: OPENAI_API_KEY not found in environment variables")
    client = None
else:
    print(f"API key loaded: {api_key[:8]}...") # Debug print to verify key is loaded
    client = OpenAI(api_key=api_key)

class Rarity(Enum):
    CONTRABAND = "CONTRABAND"
    GOLD = "GOLD"
    RED = "RED"
    PINK = "PINK"
    PURPLE = "PURPLE"
    BLUE = "BLUE"
    LIGHT_BLUE = "LIGHT_BLUE"
    GREY = "GREY"

class Wear(Enum):
    BS = "Battle-Scarred"
    WW = "Well-Worn"
    FT = "Field-Tested"
    MW = "Minimal Wear"
    FN = "Factory New"

# Roulette
RED_NUMBERS = {1, 3, 5, 7, 9, 12, 14, 16, 18, 19, 21, 23, 25, 27, 30, 32, 34, 36}
BLACK_NUMBERS = {2, 4, 6, 8, 10, 11, 13, 15, 17, 20, 22, 24, 26, 28, 29, 31, 33, 35}    

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

CASE_FILE_MAPPING = {
    'csgo': 'weapon_case_1',
    'esports': 'esports_2013',
    'bravo': 'operation_bravo',
    'csgo2': 'weapon_case_2',
    'esports_winter': 'esports_2013_winter',
    'winter_offensive': 'winter_offensive_case',
    'csgo3': 'weapon_case_3',
    'phoenix': 'operation_phoenix_case',
    'huntsman': 'huntsman_case',
    'breakout': 'operation_breakout_case',
    'esports_summer': 'esports_2014_summer',
    'vanguard': 'operation_vanguard_case',
    'chroma': 'chroma_case',
    'chroma_2': 'chroma_2_case',
    'falchion': 'falchion_case',
    'shadow': 'shadow_case',
    'revolution': 'revolution_case',
    'wildfire': 'operation_wildfire_case',
    'revolver': 'revolver_case',
    'chroma_3': 'chroma_3_case',
    'gamma': 'gamma_case',
    'gamma_2': 'gamma_2_case',
    'hydra': 'operation_hydra_case',
    'glove': 'glove_case',
    'spectrum': 'spectrum_case',
    'spectrum_2': 'spectrum_2_case',
    'clutch': 'clutch_case',
    'cs20': 'cs20_case',
    'danger_zone': 'danger_zone_case',
    'horizon': 'horizon_case',
    'riptide': 'operation_riptide_case',
    'shattered_web': 'shattered_web_case',
    'dreams_&_nightmares': 'dreams_&_nightmares_case',
    'fracture': 'fracture_case',
    'gallery': 'gallery_case',
    'kilowatt': 'kilowatt_case',
    'recoil': 'recoil_case',
    'snakebite': 'snakebite_case',
    'broken_fang': 'operation_broken_fang_case',
    'prisma': 'prisma_case',
    'prisma_2': 'prisma_2_case'
}

CASE_TYPES = [
    'csgo', 
    'esports', 
    'bravo', 
    'csgo2', 
    'esports_winter', 
    'winter_offensive', 
    'csgo3', 
    'phoenix', 
    'huntsman', 
    'breakout', 
    'esports_summer', 
    'vanguard', 
    'chroma', 
    'chroma_2', 
    'falchion',
    'shadow',
    'revolution',
    'wildfire',
    'revolver',
    'chroma_3',
    'gamma',
    'gamma_2',
    'hydra',
    'glove',
    'spectrum',
    'spectrum_2',
    'clutch',
    'cs20',
    'danger_zone',
    'horizon',
    'riptide',
    'shattered_web',
    'dreams_&_nightmares',
    'fracture',
    'gallery',
    'kilowatt',
    'recoil',
    'snakebite',
    'broken_fang',
    'prisma',
    'prisma_2'
]

CASE_SKINS_FOLDER_NAMES = {
    'csgo': 'weapon_case_1',
    'esports': 'esports_2013',
    'bravo': 'operation_bravo_case',
    'csgo2': 'weapon_case_2',
    'esports_winter': 'esports_2013_winter',
    'winter_offensive': 'winter_offensive_case',
    'csgo3': 'weapon_case_3',
    'phoenix': 'operation_phoenix_case',
    'huntsman': 'huntsman_case',
    'breakout': 'operation_breakout_case',
    'esports_summer': 'esports_2014_summer',
    'vanguard': 'operation_vanguard_case',
    'chroma': 'chroma_case',
    'chroma_2': 'chroma_2_case',
    'falchion': 'falchion_case',
    'shadow': 'shadow_case',
    'revolution': 'revolution_case',
    'wildfire': 'operation_wildfire_case',
    'revolver': 'revolver_case',
    'chroma_3': 'chroma_3_case',
    'gamma': 'gamma_case',
    'gamma_2': 'gamma_2_case',
    'hydra': 'operation_hydra_case',
    'glove': 'glove_case',
    'spectrum': 'spectrum_case',
    'spectrum_2': 'spectrum_2_case',
    'clutch': 'clutch_case',
    'cs20': 'cs20_case',
    'danger_zone': 'danger_zone_case',
    'horizon': 'horizon_case',
    'riptide': 'operation_riptide_case',
    'shattered_web': 'shattered_web_case',
    'dreams_&_nightmares': 'dreams_&_nightmares_case',
    'fracture': 'fracture_case',
    'gallery': 'gallery_case',
    'kilowatt': 'kilowatt_case',
    'recoil': 'recoil_case',
    'snakebite': 'snakebite_case',
    'broken_fang': 'operation_broken_fang_case',
    'prisma': 'prisma_case',
    'prisma_2': 'prisma_2_case'
}

CASE_DATA = {
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
    'breakout': {
        'name': 'Operation Breakout Case',
        'image': 'operation_breakout_case.png',
        'is_case': True,
        'type': 'breakout'
    },
    'esports_summer': {
        'name': 'eSports 2014 Summer Case',
        'image': 'esports_2014_summer_case.png',
        'is_case': True,
        'type': 'esports_summer'
    },
    'vanguard': {
        'name': 'Operation Vanguard Case',
        'image': 'operation_vanguard_case.png',
        'is_case': True,
        'type': 'vanguard'
    },
    'chroma': {
        'name': 'Chroma Case',
        'image': 'chroma_case.png',
        'is_case': True,
        'type': 'chroma'
    },
    'chroma_2': {
        'name': 'Chroma 2 Case',
        'image': 'chroma_2_case.png',
        'is_case': True,
        'type': 'chroma_2'
    },
    'falchion': {
        'name': 'Falchion Case',
        'image': 'falchion_case.png',
        'is_case': True,
        'type': 'falchion'
    },
    'shadow': {
        'name': 'Shadow Case',
        'image': 'shadow_case.png',
        'is_case': True,
        'type': 'shadow'
    },
    'revolution': {
        'name': 'Revolution Case',
        'image': 'revolution_case.png',
        'is_case': True,
        'type': 'revolution'
    },
    'wildfire': {
        'name': 'Operation Wildfire Case',
        'image': 'operation_wildfire_case.png',
        'is_case': True,
        'type': 'wildfire'
    },
    'revolver': {
        'name': 'Revolver Case',
        'image': 'revolver_case.png',
        'is_case': True,
        'type': 'revolver'
    },
    'chroma_3': {
        'name': 'Chroma 3 Case',
        'image': 'chroma_3_case.png',
        'is_case': True,
        'type': 'chroma_3'
    },
    'gamma': {
        'name': 'Gamma Case',
        'image': 'gamma_case.png',
        'is_case': True,
        'type': 'gamma'
    },
    'gamma_2': {
        'name': 'Gamma 2 Case',
        'image': 'gamma_2_case.png',
        'is_case': True,
        'type': 'gamma_2'
    },
    'hydra': {
        'name': 'Operation Hydra Case',
        'image': 'operation_hydra_case.png',
        'is_case': True,
        'type': 'hydra'
    },
    'glove': {
        'name': 'Glove Case',
        'image': 'glove_case.png',
        'is_case': True,
        'type': 'glove'
    },
    'spectrum': {
        'name': 'Spectrum Case',
        'image': 'spectrum_case.png',
        'is_case': True,
        'type': 'spectrum'
    },
    'spectrum_2': {
        'name': 'Spectrum 2 Case',
        'image': 'spectrum_2_case.png',
        'is_case': True,
        'type': 'spectrum_2'
    },
    'clutch': {
        'name': 'Clutch Case',
        'image': 'clutch_case.png',
        'is_case': True,
        'type': 'clutch'
    },
    'cs20': {
        'name': 'CS20 Case',
        'image': 'cs20_case.png',
        'is_case': True,
        'type': 'cs20'
    },
    'danger_zone': {
        'name': 'Danger Zone Case',
        'image': 'danger_zone_case.png',
        'is_case': True,
        'type': 'danger_zone'
    },
    'horizon': {
        'name': 'Horizon Case',
        'image': 'horizon_case.png',
        'is_case': True,
        'type': 'horizon'
    },
    'riptide': {
        'name': 'Operation Riptide Case',
        'image': 'operation_riptide_case.png',
        'is_case': True,
        'type': 'riptide'
    },
    'shattered_web': {
        'name': 'Shattered Web Case',
        'image': 'shattered_web_case.png',
        'is_case': True,
        'type': 'shattered_web'
    },
    'dreams_&_nightmares': {
        'name': 'Dreams & Nightmares Case',
        'image': 'dreams_&_nightmares_case.png',
        'is_case': True,
        'type': 'dreams_&_nightmares'
    },
    'fracture': {
        'name': 'Fracture Case',
        'image': 'fracture_case.png',
        'is_case': True,
        'type': 'fracture'
    },
    'gallery': {
        'name': 'Gallery Case',
        'image': 'gallery_case.png',
        'is_case': True,
        'type': 'gallery'
    },
    'kilowatt': {
        'name': 'Kilowatt Case',
        'image': 'kilowatt_case.png',
        'is_case': True,
        'type': 'kilowatt'
    },
    'recoil': {
        'name': 'Recoil Case',
        'image': 'recoil_case.png',
        'is_case': True,
        'type': 'recoil'
    },
    'snakebite': {
        'name': 'Snakebite Case',
        'image': 'snakebite_case.png',
        'is_case': True,
        'type': 'snakebite'
    },
    'broken_fang': {
        'name': 'Operation Broken Fang Case',
        'image': 'operation_broken_fang_case.png',
        'is_case': True,
        'type': 'broken_fang'
    },
    'prisma': {
        'name': 'Prisma Case',
        'image': 'prisma_case.png',
        'is_case': True,
        'type': 'prisma'
    },
    'prisma_2': {
        'name': 'Prisma 2 Case',
        'image': 'prisma_2_case.png',
        'is_case': True,
        'type': 'prisma_2'
    }
}

SOUVENIR_CASE_FILE_MAPPING = {
    'cache_dreamhack_2014': 'cache_dreamhack_2014',
    'cobblestone_cologne_2014': 'cobblestone_cologne_2014',
    'dreamhack_2013': 'dreamhack_2013'
}

SOUVENIR_CASE_DATA = {
    'cache_dreamhack_2014': {
        'name': 'Cache Souvenir Package DreamHack 2014',
        'image': 'cache_dreamhack_2014.png',
        'is_case': True,
        'is_souvenir': True,
        'type': 'cache_dreamhack_2014'
    },
    'cobblestone_cologne_2014': {
        'name': 'Cobblestone Souvenir Package Cologne 2014',
        'image': 'cobblestone_cologne_2014.png',
        'is_case': True,
        'is_souvenir': True,
        'type': 'cobblestone_cologne_2014'
    },
    'dreamhack_2013': {
        'name': 'DreamHack 2013 Souvenir Package',
        'image': 'dreamhack_2013.png',
        'is_case': True,
        'is_souvenir': True,
        'type': 'dreamhack_2013'
    }
}

SOUVENIR_CASE_TYPES = list(SOUVENIR_CASE_FILE_MAPPING.keys())

STICKER_CAPSULE_FILE_MAPPING = {
    'challengers_cluj_napoca_2015': 'challengers_cluj_napoca_2015',
    'challengers_columbus_2016': 'challengers_columbus_2016',
    'challengers_katowice_2014': 'challengers_katowice_2014',
    'legends_boston_2018': 'legends_boston_2018',
    'legends_cologne_2014': 'legends_cologne_2014',
    'legends_columbus_2016': 'legends_columbus_2016',
    'legends_dreamhack_2014': 'legends_dreamhack_2014',
    'legends_katowice_2014': 'legends_katowice_2014',
    'legends_katowice_2015': 'legends_katowice_2015'
}

STICKER_CAPSULE_DATA = {
    'challengers_cluj_napoca_2015': {
        'name': 'Cluj-Napoca 2015 Challengers',
        'image': 'challengers_cluj_napoca_2015.png',
        'is_capsule': True,
        'type': 'challengers_cluj_napoca_2015'
    },
    'challengers_columbus_2016': {
        'name': 'MLG Columbus 2016 Challengers',
        'image': 'challengers_columbus_2016.png',
        'is_capsule': True,
        'type': 'challengers_columbus_2016'
    },
    'challengers_katowice_2014': {
        'name': 'Katowice 2014 Challengers',
        'image': 'challengers_katowice_2014.png',
        'is_capsule': True,
        'type': 'challengers_katowice_2014'
    },
    'legends_boston_2018': {
        'name': 'Boston 2018 Legends',
        'image': 'legends_boston_2018.png',
        'is_capsule': True,
        'type': 'legends_boston_2018'
    },
    'legends_cologne_2014': {
        'name': 'Cologne 2014 Legends',
        'image': 'legends_cologne_2014.png',
        'is_capsule': True,
        'type': 'legends_cologne_2014'
    },
    'legends_columbus_2016': {
        'name': 'MLG Columbus 2016 Legends',
        'image': 'legends_columbus_2016.png',
        'is_capsule': True,
        'type': 'legends_columbus_2016'
    },
    'legends_dreamhack_2014': {
        'name': 'DreamHack 2014 Legends',
        'image': 'legends_dreamhack_2014.png',
        'is_capsule': True,
        'type': 'legends_dreamhack_2014'
    },
    'legends_katowice_2014': {
        'name': 'Katowice 2014 Legends',
        'image': 'legends_katowice_2014.png',
        'is_capsule': True,
        'type': 'legends_katowice_2014'
    },
    'legends_katowice_2015': {
        'name': 'Katowice 2015 Legends',
        'image': 'legends_katowice_2015.png',
        'is_capsule': True,
        'type': 'legends_katowice_2015'
    }
}

# Sticker capsule drop chances (in percentage)
STICKER_DROP_CHANCES = {
    'blue': 80.0,
    'purple': 16.0,
    'pink': 3.841  # exotic
}

# Add souvenir case mappings
SOUVENIR_DROP_CHANCES = {
    'red': 0.26,
    'pink': 3.2,
    'purple': 15.98,
    'blue': 39.52,
    'light_blue': 35.0,
    'grey': 6.0
}

# Add souvenir chance
SOUVENIR_CHANCE = 10  # 10% chance for souvenir items