#!/usr/bin/env python3
"""
Testes abrangentes para validar os critérios de desempate no poker.
Testa todos os cenários onde dois jogadores têm o mesmo tipo de mão.
"""

import pytest
from card import Card
from player import Player


def test_pair_with_different_kickers():
    """Par com kickers diferentes - deve considerar os 3 kickers"""
    player1 = Player("Player 1")
    player2 = Player("Player 2")

    # Mesa com par de Ases e kickers compartilhados
    community = [
        Card('A', 'Hearts'),
        Card('A', 'Spades'),
        Card('K', 'Diamonds'),
        Card('Q', 'Clubs'),
        Card('9', 'Hearts')
    ]

    # Player 1: J-8 como kickers (AA-K-Q-J)
    player1.hand = [Card('J', 'Diamonds'), Card('8', 'Spades')]
    # Player 2: 10-7 como kickers (AA-K-Q-10)
    player2.hand = [Card('10', 'Clubs'), Card('7', 'Hearts')]

    hand1_name, hand1_value = player1.get_hand_value(community)
    hand2_name, hand2_value = player2.get_hand_value(community)

    # Ambos devem ter "Par"
    assert hand1_name == "Par"
    assert hand2_name == "Par"

    # Player 1 deve vencer (tem J como terceiro kicker, player 2 tem 10)
    assert hand1_value > hand2_value, f"Player 1 ({hand1_value}) deveria vencer Player 2 ({hand2_value})"


def test_two_pair_with_different_kicker():
    """Dois pares com kicker diferente"""
    player1 = Player("Player 1")
    player2 = Player("Player 2")

    # Mesa: AA-KK-5-3-2
    community = [
        Card('A', 'Hearts'),
        Card('A', 'Spades'),
        Card('K', 'Diamonds'),
        Card('K', 'Clubs'),
        Card('3', 'Hearts')
    ]

    # Player 1: 5 como kicker
    player1.hand = [Card('5', 'Hearts'), Card('2', 'Spades')]
    # Player 2: 3 como kicker (pior)
    player2.hand = [Card('4', 'Diamonds'), Card('2', 'Clubs')]

    hand1_name, hand1_value = player1.get_hand_value(community)
    hand2_name, hand2_value = player2.get_hand_value(community)

    assert hand1_name == "Dois Pares"
    assert hand2_name == "Dois Pares"

    # Player 1 deve vencer (kicker 5 > 4)
    assert hand1_value > hand2_value


def test_three_of_kind_with_different_kickers():
    """Trinca com kickers diferentes"""
    player1 = Player("Player 1")
    player2 = Player("Player 2")

    # Mesa: KKK-A-2
    community = [
        Card('K', 'Hearts'),
        Card('K', 'Spades'),
        Card('K', 'Diamonds'),
        Card('A', 'Clubs'),
        Card('2', 'Hearts')
    ]

    # Player 1: Q-5 como kickers (KKK-A-Q)
    player1.hand = [Card('Q', 'Spades'), Card('5', 'Diamonds')]
    # Player 2: J-4 como kickers (KKK-A-J)
    player2.hand = [Card('J', 'Diamonds'), Card('4', 'Clubs')]

    hand1_name, hand1_value = player1.get_hand_value(community)
    hand2_name, hand2_value = player2.get_hand_value(community)

    assert hand1_name == "Trinca"
    assert hand2_name == "Trinca"

    # Player 1 deve vencer (segundo kicker Q > J)
    assert hand1_value > hand2_value


def test_flush_with_different_cards():
    """Flush com cartas diferentes - deve comparar todas as 5"""
    player1 = Player("Player 1")
    player2 = Player("Player 2")

    # Mesa tem 3 copas
    community = [
        Card('A', 'Hearts'),
        Card('K', 'Hearts'),
        Card('9', 'Hearts'),
        Card('2', 'Spades'),
        Card('3', 'Diamonds')
    ]

    # Player 1: completa flush com 8-5 (A-K-9-8-5)
    player1.hand = [Card('8', 'Hearts'), Card('5', 'Hearts')]
    # Player 2: completa flush com 7-6 (A-K-9-7-6)
    player2.hand = [Card('7', 'Hearts'), Card('6', 'Hearts')]

    hand1_name, hand1_value = player1.get_hand_value(community)
    hand2_name, hand2_value = player2.get_hand_value(community)

    assert hand1_name == "Flush"
    assert hand2_name == "Flush"

    # Player 1 deve vencer (4ª carta: 8 > 7)
    assert hand1_value > hand2_value


