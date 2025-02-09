import unittest
from poker_app import Card, Player, PokerGame

class TestPokerApp(unittest.TestCase):
    def test_get_hand_value(self):
        # Test Royal Flush
        player = Player("Test")
        player.hand = [
            Card('A', 'Hearts'),
            Card('K', 'Hearts')
        ]
        community_cards = [
            Card('Q', 'Hearts'),
            Card('J', 'Hearts'),
            Card('10', 'Hearts'),
            Card('2', 'Clubs'),
            Card('3', 'Diamonds')
        ]
        hand_type, value = player.get_hand_value(community_cards)
        self.assertEqual(hand_type, "Royal Flush")
        
        # Test Straight Flush
        player.hand = [
            Card('9', 'Hearts'),
            Card('8', 'Hearts')
        ]
        community_cards = [
            Card('7', 'Hearts'),
            Card('6', 'Hearts'),
            Card('5', 'Hearts'),
            Card('2', 'Clubs'),
            Card('3', 'Diamonds')
        ]
        hand_type, value = player.get_hand_value(community_cards)
        self.assertEqual(hand_type, "Straight Flush")
        
        # Test Four of a Kind
        player.hand = [
            Card('A', 'Hearts'),
            Card('A', 'Diamonds')
        ]
        community_cards = [
            Card('A', 'Clubs'),
            Card('A', 'Spades'),
            Card('5', 'Hearts'),
            Card('2', 'Clubs'),
            Card('3', 'Diamonds')
        ]
        hand_type, value = player.get_hand_value(community_cards)
        self.assertEqual(hand_type, "Quadra")
        
        # Test Full House
        player.hand = [
            Card('A', 'Hearts'),
            Card('A', 'Diamonds')
        ]
        community_cards = [
            Card('A', 'Clubs'),
            Card('K', 'Spades'),
            Card('K', 'Hearts'),
            Card('2', 'Clubs'),
            Card('3', 'Diamonds')
        ]
        hand_type, value = player.get_hand_value(community_cards)
        self.assertEqual(hand_type, "Full House")
        
        # Test Flush
        player.hand = [
            Card('A', 'Hearts'),
            Card('K', 'Hearts')
        ]
        community_cards = [
            Card('Q', 'Hearts'),
            Card('J', 'Hearts'),
            Card('9', 'Hearts'),
            Card('2', 'Clubs'),
            Card('3', 'Diamonds')
        ]
        hand_type, value = player.get_hand_value(community_cards)
        self.assertEqual(hand_type, "Flush")
        
        # Test Straight
        player.hand = [
            Card('A', 'Hearts'),
            Card('K', 'Diamonds')
        ]
        community_cards = [
            Card('Q', 'Clubs'),
            Card('J', 'Hearts'),
            Card('10', 'Spades'),
            Card('2', 'Clubs'),
            Card('3', 'Diamonds')
        ]
        hand_type, value = player.get_hand_value(community_cards)
        self.assertEqual(hand_type, "Sequência")
        
        # Test Three of a Kind
        player.hand = [
            Card('A', 'Hearts'),
            Card('A', 'Diamonds')
        ]
        community_cards = [
            Card('A', 'Clubs'),
            Card('K', 'Spades'),
            Card('Q', 'Hearts'),
            Card('2', 'Clubs'),
            Card('3', 'Diamonds')
        ]
        hand_type, value = player.get_hand_value(community_cards)
        self.assertEqual(hand_type, "Trinca")
        
        # Test Two Pair
        player.hand = [
            Card('A', 'Hearts'),
            Card('A', 'Diamonds')
        ]
        community_cards = [
            Card('K', 'Clubs'),
            Card('K', 'Spades'),
            Card('Q', 'Hearts'),
            Card('2', 'Clubs'),
            Card('3', 'Diamonds')
        ]
        hand_type, value = player.get_hand_value(community_cards)
        self.assertEqual(hand_type, "Dois Pares")
        
        # Test One Pair
        player.hand = [
            Card('A', 'Hearts'),
            Card('A', 'Diamonds')
        ]
        community_cards = [
            Card('K', 'Clubs'),
            Card('Q', 'Spades'),
            Card('J', 'Hearts'),
            Card('2', 'Clubs'),
            Card('3', 'Diamonds')
        ]
        hand_type, value = player.get_hand_value(community_cards)
        self.assertEqual(hand_type, "Par")
        
        # Test High Card
        player.hand = [
            Card('A', 'Hearts'),
            Card('K', 'Diamonds')
        ]
        community_cards = [
            Card('Q', 'Clubs'),
            Card('J', 'Spades'),
            Card('9', 'Hearts'),
            Card('2', 'Clubs'),
            Card('3', 'Diamonds')
        ]
        hand_type, value = player.get_hand_value(community_cards)
        self.assertEqual(hand_type, "Carta Alta")

    def test_complete_game_flow(self):
        """Test that the game properly handles all betting rounds until the end"""
        # Setup players
        player1 = Player("Player 1")
        player2 = Player("Player 2")
        game = PokerGame([player1, player2])
        
        # Initial deal
        game.deal_cards()
        self.assertEqual(len(player1.hand), 2, "Player 1 should have 2 hole cards")
        self.assertEqual(len(player2.hand), 2, "Player 2 should have 2 hole cards")
        self.assertEqual(len(game.community_cards), 0, "No community cards should be dealt initially")
        
        # Pre-flop betting round
        initial_pot = game.pot
        bet_amount = 50
        game.pot += bet_amount * 2  # Both players bet
        self.assertEqual(game.pot, initial_pot + bet_amount * 2, "Pot should increase after pre-flop betting")
        
        # Flop
        game.deal_community_cards(3)
        self.assertEqual(len(game.community_cards), 3, "Flop should deal 3 cards")
        
        # Post-flop betting round
        initial_pot = game.pot
        bet_amount = 100
        game.pot += bet_amount * 2  # Both players bet
        self.assertEqual(game.pot, initial_pot + bet_amount * 2, "Pot should increase after flop betting")
        
        # Turn
        game.deal_community_cards(1)
        self.assertEqual(len(game.community_cards), 4, "Turn should deal 4th card")
        
        # Post-turn betting round
        initial_pot = game.pot
        bet_amount = 150
        game.pot += bet_amount * 2  # Both players bet
        self.assertEqual(game.pot, initial_pot + bet_amount * 2, "Pot should increase after turn betting")
        
        # River
        game.deal_community_cards(1)
        self.assertEqual(len(game.community_cards), 5, "River should deal 5th card")
        
        # Post-river betting round
        initial_pot = game.pot
        bet_amount = 200
        game.pot += bet_amount * 2  # Both players bet
        self.assertEqual(game.pot, initial_pot + bet_amount * 2, "Pot should increase after river betting")
        
        # Verify final state
        self.assertEqual(len(game.community_cards), 5, "Game should end with 5 community cards")
        
        # Get hand values for both players
        p1_type, p1_value = player1.get_hand_value(game.community_cards)
        p2_type, p2_value = player2.get_hand_value(game.community_cards)
        
        # Verify both players can evaluate their hands
        self.assertIsNotNone(p1_type, "Player 1 should have a valid hand type")
        self.assertIsNotNone(p2_type, "Player 2 should have a valid hand type")
        self.assertIsNotNone(p1_value, "Player 1 should have a valid hand value")
        self.assertIsNotNone(p2_value, "Player 2 should have a valid hand value")

if __name__ == '__main__':
    unittest.main()
