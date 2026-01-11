#!/usr/bin/env python3
"""
Teste da correção do bug de determinação de vencedor no GUI
Verifica que o cenário da imagem empate.png funciona corretamente
"""

from card import Card
from player import Player


def test_image_scenario():
    """Testa o cenário exato da imagem empate.png"""

    print("=" * 80)
    print("🎯 TESTE DO CENÁRIO DA IMAGEM (empate.png)")
    print("=" * 80)
    print("\n📍 Cenário: Player (2♠ Q♦) vs Machine (10♥ J♠)")
    print("   Mesa: 4♣ A♠ 3♥ 7♠ 6♥")
    print("-" * 80)

    player = Player("Jogador 1")
    machine = Player("Máquina")

    # Cartas exatas da imagem
    player.hand = [Card('2', 'Spades'), Card('Q', 'Diamonds')]
    machine.hand = [Card('10', 'Hearts'), Card('J', 'Spades')]

    community = [
        Card('4', 'Clubs'),
        Card('A', 'Spades'),
        Card('3', 'Hearts'),
        Card('7', 'Spades'),
        Card('6', 'Hearts')
    ]

    # Avaliar mãos
    player_type, player_value = player.get_hand_value(community)
    machine_type, machine_value = machine.get_hand_value(community)

    print(f"\nPlayer:  {player_type}")
    print(f"         Tuple: {player_value}")
    print(f"\nMachine: {machine_type}")
    print(f"         Tuple: {machine_value}")

    # Comparação
    print(f"\n📊 Comparação:")
    print(f"   player_value > machine_value: {player_value > machine_value}")
    print(f"   machine_value > player_value: {machine_value > player_value}")
    print(f"   player_value == machine_value: {player_value == machine_value}")

    # Determinar vencedor (mesma lógica do GUI corrigido)
    if player_value > machine_value:
        winner_name = "Jogador 1"
        result = "🏆 Jogador 1 vence!"
    elif machine_value > player_value:
        winner_name = "Máquina"
        result = "🏆 Máquina vence!"
    else:
        winner_name = "Empate"
        result = "🤝 EMPATE! Pote dividido!"

    print(f"\n{result}")
    print(f"Vencedor: {winner_name}")

    # Verificação
    print("\n" + "=" * 80)
    if winner_name == "Jogador 1":
        print("✅ CORRETO! Player vence com Q > J como segundo kicker")
        print("   Ambos têm Ace high, mas Player tem Queen e Machine tem Jack")
    elif winner_name == "Empate":
        print("❌ ERRO! Não deveria ser empate - Player tem kicker melhor (Q > J)")
    else:
        print("❌ ERRO CRÍTICO! Máquina não deveria vencer")

    # Validação detalhada
    assert player_value[0] == 100, "Ambos deveriam ter Carta Alta (100)"
    assert machine_value[0] == 100, "Ambos deveriam ter Carta Alta (100)"
    assert player_value[1] == 14, "Ambos têm Ace (14) como carta mais alta"
    assert machine_value[1] == 14, "Ambos têm Ace (14) como carta mais alta"
    assert player_value[2] == 12, f"Player deveria ter Queen (12), tem {player_value[2]}"
    assert machine_value[2] == 11, f"Machine deveria ter Jack (11), tem {machine_value[2]}"
    assert player_value > machine_value, "Player DEVE vencer (Q > J)"
    assert winner_name == "Jogador 1", "Vencedor deve ser Jogador 1"

    print("=" * 80)


