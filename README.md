# CS:GO Case Clicker

A modern web-based CS:GO case clicker game with various gambling features, trading mechanics, and a responsive UI built with Vue.js.

## Features

- 🎮 **Game Modes**
  - Case Opening System
  - Roulette
  - Jackpot
  - Coinflip
  - Crash Game
  - Blackjack
  - Trading System
  - Inventory Management
  - Shop System
  - Upgrades

- 💰 **Economy System**
  - Virtual Currency
  - Item Trading with Bots
  - Daily Trading Opportunities
  - Achievement System
  - Case Price & Float System

## Tech Stack

- **Frontend**:
  - Vue.js 3
  - Vuex for state management
  - Vue Router
  - Tailwind CSS
  - Modern ES6+ JavaScript

- **Backend**:
  - Python/Flask
  - RESTful API architecture
  - JSON-based data storage

- **Data Storage**:
  - Local JSON files for persistence
  - In-memory caching for performance

## Project Structure

```
case-clicker/
├── frontend/                # Vue.js frontend application
│   ├── src/                # Source files
│   │   ├── components/     # Vue components
│   │   ├── views/          # Vue views/pages
│   │   ├── store/          # Vuex store
│   │   └── router/         # Vue router
│   ├── public/             # Static assets
│   └── dist/               # Production build
│
├── Backend/
│   ├── app.py             # Main Flask application
│   ├── config.py          # Configuration settings
│   ├── models.py          # Database models
│   ├── bots.py           # Trading bot logic
│   ├── casino.py         # Gambling game logic
│   ├── blackjack.py      # Blackjack game logic
│   ├── user_data.py      # User management
│   ├── achievements.py   # Achievement system
│   ├── daily_trades.py   # Trading system
│   └── crash_simulation.py # Crash game logic
│
├── data/                  # Game data
├── cases/                 # Case definitions
└── static/               # Static assets for backend
```

## Setup Instructions

1. Clone the repository:
```bash
git clone https://github.com/yourusername/case-clicker.git
cd case-clicker
```

2. Backend Setup:
```bash
# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install Python dependencies
pip install -r requirements.txt

# Set up environment variables
# Create .env file with necessary configurations
```

3. Frontend Setup:
```bash
cd frontend
npm install
```

4. Running the Application:

Development mode:
```bash
# Terminal 1 - Backend
flask run

# Terminal 2 - Frontend
cd frontend
npm run serve
```

Production mode:
```bash
cd frontend
npm run build
# Then serve the backend with your preferred production server
```

## Game Features Details

### Case Opening
- Open various CS:GO-style cases
- Different rarity levels for items
- Advanced float value system for skins
- Real-time price updates

### Trading System
- Advanced bot trading system
- Market-based pricing algorithm
- Daily trading opportunities
- Trade-up contracts

### Gambling Games
- **Roulette**: Classic CS:GO roulette with multiple betting options
- **Jackpot**: Pool betting system with multiple players
- **Coinflip**: 50/50 chance gambling
- **Crash**: Multiplier-based gambling game
- **Blackjack**: Classic card game implementation

### Progression System
- Comprehensive achievement system
- Upgrade system for better odds
- Daily rewards and bonuses
- User statistics tracking

## Contributing

Feel free to submit issues and enhancement requests!

## License

This project is licensed under the MIT License - see the LICENSE file for details.