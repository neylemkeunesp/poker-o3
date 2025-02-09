import unittest
import random
from game import Game
from player import Player
from poker_game import PokerGame

class TestChipConservation(unittest.TestCase):
    def test_chip_conservation(self):
        # Initialize players
        player1 = Player("Player 1", is_machine=True)
        player2 = Player("Player 2", is_machine=True)

        # Initialize game
        poker_game = PokerGame([player1, player2])
        game = Game()
        game.player1 = player1
        game.player2 = player2
        game.pot = 0  # Initialize the pot

        # Simulate a few games
        num_games = 3
        initial_total_chips = player1.chips + player2.chips

        for _ in range(num_games):
            # Deal cards
            poker_game.deal_cards()
            game.community_cards = []  # Reset community cards

            # Betting round
            game.current_bet = 0
            players = [player1, player2]
            for player in players:
                if not player.folded:
                    # Simulate random actions (call or raise)
                    action = random.choice(["call", "raise"])
                    if action == "raise":
                        amount = random.randint(20, player.chips)  # Random raise amount
                        game.current_bet = amount
                    else:
                        amount = min(game.current_bet, player.chips)
                    game.pot += amount
                    player.chips -= amount

            game._showdown([player1, player2])  # Simulate showdown
            game.pot = 0  # Reset the pot

        # Check if total chips remain constant
        final_total_chips = player1.chips + player2.chips
        self.assertEqual(initial_total_chips, final_total_chips, "Total chip count should remain constant")

if __name__ == '__main__':
    unittest.main()
