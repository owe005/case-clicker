# CS:GO Case Clicker

A web-based CS:GO case clicker game with various gambling features and trading mechanics.

## Features

- 🎮 **Game Modes**
  - Case Opening System
  - Roulette
  - Jackpot
  - Coinflip
  - Crash Game
  - Trading System
  - Inventory Management
  - Shop System
  - Upgrades

- 💰 **Economy System**
  - Virtual Currency
  - Item Trading
  - Daily Trades
  - Achievement System

## Tech Stack

- Backend: Python/Flask
- Frontend: HTML, CSS, JavaScript
- Database: SQLite (via SQLAlchemy)

## Project Structure

```
case-clicker/
├── app.py              # Main Flask application
├── config.py           # Configuration settings
├── models.py           # Database models
├── bots.py            # Trading bot logic
├── casino.py          # Gambling game logic
├── user_data.py       # User management
├── achievements.py    # Achievement system
├── daily_trades.py    # Trading system
├── templates/         # HTML templates
├── static/            # CSS, JS, and assets
├── data/             # Game data
└── cases/            # Case definitions
```

## Setup Instructions

1. Clone the repository:
```bash
git clone https://github.com/yourusername/case-clicker.git
cd case-clicker
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
Create a `.env` file with necessary configurations.

5. Initialize the database:
```bash
flask db init
flask db migrate
flask db upgrade
```

6. Run the application:
```bash
flask run
```

## Game Features Details

### Case Opening
- Open various CS:GO-style cases
- Different rarity levels for items
- Float value system for skins

### Trading System
- Trade items with bots
- Daily trading opportunities
- Market value based pricing

### Gambling Games
- **Roulette**: Classic CS:GO roulette with multiple betting options
- **Jackpot**: Pool betting system with multiple players
- **Coinflip**: 50/50 chance gambling
- **Crash**: Multiplier-based gambling game

### Progression System
- Achievement system for rewards
- Upgrade system for better odds
- Daily rewards and bonuses

## Contributing

Feel free to submit issues and enhancement requests!

## License

This project is licensed under the MIT License - see the LICENSE file for details.