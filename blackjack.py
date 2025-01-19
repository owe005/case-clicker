import random
from dataclasses import dataclass
from typing import List, Optional, Tuple

# Card representation
@dataclass
class Card:
    rank: str
    suit: str
    value: int
    is_ace: bool = False
    
    def to_dict(self) -> dict:
        return {
            'rank': self.rank,
            'suit': self.suit,
            'value': self.value,
            'is_ace': self.is_ace
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Card':
        return cls(
            rank=data['rank'],
            suit=data['suit'],
            value=data.get('value', 0),
            is_ace=data.get('is_ace', False)
        )

class Hand:
    def __init__(self):
        self.cards: List[Card] = []
        self.bet: float = 0.0
        self.doubled: bool = False
        self.can_split: bool = False
        self.insurance: float = 0.0
        
    def to_dict(self) -> dict:
        return {
            'cards': [card.to_dict() for card in self.cards],
            'bet': self.bet,
            'doubled': self.doubled,
            'can_split': self.can_split,
            'insurance': self.insurance
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Hand':
        hand = cls()
        hand.cards = [Card.from_dict(card_data) for card_data in data['cards']]
        hand.bet = data.get('bet', 0.0)
        hand.doubled = data.get('doubled', False)
        hand.can_split = data.get('can_split', False)
        hand.insurance = data.get('insurance', 0.0)
        return hand
        
    @property
    def value(self) -> int:
        total = 0
        aces = 0
        
        for card in self.cards:
            if card.is_ace:
                aces += 1
            total += card.value
            
        # Handle aces
        while total > 21 and aces > 0:
            total -= 10
            aces -= 1
            
        return total
        
    @property
    def is_blackjack(self) -> bool:
        return len(self.cards) == 2 and self.value == 21
        
    @property
    def is_busted(self) -> bool:
        return self.value > 21
        
    def can_double(self) -> bool:
        return len(self.cards) == 2 and not self.doubled
        
    def add_card(self, card: Card):
        self.cards.append(card)
        # Check if we can split whenever we have exactly 2 cards
        self.can_split = len(self.cards) == 2 and (
            self.cards[0].rank == self.cards[1].rank or 
            (self.cards[0].value == 10 and self.cards[1].value == 10)
        )

class BlackjackGame:
    def __init__(self):
        self.deck = self._create_deck()
        self.dealer_hand = Hand()
        self.player_hands: List[Hand] = []
        self.current_hand_index: int = 0
        self.game_over: bool = False
        self.shuffle_threshold = 52  # Reshuffle when less than this many cards remain
        
    @classmethod
    def from_state(cls, state: dict) -> 'BlackjackGame':
        """Reconstruct a BlackjackGame instance from a state dictionary."""
        game = cls()
        
        # Reconstruct dealer hand
        for card_data in state['dealer_hand']['cards']:
            game.dealer_hand.add_card(Card(card_data['rank'], card_data['suit'], 0, card_data['rank'] == 'A'))
        
        # Reconstruct player hands
        game.player_hands = []
        for hand_data in state['player_hands']:
            hand = Hand()
            for card_data in hand_data['cards']:
                hand.add_card(Card(card_data['rank'], card_data['suit'], 0, card_data['rank'] == 'A'))
            hand.bet = hand_data['bet']
            hand.doubled = hand_data.get('doubled', False)
            hand.insurance = hand_data.get('insurance', 0)
            game.player_hands.append(hand)
        
        game.current_hand_index = state['current_hand_index']
        game.game_over = state['game_over']
        return game
    
    def to_state(self) -> dict:
        """Convert the current game state to a dictionary for storage."""
        return {
            'dealer_hand': {
                'cards': [{'rank': c.rank, 'suit': c.suit} for c in self.dealer_hand.cards],
                'value': self.dealer_hand.value
            },
            'player_hands': [{
                'cards': [{'rank': c.rank, 'suit': c.suit} for c in hand.cards],
                'value': hand.value,
                'bet': hand.bet,
                'doubled': hand.doubled,
                'insurance': hand.insurance
            } for hand in self.player_hands],
            'current_hand_index': self.current_hand_index,
            'game_over': self.game_over
        }
        
    def _create_deck(self, num_decks: int = 6) -> List[Card]:
        ranks = {
            '2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9, '10': 10,
            'J': 10, 'Q': 10, 'K': 10, 'A': 11
        }
        suits = ['♠', '♥', '♦', '♣']
        deck = []
        
        for _ in range(num_decks):
            for suit in suits:
                for rank, value in ranks.items():
                    deck.append(Card(rank, suit, value, rank == 'A'))
                    
        random.shuffle(deck)
        return deck
        
    def check_deck(self):
        if len(self.deck) < self.shuffle_threshold:
            self.deck = self._create_deck()
            
    def start_game(self, bet: float) -> dict:
        self.check_deck()
        self.game_over = False
        self.dealer_hand = Hand()
        self.player_hands = [Hand()]
        self.current_hand_index = 0
        
        # Set initial bet
        self.player_hands[0].bet = bet
        
        # Deal initial cards
        self.player_hands[0].add_card(self.deck.pop())
        self.dealer_hand.add_card(self.deck.pop())
        self.player_hands[0].add_card(self.deck.pop())
        self.dealer_hand.add_card(self.deck.pop())
        
        # Check for dealer blackjack possibility
        insurance_available = self.dealer_hand.cards[0].rank == 'A'
        
        # Return both display state and internal state
        return {
            'display_state': self.get_game_state(insurance_available),
            'internal_state': self.to_state()
        }
        
    def hit(self) -> dict:
        if self.game_over:
            return {
                'display_state': self.get_game_state(),
                'internal_state': self.to_state()
            }
            
        current_hand = self.player_hands[self.current_hand_index]
        current_hand.add_card(self.deck.pop())
        
        if current_hand.is_busted:
            self.move_to_next_hand()
            
        return {
            'display_state': self.get_game_state(),
            'internal_state': self.to_state()
        }
        
    def stand(self) -> dict:
        if self.game_over:
            return {
                'display_state': self.get_game_state(),
                'internal_state': self.to_state()
            }
            
        self.move_to_next_hand()
        return {
            'display_state': self.get_game_state(),
            'internal_state': self.to_state()
        }
        
    def double_down(self) -> dict:
        if self.game_over:
            return {
                'display_state': self.get_game_state(),
                'internal_state': self.to_state()
            }
            
        current_hand = self.player_hands[self.current_hand_index]
        if not current_hand.can_double():
            return {
                'display_state': self.get_game_state(),
                'internal_state': self.to_state()
            }
            
        current_hand.doubled = True
        current_hand.bet *= 2
        current_hand.add_card(self.deck.pop())
        
        if current_hand.is_busted:
            self.move_to_next_hand()
            
        return {
            'display_state': self.get_game_state(),
            'internal_state': self.to_state()
        }
        
    def split(self) -> dict:
        if self.game_over:
            return {
                'display_state': self.get_game_state(),
                'internal_state': self.to_state()
            }
            
        current_hand = self.player_hands[self.current_hand_index]
        if not current_hand.can_split:
            return {
                'display_state': self.get_game_state(),
                'internal_state': self.to_state()
            }
            
        # Create new hand with second card
        new_hand = Hand()
        new_hand.bet = current_hand.bet
        new_hand.add_card(current_hand.cards.pop())
        
        # Add new card to each hand
        current_hand.add_card(self.deck.pop())
        new_hand.add_card(self.deck.pop())
        
        # Insert new hand after current hand
        self.player_hands.insert(self.current_hand_index + 1, new_hand)
        
        # Reset current hand index to allow player to act on both hands
        self.current_hand_index = 0
        
        return {
            'display_state': self.get_game_state(),
            'internal_state': self.to_state()
        }
        
    def insurance(self) -> dict:
        if self.game_over or not self.dealer_hand.cards[1].rank == 'A':
            return {
                'display_state': self.get_game_state(),
                'internal_state': self.to_state()
            }
            
        current_hand = self.player_hands[self.current_hand_index]
        current_hand.insurance = current_hand.bet / 2
        
        return {
            'display_state': self.get_game_state(),
            'internal_state': self.to_state()
        }
        
    def move_to_next_hand(self):
        self.current_hand_index += 1
        if self.current_hand_index >= len(self.player_hands):
            self.play_dealer_hand()
            
    def play_dealer_hand(self):
        # Dealer must hit on soft 17
        while self.dealer_hand.value < 17 or (
            self.dealer_hand.value == 17 and 
            any(card.is_ace for card in self.dealer_hand.cards)
        ):
            self.dealer_hand.add_card(self.deck.pop())
            
        self.game_over = True
        
    def get_hand_result(self, hand: Hand) -> Tuple[str, float]:
        if hand.is_busted:
            return 'BUST', -hand.bet
            
        if hand.is_blackjack and not self.dealer_hand.is_blackjack:
            return 'BLACKJACK', hand.bet * 1.5
            
        if self.dealer_hand.is_blackjack:
            if hand.insurance > 0:
                insurance_win = hand.insurance * 2
            else:
                insurance_win = 0
                
            if hand.is_blackjack:
                return 'PUSH', insurance_win
            return 'DEALER BLACKJACK', -hand.bet + insurance_win
            
        if self.dealer_hand.is_busted:
            return 'DEALER BUST', hand.bet
            
        if hand.value > self.dealer_hand.value:
            return 'WIN', hand.bet
        elif hand.value < self.dealer_hand.value:
            return 'LOSE', -hand.bet
        else:
            return 'PUSH', 0
            
    def get_game_state(self, insurance_available: bool = False) -> dict:
        """Get the current game state in a format suitable for the frontend."""
        # Convert dealer's hand to display format
        dealer_cards = [
            {
                'rank': card.rank,
                'suit': card.suit,
                'value': card.value,
                'is_ace': card.is_ace
            } for card in self.dealer_hand.cards
        ]
        
        # Convert player hands to display format
        player_hands = []
        for i, hand in enumerate(self.player_hands):
            player_hand = {
                'cards': [
                    {
                        'rank': card.rank,
                        'suit': card.suit,
                        'value': card.value,
                        'is_ace': card.is_ace
                    } for card in hand.cards
                ],
                'value': hand.value,
                'bet': hand.bet,
                'doubled': hand.doubled,
                'can_split': hand.can_split,
                'insurance': hand.insurance,
                'is_current': i == self.current_hand_index,
                'is_busted': hand.is_busted,
                'is_blackjack': hand.is_blackjack
            }
            
            # Add result and payout info if game is over
            if self.game_over:
                player_hand['result'] = self.get_hand_result(hand)[0]  # Add result to the hand
                player_hand['payout'] = self.calculate_payout(hand)
                
            player_hands.append(player_hand)
            
        return {
            'dealer_hand': {
                'cards': dealer_cards,
                'value': self.dealer_hand.value if self.game_over else None
            },
            'player_hands': player_hands,
            'current_hand_index': self.current_hand_index,
            'game_over': self.game_over,
            'insurance_available': insurance_available
        } 
        
    def calculate_payout(self, hand: Hand) -> float:
        """Calculate the payout for a hand."""
        if hand.is_busted:
            return 0
            
        dealer_value = self.dealer_hand.value
        hand_value = hand.value
        
        # Handle blackjack
        if hand.is_blackjack:
            if self.dealer_hand.is_blackjack:
                return hand.bet  # Push
            return hand.bet * 2.5  # Blackjack pays 3:2
            
        # Handle dealer blackjack
        if self.dealer_hand.is_blackjack:
            if hand.insurance:
                return hand.insurance * 2  # Insurance pays 2:1
            return 0
            
        # Handle dealer bust
        if dealer_value > 21:
            return hand.bet * 2
            
        # Compare values
        if hand_value > dealer_value:
            return hand.bet * 2
        elif hand_value == dealer_value:
            return hand.bet  # Push
        return 0 