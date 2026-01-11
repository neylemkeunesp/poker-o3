#!/usr/bin/env python3
"""
Simulação completa do GUI para o cenário empate4.png
"""

from card import Card
from player import Player


def simulate_empate4_gui():
    """Simula a lógica exata do GUI para empate4.png"""

    print("=" * 80)
    print("🎯 SIMULAÇÃO COMPLETA DO GUI - empate4.png")
    print("=" * 80)

    # Setup igual ao GUI
    player = Player("Jogador 1")
    machine = Player("Máquina", is_machine=True)

    print("\n📍 Setup:")
    print("   player.hand (VOCÊ): K♠ 5♠")
    print("   machine.hand (MÁQUINA): 3♦ 7♦")
    print("   community: 6♥ 6♠ 2♦ Q♠ 10♦")
    print("-" * 80)

    player.hand = [Card('K', 'Spades'), Card('5', 'Spades')]
    machine.hand = [Card('3', 'Diamonds'), Card('7', 'Diamonds')]

    community_cards = [
        Card('6', 'Hearts'),
        Card('6', 'Spades'),
        Card('2', 'Diamonds'),
        Card('Q', 'Spades'),
        Card('10', 'Diamonds')
    ]

    # Lógica exata do GUI (end_hand)
    print("\n🔍 Executando end_hand():")

    print("\n1. Evaluate both player's hands")
    player_type, player_value = player.get_hand_value(community_cards)
    machine_type, machine_value = machine.get_hand_value(community_cards)

    print(f"   player_type = {player_type}")
    print(f"   player_value = {player_value}")
    print(f"   machine_type = {machine_type}")
    print(f"   machine_value = {machine_value}")

    print("\n2. Display hand results")
    result = f"\nJogador 1 tem {player_type}\nMáquina tem {machine_type}\n"

    print("\n3. Comparação:")
    print(f"   player_value > machine_value: {player_value > machine_value}")
    print(f"   machine_value > player_value: {machine_value > player_value}")
    print(f"   player_value == machine_value: {player_value == machine_value}")

    # Comparação elemento por elemento
    print("\n   Comparação elemento por elemento:")
    for i in range(len(player_value)):
        p = player_value[i]
        m = machine_value[i]
        if p > m:
            comp = ">"
        elif p < m:
            comp = "<"
        else:
            comp = "=="
        print(f"   [{i}]: {p} {comp} {m}")

    # Determinação do vencedor
    if player_value > machine_value:
        winner_name = "Jogador 1"
        winner_hand_type = player_type
        result += f"🏆 {winner_name} vence!"
        print(f"\n   >>> BRANCH: player_value > machine_value ✓")
    elif machine_value > player_value:
        winner_name = "Máquina"
        winner_hand_type = machine_type
        result += f"🏆 {winner_name} vence!"
        print(f"\n   >>> BRANCH: machine_value > player_value")
    else:
        winner_name = "Empate"
        winner_hand_type = player_type
        result += f"🤝 EMPATE! Pote dividido!"
        print(f"\n   >>> BRANCH: empate")

    print(f"\n4. Resultado final: {winner_name}")
    print(f"   {result}")

    # Verificação
    print("\n" + "=" * 80)
    print("📋 VERIFICAÇÃO:")
    print("=" * 80)
    print(f"   Vencedor calculado pelo código ATUAL: {winner_name}")
    print(f"   Vencedor na imagem: Empate")

    if winner_name == "Jogador 1":
        print("\n✅ CÓDIGO ATUAL CORRETO!")
        print("   O código AGORA calcula o vencedor corretamente")
        print("   A imagem mostra um empate porque foi tirada com CÓDIGO ANTIGO")
        print("\n📝 EXPLICAÇÃO:")
        print(f"   Ambos têm Par de 6s")
        print(f"   Jogador: kickers K-Q-10 → {player_value}")
        print(f"   Máquina: kickers Q-10-7 → {machine_value}")
        print(f"   K (13) > Q (12) na posição [2]")
        print(f"   JOGADOR VENCE!")
    elif winner_name == "Empate":
        print("\n❌ AINDA HÁ UM BUG!")
        print("   O código está considerando empate incorretamente")
        print("   Precisa investigar mais")
    else:
        print("\n❌ ERRO! Máquina não deveria vencer")

    print("=" * 80)


if __name__ == "__main__":
    simulate_empate4_gui()
