#!/usr/bin/env python3
"""
Teste detalhado de conservação de fichas
Simula uma mão completa de poker e verifica se os chips são conservados
"""

class MockGame:
    def __init__(self):
        self.pot = 0
        self.min_raise = 50

class MockPlayer:
    def __init__(self, name, chips=1000):
        self.name = name
        self.chips = chips
        self.folded = False

def log_state(action, player, machine, pot):
    total = player.chips + machine.chips + pot
    print(f"\n[{action}]")
    print(f"  Jogador: {player.chips} chips")
    print(f"  Máquina: {machine.chips} chips")
    print(f"  Pote: {pot} chips")
    print(f"  Total: {total} chips", end="")
    if total != 2000:
        print(f" ⚠️ ERRO! Esperado: 2000, Diferença: {total-2000:+d}")
    else:
        print(" ✓")
    return total == 2000

# Inicialização
player = MockPlayer("Jogador", 1000)
machine = MockPlayer("Máquina", 1000)
game = MockGame()

player_bet_in_round = 0
machine_bet_in_round = 0
current_bet = 0

print("=" * 60)
print("SIMULAÇÃO DE MÃO COMPLETA DE POKER")
print("=" * 60)

# Estado inicial
ok = log_state("Início", player, machine, game.pot)
if not ok:
    print("\n❌ ERRO NO INÍCIO!")
    exit(1)

# Blinds
print("\n--- PRÉ-FLOP: BLINDS ---")
small_blind = 25
big_blind = 50

player.chips -= small_blind
machine.chips -= big_blind
game.pot = small_blind + big_blind
player_bet_in_round = small_blind
machine_bet_in_round = big_blind
current_bet = big_blind

ok = log_state("Blinds postados", player, machine, game.pot)
if not ok:
    print("\n❌ ERRO APÓS BLINDS!")
    exit(1)

print(f"\n  player_bet_in_round: {player_bet_in_round}")
print(f"  machine_bet_in_round: {machine_bet_in_round}")
print(f"  current_bet: {current_bet}")

# Jogador Call (igualar o big blind)
print("\n--- PRÉ-FLOP: JOGADOR CALL ---")
additional_bet = machine_bet_in_round - player_bet_in_round
print(f"  Jogador precisa pagar: {additional_bet}")

player.chips -= additional_bet
game.pot += additional_bet
player_bet_in_round += additional_bet

ok = log_state("Jogador Call", player, machine, game.pot)
if not ok:
    print("\n❌ ERRO APÓS JOGADOR CALL!")
    exit(1)

print(f"\n  player_bet_in_round: {player_bet_in_round}")
print(f"  machine_bet_in_round: {machine_bet_in_round}")

# Máquina Raise
print("\n--- PRÉ-FLOP: MÁQUINA RAISE ---")
call_amount = player_bet_in_round - machine_bet_in_round
raise_amount = game.min_raise
total_amount = call_amount + raise_amount
print(f"  call_amount: {call_amount}")
print(f"  raise_amount: {raise_amount}")
print(f"  total_amount: {total_amount}")

machine.chips -= total_amount
game.pot += total_amount
machine_bet_in_round += total_amount
current_bet = machine_bet_in_round

ok = log_state("Máquina Raise", player, machine, game.pot)
if not ok:
    print("\n❌ ERRO APÓS MÁQUINA RAISE!")
    exit(1)

print(f"\n  player_bet_in_round: {player_bet_in_round}")
print(f"  machine_bet_in_round: {machine_bet_in_round}")
print(f"  current_bet: {current_bet}")

# Jogador Call (igualar o raise)
print("\n--- PRÉ-FLOP: JOGADOR CALL RAISE ---")
additional_bet = machine_bet_in_round - player_bet_in_round
print(f"  Jogador precisa pagar: {additional_bet}")

player.chips -= additional_bet
game.pot += additional_bet
player_bet_in_round += additional_bet

ok = log_state("Jogador Call Raise", player, machine, game.pot)
if not ok:
    print("\n❌ ERRO APÓS JOGADOR CALL RAISE!")
    exit(1)

print(f"\n  player_bet_in_round: {player_bet_in_round}")
print(f"  machine_bet_in_round: {machine_bet_in_round}")

# Reset para próxima rodada (FLOP)
print("\n--- FLOP: RESET DAS APOSTAS ---")
player_bet_in_round = 0
machine_bet_in_round = 0
current_bet = 0

ok = log_state("Reset para Flop", player, machine, game.pot)
if not ok:
    print("\n❌ ERRO APÓS RESET!")
    exit(1)

print(f"\n  player_bet_in_round: {player_bet_in_round}")
print(f"  machine_bet_in_round: {machine_bet_in_round}")
print(f"  current_bet: {current_bet}")

# Máquina Check
print("\n--- FLOP: MÁQUINA CHECK ---")
ok = log_state("Máquina Check", player, machine, game.pot)
if not ok:
    print("\n❌ ERRO APÓS MÁQUINA CHECK!")
    exit(1)

# Jogador Raise
print("\n--- FLOP: JOGADOR RAISE ---")
call_amount = machine_bet_in_round - player_bet_in_round
raise_amount = game.min_raise
total_amount = call_amount + raise_amount
print(f"  call_amount: {call_amount}")
print(f"  raise_amount: {raise_amount}")
print(f"  total_amount: {total_amount}")

player.chips -= total_amount
game.pot += total_amount
player_bet_in_round += total_amount
current_bet = player_bet_in_round

ok = log_state("Jogador Raise", player, machine, game.pot)
if not ok:
    print("\n❌ ERRO APÓS JOGADOR RAISE!")
    exit(1)

print(f"\n  player_bet_in_round: {player_bet_in_round}")
print(f"  machine_bet_in_round: {machine_bet_in_round}")
print(f"  current_bet: {current_bet}")

# Máquina Call
print("\n--- FLOP: MÁQUINA CALL ---")
call_amount = player_bet_in_round - machine_bet_in_round
print(f"  Máquina precisa pagar: {call_amount}")

machine.chips -= call_amount
game.pot += call_amount
machine_bet_in_round += call_amount

ok = log_state("Máquina Call", player, machine, game.pot)
if not ok:
    print("\n❌ ERRO APÓS MÁQUINA CALL!")
    exit(1)

# Showdown - Jogador vence
print("\n--- SHOWDOWN: JOGADOR VENCE ---")
pot_amount = game.pot
player.chips += pot_amount
game.pot = 0

ok = log_state("Jogador vence", player, machine, game.pot)
if not ok:
    print("\n❌ ERRO APÓS PAGAMENTO!")
    exit(1)

print("\n" + "=" * 60)
print("✓ TESTE COMPLETO - CONSERVAÇÃO DE FICHAS OK!")
print("=" * 60)
