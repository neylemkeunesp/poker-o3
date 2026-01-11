#!/usr/bin/env python3
"""
Teste específico para desempate com múltiplas cartas (kickers profundos)
Valida se a comparação funciona até a última carta
"""

import pytest
from card import Card
from player import Player


def test_pair_third_kicker_matters():
    """Par: Terceiro kicker deve decidir quando primeiros dois são iguais"""
    player1 = Player("Player 1")
    player2 = Player("Player 2")

    # Mesa: AA-K-Q-2
    community = [
        Card('A', 'Hearts'),
        Card('A', 'Spades'),
        Card('K', 'Diamonds'),
        Card('Q', 'Clubs'),
        Card('2', 'Hearts')
    ]

    # Player 1: J-5 → AA-K-Q-J (terceiro kicker = J)
    player1.hand = [Card('J', 'Hearts'), Card('5', 'Diamonds')]
    # Player 2: 10-4 → AA-K-Q-10 (terceiro kicker = 10)
    player2.hand = [Card('10', 'Spades'), Card('4', 'Clubs')]

    hand1_name, hand1_value = player1.get_hand_value(community)
    hand2_name, hand2_value = player2.get_hand_value(community)

    print(f"\n🎯 Teste: Par - Terceiro Kicker")
    print(f"Player 1: {hand1_name} - {hand1_value}")
    print(f"Player 2: {hand2_name} - {hand2_value}")

    assert hand1_name == "Par"
    assert hand2_name == "Par"
    assert hand1_value > hand2_value, f"Player 1 (J kicker) deveria vencer Player 2 (10 kicker)\nP1: {hand1_value}\nP2: {hand2_value}"
    print("✅ Terceiro kicker funcionando corretamente!")


def test_high_card_fifth_card_matters():
    """High Card: Quinta carta deve decidir quando primeiras quatro são iguais"""
    player1 = Player("Player 1")
    player2 = Player("Player 2")

    # Mesa: A-K-Q-J-2
    community = [
        Card('A', 'Hearts'),
        Card('K', 'Spades'),
        Card('Q', 'Diamonds'),
        Card('J', 'Clubs'),
        Card('2', 'Hearts')
    ]

    # Player 1: 9-3 → A-K-Q-J-9 (quinta carta = 9)
    player1.hand = [Card('9', 'Hearts'), Card('3', 'Diamonds')]
    # Player 2: 8-4 → A-K-Q-J-8 (quinta carta = 8)
    player2.hand = [Card('8', 'Spades'), Card('4', 'Clubs')]

    hand1_name, hand1_value = player1.get_hand_value(community)
    hand2_name, hand2_value = player2.get_hand_value(community)

    print(f"\n🎯 Teste: High Card - Quinta Carta")
    print(f"Player 1: {hand1_name} - {hand1_value}")
    print(f"Player 2: {hand2_name} - {hand2_value}")

    assert hand1_name == "Carta Alta"
    assert hand2_name == "Carta Alta"
    assert hand1_value > hand2_value, f"Player 1 (9 quinta) deveria vencer Player 2 (8 quinta)\nP1: {hand1_value}\nP2: {hand2_value}"
    print("✅ Quinta carta funcionando corretamente!")


def test_flush_fifth_card_matters():
    """Flush: Quinta carta deve decidir quando primeiras quatro são iguais"""
    player1 = Player("Player 1")
    player2 = Player("Player 2")

    # Mesa: A♥K♥Q♥J♥-2♠
    community = [
        Card('A', 'Hearts'),
        Card('K', 'Hearts'),
        Card('Q', 'Hearts'),
        Card('J', 'Hearts'),
        Card('2', 'Spades')
    ]

    # Player 1: 9♥-3♠ → Flush A♥K♥Q♥J♥9♥ (quinta = 9)
    player1.hand = [Card('9', 'Hearts'), Card('3', 'Spades')]
    # Player 2: 8♥-4♠ → Flush A♥K♥Q♥J♥8♥ (quinta = 8)
    player2.hand = [Card('8', 'Hearts'), Card('4', 'Spades')]

    hand1_name, hand1_value = player1.get_hand_value(community)
    hand2_name, hand2_value = player2.get_hand_value(community)

    print(f"\n🎯 Teste: Flush - Quinta Carta")
    print(f"Player 1: {hand1_name} - {hand1_value}")
    print(f"Player 2: {hand2_name} - {hand2_value}")

    assert hand1_name == "Flush"
    assert hand2_name == "Flush"
    assert hand1_value > hand2_value, f"Player 1 (9♥ quinta) deveria vencer Player 2 (8♥ quinta)\nP1: {hand1_value}\nP2: {hand2_value}"
    print("✅ Quinta carta do flush funcionando corretamente!")


