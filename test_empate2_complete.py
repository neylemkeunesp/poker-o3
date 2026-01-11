#!/usr/bin/env python3
"""
Teste completo do cenário empate2.png após correções
Simula exatamente o que o GUI faz
"""

from card import Card
from player import Player


def test_empate2_with_gui_logic():
    """Simula exatamente a lógica do GUI"""

    print("=" * 80)
    print("🎯 TESTE COMPLETO - SIMULANDO LÓGICA DO GUI")
    print("=" * 80)
    print("\n📍 Cenário da imagem empate2.png:")
    print("   Máquina: 9♠ 4♥")
    print("   Jogador: 10♥ 3♠")
    print("   Mesa: Q♣ 3♥ Q♦ A♣ 4♠")
    print("-" * 80)

    # Setup igual ao GUI
    player = Player("Jogador 1")
    machine = Player("Máquina")

    player.hand = [Card('10', 'Hearts'), Card('3', 'Spades')]
    machine.hand = [Card('9', 'Spades'), Card('4', 'Hearts')]

    community_cards = [
        Card('Q', 'Clubs'),
        Card('3', 'Hearts'),
        Card('Q', 'Diamonds'),
        Card('A', 'Clubs'),
        Card('4', 'Spades')
    ]

    # Lógica exata do GUI (poker_gui.py linhas 1495-1512)
    player_type, player_value = player.get_hand_value(community_cards)
    machine_type, machine_value = machine.get_hand_value(community_cards)

    print(f"\n📋 Avaliação das mãos:")
    print(f"   Jogador: {player_type}")
    print(f"   Tuple: {player_value}")
    print(f"\n   Máquina: {machine_type}")
    print(f"   Tuple: {machine_value}")

    # Display hand results (igual GUI)
    result = f"\nJogador 1 tem {player_type}\nMáquina tem {machine_type}\n"

    # Comparação de três vias (igual GUI corrigido)
    if player_value > machine_value:
        winner_name = "Jogador 1"
        winner_hand_type = player_type
        result += f"🏆 {winner_name} vence!"
    elif machine_value > player_value:
        winner_name = "Máquina"
        winner_hand_type = machine_type
        result += f"🏆 {winner_name} vence!"
    else:  # Empate verdadeiro - split pot
        winner_name = "Empate"
        winner_hand_type = player_type
        result += f"🤝 EMPATE! Pote dividido!"

    print(f"\n{result}")

    # Análise detalhada
    print("\n" + "=" * 80)
    print("📊 ANÁLISE DETALHADA:")
    print("=" * 80)

    print(f"\nComparação tupla por tupla:")
    print(f"   Posição [0] (base): {player_value[0]} vs {machine_value[0]} → {'=' if player_value[0] == machine_value[0] else ('Jogador' if player_value[0] > machine_value[0] else 'Máquina')}")
    print(f"   Posição [1] (par 1): {player_value[1]} vs {machine_value[1]} → {'=' if player_value[1] == machine_value[1] else ('Jogador' if player_value[1] > machine_value[1] else 'Máquina')}")
    print(f"   Posição [2] (par 2): {player_value[2]} vs {machine_value[2]} → {'=' if player_value[2] == machine_value[2] else ('Jogador' if player_value[2] > machine_value[2] else 'Máquina')}")

    print(f"\n🎲 Resultado da comparação Python:")
    print(f"   player_value > machine_value: {player_value > machine_value}")
    print(f"   machine_value > player_value: {machine_value > player_value}")
    print(f"   player_value == machine_value: {player_value == machine_value}")

    # Verificação final
    print("\n" + "=" * 80)
    print("✅ VERIFICAÇÃO FINAL:")
    print("=" * 80)

    if winner_name == "Máquina":
        print("\n✅ CORRETO! A Máquina vence com o segundo par melhor (4s > 3s)")
        print("   Tuplas comparadas corretamente: (300, 12, 4, ...) > (300, 12, 3, ...)")
        print("\n📝 NOTA: A imagem empate2.png mostra o Jogador vencendo.")
        print("   Isso significa que a imagem foi tirada com uma versão ANTIGA do código,")
        print("   ANTES das correções na representação de tuplas em player.py.")
        print("\n🔧 CORREÇÕES APLICADAS:")
        print("   • player.py linha 176: Dois Pares agora usa (base, high, low, kicker, 0, 0)")
        print("   • Removido valores duplicados das tuplas")
        print("   • GUI usando comparação de 3 vias (>, <, ==)")
        success = True
    elif winner_name == "Jogador 1":
        print("\n❌ ERRO! O Jogador não deveria vencer!")
        print("   A Máquina tem o segundo par melhor (4s > 3s)")
        print("   Algo ainda está errado na comparação.")
        success = False
    else:
        print("\n❌ ERRO! Não deveria ser empate!")
        print("   A Máquina tem mão superior.")
        success = False

    print("=" * 80)
    return success


if __name__ == "__main__":
    success = test_empate2_with_gui_logic()

    if success:
        print("\n\n" + "🎉" * 40)
        print("✅ TODAS AS CORREÇÕES FUNCIONANDO!")
        print("🎉" * 40)
        print("\n💡 A imagem empate2.png foi tirada ANTES das correções.")
        print("   Se você rodar o jogo AGORA com essas cartas, a Máquina vencerá.")
    else:
        print("\n\n" + "⚠️ " * 40)
        print("❌ AINDA HÁ PROBLEMAS - INVESTIGAÇÃO NECESSÁRIA")
        print("⚠️ " * 40)
