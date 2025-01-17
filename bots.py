import json
import random
from typing import Any, Dict, List

from config import BOT_PERSONALITIES, CASE_FILE_MAPPING, CASE_TYPES, client, STICKER_CAPSULE_FILE_MAPPING
from cases_prices_and_floats import generate_float_for_wear

images_bots_avatars = {
    'Astrid47': 'bot1.png',
    'Kai.Jayden_02': 'bot2.png',
    'Orion_Phoenix98': 'bot3.png',
    'ElaraB_23': 'bot4.png',
    'Theo.91': 'bot5.png',
    'Nova-Lyn': 'bot6.png',
    'FelixHaven19': 'bot7.png',
    'Aria.Stella85': 'bot8.png',
    'Lucien_Kai': 'bot9.png',
    'Mira-Eclipse': 'bot10.png'
}

def generate_bot_players(num_bots: int, mode_limits: dict) -> List[Dict[str, Any]]:
    bot_names = [
        "_Astrid47", "Kai.Jayden_02", "Orion_Phoenix98", "ElaraB_23", "Theo.91", 
        "Nova-Lyn", "FelixHaven19", "Aria.Stella85", "Lucien_Kai", "Mira-Eclipse"
    ]
    
    # Load all case data and sticker data
    all_items = []  # Combined list for both skins and stickers
    
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
                        all_items.append({
                            'weapon': item['weapon'],
                            'name': item['name'],
                            'prices': item['prices'],
                            'case_type': case_type,
                            'case_file': file_name,
                            'image': item.get('image', f"{item['weapon'].lower().replace(' ', '')}_{item['name'].lower().replace(' ', '_')}.png"),
                            'rarity': grade.upper(),
                            'is_sticker': False
                        })
        except Exception as e:
            print(f"Error loading case {case_type}: {e}")
            continue
    
    # Load stickers from each capsule
    for capsule_type, file_name in STICKER_CAPSULE_FILE_MAPPING.items():
        try:
            with open(f'stickers/{file_name}.json', 'r') as f:
                capsule_data = json.load(f)
                # Add all stickers to the pool
                for grade, stickers in capsule_data['stickers'].items():
                    for sticker in stickers:
                        all_items.append({
                            'name': sticker['name'],
                            'price': float(sticker['price']),
                            'case_type': capsule_type,
                            'image': sticker['image'],
                            'rarity': grade.upper(),
                            'is_sticker': True
                        })
        except Exception as e:
            print(f"Error loading sticker capsule {capsule_type}: {e}")
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
            if not all_items:
                break
                
            item = random.choice(all_items)
            
            if item['is_sticker']:
                # Sticker items already have a direct price
                price = item['price']
                if mode_limits['min'] <= price <= mode_limits['max']:
                    bot_items.append({
                        'name': item['name'],
                        'price': price,
                        'case_type': item['case_type'],
                        'image': item['image'],
                        'rarity': item['rarity'],
                        'is_sticker': True
                    })
            else:
                # Handle weapon skins
                wear_options = [w for w in item['prices'].keys() 
                              if not w.startswith('ST_') and w != 'NO']
                if not wear_options:
                    continue
                    
                wear = random.choice(wear_options)
                stattrak = random.random() < 0.1  # 10% chance
                
                price_key = f"ST_{wear}" if stattrak else wear
                try:
                    price = float(item['prices'].get(price_key, 0))
                    
                    # Only add if price is within mode range
                    if mode_limits['min'] <= price <= mode_limits['max']:
                        bot_items.append({
                            'weapon': item['weapon'],
                            'name': item['name'],
                            'wear': wear,
                            'rarity': item['rarity'],
                            'stattrak': stattrak,
                            'price': price,
                            'case_type': item['case_type'],
                            'case_file': item['case_file'],
                            'image': item.get('image', f"{item['weapon'].lower().replace(' ', '')}_{item['name'].lower().replace(' ', '_')}.png"),
                            'float_value': generate_float_for_wear(wear),
                            'is_sticker': False
                        })
                except (ValueError, TypeError):
                    continue
        
        if bot_items:
            bots.append({
                'name': bot_name,
                'items': bot_items
            })
    
    return bots

def format_trade_info(trade):
    """Format a single trade into a readable string"""
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
    
    return f"{trade['botName']} is trading: {', '.join(offering)} for {', '.join(requesting)}"

def get_trades_context():
    """Load and format all current trades"""
    try:
        with open('data/daily_trades.json', 'r') as f:
            daily_trades = json.load(f)
            trades_info = [format_trade_info(trade) for trade in daily_trades.get('trades', [])]
            return "\n".join(trades_info)
    except Exception as e:
        print(f"Error loading trades: {e}")
        return "No active trades available."

def create_system_message(bot_name, personality, trades_context):
    """Create the system message for the chat bot"""
    return f"""You are {bot_name}, {personality} in a CS:GO trading chatroom.
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

def format_conversation_history(chat_history, message):
    """Format chat history for OpenAI API"""
    conversation = []
    for msg in chat_history[-5:]:
        role = "assistant" if msg['isBot'] else "user"
        content = msg['message']
        conversation.append({"role": role, "content": content})
    conversation.append({"role": "user", "content": message})
    return conversation

def format_bot_selection_system_message(chat_history, message):
    return f"""You are a bot selector for a CS:GO trading chat.
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

def format_bot_selection_history(chat_history, message):
    conversation_history = []
    for msg in chat_history[-5:]:
        role = "assistant" if msg['isBot'] else "user"
        content = f"{msg['sender']}: {msg['message']}"
        conversation_history.append({"role": role, "content": content})

    conversation_history.append({"role": "user", "content": f"User: {message}"})
    return conversation_history

def select_bot_with_ai(system_message, conversation_history):
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
        
    return selected_bot