# Taxas Hold'em Poker

A Python-based Texas Hold'em poker game implementation featuring machine learning capabilities and an interactive GUI.

## Features

- Complete poker game engine with:
  - Card and deck management
  - Hand distribution (human and machine players)
  - Game phases (pre-flop, flop, turn, river) with betting
  - Pot management with rake (fees)
  - Hand evaluation and showdown logic
  - Game history tracking in JSON
  - Player rankings system

- Machine Learning Implementation:
  - Q-learning based AI player
  - Dynamic strategy adaptation
  - Position-based decision making
  - Hand strength evaluation
  - Opponent modeling
  - Persistent Q-table storage

- Game Modes:
  - Player vs Machine: Test your skills against the AI
  - Machine vs Machine: Run simulations to test AI strategies

## Requirements

- Python 3.10 or higher

## Installation

1. Clone the repository:
```bash
git clone [your-repo-url]
cd poker-o3
```

2. Create and activate a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -e .
```

## Usage

Run the main game:
```bash
python poker_app.py
```

This will present you with two game modes:
1. Player vs Machine - Play against the AI
2. Machine vs Machine - Run AI strategy tests

### Player vs Machine Mode
- Start with 1000 chips each
- Play continues until one player loses all chips
- Make decisions to call, raise, or fold based on your hand
- Watch the AI adapt its strategy through Q-learning

### Machine vs Machine Mode
- Specify number of games to simulate
- Watch AI players compete and learn
- Analysis of win rates and chip statistics
- Useful for testing and improving AI strategies

## Project Structure

- `poker_app.py`: Main game engine and logic
- `poker_gui.py`: GUI implementation
- `card_graphics.py`: Card visualization
- `machine_vs_machine_test.py`: AI testing framework
- `q_table.json`: AI learning data storage
- `history.json`: Game history tracking
- `ranking.json`: Player rankings

## Game Mechanics

The game follows standard Texas Hold'em rules with some unique features:
- 10% rake on each pot
- Persistent player rankings
- Detailed hand history tracking
- Real-time hand strength evaluation
- Dynamic AI decision making

## AI Features

The machine learning implementation includes:
- Q-learning with eligibility traces
- Dynamic exploration/exploitation balance
- Position-based strategy adjustment
- Hand strength evaluation
- Opponent modeling and adaptation
- Persistent learning across sessions

## Contributing

Feel free to submit issues and enhancement requests!