def test_high_card_fourth_card_matters():
    """High Card: Quarta carta deve decidir quando primeiras três são iguais"""
    player1 = Player("Player 1")
    player2 = Player("Player 2")

    # Mesa: A-K-Q-3-2
    community = [
        Card('A', 'Hearts'),
        Card('K', 'Spades'),
        Card('Q', 'Diamonds'),
        Card('3', 'Clubs'),
        Card('2', 'Hearts')
    ]

    # Player 1: J-5 → A-K-Q-J-5 (quarta carta = J)
    player1.hand = [Card('J', 'Hearts'), Card('5', 'Diamonds')]
    # Player 2: 10-6 → A-K-Q-10-6 (quarta carta = 10)
    player2.hand = [Card('10', 'Spades'), Card('6', 'Clubs')]

    hand1_name, hand1_value = player1.get_hand_value(community)
    hand2_name, hand2_value = player2.get_hand_value(community)

    print(f"\n🎯 Teste: High Card - Quarta Carta")
    print(f"Player 1: {hand1_name} - {hand1_value}")
    print(f"Player 2: {hand2_name} - {hand2_value}")

    assert hand1_name == "Carta Alta"
    assert hand2_name == "Carta Alta"
    assert hand1_value > hand2_value, f"Player 1 (J quarta) deveria vencer Player 2 (10 quarta)\nP1: {hand1_value}\nP2: {hand2_value}"
    print("✅ Quarta carta funcionando corretamente!")


def test_trips_second_kicker_matters():
    """Trinca: Segundo kicker deve decidir quando primeiro é igual"""
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

    # Player 1: Q-5 → KKK-A-Q (segundo kicker = Q)
    player1.hand = [Card('Q', 'Hearts'), Card('5', 'Diamonds')]
    # Player 2: J-6 → KKK-A-J (segundo kicker = J)
    player2.hand = [Card('J', 'Spades'), Card('6', 'Clubs')]

    hand1_name, hand1_value = player1.get_hand_value(community)
    hand2_name, hand2_value = player2.get_hand_value(community)

    print(f"\n🎯 Teste: Trinca - Segundo Kicker")
    print(f"Player 1: {hand1_name} - {hand1_value}")
    print(f"Player 2: {hand2_name} - {hand2_value}")

    assert hand1_name == "Trinca"
    assert hand2_name == "Trinca"
    assert hand1_value > hand2_value, f"Player 1 (Q kicker) deveria vencer Player 2 (J kicker)\nP1: {hand1_value}\nP2: {hand2_value}"
    print("✅ Segundo kicker da trinca funcionando corretamente!")


def test_flush_fourth_card_matters():
    """Flush: Quarta carta deve decidir quando primeiras três são iguais"""
    player1 = Player("Player 1")
    player2 = Player("Player 2")

    # Mesa: A♥K♥Q♥-5♠-2♠
    community = [
        Card('A', 'Hearts'),
        Card('K', 'Hearts'),
        Card('Q', 'Hearts'),
        Card('5', 'Spades'),
        Card('2', 'Spades')
    ]

    # Player 1: J♥9♥ → Flush A♥K♥Q♥J♥9♥ (quarta = J)
    player1.hand = [Card('J', 'Hearts'), Card('9', 'Hearts')]
    # Player 2: 10♥8♥ → Flush A♥K♥Q♥10♥8♥ (quarta = 10)
    player2.hand = [Card('10', 'Hearts'), Card('8', 'Hearts')]

    hand1_name, hand1_value = player1.get_hand_value(community)
    hand2_name, hand2_value = player2.get_hand_value(community)

    print(f"\n🎯 Teste: Flush - Quarta Carta")
    print(f"Player 1: {hand1_name} - {hand1_value}")
    print(f"Player 2: {hand2_name} - {hand2_value}")

    assert hand1_name == "Flush"
    assert hand2_name == "Flush"
    assert hand1_value > hand2_value, f"Player 1 (J quarta) deveria vencer Player 2 (10 quarta)\nP1: {hand1_value}\nP2: {hand2_value}"
    print("✅ Quarta carta do flush funcionando corretamente!")