def test_full_house_with_different_pairs():
    """Full House com pares diferentes"""
    player1 = Player("Player 1")
    player2 = Player("Player 2")

    # Mesa: AAA-KK
    community = [
        Card('A', 'Hearts'),
        Card('A', 'Spades'),
        Card('A', 'Diamonds'),
        Card('K', 'Clubs'),
        Card('2', 'Hearts')
    ]

    # Player 1: tem par de K (AAA-KK)
    player1.hand = [Card('K', 'Hearts'), Card('3', 'Spades')]
    # Player 2: tem par de Q (AAA-QQ)
    player2.hand = [Card('Q', 'Diamonds'), Card('Q', 'Clubs')]

    hand1_name, hand1_value = player1.get_hand_value(community)
    hand2_name, hand2_value = player2.get_hand_value(community)

    assert hand1_name == "Full House"
    assert hand2_name == "Full House"

    # Player 1 deve vencer (par de K > par de Q)
    assert hand1_value > hand2_value


def test_four_of_kind_with_different_kickers():
    """Quadra com kickers diferentes"""
    player1 = Player("Player 1")
    player2 = Player("Player 2")

    # Mesa: AAAA
    community = [
        Card('A', 'Hearts'),
        Card('A', 'Spades'),
        Card('A', 'Diamonds'),
        Card('A', 'Clubs'),
        Card('2', 'Hearts')
    ]

    # Player 1: kicker K
    player1.hand = [Card('K', 'Hearts'), Card('3', 'Spades')]
    # Player 2: kicker Q
    player2.hand = [Card('Q', 'Diamonds'), Card('4', 'Clubs')]

    hand1_name, hand1_value = player1.get_hand_value(community)
    hand2_name, hand2_value = player2.get_hand_value(community)

    assert hand1_name == "Quadra"
    assert hand2_name == "Quadra"

    # Player 1 deve vencer (kicker K > Q)
    assert hand1_value > hand2_value


def test_high_card_all_five_matter():
    """Carta alta - todas as 5 cartas importam"""
    player1 = Player("Player 1")
    player2 = Player("Player 2")

    # Mesa: A-K-Q-9-2
    community = [
        Card('A', 'Hearts'),
        Card('K', 'Spades'),
        Card('Q', 'Diamonds'),
        Card('9', 'Clubs'),
        Card('2', 'Hearts')
    ]

    # Player 1: J-8 (A-K-Q-J-9)
    player1.hand = [Card('J', 'Hearts'), Card('8', 'Spades')]
    # Player 2: J-7 (A-K-Q-J-9)
    player2.hand = [Card('J', 'Diamonds'), Card('7', 'Clubs')]

    hand1_name, hand1_value = player1.get_hand_value(community)
    hand2_name, hand2_value = player2.get_hand_value(community)

    assert hand1_name == "Carta Alta"
    assert hand2_name == "Carta Alta"

    # Devem empatar - ambos usam A-K-Q-J-9 da mesa
    assert hand1_value == hand2_value


def test_straight_high_card_matters():
    """Sequência - carta mais alta importa"""
    player1 = Player("Player 1")
    player2 = Player("Player 2")

    # Mesa: 5-6-7-8
    community = [
        Card('5', 'Hearts'),
        Card('6', 'Spades'),
        Card('7', 'Diamonds'),
        Card('8', 'Clubs'),
        Card('K', 'Hearts')
    ]

    # Player 1: 9 (5-6-7-8-9)
    player1.hand = [Card('9', 'Hearts'), Card('2', 'Spades')]
    # Player 2: 4 (4-5-6-7-8)
    player2.hand = [Card('4', 'Diamonds'), Card('3', 'Clubs')]

    hand1_name, hand1_value = player1.get_hand_value(community)
    hand2_name, hand2_value = player2.get_hand_value(community)

    assert hand1_name == "Sequência"
    assert hand2_name == "Sequência"

    # Player 1 deve vencer (9-high straight > 8-high straight)
    assert hand1_value > hand2_value


