#!/usr/bin/env python3
"""
Teste do cenário da imagem empate4.png
"""

from card import Card
from player import Player


def test_empate4():
    """Testa o cenário exato da imagem empate4.png"""

    print("=" * 80)
    print("🎯 TESTE DO CENÁRIO DA IMAGEM (empate4.png)")
    print("=" * 80)
    print("\n📍 Cenário:")
    print("   Máquina: 3♦ 7♦")
    print("   Jogador: K♠ 5♠")
    print("   Mesa: 6♥ 6♠ 2♦ Q♠ 10♦")
    print("-" * 80)

    machine = Player("Máquina")
    player = Player("Jogador")

    # Cartas exatas da imagem
    machine.hand = [Card('3', 'Diamonds'), Card('7', 'Diamonds')]
    player.hand = [Card('K', 'Spades'), Card('5', 'Spades')]

    community = [
        Card('6', 'Hearts'),
        Card('6', 'Spades'),
        Card('2', 'Diamonds'),
        Card('Q', 'Spades'),
        Card('10', 'Diamonds')
    ]

    # Avaliar mãos
    machine_type, machine_value = machine.get_hand_value(community)
    player_type, player_value = player.get_hand_value(community)

    print(f"\nMáquina (3♦ 7♦):")
    print(f"   Mão: {machine_type}")
    print(f"   Tuple: {machine_value}")
    print(f"   7 cartas: 3♦ 7♦ 6♥ 6♠ 2♦ Q♠ 10♦")
    if machine_type == "Par":
        print(f"   Par de 6s, kickers: Q-10-7")
        print(f"   Melhor mão: 6-6-Q-10-7")

    print(f"\nJogador (K♠ 5♠):")
    print(f"   Mão: {player_type}")
    print(f"   Tuple: {player_value}")
    print(f"   7 cartas: K♠ 5♠ 6♥ 6♠ 2♦ Q♠ 10♦")
    if player_type == "Par":
        print(f"   Par de 6s, kickers: K-Q-10")
        print(f"   Melhor mão: 6-6-K-Q-10")

    # Comparação detalhada
    print(f"\n📊 Comparação Detalhada:")
    print(f"   Tipo: {player_type} vs {machine_type}")
    print(f"   Base: {player_value[0]} vs {machine_value[0]}")
    print(f"   Par: {player_value[1]} vs {machine_value[1]}")
    print(f"   Kicker 1: {player_value[2]} vs {machine_value[2]}")
    print(f"   Kicker 2: {player_value[3]} vs {machine_value[3]}")
    print(f"   Kicker 3: {player_value[4]} vs {machine_value[4]}")

    print(f"\n   player_value > machine_value: {player_value > machine_value}")
    print(f"   machine_value > player_value: {machine_value > player_value}")
    print(f"   player_value == machine_value: {player_value == machine_value}")

    # Determinar vencedor correto
    if player_value > machine_value:
        winner_name = "Jogador"
        result = "🏆 Jogador vence!"
        explanation = f"Jogador tem kicker melhor (K > 7)"
    elif machine_value > player_value:
        winner_name = "Máquina"
        result = "🏆 Máquina vence!"
        explanation = f"Máquina tem mão superior"
    else:
        winner_name = "Empate"
        result = "🤝 EMPATE! Pote dividido!"
        explanation = "Mãos idênticas"

    print(f"\n{result}")
    print(f"Explicação: {explanation}")

    # Verificação contra a imagem
    print("\n" + "=" * 80)
    print("📋 VERIFICAÇÃO:")
    print("   Resultado na imagem: EMPATE (Jogador 1420, Máquina 580 = 2000 total)")
    print(f"   Resultado correto calculado: {winner_name} deve vencer")

    # Análise dos chips
    print("\n💰 Análise das fichas:")
    print("   Total: 1420 + 580 = 2000 ✓ (conservação mantida)")
    print("   Indica que houve split pot (ambos ganharam ~220)")

    if winner_name == "Jogador":
        print("\n❌ ERRO NO JOGO!")
        print("   O Jogador deveria ter vencido SOZINHO")
        print("   Ambos têm Par de 6s, mas Jogador tem K como kicker")
        print("   Máquina tem apenas Q-10-7")
        print("   K (13) > Q (12)")
    elif winner_name == "Empate":
        print("\n✅ Resultado correto (se as tuplas são realmente iguais)")
    else:
        print("\n❌ ERRO! Máquina não deveria vencer")

    print("=" * 80)

    return {
        'machine_type': machine_type,
        'machine_value': machine_value,
        'player_type': player_type,
        'player_value': player_value,
        'correct_winner': winner_name
    }


if __name__ == "__main__":
    result = test_empate4()

    print("\n\n📊 RESUMO TÉCNICO:")
    print(f"   Máquina: {result['machine_type']} - {result['machine_value']}")
    print(f"   Jogador: {result['player_type']} - {result['player_value']}")
    print(f"   Vencedor correto: {result['correct_winner']}")
