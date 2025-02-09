import unittest
from poker_app import Card, Player

class TestWinningHand(unittest.TestCase):
    def setUp(self):
        self.player1 = Player("Player 1")
        self.player2 = Player("Player 2")
        
    def test_compare_hands(self):
        # Teste 1: Royal Flush vs. Straight Flush
        print("\nTeste 1: Royal Flush vs. Straight Flush")
        # Royal Flush em Copas
        self.player1.hand = [
            Card('A', 'Hearts'),
            Card('K', 'Hearts')
        ]
        community_cards1 = [
            Card('Q', 'Hearts'),
            Card('J', 'Hearts'),
            Card('10', 'Hearts'),
            Card('2', 'Clubs'),
            Card('3', 'Diamonds')
        ]
        
        # Straight Flush 9-5 em Paus
        self.player2.hand = [
            Card('9', 'Clubs'),
            Card('8', 'Clubs')
        ]
        community_cards2 = [
            Card('7', 'Clubs'),
            Card('6', 'Clubs'),
            Card('5', 'Clubs'),
            Card('2', 'Hearts'),
            Card('3', 'Diamonds')
        ]
        
        hand1_type, value1 = self.player1.get_hand_value(community_cards1)
        hand2_type, value2 = self.player2.get_hand_value(community_cards2)
        
        print(f"Jogador 1: {hand1_type} (valor: {value1})")
        print(f"Cartas: {self.player1.show_hand()} + {', '.join(str(c) for c in community_cards1)}")
        print(f"\nJogador 2: {hand2_type} (valor: {value2})")
        print(f"Cartas: {self.player2.show_hand()} + {', '.join(str(c) for c in community_cards2)}")
        print(f"\nVencedor: {'Jogador 1' if value1 > value2 else 'Jogador 2'}")
        
        self.assertTrue(value1 > value2, "Royal Flush deve vencer Straight Flush")
        
        # Teste 2: Full House vs. Flush
        print("\nTeste 2: Full House vs. Flush")
        # Full House: Ases full of Kings
        self.player1.hand = [
            Card('A', 'Hearts'),
            Card('A', 'Diamonds')
        ]
        community_cards1 = [
            Card('A', 'Clubs'),
            Card('K', 'Spades'),
            Card('K', 'Hearts'),
            Card('2', 'Diamonds'),
            Card('3', 'Clubs')
        ]
        
        # Flush em Ouros
        self.player2.hand = [
            Card('A', 'Diamonds'),
            Card('10', 'Diamonds')
        ]
        community_cards2 = [
            Card('7', 'Diamonds'),
            Card('4', 'Diamonds'),
            Card('2', 'Diamonds'),
            Card('K', 'Hearts'),
            Card('Q', 'Clubs')
        ]
        
        hand1_type, value1 = self.player1.get_hand_value(community_cards1)
        hand2_type, value2 = self.player2.get_hand_value(community_cards2)
        
        print(f"Jogador 1: {hand1_type} (valor: {value1})")
        print(f"Cartas: {self.player1.show_hand()} + {', '.join(str(c) for c in community_cards1)}")
        print(f"\nJogador 2: {hand2_type} (valor: {value2})")
        print(f"Cartas: {self.player2.show_hand()} + {', '.join(str(c) for c in community_cards2)}")
        print(f"\nVencedor: {'Jogador 1' if value1 > value2 else 'Jogador 2'}")
        
        self.assertTrue(value1 > value2, "Full House deve vencer Flush")
        
        # Teste 3: Straight vs. Three of a Kind
        print("\nTeste 3: Straight vs. Three of a Kind")
        # Sequência 10-6
        self.player1.hand = [
            Card('10', 'Hearts'),
            Card('9', 'Diamonds')
        ]
        community_cards1 = [
            Card('8', 'Clubs'),
            Card('7', 'Spades'),
            Card('6', 'Hearts'),
            Card('2', 'Diamonds'),
            Card('3', 'Clubs')
        ]
        
        # Trinca de Damas
        self.player2.hand = [
            Card('Q', 'Hearts'),
            Card('Q', 'Diamonds')
        ]
        community_cards2 = [
            Card('Q', 'Clubs'),
            Card('7', 'Spades'),
            Card('2', 'Hearts'),
            Card('3', 'Diamonds'),
            Card('4', 'Clubs')
        ]
        
        hand1_type, value1 = self.player1.get_hand_value(community_cards1)
        hand2_type, value2 = self.player2.get_hand_value(community_cards2)
        
        print(f"Jogador 1: {hand1_type} (valor: {value1})")
        print(f"Cartas: {self.player1.show_hand()} + {', '.join(str(c) for c in community_cards1)}")
        print(f"\nJogador 2: {hand2_type} (valor: {value2})")
        print(f"Cartas: {self.player2.show_hand()} + {', '.join(str(c) for c in community_cards2)}")
        print(f"\nVencedor: {'Jogador 1' if value1 > value2 else 'Jogador 2'}")
        
        self.assertTrue(value1 > value2, "Straight deve vencer Three of a Kind")

if __name__ == '__main__':
    unittest.main(verbosity=2)
