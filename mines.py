import random
import math
from typing import List, Dict, Tuple

class MinesGame:
    def __init__(self, grid_size: int, num_mines: int, bet_amount: float):
        self.grid_size = grid_size
        self.num_mines = num_mines
        self.bet_amount = bet_amount
        self.grid = self._create_grid()
        self.revealed = set()  # Set of revealed positions (x, y)
        self.game_over = False
        self.won = False
        self.current_multiplier = 1.0  # Start with multiplier of 1
    
    def _create_grid(self) -> List[List[bool]]:
        """Creates a grid with randomly placed mines. True represents a mine."""
        total_tiles = self.grid_size * self.grid_size
        # Create a list of all positions
        positions = [(x, y) for x in range(self.grid_size) for y in range(self.grid_size)]
        # Randomly select positions for mines
        mine_positions = random.sample(positions, self.num_mines)
        
        # Create the grid
        grid = [[False] * self.grid_size for _ in range(self.grid_size)]
        for x, y in mine_positions:
            grid[x][y] = True
            
        return grid
    
    def reveal(self, x: int, y: int) -> Dict:
        """Reveals a tile at position (x, y). Returns game state."""
        if self.game_over:
            return {"error": "Game is already over"}
            
        if (x, y) in self.revealed:
            return {"error": "Tile already revealed"}
            
        # Debug: Print initial state
        print(f"\nDEBUG: Starting reveal at ({x}, {y})")
        print(f"DEBUG: Current multiplier before calculation: {self.current_multiplier}")
        
        # Update multiplier before adding new tile to revealed set
        total_tiles = self.grid_size * self.grid_size
        k = len(self.revealed)  # k is the number of previously revealed tiles
        
        # Calculate multiplier for this specific reveal
        numerator = total_tiles - k
        denominator = total_tiles - k - self.num_mines
        
        # Debug: Print calculation details
        print(f"DEBUG: Grid size: {self.grid_size}x{self.grid_size}")
        print(f"DEBUG: Total tiles: {total_tiles}")
        print(f"DEBUG: Number of mines: {self.num_mines}")
        print(f"DEBUG: Previously revealed tiles (k): {k}")
        print(f"DEBUG: Numerator (total_tiles - k): {numerator}")
        print(f"DEBUG: Denominator (total_tiles - k - num_mines): {denominator}")
        
        factor = numerator / denominator
        print(f"DEBUG: Factor for this reveal (numerator/denominator): {factor}")
        
        # Apply 5% house edge
        factor = factor * 0.95
        print(f"DEBUG: Factor after house edge: {factor}")
        
        self.current_multiplier *= factor
        print(f"DEBUG: New multiplier after multiplication: {self.current_multiplier}")
        
        self.current_multiplier = round(self.current_multiplier, 2)
        print(f"DEBUG: Final multiplier after rounding: {self.current_multiplier}")
        
        # Now add to revealed set
        self.revealed.add((x, y))
        
        # Check if mine hit
        if self.grid[x][y]:
            self.game_over = True
            return {
                "status": "game_over",
                "hit_mine": True,
                "grid": self.grid,
                "multiplier": 0,
                "potential_win": 0
            }
        
        potential_win = self.bet_amount * self.current_multiplier
        print(f"DEBUG: Potential win: ${potential_win}")
        
        # Check if all safe tiles revealed (win condition)
        total_safe_tiles = self.grid_size * self.grid_size - self.num_mines
        if len(self.revealed) == total_safe_tiles:
            self.game_over = True
            self.won = True
            return {
                "status": "win",
                "hit_mine": False,
                "grid": self.grid,
                "multiplier": self.current_multiplier,
                "potential_win": potential_win
            }
            
        return {
            "status": "continue",
            "hit_mine": False,
            "revealed": list(self.revealed),
            "multiplier": self.current_multiplier,
            "potential_win": potential_win
        }
    
    def cash_out(self) -> Dict:
        """Allows player to cash out current winnings."""
        if self.game_over:
            return {"error": "Game is already over"}
            
        if not self.revealed:
            return {"error": "Must reveal at least one tile to cash out"}
            
        self.game_over = True
        self.won = True
        
        return {
            "status": "cash_out",
            "multiplier": self.current_multiplier,
            "win_amount": self.bet_amount * self.current_multiplier,
            "revealed": list(self.revealed),
            "grid": self.grid
        }
    
    @staticmethod
    def validate_params(grid_size: int, num_mines: int, bet_amount: float) -> Tuple[bool, str]:
        """Validates game parameters."""
        if grid_size < 4 or grid_size > 8:
            return False, "Grid size must be between 4 and 8"
            
        total_tiles = grid_size * grid_size
        if num_mines < 1 or num_mines > total_tiles - 1:
            return False, f"Number of mines must be between 1 and {total_tiles - 1}"
            
        if bet_amount <= 0:
            return False, "Bet amount must be greater than 0"
            
        return True, "" 