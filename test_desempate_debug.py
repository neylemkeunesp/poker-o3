#!/usr/bin/env python3
"""
Teste de debug dos critérios de desempate
Quando ambos têm a mesma mão (ex: ambos têm um par)
"""

from card import Card
from player import Player


def test_same_hand_type():
    """Testa desempate quando ambos têm o mesmo tipo de mão"""

    print("=" * 80)
    print("🔍 TESTE DE CRITÉRIOS DE DESEMPATE")
    print("=" * 80)

    # TESTE 1: Ambos têm um PAR - diferentes pares
    print("\n📍 TESTE 1: Ambos têm PAR - Pares diferentes")
    print("-" * 80)

    player = Player("Jogador")
    machine = Player("Máquina")

    # Mesa: A-K-Q-7-2
    community = [
        Card('A', 'Clubs'),
        Card('K', 'Hearts'),
        Card('Q', 'Diamonds'),
        Card('7', 'Spades'),
        Card('2', 'Hearts')
    ]

    # Jogador: Par de Ases (A-A) com K-Q-7
    player.hand = [Card('A', 'Hearts'), Card('3', 'Clubs')]
    # Máquina: Par de Reis (K-K) com A-Q-7
    machine.hand = [Card('K', 'Clubs'), Card('4', 'Diamonds')]

    player_type, player_value = player.get_hand_value(community)
    machine_type, machine_value = machine.get_hand_value(community)

    print(f"Mesa: A♣ K♥ Q♦ 7♠ 2♥")
    print(f"\nJogador (A♥ 3♣): {player_type}")
    print(f"   Tuple: {player_value}")
    print(f"   Análise: Par de Ases, kickers K-Q-7")

    print(f"\nMáquina (K♣ 4♦): {machine_type}")
    print(f"   Tuple: {machine_value}")
    print(f"   Análise: Par de Reis, kickers A-Q-7")

    if player_value > machine_value:
        print(f"\n✅ CORRETO: Jogador vence (A > K no par)")
    elif machine_value > player_value:
        print(f"\n❌ ERRO: Máquina não deveria vencer (K < A)")
    else:
        print(f"\n❌ ERRO: Não deveria ser empate!")

    # TESTE 2: Ambos têm PAR IGUAL - diferentes kickers
    print("\n\n📍 TESTE 2: Ambos têm PAR DE ASES - Kickers diferentes")
    print("-" * 80)

    player = Player("Jogador")
    machine = Player("Máquina")

    # Mesa: A-K-Q-7-2
    community = [
        Card('A', 'Clubs'),
        Card('K', 'Hearts'),
        Card('Q', 'Diamonds'),
        Card('7', 'Spades'),
        Card('2', 'Hearts')
    ]

    # Jogador: A-A com kickers K-Q-J (J na mão)
    player.hand = [Card('A', 'Hearts'), Card('J', 'Clubs')]
    # Máquina: A-A com kickers K-Q-10 (10 na mão)
    machine.hand = [Card('A', 'Diamonds'), Card('10', 'Spades')]

    player_type, player_value = player.get_hand_value(community)
    machine_type, machine_value = machine.get_hand_value(community)

    print(f"Mesa: A♣ K♥ Q♦ 7♠ 2♥")
    print(f"\nJogador (A♥ J♣): {player_type}")
    print(f"   Tuple: {player_value}")
    print(f"   Melhor mão: A-A-K-Q-J")

    print(f"\nMáquina (A♦ 10♠): {machine_type}")
    print(f"   Tuple: {machine_value}")
    print(f"   Melhor mão: A-A-K-Q-10")

    if player_value > machine_value:
        print(f"\n✅ CORRETO: Jogador vence (J > 10 no kicker)")
    elif machine_value > player_value:
        print(f"\n❌ ERRO: Máquina não deveria vencer")
    else:
        print(f"\n❌ ERRO: Não deveria ser empate!")

    # TESTE 3: DOIS PARES iguais - diferentes kickers
    print("\n\n📍 TESTE 3: Ambos têm DOIS PARES A-A-K-K - Kickers diferentes")
    print("-" * 80)

    player = Player("Jogador")
    machine = Player("Máquina")

    # Mesa: A-A-K-K-7
    community = [
        Card('A', 'Clubs'),
        Card('A', 'Hearts'),
        Card('K', 'Diamonds'),
        Card('K', 'Spades'),
        Card('7', 'Hearts')
    ]

    # Jogador: Dois pares A-A-K-K com kicker Q
    player.hand = [Card('Q', 'Clubs'), Card('2', 'Diamonds')]
    # Máquina: Dois pares A-A-K-K com kicker J
    machine.hand = [Card('J', 'Hearts'), Card('3', 'Spades')]

    player_type, player_value = player.get_hand_value(community)
    machine_type, machine_value = machine.get_hand_value(community)

    print(f"Mesa: A♣ A♥ K♦ K♠ 7♥")
    print(f"\nJogador (Q♣ 2♦): {player_type}")
    print(f"   Tuple: {player_value}")
    print(f"   Melhor mão: A-A-K-K-Q")

    print(f"\nMáquina (J♥ 3♠): {machine_type}")
    print(f"   Tuple: {machine_value}")
    print(f"   Melhor mão: A-A-K-K-J")

    if player_value > machine_value:
        print(f"\n✅ CORRETO: Jogador vence (Q > J no kicker)")
    elif machine_value > player_value:
        print(f"\n❌ ERRO: Máquina não deveria vencer")
    else:
        print(f"\n❌ ERRO: Não deveria ser empate!")

    # TESTE 4: TRINCA igual - diferentes kickers
    print("\n\n📍 TESTE 4: Ambos têm TRINCA de ASES - Kickers diferentes")
    print("-" * 80)

    player = Player("Jogador")
    machine = Player("Máquina")

    # Mesa: A-A-A-K-Q
    community = [
        Card('A', 'Clubs'),
        Card('A', 'Hearts'),
        Card('A', 'Diamonds'),
        Card('K', 'Spades'),
        Card('Q', 'Hearts')
    ]

    # Jogador: Trinca de Ases com kickers K-J (J na mão)
    player.hand = [Card('J', 'Clubs'), Card('2', 'Diamonds')]
    # Máquina: Trinca de Ases com kickers K-10 (10 na mão)
    machine.hand = [Card('10', 'Hearts'), Card('3', 'Spades')]

    player_type, player_value = player.get_hand_value(community)
    machine_type, machine_value = machine.get_hand_value(community)

    print(f"Mesa: A♣ A♥ A♦ K♠ Q♥")
    print(f"\nJogador (J♣ 2♦): {player_type}")
    print(f"   Tuple: {player_value}")
    print(f"   Melhor mão: A-A-A-K-J")

    print(f"\nMáquina (10♥ 3♠): {machine_type}")
    print(f"   Tuple: {machine_value}")
    print(f"   Melhor mão: A-A-A-K-10")

    if player_value > machine_value:
        print(f"\n✅ CORRETO: Jogador vence (J > 10 no segundo kicker)")
    elif machine_value > player_value:
        print(f"\n❌ ERRO: Máquina não deveria vencer")
    else:
        print(f"\n❌ ERRO: Não deveria ser empate!")

    # TESTE 5: FLUSH - diferentes cartas altas
    print("\n\n📍 TESTE 5: Ambos têm FLUSH de copas - Cartas diferentes")
    print("-" * 80)

    player = Player("Jogador")
    machine = Player("Máquina")

    # Mesa: A♥-K♥-Q♥-7♥-2♣
    community = [
        Card('A', 'Hearts'),
        Card('K', 'Hearts'),
        Card('Q', 'Hearts'),
        Card('7', 'Hearts'),
        Card('2', 'Clubs')
    ]

    # Jogador: Flush A-K-Q-J-7 (J♥ na mão)
    player.hand = [Card('J', 'Hearts'), Card('3', 'Clubs')]
    # Máquina: Flush A-K-Q-10-7 (10♥ na mão)
    machine.hand = [Card('10', 'Hearts'), Card('4', 'Diamonds')]

    player_type, player_value = player.get_hand_value(community)
    machine_type, machine_value = machine.get_hand_value(community)

    print(f"Mesa: A♥ K♥ Q♥ 7♥ 2♣")
    print(f"\nJogador (J♥ 3♣): {player_type}")
    print(f"   Tuple: {player_value}")
    print(f"   Melhor mão: A♥-K♥-Q♥-J♥-7♥")

    print(f"\nMáquina (10♥ 4♦): {machine_type}")
    print(f"   Tuple: {machine_value}")
    print(f"   Melhor mão: A♥-K♥-Q♥-10♥-7♥")

    if player_value > machine_value:
        print(f"\n✅ CORRETO: Jogador vence (J > 10 na 4ª carta do flush)")
    elif machine_value > player_value:
        print(f"\n❌ ERRO: Máquina não deveria vencer")
    else:
        print(f"\n❌ ERRO: Não deveria ser empate!")

    print("\n" + "=" * 80)


if __name__ == "__main__":
    test_same_hand_type()
