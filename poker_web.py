#!/usr/bin/env python3
"""
Flask Web Server for Texas Hold'em Poker
Provides REST API for game state and actions
"""

from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import os
import json
from poker_app import Card, Player, PokerGame

app = Flask(__name__, static_folder='static')
CORS(app)  # Enable CORS for API access

# Game state management
class GameState:
    def __init__(self):
        self.player = Player("Você")
        self.machine = Player("Máquina", is_machine=True)
        self.game = None
        self.current_phase = "waiting"
        self.winner = None
        self.game_over = False
        
    def new_hand(self):
        """Start a new hand"""
        self.player.hand = []
        self.player.folded = False
        self.player.current_bet = 0
        
        self.machine.hand = []
        self.machine.folded = False
        self.machine.current_bet = 0
        
        self.game = PokerGame([self.player, self.machine])
        self.game.deal_cards()
        self.current_phase = "preflop"
        self.winner = None
        self.game_over = False
        
    def get_state(self):
        """Get current game state as dictionary"""
        if not self.game:
            return {
                'initialized': False,
                'phase': 'waiting',
                'player': {'chips': self.player.chips, 'hand': []},
                'machine': {'chips': self.machine.chips, 'hand': []},
                'pot': 0,
                'current_bet': 0,
                'community_cards': []
            }
        
        return {
            'initialized': True,
            'phase': self.current_phase,
            'player': {
                'name': self.player.name,
                'chips': self.player.chips,
                'hand': [{'rank': c.rank, 'suit': c.suit} for c in self.player.hand],
                'folded': self.player.folded,
                'current_bet': self.player.current_bet
            },
            'machine': {
                'name': self.machine.name,
                'chips': self.machine.chips,
                'hand_count': len(self.machine.hand),  # Don't reveal machine cards
                'folded': self.machine.folded,
                'current_bet': self.machine.current_bet
            },
            'pot': self.game.pot,
            'current_bet': self.game.current_bet,
            'community_cards': [{'rank': c.rank, 'suit': c.suit} for c in self.game.community_cards],
            'winner': self.winner,
            'game_over': self.game_over
        }
    
    def process_action(self, action, amount=0):
        """Process player action and get machine response"""
        if self.game_over or self.player.folded:
            return {'error': 'Game is over or player has folded'}
        
        # Process player action
        if action == 'fold':
            self.player.folded = True
            self.winner = self.machine.name
            self.game_over = True
            self.machine.chips += self.game.pot
            self.game.pot = 0
            return {'status': 'success', 'message': 'Player folded'}
        
        elif action == 'call':
            call_amount = min(self.game.current_bet - self.player.current_bet, self.player.chips)
            self.player.chips -= call_amount
            self.player.current_bet += call_amount
            self.game.pot += call_amount
            
        elif action == 'raise':
            raise_amount = min(amount, self.player.chips)
            self.player.chips -= raise_amount
            self.player.current_bet += raise_amount
            self.game.pot += raise_amount
            self.game.current_bet = self.player.current_bet
        
        # Machine's turn
        if not self.machine.folded:
            machine_action, machine_amount = self.machine.make_decision(
                self.game.community_cards,
                self.game.current_bet - self.machine.current_bet,
                20
            )
            
            if machine_action == 'fold':
                self.machine.folded = True
                self.winner = self.player.name
                self.game_over = True
                self.player.chips += self.game.pot
                self.game.pot = 0
                return {'status': 'success', 'message': 'Machine folded', 'machine_action': 'fold'}
            
            elif machine_action == 'call':
                call_amount = min(self.game.current_bet - self.machine.current_bet, self.machine.chips)
                self.machine.chips -= call_amount
                self.machine.current_bet += call_amount
                self.game.pot += call_amount
                
            elif machine_action == 'raise':
                self.machine.chips -= machine_amount
                self.machine.current_bet += machine_amount
                self.game.pot += machine_amount
                self.game.current_bet = self.machine.current_bet
        
        # Check if betting round is complete
        if self.player.current_bet == self.machine.current_bet:
            self.advance_phase()
        
        return {'status': 'success', 'machine_action': machine_action, 'machine_amount': machine_amount}
    
    def advance_phase(self):
        """Advance to next game phase"""
        if self.current_phase == "preflop":
            self.game.deal_community_cards(3)  # Flop
            self.current_phase = "flop"
            self.reset_bets()
        elif self.current_phase == "flop":
            self.game.deal_community_cards(1)  # Turn
            self.current_phase = "turn"
            self.reset_bets()
        elif self.current_phase == "turn":
            self.game.deal_community_cards(1)  # River
            self.current_phase = "river"
            self.reset_bets()
        elif self.current_phase == "river":
            self.showdown()
    
    def reset_bets(self):
        """Reset current bets for new betting round"""
        self.player.current_bet = 0
        self.machine.current_bet = 0
        self.game.current_bet = 0
    
    def showdown(self):
        """Determine winner at showdown"""
        player_hand = self.player.get_hand_value(self.game.community_cards)
        machine_hand = self.machine.get_hand_value(self.game.community_cards)
        
        if player_hand[1] > machine_hand[1]:
            self.winner = self.player.name
            self.player.chips += self.game.pot
        elif machine_hand[1] > player_hand[1]:
            self.winner = self.machine.name
            self.machine.chips += self.game.pot
        else:
            # Split pot
            split = self.game.pot // 2
            self.player.chips += split
            self.machine.chips += split + (self.game.pot % 2)
            self.winner = "Empate"
        
        self.game.pot = 0
        self.game_over = True
        self.current_phase = "showdown"

# Global game state
game_state = GameState()

@app.route('/')
def index():
    """Serve the main HTML page"""
    return send_from_directory('static', 'index.html')

@app.route('/api/game/state', methods=['GET'])
def get_game_state():
    """Get current game state"""
    return jsonify(game_state.get_state())

@app.route('/api/game/new', methods=['POST'])
def new_game():
    """Start a new game"""
    try:
        game_state.new_hand()
        return jsonify({'status': 'success', 'message': 'New hand started', 'state': game_state.get_state()})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/game/action', methods=['POST'])
def game_action():
    """Handle player action"""
    try:
        data = request.json
        if not data or 'action' not in data:
            return jsonify({'error': 'Invalid request - action required'}), 400
        
        action = data.get('action')
        amount = data.get('amount', 0)
        
        if action not in ['call', 'raise', 'fold']:
            return jsonify({'error': 'Invalid action'}), 400
        
        result = game_state.process_action(action, amount)
        result['state'] = game_state.get_state()
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/game/stats', methods=['GET'])
def get_stats():
    """Get game statistics"""
    return jsonify({
        'player_chips': game_state.player.chips,
        'machine_chips': game_state.machine.chips,
        'total_chips': game_state.player.chips + game_state.machine.chips
    })

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    print("=" * 60)
    print("🃏 TEXAS HOLD'EM POKER - WEB SERVER 🃏")
    print("=" * 60)
    print("\n🌐 Server starting on http://localhost:5001")
    print("📱 Open your browser and navigate to http://localhost:5001")
    print("\n✨ Features:")
    print("   - Modern web interface")
    print("   - Real-time game updates")
    print("   - Play against AI")
    print("\n⌨️  Press Ctrl+C to stop the server\n")
    print("=" * 60)
    
    app.run(debug=False, host='0.0.0.0', port=5001)
