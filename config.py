# Standard library imports
import os
from enum import Enum

# Third-party imports
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv()

# Featured skins refresh interval
REFRESH_INTERVAL = 3600 

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
    'horizon': 'horizon_case'
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
    'horizon'
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
    'horizon': 'horizon_case'
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
    }
}

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