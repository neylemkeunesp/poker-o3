#!/usr/bin/env python3
"""
Teste CORRETO de critérios de desempate
"""

from card import Card
from player import Player


def test_desempate_real():
    """Testa casos reais de desempate"""

    print("=" * 80)
    print("🔍 TESTE CORRETO DE DESEMPATE")
    print("=" * 80)

    # TESTE 1: Trinca com kickers diferentes (correto)
    print("\n📍 TESTE 1: TRINCA de 7s - Kickers diferentes")
    print("-" * 80)

    player = Player("Jogador")
    machine = Player("Máquina")

    # Mesa: 7-7-7-K-5
    community = [
        Card('7', 'Clubs'),
        Card('7', 'Hearts'),
        Card('7', 'Diamonds'),
        Card('K', 'Spades'),
        Card('5', 'Hearts')
    ]

    # Jogador: 7-7-7-A-K (A na mão é maior que K da mesa)
    player.hand = [Card('A', 'Hearts'), Card('2', 'Clubs')]
    # Máquina: 7-7-7-Q-K (Q na mão é menor que K da mesa)
    machine.hand = [Card('Q', 'Diamonds'), Card('3', 'Spades')]

    player_type, player_value = player.get_hand_value(community)
    machine_type, machine_value = machine.get_hand_value(community)

    print(f"Mesa: 7♣ 7♥ 7♦ K♠ 5♥")
    print(f"\nJogador (A♥ 2♣): {player_type}")
    print(f"   Tuple: {player_value}")
    print(f"   Melhor mão: 7-7-7-A-K")

    print(f"\nMáquina (Q♦ 3♠): {machine_type}")
    print(f"   Tuple: {machine_value}")
    print(f"   Melhor mão: 7-7-7-K-Q")

    if player_value > machine_value:
        print(f"\n✅ CORRETO: Jogador vence (A > K no primeiro kicker)")
    else:
        print(f"\n❌ ERRO: Jogador deveria vencer!")

    # TESTE 2: Dois pares com segundo par diferente
    print("\n\n📍 TESTE 2: DOIS PARES - Segundo par diferente")
    print("-" * 80)

    player = Player("Jogador")
    machine = Player("Máquina")

    # Mesa: A-A-K-Q-7
    community = [
        Card('A', 'Clubs'),
        Card('A', 'Hearts'),
        Card('K', 'Diamonds'),
        Card('Q', 'Spades'),
        Card('7', 'Hearts')
    ]

    # Jogador: A-A-K-K (K na mão forma segundo par)
    player.hand = [Card('K', 'Hearts'), Card('2', 'Clubs')]
    # Máquina: A-A-Q-Q (Q na mão forma segundo par)
    machine.hand = [Card('Q', 'Diamonds'), Card('3', 'Spades')]

    player_type, player_value = player.get_hand_value(community)
    machine_type, machine_value = machine.get_hand_value(community)

    print(f"Mesa: A♣ A♥ K♦ Q♠ 7♥")
    print(f"\nJogador (K♥ 2♣): {player_type}")
    print(f"   Tuple: {player_value}")
    print(f"   Melhor mão: A-A-K-K-Q")

    print(f"\nMáquina (Q♦ 3♠): {machine_type}")
    print(f"   Tuple: {machine_value}")
    print(f"   Melhor mão: A-A-Q-Q-K")

    if player_value > machine_value:
        print(f"\n✅ CORRETO: Jogador vence (K-K > Q-Q no segundo par)")
    else:
        print(f"\n❌ ERRO: Jogador deveria vencer!")

    # TESTE 3: Par com todos os kickers diferentes
    print("\n\n📍 TESTE 3: PAR de 2s - Kickers muito diferentes")
    print("-" * 80)

    player = Player("Jogador")
    machine = Player("Máquina")

    # Mesa: 2-2-3-4-5
    community = [
        Card('2', 'Clubs'),
        Card('2', 'Hearts'),
        Card('3', 'Diamonds'),
        Card('4', 'Spades'),
        Card('5', 'Hearts')
    ]

    # Jogador: 2-2-A-K-5 (A e K na mão)
    player.hand = [Card('A', 'Hearts'), Card('K', 'Clubs')]
    # Máquina: 2-2-Q-J-5 (Q e J na mão)
    machine.hand = [Card('Q', 'Diamonds'), Card('J', 'Spades')]

    player_type, player_value = player.get_hand_value(community)
    machine_type, machine_value = machine.get_hand_value(community)

    print(f"Mesa: 2♣ 2♥ 3♦ 4♠ 5♥")
    print(f"\nJogador (A♥ K♣): {player_type}")
    print(f"   Tuple: {player_value}")
    print(f"   Melhor mão: 2-2-A-K-5")

    print(f"\nMáquina (Q♦ J♠): {machine_type}")
    print(f"   Tuple: {machine_value}")
    print(f"   Melhor mão: 2-2-Q-J-5")

    if player_value > machine_value:
        print(f"\n✅ CORRETO: Jogador vence (A-K-5 > Q-J-5 nos kickers)")
    else:
        print(f"\n❌ ERRO: Jogador deveria vencer!")

    # TESTE 4: Carta Alta - desempate profundo
    print("\n\n📍 TESTE 4: CARTA ALTA - Desempate na 5ª carta")
    print("-" * 80)

    player = Player("Jogador")
    machine = Player("Máquina")

    # Mesa: A-K-Q-J-3
    community = [
        Card('A', 'Clubs'),
        Card('K', 'Hearts'),
        Card('Q', 'Diamonds'),
        Card('J', 'Spades'),
        Card('3', 'Hearts')
    ]

    # Jogador: A-K-Q-J-9 (9 na mão)
    player.hand = [Card('9', 'Hearts'), Card('2', 'Clubs')]
    # Máquina: A-K-Q-J-8 (8 na mão)
    machine.hand = [Card('8', 'Diamonds'), Card('4', 'Spades')]

    player_type, player_value = player.get_hand_value(community)
    machine_type, machine_value = machine.get_hand_value(community)

    print(f"Mesa: A♣ K♥ Q♦ J♠ 3♥")
    print(f"\nJogador (9♥ 2♣): {player_type}")
    print(f"   Tuple: {player_value}")
    print(f"   Melhor mão: A-K-Q-J-9")

    print(f"\nMáquina (8♦ 4♠): {machine_type}")
    print(f"   Tuple: {machine_value}")
    print(f"   Melhor mão: A-K-Q-J-8")

    if player_value > machine_value:
        print(f"\n✅ CORRETO: Jogador vence (9 > 8 na 5ª carta)")
    else:
        print(f"\n❌ ERRO: Jogador deveria vencer!")

    # TESTE 5: Empate VERDADEIRO
    print("\n\n📍 TESTE 5: EMPATE VERDADEIRO")
    print("-" * 80)

    player = Player("Jogador")
    machine = Player("Máquina")

    # Mesa: A-K-Q-J-10 (Broadway straight)
    community = [
        Card('A', 'Clubs'),
        Card('K', 'Hearts'),
        Card('Q', 'Diamonds'),
        Card('J', 'Spades'),
        Card('10', 'Hearts')
    ]

    # Ambos têm lixo
    player.hand = [Card('2', 'Hearts'), Card('3', 'Clubs')]
    machine.hand = [Card('4', 'Diamonds'), Card('5', 'Spades')]

    player_type, player_value = player.get_hand_value(community)
    machine_type, machine_value = machine.get_hand_value(community)

    print(f"Mesa: A♣ K♥ Q♦ J♠ 10♥")
    print(f"\nJogador (2♥ 3♣): {player_type}")
    print(f"   Tuple: {player_value}")

    print(f"\nMáquina (4♦ 5♠): {machine_type}")
    print(f"   Tuple: {machine_value}")

    if player_value == machine_value:
        print(f"\n✅ CORRETO: Empate verdadeiro! Ambos jogam a sequência da mesa")
    else:
        print(f"\n❌ ERRO: Deveria ser empate!")

    print("\n" + "=" * 80)


if __name__ == "__main__":
    test_desempate_real()