def test_ace_low_straight():
    """Sequência A-2-3-4-5 (wheel) - A conta como 1"""
    player1 = Player("Player 1")

    player1.hand = [Card('A', 'Hearts'), Card('2', 'Spades')]
    community = [
        Card('3', 'Diamonds'),
        Card('4', 'Clubs'),
        Card('5', 'Hearts'),
        Card('K', 'Spades'),
        Card('Q', 'Diamonds')
    ]

    hand1_name, hand1_value = player1.get_hand_value(community)

    assert hand1_name == "Sequência"
    # Wheel é 5-high straight
    assert hand1_value[1] == 5, f"Expected 5-high straight, got {hand1_value}"


def test_true_tie_split_pot():
    """Empate verdadeiro - mãos exatamente iguais"""
    player1 = Player("Player 1")
    player2 = Player("Player 2")

    # Mesa tem o par e todos os kickers
    community = [
        Card('A', 'Hearts'),
        Card('A', 'Spades'),
        Card('K', 'Diamonds'),
        Card('Q', 'Clubs'),
        Card('J', 'Hearts')
    ]

    # Ambos jogadores têm cartas baixas que não contam
    player1.hand = [Card('2', 'Hearts'), Card('3', 'Spades')]
    player2.hand = [Card('4', 'Diamonds'), Card('5', 'Clubs')]

    hand1_name, hand1_value = player1.get_hand_value(community)
    hand2_name, hand2_value = player2.get_hand_value(community)

    assert hand1_name == "Par"
    assert hand2_name == "Par"

    # Devem empatar - ambos jogam A-A-K-Q-J da mesa
    assert hand1_value == hand2_value


def test_straight_flush_high_card():
    """Straight Flush - carta alta importa"""
    player1 = Player("Player 1")
    player2 = Player("Player 2")

    # Mesa: 6-7-8-9 de Hearts + carta de outro naipe
    community = [
        Card('6', 'Hearts'),
        Card('7', 'Hearts'),
        Card('8', 'Hearts'),
        Card('9', 'Hearts'),
        Card('K', 'Spades')
    ]

    # Player 1: 10 de Hearts (straight flush 6-10)
    player1.hand = [Card('10', 'Hearts'), Card('2', 'Spades')]
    # Player 2: 5 de Hearts (straight flush 5-9)
    player2.hand = [Card('5', 'Hearts'), Card('3', 'Diamonds')]

    hand1_name, hand1_value = player1.get_hand_value(community)
    hand2_name, hand2_value = player2.get_hand_value(community)

    assert hand1_name == "Straight Flush"
    assert hand2_name == "Straight Flush"

    # Player 1 deve vencer (10-high > 9-high)
    assert hand1_value > hand2_value


def test_royal_flush_always_ties():
    """Royal Flush sempre empata (só existe uma combinação)"""
    player1 = Player("Player 1")
    player2 = Player("Player 2")

    # Mesa: 10-J-Q-K-A de Hearts (Royal Flush completo na mesa)
    community = [
        Card('10', 'Hearts'),
        Card('J', 'Hearts'),
        Card('Q', 'Hearts'),
        Card('K', 'Hearts'),
        Card('A', 'Hearts')
    ]

    # Jogadores têm cartas irrelevantes
    player1.hand = [Card('2', 'Spades'), Card('3', 'Diamonds')]
    player2.hand = [Card('4', 'Clubs'), Card('5', 'Spades')]

    hand1_name, hand1_value = player1.get_hand_value(community)
    hand2_name, hand2_value = player2.get_hand_value(community)

    assert hand1_name == "Royal Flush"
    assert hand2_name == "Royal Flush"

    # Devem empatar - Royal Flush é sempre igual
    assert hand1_value == hand2_value


def test_two_pair_both_pairs_matter():
    """Dois pares - ambos os pares importam para desempate"""
    player1 = Player("Player 1")
    player2 = Player("Player 2")

    # Mesa: AA-KK-5
    community = [
        Card('A', 'Hearts'),
        Card('A', 'Spades'),
        Card('K', 'Diamonds'),
        Card('5', 'Clubs'),
        Card('2', 'Hearts')
    ]

    # Player 1: tem par de K (AA-KK)
    player1.hand = [Card('K', 'Hearts'), Card('3', 'Spades')]
    # Player 2: tem par de Q (AA-QQ)
    player2.hand = [Card('Q', 'Diamonds'), Card('Q', 'Clubs')]

    hand1_name, hand1_value = player1.get_hand_value(community)
    hand2_name, hand2_value = player2.get_hand_value(community)

    assert hand1_name == "Dois Pares"
    assert hand2_name == "Dois Pares"

    # Player 1 deve vencer (segundo par K > Q)
    assert hand1_value > hand2_value


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