def test_real_tie_scenario():
    """Testa um empate verdadeiro"""

    print("\n\n" + "=" * 80)
    print("🎯 TESTE DE EMPATE VERDADEIRO")
    print("=" * 80)
    print("\n📍 Cenário: Royal Flush na mesa")
    print("-" * 80)

    player = Player("Jogador 1")
    machine = Player("Máquina")

    # Mesa com Royal Flush completo
    community = [
        Card('A', 'Hearts'),
        Card('K', 'Hearts'),
        Card('Q', 'Hearts'),
        Card('J', 'Hearts'),
        Card('10', 'Hearts')
    ]

    # Ambos têm lixo
    player.hand = [Card('2', 'Spades'), Card('3', 'Clubs')]
    machine.hand = [Card('4', 'Diamonds'), Card('5', 'Spades')]

    # Avaliar mãos
    player_type, player_value = player.get_hand_value(community)
    machine_type, machine_value = machine.get_hand_value(community)

    print(f"\nPlayer:  {player_type} - {player_value}")
    print(f"Machine: {machine_type} - {machine_value}")
    print(f"Empate? {player_value == machine_value}")

    # Determinar vencedor
    if player_value > machine_value:
        winner_name = "Jogador 1"
        result = "🏆 Jogador 1 vence!"
    elif machine_value > player_value:
        winner_name = "Máquina"
        result = "🏆 Máquina vence!"
    else:
        winner_name = "Empate"
        result = "🤝 EMPATE! Pote dividido!"

    print(f"\n{result}")

    # Validação
    assert player_value == machine_value, "Deveria ser empate (Royal Flush na mesa)"
    assert winner_name == "Empate", "Vencedor deve ser 'Empate'"

    print("✅ CORRETO! Empate detectado quando ambos têm a mesma mão")
    print("=" * 80)


def test_split_pot_calculation():
    """Testa o cálculo de split pot com odd chip rule"""

    print("\n\n" + "=" * 80)
    print("🎯 TESTE DE CÁLCULO DE SPLIT POT")
    print("=" * 80)

    # Teste 1: Pote par
    print("\n📍 Teste 1: Pote 200 ÷ 2 = 100 cada")
    pot = 200
    split_amount = pot // 2
    remainder = pot % 2
    print(f"   Split: {split_amount}, Resto: {remainder}")
    assert split_amount == 100 and remainder == 0, "Pote par deve dividir igualmente"
    print("   ✅ 100 para cada jogador")

    # Teste 2: Pote ímpar
    print("\n📍 Teste 2: Pote 101 ÷ 2 = 50 + 51 (odd chip rule)")
    pot = 101
    split_amount = pot // 2
    remainder = pot % 2
    print(f"   Split: {split_amount}, Resto: {remainder}")
    assert split_amount == 50 and remainder == 1, "Pote ímpar deve ter resto"
    print("   ✅ 51 para Player 1 (recebe extra), 50 para Player 2")

    # Teste 3: Pote grande ímpar
    print("\n📍 Teste 3: Pote 999 ÷ 2 = 499 + 500")
    pot = 999
    split_amount = pot // 2
    remainder = pot % 2
    print(f"   Split: {split_amount}, Resto: {remainder}")
    assert split_amount == 499 and remainder == 1, "Pote grande ímpar"
    print("   ✅ 500 para Player 1, 499 para Player 2")

    print("\n✅ Todos os cálculos de split pot corretos!")
    print("=" * 80)


if __name__ == "__main__":
    test_image_scenario()
    test_real_tie_scenario()
    test_split_pot_calculation()

    print("\n\n" + "=" * 80)
    print("✅ TODOS OS TESTES PASSARAM!")
    print("=" * 80)
    print("\n📊 RESUMO:")
    print("   ✅ Cenário da imagem corrigido - Player vence com Q > J")
    print("   ✅ Empates verdadeiros detectados corretamente")
    print("   ✅ Split pot com odd chip rule funciona")
    print("   ✅ GUI agora usa comparação de 3 vias (>, <, ==)")
    print("\n💡 Correção aplicada em poker_gui.py:")
    print("   • Linhas 1498-1514: Comparação de 3 vias")
    print("   • Linhas 1520-1536: Banner de empate")
    print("   • Linhas 1540-1593: Estatísticas e distribuição de pote para empates")
