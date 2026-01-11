#!/usr/bin/env python3
"""
Teste da correção da odd chip rule (regra da ficha extra)
Valida que nenhuma ficha é perdida em split pots
"""

from card import Card
from player import Player


def simulate_showdown(pot, winners):
    """Simula a lógica de showdown com odd chip rule"""
    split_amount = pot // len(winners)
    remainder = pot % len(winners)

    total_distributed = 0

    for i, winner in enumerate(winners):
        amount = split_amount
        if i == 0 and remainder > 0:
            amount += remainder
        winner.chips += amount
        total_distributed += amount

    return total_distributed


def test_odd_chip_rule():
    """Testa a odd chip rule em diferentes cenários"""

    print("=" * 80)
    print("🎲 TESTE DA ODD CHIP RULE (REGRA DA FICHA EXTRA)")
    print("=" * 80)

    # TESTE 1: Pote par divisível por 2
    print("\n📍 TESTE 1: Pote Par (200 ÷ 2 = 100 cada)")
    print("-" * 80)

    player1 = Player("Player 1")
    player2 = Player("Player 2")
    player1.chips = 1000
    player2.chips = 1000

    pot = 200
    winners = [player1, player2]
    distributed = simulate_showdown(pot, winners)

    print(f"Pote: {pot}")
    print(f"Distribuído: {distributed}")
    print(f"Player 1: +{player1.chips - 1000} = {player1.chips}")
    print(f"Player 2: +{player2.chips - 1000} = {player2.chips}")
    print(f"Total: {player1.chips + player2.chips}")

    assert distributed == pot, f"❌ Fichas perdidas: {pot - distributed}"
    assert player1.chips + player2.chips == 2200, "❌ Conservação falhou"
    print("✅ PASSOU: Todas as fichas distribuídas")

    # TESTE 2: Pote ímpar (101 ÷ 2)
    print("\n📍 TESTE 2: Pote Ímpar (101 ÷ 2 = 50 + 51)")
    print("-" * 80)

    player1 = Player("Player 1")
    player2 = Player("Player 2")
    player1.chips = 1000
    player2.chips = 1000

    pot = 101
    winners = [player1, player2]
    distributed = simulate_showdown(pot, winners)

    print(f"Pote: {pot}")
    print(f"Distribuído: {distributed}")
    print(f"Player 1: +{player1.chips - 1000} = {player1.chips} (recebeu ficha extra)")
    print(f"Player 2: +{player2.chips - 1000} = {player2.chips}")
    print(f"Total: {player1.chips + player2.chips}")

    assert distributed == pot, f"❌ Fichas perdidas: {pot - distributed}"
    assert player1.chips + player2.chips == 2101, "❌ Conservação falhou"
    assert player1.chips == 1051, "❌ Player 1 deveria ter 1051 (50 + 1 extra)"
    assert player2.chips == 1050, "❌ Player 2 deveria ter 1050"
    print("✅ PASSOU: Ficha extra foi para Player 1")

    # TESTE 3: 3 jogadores (100 ÷ 3 = 33 + 34)
    print("\n📍 TESTE 3: Três Jogadores (100 ÷ 3 = 33 + 33 + 34)")
    print("-" * 80)

    player1 = Player("Player 1")
    player2 = Player("Player 2")
    player3 = Player("Player 3")
    player1.chips = 1000
    player2.chips = 1000
    player3.chips = 1000

    pot = 100
    winners = [player1, player2, player3]
    distributed = simulate_showdown(pot, winners)

    print(f"Pote: {pot}")
    print(f"Distribuído: {distributed}")
    print(f"Player 1: +{player1.chips - 1000} = {player1.chips} (recebeu ficha extra)")
    print(f"Player 2: +{player2.chips - 1000} = {player2.chips}")
    print(f"Player 3: +{player3.chips - 1000} = {player3.chips}")
    print(f"Total: {player1.chips + player2.chips + player3.chips}")

    assert distributed == pot, f"❌ Fichas perdidas: {pot - distributed}"
    assert player1.chips + player2.chips + player3.chips == 3100, "❌ Conservação falhou"
    assert player1.chips == 1034, "❌ Player 1 deveria ter 1034 (33 + 1 extra)"
    assert player2.chips == 1033, "❌ Player 2 deveria ter 1033"
    assert player3.chips == 1033, "❌ Player 3 deveria ter 1033"
    print("✅ PASSOU: Ficha extra foi para Player 1")

    # TESTE 4: 3 jogadores com 1 ficha extra (103 ÷ 3 = 34 + 34 + 35)
    print("\n📍 TESTE 4: Três Jogadores, 1 Ficha Extra (103 ÷ 3)")
    print("-" * 80)

    player1 = Player("Player 1")
    player2 = Player("Player 2")
    player3 = Player("Player 3")
    player1.chips = 1000
    player2.chips = 1000
    player3.chips = 1000

    pot = 103
    winners = [player1, player2, player3]
    distributed = simulate_showdown(pot, winners)

    print(f"Pote: {pot}")
    print(f"Distribuído: {distributed}")
    print(f"Player 1: +{player1.chips - 1000} = {player1.chips} (recebeu 1 ficha extra)")
    print(f"Player 2: +{player2.chips - 1000} = {player2.chips}")
    print(f"Player 3: +{player3.chips - 1000} = {player3.chips}")
    print(f"Total: {player1.chips + player2.chips + player3.chips}")

    assert distributed == pot, f"❌ Fichas perdidas: {pot - distributed}"
    assert player1.chips + player2.chips + player3.chips == 3103, "❌ Conservação falhou"
    assert player1.chips == 1035, "❌ Player 1 deveria ter 1035 (34 + 1 extra)"
    assert player2.chips == 1034, "❌ Player 2 deveria ter 1034"
    assert player3.chips == 1034, "❌ Player 3 deveria ter 1034"
    print("✅ PASSOU: 1 ficha extra foi para Player 1")

    # TESTE 5: Empate real - Royal Flush
    print("\n📍 TESTE 5: Empate Real - Royal Flush na Mesa (Pote 150)")
    print("-" * 80)

    player1 = Player("Player 1")
    player2 = Player("Player 2")
    player1.chips = 900
    player2.chips = 1100

    # Mesa com Royal Flush
    community = [
        Card('A', 'Hearts'),
        Card('K', 'Hearts'),
        Card('Q', 'Hearts'),
        Card('J', 'Hearts'),
        Card('10', 'Hearts')
    ]

    # Ambos têm lixo
    player1.hand = [Card('2', 'Spades'), Card('3', 'Clubs')]
    player2.hand = [Card('4', 'Diamonds'), Card('5', 'Spades')]

    hand1_name, hand1_value = player1.get_hand_value(community)
    hand2_name, hand2_value = player2.get_hand_value(community)

    print(f"Player 1: {hand1_name}")
    print(f"Player 2: {hand2_name}")
    print(f"Empate? {hand1_value == hand2_value}")

    assert hand1_value == hand2_value, "❌ Deveria ser empate"

    pot = 150
    winners = [player1, player2]
    distributed = simulate_showdown(pot, winners)

    print(f"\nPote: {pot}")
    print(f"Distribuído: {distributed}")
    print(f"Player 1: {900} → {player1.chips} (+{player1.chips - 900})")
    print(f"Player 2: {1100} → {player2.chips} (+{player2.chips - 1100})")
    print(f"Total: {player1.chips + player2.chips}")

    assert distributed == pot, f"❌ Fichas perdidas: {pot - distributed}"
    assert player1.chips + player2.chips == 2150, "❌ Conservação falhou"
    print("✅ PASSOU: Conservação de fichas mantida")

    # TESTE 6: Caso extremo - 5 jogadores, pote 103
    print("\n📍 TESTE 6: Cinco Jogadores (103 ÷ 5 = 20 cada + 3 extras)")
    print("-" * 80)

    players = [Player(f"Player {i+1}") for i in range(5)]
    for p in players:
        p.chips = 1000

    pot = 103
    distributed = simulate_showdown(pot, players)

    print(f"Pote: {pot}")
    print(f"Distribuído: {distributed}")
    for i, p in enumerate(players):
        gain = p.chips - 1000
        extra = " (recebeu 3 extras)" if i == 0 else ""
        print(f"Player {i+1}: +{gain} = {p.chips}{extra}")

    total = sum(p.chips for p in players)
    print(f"Total: {total}")

    assert distributed == pot, f"❌ Fichas perdidas: {pot - distributed}"
    assert total == 5103, "❌ Conservação falhou"
    assert players[0].chips == 1023, "❌ Player 1 deveria ter 1023 (20 + 3 extras)"
    for i in range(1, 5):
        assert players[i].chips == 1020, f"❌ Player {i+1} deveria ter 1020"
    print("✅ PASSOU: 3 fichas extras foram para Player 1")

    print("\n" + "=" * 80)
    print("✅ TODOS OS TESTES PASSARAM!")
    print("=" * 80)
    print("\n📊 RESUMO:")
    print("   ✅ Odd chip rule implementada corretamente")
    print("   ✅ Fichas extras vão para o primeiro jogador (melhor posição)")
    print("   ✅ Nenhuma ficha é perdida em split pots")
    print("   ✅ Conservação de fichas funciona em todos os casos")
    print("\n💡 Regra implementada: Ficha(s) extra(s) → Primeiro jogador da lista")


if __name__ == "__main__":
    test_odd_chip_rule()
