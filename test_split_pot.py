#!/usr/bin/env python3
"""
Teste do sistema de split pot (divisão de pote em empates)
"""

from card import Card
from player import Player


def test_split_pot_logic():
    """Testa a lógica de divisão de pote em empates"""

    print("=" * 80)
    print("🎲 TESTE DE SPLIT POT (EMPATE VERDADEIRO)")
    print("=" * 80)

    # Simula o que o código de showdown faz

    # CENÁRIO 1: Empate perfeito - mesma mão da mesa
    print("\n📍 CENÁRIO 1: Empate Perfeito (Ambos jogam a mesa)")
    print("-" * 80)

    player1 = Player("Player 1")
    player2 = Player("Player 2")

    # Ambos com 1000 fichas
    player1.chips = 1000
    player2.chips = 1000

    # Mesa tem Royal Flush completo
    community = [
        Card('A', 'Hearts'),
        Card('K', 'Hearts'),
        Card('Q', 'Hearts'),
        Card('J', 'Hearts'),
        Card('10', 'Hearts')
    ]

    # Jogadores têm lixo
    player1.hand = [Card('2', 'Spades'), Card('3', 'Clubs')]
    player2.hand = [Card('4', 'Diamonds'), Card('5', 'Spades')]

    hand1_name, hand1_value = player1.get_hand_value(community)
    hand2_name, hand2_value = player2.get_hand_value(community)

    print(f"Player 1: {hand1_name} - {hand1_value}")
    print(f"Player 2: {hand2_name} - {hand2_value}")
    print(f"Empate? {hand1_value == hand2_value}")

    # Simula o código de showdown
    pot = 200
    active_players = [player1, player2]
    hand_values = [(p, p.get_hand_value(community)) for p in active_players]
    best_value = max(hand_values, key=lambda x: x[1][1])
    winners = [p for p, v in hand_values if v[1] == best_value[1][1]]

    print(f"\nPote antes: {pot}")
    print(f"Vencedores: {len(winners)}")

    if len(winners) == 1:
        winner = winners[0]
        winner.chips += pot
        print(f"🏆 {winner.name} vence {pot} chips")
    else:
        # Split pot
        split_amount = pot // len(winners)
        remainder = pot % len(winners)
        print(f"💰 Split pot: {pot} / {len(winners)} = {split_amount} cada")
        if remainder > 0:
            print(f"⚠️  PROBLEMA: {remainder} fichas órfãs (não divisível igualmente)!")

        for winner in winners:
            winner.chips += split_amount
            print(f"   🏆 {winner.name} recebe {split_amount} chips")

    print(f"\nFichas após:")
    print(f"   Player 1: {player1.chips}")
    print(f"   Player 2: {player2.chips}")
    print(f"   Total: {player1.chips + player2.chips}")

    if player1.chips + player2.chips == 2000:
        print("✅ Conservação de fichas: OK")
    else:
        print(f"❌ Conservação de fichas: FALHOU! Deveria ser 2000, é {player1.chips + player2.chips}")

    # CENÁRIO 2: Pote ímpar (não divisível)
    print("\n📍 CENÁRIO 2: Pote Ímpar (101 fichas, 2 jogadores)")
    print("-" * 80)

    player1 = Player("Player 1")
    player2 = Player("Player 2")
    player1.chips = 1000
    player2.chips = 1000

    # Mesmo cenário de empate
    player1.hand = [Card('2', 'Spades'), Card('3', 'Clubs')]
    player2.hand = [Card('4', 'Diamonds'), Card('5', 'Spades')]

    pot = 101  # Pote ímpar
    active_players = [player1, player2]
    hand_values = [(p, p.get_hand_value(community)) for p in active_players]
    best_value = max(hand_values, key=lambda x: x[1][1])
    winners = [p for p, v in hand_values if v[1] == best_value[1][1]]

    print(f"Pote: {pot}")
    print(f"Vencedores: {len(winners)}")

    split_amount = pot // len(winners)
    remainder = pot % len(winners)

    print(f"💰 Split: {pot} / {len(winners)} = {split_amount} cada")
    print(f"⚠️  Resto: {remainder} ficha(s)")

    for winner in winners:
        winner.chips += split_amount

    print(f"\nFichas após split:")
    print(f"   Player 1: {player1.chips} (ganhou {split_amount})")
    print(f"   Player 2: {player2.chips} (ganhou {split_amount})")
    print(f"   Total: {player1.chips + player2.chips}")
    print(f"   Fichas perdidas: {remainder}")

    if remainder > 0:
        print(f"\n❌ PROBLEMA DETECTADO:")
        print(f"   • {remainder} ficha(s) desapareceram!")
        print(f"   • Total deveria ser 2000 + {pot} = {2000 + pot}")
        print(f"   • Total real: {player1.chips + player2.chips}")
        print(f"   • Diferença: {2000 + pot - (player1.chips + player2.chips)}")

    # CENÁRIO 3: Empate triplo (3 jogadores)
    print("\n📍 CENÁRIO 3: Empate Triplo (3 jogadores, pote 100)")
    print("-" * 80)

    player1 = Player("Player 1")
    player2 = Player("Player 2")
    player3 = Player("Player 3")

    player1.chips = 1000
    player2.chips = 1000
    player3.chips = 1000

    player1.hand = [Card('2', 'Spades'), Card('3', 'Clubs')]
    player2.hand = [Card('4', 'Diamonds'), Card('5', 'Spades')]
    player3.hand = [Card('6', 'Hearts'), Card('7', 'Clubs')]

    pot = 100
    active_players = [player1, player2, player3]
    hand_values = [(p, p.get_hand_value(community)) for p in active_players]
    best_value = max(hand_values, key=lambda x: x[1][1])
    winners = [p for p, v in hand_values if v[1] == best_value[1][1]]

    print(f"Pote: {pot}")
    print(f"Vencedores: {len(winners)}")

    split_amount = pot // len(winners)
    remainder = pot % len(winners)

    print(f"💰 Split: {pot} / {len(winners)} = {split_amount} cada")
    print(f"⚠️  Resto: {remainder} ficha(s)")

    for winner in winners:
        winner.chips += split_amount

    print(f"\nFichas após split:")
    print(f"   Player 1: {player1.chips} (ganhou {split_amount})")
    print(f"   Player 2: {player2.chips} (ganhou {split_amount})")
    print(f"   Player 3: {player3.chips} (ganhou {split_amount})")
    print(f"   Total: {player1.chips + player2.chips + player3.chips}")
    print(f"   Fichas perdidas: {remainder}")

    if remainder > 0:
        print(f"\n❌ PROBLEMA: {remainder} ficha(s) desapareceram!")

    # CENÁRIO 4: Empate real de jogo
    print("\n📍 CENÁRIO 4: Empate Real - Par de Ases com mesmos kickers")
    print("-" * 80)

    player1 = Player("Player 1")
    player2 = Player("Player 2")
    player1.chips = 1000
    player2.chips = 1000

    # Mesa: AA-K-Q-J
    community = [
        Card('A', 'Hearts'),
        Card('A', 'Spades'),
        Card('K', 'Diamonds'),
        Card('Q', 'Clubs'),
        Card('J', 'Hearts')
    ]

    # Ambos têm cartas baixas que não contam
    player1.hand = [Card('2', 'Spades'), Card('3', 'Clubs')]
    player2.hand = [Card('4', 'Diamonds'), Card('5', 'Spades')]

    hand1_name, hand1_value = player1.get_hand_value(community)
    hand2_name, hand2_value = player2.get_hand_value(community)

    print(f"Mesa: AA-K-Q-J")
    print(f"Player 1 (2-3): {hand1_name} - {hand1_value}")
    print(f"Player 2 (4-5): {hand2_name} - {hand2_value}")
    print(f"Empate? {hand1_value == hand2_value}")

    if hand1_value == hand2_value:
        print("✅ Sistema detectou empate corretamente!")
        print("   Ambos jogam: AA com kickers K-Q-J da mesa")
    else:
        print("❌ ERRO: Deveria ser empate!")

    pot = 150
    split_amount = pot // 2
    remainder = pot % 2

    print(f"\nPote: {pot}")
    print(f"Split: {split_amount} para cada")
    if remainder > 0:
        print(f"⚠️  Resto: {remainder} ficha")

    print("\n" + "=" * 80)
    print("📊 RESUMO DOS PROBLEMAS ENCONTRADOS")
    print("=" * 80)
    print("\n1. ✅ Sistema detecta empates corretamente (comparação de tuplas)")
    print("2. ✅ Split pot implementado (linhas 834-839 em poker_app.py)")
    print("3. ❌ PROBLEMA: Divisão inteira (//) perde fichas quando não é divisível")
    print("   Exemplos:")
    print("   • Pote 101 / 2 jogadores = 50 cada, 1 ficha perdida")
    print("   • Pote 100 / 3 jogadores = 33 cada, 1 ficha perdida")
    print("   • Pote 103 / 5 jogadores = 20 cada, 3 fichas perdidas")
    print("\n💡 SOLUÇÃO SUGERIDA:")
    print("   • Dar a(s) ficha(s) extra(s) para o jogador em melhor posição")
    print("   • Ou implementar 'odd chip rule' do poker profissional")
    print("   • Exemplo: Pote 101 / 2 = 51 para P1 (posição), 50 para P2")


if __name__ == "__main__":
    test_split_pot_logic()
