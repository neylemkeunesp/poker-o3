#!/usr/bin/env python3
"""
Teste do cenário da imagem empate2.png
Verifica qual deveria ser o vencedor correto
"""

from card import Card
from player import Player


def test_empate2_scenario():
    """Testa o cenário exato da imagem empate2.png"""

    print("=" * 80)
    print("🎯 TESTE DO CENÁRIO DA IMAGEM (empate2.png)")
    print("=" * 80)
    print("\n📍 Cenário:")
    print("   Máquina: 9♠ 4♥")
    print("   Jogador: 10♥ 3♠")
    print("   Mesa: Q♣ 3♥ Q♦ A♣ 4♠")
    print("-" * 80)

    machine = Player("Máquina")
    player = Player("Jogador 1")

    # Cartas exatas da imagem
    machine.hand = [Card('9', 'Spades'), Card('4', 'Hearts')]
    player.hand = [Card('10', 'Hearts'), Card('3', 'Spades')]

    community = [
        Card('Q', 'Clubs'),
        Card('3', 'Hearts'),
        Card('Q', 'Diamonds'),
        Card('A', 'Clubs'),
        Card('4', 'Spades')
    ]

    # Avaliar mãos
    machine_type, machine_value = machine.get_hand_value(community)
    player_type, player_value = player.get_hand_value(community)

    print(f"\nMáquina (9♠ 4♥):")
    print(f"   Mão: {machine_type}")
    print(f"   Tuple: {machine_value}")
    print(f"   Análise: Par de Queens (mesa) + Par de 4s (4♥ mão + 4♠ mesa)")
    print(f"   Melhores 5 cartas: Q-Q-4-4-A")

    print(f"\nJogador (10♥ 3♠):")
    print(f"   Mão: {player_type}")
    print(f"   Tuple: {player_value}")
    print(f"   Análise: Par de Queens (mesa) + Par de 3s (3♠ mão + 3♥ mesa)")
    print(f"   Melhores 5 cartas: Q-Q-3-3-A")

    # Comparação detalhada
    print(f"\n📊 Comparação Detalhada:")
    print(f"   Tipo de mão: {machine_type} vs {player_type}")
    print(f"   Base value: {machine_value[0]} vs {player_value[0]}")

    if len(machine_value) > 1:
        print(f"   Par maior: {machine_value[1]} vs {player_value[1]}")
    if len(machine_value) > 2:
        print(f"   Par menor: {machine_value[2]} vs {player_value[2]}")
    if len(machine_value) > 3:
        print(f"   Kicker 1: {machine_value[3]} vs {player_value[3]}")

    print(f"\n   machine_value > player_value: {machine_value > player_value}")
    print(f"   player_value > machine_value: {player_value > machine_value}")
    print(f"   machine_value == player_value: {machine_value == player_value}")

    # Determinar vencedor correto
    if machine_value > player_value:
        winner_name = "Máquina"
        result = "🏆 Máquina vence!"
        explanation = "Máquina tem dois pares Q-Q-4-4, Jogador tem Q-Q-3-3. 4 > 3 no segundo par."
    elif player_value > machine_value:
        winner_name = "Jogador 1"
        result = "🏆 Jogador 1 vence!"
        explanation = "Jogador tem mão superior."
    else:
        winner_name = "Empate"
        result = "🤝 EMPATE! Pote dividido!"
        explanation = "Mãos idênticas."

    print(f"\n{result}")
    print(f"Vencedor correto: {winner_name}")
    print(f"Explicação: {explanation}")

    # Verificação contra a imagem
    print("\n" + "=" * 80)
    print("📋 VERIFICAÇÃO:")
    print("   Resultado mostrado na imagem: Jogador venceu")
    print(f"   Resultado correto calculado: {winner_name} deve vencer")

    if winner_name == "Jogador 1":
        print("\n✅ CORRETO! O jogo está funcionando corretamente.")
        print("   Jogador tem a mão superior.")
    elif winner_name == "Máquina":
        print("\n❌ ERRO! O jogo deu vitória errada!")
        print("   A Máquina deveria ter vencido com o segundo par melhor (4s > 3s).")
        print("   Possível bug na avaliação de Dois Pares.")
    else:
        print("\n❌ ERRO! Não deveria ser empate.")

    print("=" * 80)

    # Retornar para debugging
    return {
        'machine_type': machine_type,
        'machine_value': machine_value,
        'player_type': player_type,
        'player_value': player_value,
        'correct_winner': winner_name
    }


if __name__ == "__main__":
    result = test_empate2_scenario()

    print("\n\n📊 RESUMO TÉCNICO:")
    print(f"   Máquina: {result['machine_type']} - {result['machine_value']}")
    print(f"   Jogador: {result['player_type']} - {result['player_value']}")
    print(f"   Vencedor correto: {result['correct_winner']}")
