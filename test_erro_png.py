#!/usr/bin/env python3
"""
Teste do cenário da imagem erro.png
"""

from card import Card
from player import Player


def test_erro_png():
    """Testa o cenário exato da imagem erro.png"""

    print("=" * 80)
    print("🎯 TESTE DO CENÁRIO DA IMAGEM (erro.png)")
    print("=" * 80)
    print("\n📍 Cenário:")
    print("   Máquina: 7♥ 9♦")
    print("   Jogador: 3♦ A♥")
    print("   Mesa: 2♦ 6♦ 8♠ 7♣ 10♣")
    print("-" * 80)

    machine = Player("Máquina")
    player = Player("Jogador")

    # Cartas exatas da imagem
    machine.hand = [Card('7', 'Hearts'), Card('9', 'Diamonds')]
    player.hand = [Card('3', 'Diamonds'), Card('A', 'Hearts')]

    community = [
        Card('2', 'Diamonds'),
        Card('6', 'Diamonds'),
        Card('8', 'Spades'),
        Card('7', 'Clubs'),
        Card('10', 'Clubs')
    ]

    # Avaliar mãos
    machine_type, machine_value = machine.get_hand_value(community)
    player_type, player_value = player.get_hand_value(community)

    print(f"\nMáquina (7♥ 9♦):")
    print(f"   Mão: {machine_type}")
    print(f"   Tuple: {machine_value}")
    print(f"   Análise: 7 cartas disponíveis: 7♥ 9♦ 2♦ 6♦ 8♠ 7♣ 10♣")
    if machine_type == "Par":
        print(f"   ✓ Tem PAR de 7s (7♥ + 7♣)")
        print(f"   Melhor mão: 7-7-10-9-8")
    else:
        print(f"   Tipo detectado: {machine_type}")

    print(f"\nJogador (3♦ A♥):")
    print(f"   Mão: {player_type}")
    print(f"   Tuple: {player_value}")
    print(f"   Análise: 7 cartas disponíveis: 3♦ A♥ 2♦ 6♦ 8♠ 7♣ 10♣")
    if player_type == "Carta Alta":
        print(f"   ✗ NÃO tem par, flush ou sequência")
        print(f"   Melhor mão: A-10-8-7-6")
    elif player_type == "Flush":
        print(f"   ✓ Tem FLUSH? Vamos verificar...")
        diamonds = [c for c in (player.hand + community) if c.suit == 'Diamonds']
        print(f"   Ouros: {len(diamonds)} cartas - {[f'{c.rank}♦' for c in diamonds]}")
    else:
        print(f"   Tipo detectado: {player_type}")

    # Verificar flush manualmente
    print(f"\n🔍 Verificação de FLUSH para o Jogador:")
    all_cards = player.hand + community
    diamonds = [c for c in all_cards if c.suit == 'Diamonds']
    print(f"   Cartas de Ouros disponíveis: {len(diamonds)}")
    for c in diamonds:
        print(f"      {c.rank}♦")
    if len(diamonds) >= 5:
        print(f"   ✓ TEM FLUSH! (5+ ouros)")
    else:
        print(f"   ✗ NÃO TEM FLUSH (precisa de 5, tem apenas {len(diamonds)})")

    # Comparação
    print(f"\n📊 Comparação:")
    print(f"   machine_value > player_value: {machine_value > player_value}")
    print(f"   player_value > machine_value: {player_value > machine_value}")
    print(f"   machine_value == player_value: {machine_value == player_value}")

    # Determinar vencedor correto
    if machine_value > player_value:
        winner_name = "Máquina"
        result = "🏆 Máquina vence!"
        explanation = f"Máquina tem {machine_type}, Jogador tem {player_type}"
    elif player_value > machine_value:
        winner_name = "Jogador"
        result = "🏆 Jogador vence!"
        explanation = f"Jogador tem {player_type}, Máquina tem {machine_type}"
    else:
        winner_name = "Empate"
        result = "🤝 EMPATE!"
        explanation = "Mãos idênticas"

    print(f"\n{result}")
    print(f"Explicação: {explanation}")

    # Verificação contra a imagem
    print("\n" + "=" * 80)
    print("📋 VERIFICAÇÃO:")
    print("   Resultado na imagem: Jogador venceu (tem 1220 chips)")
    print(f"   Resultado correto calculado: {winner_name} deve vencer")

    if winner_name == "Máquina":
        print("\n❌ ERRO NO JOGO!")
        print("   A Máquina deveria ter vencido com PAR de 7s")
        print("   Jogador só tem ACE HIGH")
        print("   Par (200) > Carta Alta (100)")
    elif winner_name == "Jogador":
        print("\n✅ Resultado pode estar correto")
        print(f"   Jogador tem: {player_type}")
        print(f"   Máquina tem: {machine_type}")
    else:
        print("\n❌ ERRO! Não deveria ser empate")

    print("=" * 80)

    return {
        'machine_type': machine_type,
        'machine_value': machine_value,
        'player_type': player_type,
        'player_value': player_value,
        'correct_winner': winner_name
    }


if __name__ == "__main__":
    result = test_erro_png()

    print("\n\n📊 RESUMO TÉCNICO:")
    print(f"   Máquina: {result['machine_type']} - {result['machine_value']}")
    print(f"   Jogador: {result['player_type']} - {result['player_value']}")
    print(f"   Vencedor correto: {result['correct_winner']}")