def test_flush_third_card_matters():
    """Flush: Terceira carta deve decidir quando primeiras duas são iguais"""
    player1 = Player("Player 1")
    player2 = Player("Player 2")

    # Mesa: A♥K♥-7♠-5♠-2♠
    community = [
        Card('A', 'Hearts'),
        Card('K', 'Hearts'),
        Card('7', 'Spades'),
        Card('5', 'Spades'),
        Card('2', 'Spades')
    ]

    # Player 1: Q♥J♥9♥ → Flush A♥K♥Q♥J♥9♥ (terceira = Q)
    player1.hand = [Card('Q', 'Hearts'), Card('J', 'Hearts')]
    # Preciso adicionar mais uma carta de copas na mesa
    community = [
        Card('A', 'Hearts'),
        Card('K', 'Hearts'),
        Card('7', 'Hearts'),
        Card('5', 'Spades'),
        Card('2', 'Spades')
    ]

    # Player 1: Q♥J♥ → Flush A♥K♥Q♥J♥7♥ (terceira = Q)
    player1.hand = [Card('Q', 'Hearts'), Card('J', 'Hearts')]
    # Player 2: 10♥9♥ → Flush A♥K♥10♥9♥7♥ (terceira = 10)
    player2.hand = [Card('10', 'Hearts'), Card('9', 'Hearts')]

    hand1_name, hand1_value = player1.get_hand_value(community)
    hand2_name, hand2_value = player2.get_hand_value(community)

    print(f"\n🎯 Teste: Flush - Terceira Carta")
    print(f"Player 1: {hand1_name} - {hand1_value}")
    print(f"Player 2: {hand2_name} - {hand2_value}")

    assert hand1_name == "Flush"
    assert hand2_name == "Flush"
    assert hand1_value > hand2_value, f"Player 1 (Q terceira) deveria vencer Player 2 (10 terceira)\nP1: {hand1_value}\nP2: {hand2_value}"
    print("✅ Terceira carta do flush funcionando corretamente!")


def test_detailed_tuple_comparison():
    """Teste detalhado mostrando como tuplas são comparadas"""
    player1 = Player("Player 1")
    player2 = Player("Player 2")

    # Cenário simples: Par de Ases com kickers diferentes
    community = [
        Card('A', 'Hearts'),
        Card('A', 'Spades'),
        Card('K', 'Diamonds'),
        Card('Q', 'Clubs'),
        Card('2', 'Hearts')
    ]

    # Player 1: J-5
    player1.hand = [Card('J', 'Hearts'), Card('5', 'Diamonds')]
    # Player 2: J-4
    player2.hand = [Card('J', 'Spades'), Card('4', 'Clubs')]

    hand1_name, hand1_value = player1.get_hand_value(community)
    hand2_name, hand2_value = player2.get_hand_value(community)

    print(f"\n🔍 ANÁLISE DETALHADA DE COMPARAÇÃO")
    print(f"=" * 60)
    print(f"Player 1 (J-5): {hand1_value}")
    print(f"Player 2 (J-4): {hand2_value}")
    print(f"\nComparando elemento por elemento:")
    for i, (v1, v2) in enumerate(zip(hand1_value, hand2_value)):
        status = "✅ IGUAL" if v1 == v2 else f"{'🏆 P1 VENCE' if v1 > v2 else '❌ P2 VENCE'}"
        print(f"  Posição {i}: {v1} vs {v2} → {status}")
        if v1 != v2:
            print(f"  ⚠️ DECISÃO NA POSIÇÃO {i}")
            break

    assert hand1_name == "Par"
    assert hand2_name == "Par"
    # O quarto elemento da tupla deve ser diferente (J vs J, mas próximo kicker é diferente)
    # Na verdade, ambos têm J, então deveria empatar... mas o último kicker (5 vs 4) decide
    print(f"\nResultado da comparação:")
    print(f"  Player 1 > Player 2: {hand1_value > hand2_value}")
    print(f"  Player 1 == Player 2: {hand1_value == hand2_value}")
    print(f"  Player 1 < Player 2: {hand1_value < hand2_value}")


if __name__ == "__main__":
    print("=" * 80)
    print("🧪 TESTE DE MÚLTIPLOS KICKERS (DESEMPATE PROFUNDO)")
    print("=" * 80)

    try:
        test_pair_third_kicker_matters()
        test_high_card_fifth_card_matters()
        test_flush_fifth_card_matters()
        test_high_card_fourth_card_matters()
        test_trips_second_kicker_matters()
        test_flush_fourth_card_matters()
        test_flush_third_card_matters()
        test_detailed_tuple_comparison()

        print("\n" + "=" * 80)
        print("✅ TODOS OS TESTES DE MÚLTIPLOS KICKERS PASSARAM!")
        print("=" * 80)
    except AssertionError as e:
        print("\n" + "=" * 80)
        print("❌ FALHA DETECTADA NO DESEMPATE!")
        print("=" * 80)
        print(f"\nErro: {e}")
        raise
