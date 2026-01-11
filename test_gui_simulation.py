#!/usr/bin/env python3
"""
Simulação exata do que o GUI está fazendo no cenário erro.png
"""

from card import Card
from player import Player


def simulate_gui_logic():
    """Simula a lógica exata do GUI"""

    print("=" * 80)
    print("🎯 SIMULAÇÃO EXATA DO GUI - erro.png")
    print("=" * 80)

    # Setup igual ao GUI (linha 96-97 de poker_gui.py)
    player = Player("Jogador 1")  # self.player
    machine = Player("Máquina", is_machine=True)  # self.machine

    # Cartas da imagem
    print("\n📍 Setup das cartas:")
    print("   player.hand (VOCÊ na parte de baixo): 3♦ A♥")
    print("   machine.hand (MÁQUINA na parte de cima): 7♥ 9♦")
    print("   community: 2♦ 6♦ 8♠ 7♣ 10♣")
    print("-" * 80)

    player.hand = [Card('3', 'Diamonds'), Card('A', 'Hearts')]
    machine.hand = [Card('7', 'Hearts'), Card('9', 'Diamonds')]

    community_cards = [
        Card('2', 'Diamonds'),
        Card('6', 'Diamonds'),
        Card('8', 'Spades'),
        Card('7', 'Clubs'),
        Card('10', 'Clubs')
    ]

    # Lógica exata do GUI (linhas 1495-1512)
    print("\n🔍 Executando lógica do end_hand():")
    print("\n1. Evaluate both player's hands")
    player_type, player_value = player.get_hand_value(community_cards)
    machine_type, machine_value = machine.get_hand_value(community_cards)

    print(f"   player_type = {player_type}")
    print(f"   player_value = {player_value}")
    print(f"   machine_type = {machine_type}")
    print(f"   machine_value = {machine_value}")

    print("\n2. Display hand results")
    result = f"\nJogador 1 tem {player_type}\nMáquina tem {machine_type}\n"
    print(f"   {result}")

    print("3. Comparação:")
    print(f"   if player_value > machine_value: {player_value > machine_value}")
    print(f"   elif machine_value > player_value: {machine_value > player_value}")
    print(f"   else (empate): {player_value == machine_value}")

    # Determinação do vencedor (linhas 1501-1512)
    if player_value > machine_value:
        winner_name = "Jogador 1"
        winner_hand_type = player_type
        result += f"🏆 {winner_name} vence!"
        print(f"\n   >>> BRANCH 1 EXECUTADO: player_value > machine_value")
    elif machine_value > player_value:
        winner_name = "Máquina"
        winner_hand_type = machine_type
        result += f"🏆 {winner_name} vence!"
        print(f"\n   >>> BRANCH 2 EXECUTADO: machine_value > player_value")
    else:  # Empate verdadeiro - split pot
        winner_name = "Empate"
        winner_hand_type = player_type
        result += f"🤝 EMPATE! Pote dividido!"
        print(f"\n   >>> BRANCH 3 EXECUTADO: empate")

    print(f"\n4. Resultado final:")
    print(f"   winner_name = {winner_name}")
    print(f"   winner_hand_type = {winner_hand_type}")
    print(f"   {result}")

    # Verificação
    print("\n" + "=" * 80)
    print("📋 VERIFICAÇÃO:")
    print("=" * 80)
    print(f"   Vencedor calculado: {winner_name}")
    print(f"   Vencedor na imagem: Jogador 1 (tem 1220 chips)")

    if winner_name == "Jogador 1":
        print("\n❌ PROBLEMA CONFIRMADO!")
        print("   O código está dando vitória ao Jogador quando deveria ser Máquina")
        print(f"   Máquina tem: {machine_type} {machine_value}")
        print(f"   Jogador tem: {player_type} {player_value}")
        print(f"   {machine_type} ({machine_value[0]}) > {player_type} ({player_value[0]})")
    elif winner_name == "Máquina":
        print("\n✅ CÓDIGO CORRETO!")
        print("   A Máquina está vencendo como deveria")
        print("   O problema deve estar em outro lugar (talvez arquivo errado?)")
    else:
        print("\n❌ ERRO - Não deveria ser empate!")

    print("=" * 80)


if __name__ == "__main__":
    simulate_gui_logic()
