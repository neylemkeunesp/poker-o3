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

if __name__ == '__main__':
    unittest.main()
