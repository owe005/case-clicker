from enum import Enum

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