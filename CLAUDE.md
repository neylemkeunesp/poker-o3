# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Texas Hold'em poker game implementation in Python with a Q-learning AI player. The project includes both text-based and GUI versions, machine learning capabilities for AI opponents, and game history tracking. The codebase is primarily in Portuguese (Brazilian) for user-facing text, but code comments and structure follow standard Python conventions.

## Running the Application

### Main Game (GUI)
```bash
python poker_gui.py
```

Or use the provided shell scripts (configured for WSL/Linux with VcXsrv):
```bash
./run_poker.sh           # GUI with system Python
./run_simple_poker.sh    # Simplified GUI version
./run_fixed_poker.sh     # Fixed version with improved graphics
```

### Text-Based Game
```bash
python poker_text.py
```

### Machine vs Machine Testing
```bash
python machine_vs_machine_test.py
```

### Running Tests
```bash
pytest                           # Run all tests
pytest test_poker_app.py        # Run specific test file
pytest -v                        # Verbose output
pytest --cov                     # Run with coverage report
```

## Development Environment

The project uses a virtual environment located in `.venv/`:
```bash
# Activate virtual environment
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Or install in development mode
pip install -e .
```

**Key Dependencies:**
- Pillow (PIL) - Card graphics and image manipulation
- NumPy - Numerical computations for AI
- pytest - Testing framework
- tkinter - GUI framework (included with Python)

## Architecture Overview

### Core Game Components

The codebase is organized into modular components that handle different aspects of the poker game:

1. **Card/Deck System** (`card.py`, `deck.py`)
   - `Card` class: Represents individual playing cards with rank, suit, and value
   - Cards have Portuguese translations for display (suits_pt, ranks_pt)
   - `Deck` class: Manages 52-card deck with shuffle and draw operations

2. **Player System** (`player.py`)
   - Handles both human and AI players
   - AI players use Q-learning with:
     - Q-table persistence (saved to `q_table.json`)
     - State representation based on hand strength, position, and game phase
     - Epsilon-greedy exploration strategy
     - Learning rate: 0.1, Discount factor: 0.9
   - Game sequence tracking: hands played, chip differences, win streaks
   - Hand evaluation logic (Royal Flush to High Card)

3. **Game Engine** (`poker_game.py`, `poker_app.py`)
   - `PokerGame`: Core game mechanics (dealing, community cards, pot management)
   - `poker_app.py`: Complete poker implementation with betting rounds, showdown logic
   - Betting phases: Pre-flop, Flop (3 cards), Turn (1 card), River (1 card)
   - 10% rake system on pots
   - Chip conservation enforcement (total chips should remain constant)

4. **GUI System** (`poker_gui.py`, `card_graphics.py`)
   - `PokerGUI`: Tkinter-based graphical interface
   - `CardGraphics`: Generates card images using PIL with rounded corners
   - Real-time game state display with community cards, player hands, chips
   - Action buttons for Call, Raise, Fold decisions
   - Phase indicators and game messages

5. **Persistence Layer** (`history_manager.py`, `ranking_manager.py`)
   - `HistoryManager`: Records game history to `game_history.json`
   - `RankingManager`: Tracks player win counts in `ranking.json`
   - Q-learning tables stored per-player in `q_table.json`

### File Variants and Evolution

The codebase contains several file variants indicating development iterations:
- `poker_gui.py` / `poker_gui_backup.py` - Main GUI and backup
- `fixed_poker.py` / `simpler_poker.py` - Alternative implementations with different features
- `card_graphics.py` / `card_graphics_fixed.py` - Graphics rendering variants
- `test_*.py` files - Various test scenarios (display, chip conservation, winning hands)

When modifying the codebase, prefer editing the primary files (`poker_gui.py`, `poker_app.py`, etc.) unless specifically working on an alternative implementation.

## AI/Machine Learning System

The Q-learning implementation is distributed across the `Player` class:

**State Representation:**
- Hand strength category (weak/medium/strong)
- Position (early/late)
- Game phase (pre-flop/flop/turn/river)
- Current bet relative to pot size
- Chip stack size

**Actions:**
- Fold
- Call/Check
- Raise (with dynamic amount calculation)

**Learning Process:**
- Q-table is loaded from `q_table.json` on initialization
- Updated after each hand based on reward (chip difference)
- Saved back to JSON after each game
- Exploration rate decreases over time (epsilon decay)

**Key Methods:**
- `player.make_decision()` - AI decision-making logic
- `player.load_q_table()` / `player.save_q_table()` - Persistence
- `player.get_hand_value()` - Hand strength evaluation

## Hand Evaluation

The hand evaluation system (`player.get_hand_value()`) returns a tuple of (hand_name, numeric_value):

**Hand Rankings (highest to lowest):**
1. Royal Flush (900)
2. Straight Flush (800 + high_card)
3. Quadra / Four of a Kind (700 + quad_value)
4. Full House (600 + three_kind_value)
5. Flush (500 + high_card)
6. Sequência / Straight (400 + high_card)
7. Trinca / Three of a Kind (300 + triple_value)
8. Dois Pares / Two Pair (200 + higher_pair)
9. Um Par / One Pair (100 + pair_value)
10. Carta Alta / High Card (0 + highest_value)

The evaluation considers all 7 cards (2 hole cards + 5 community cards) and handles special cases like Ace-low straights.

## Important Development Notes

### Chip Conservation
The codebase enforces chip conservation - total chips across all players should remain constant (typically 2000 for 2 players starting with 1000 each). Test this with:
```bash
pytest test_chip_conservation.py
```

### Display/Graphics Issues
The project was developed for WSL with VcXsrv X server. If encountering display issues:
- Ensure `DISPLAY` environment variable is set correctly
- Check VcXsrv is running with "Disable access control"
- Use test files: `test_display.py`, `teste_pil_tkinter.py`, `teste_sistema.py`

### Portuguese Translations
User-facing strings are in Portuguese. When adding new messages:
- Game phases: "Pré-Flop", "Flop", "Turn", "River"
- Actions: "Pagar" (Call), "Aumentar" (Raise), "Desistir" (Fold)
- Suits: "Copas" (Hearts), "Ouros" (Diamonds), "Paus" (Clubs), "Espadas" (Spades)
- Ranks: "Ás" (Ace), "Rei" (King), "Dama" (Queen), "Valete" (Jack)

### Testing Strategy
When adding features:
1. Write unit tests for game logic (see `test_poker_app.py`)
2. Test hand evaluation edge cases (Ace-low straights, split pots)
3. Verify chip conservation across betting rounds
4. Test AI learning convergence with machine vs machine games
5. Test GUI display with different screen sizes/resolutions

## Modular Design Pattern

The codebase follows a separation of concerns:
- **Model** (game logic): `card.py`, `deck.py`, `player.py`, `poker_game.py`
- **View** (presentation): `poker_gui.py`, `card_graphics.py`
- **Controller** (orchestration): `poker_app.py`, `game.py`
- **Persistence**: `history_manager.py`, `ranking_manager.py`, JSON files

When adding new features, maintain this separation. For example, betting logic belongs in `poker_game.py` or `player.py`, not in the GUI layer.
