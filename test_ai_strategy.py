#!/usr/bin/env python3
"""
Script de teste para demonstrar a nova estratégia da IA
"""

from poker_app import Player, Card

def test_ai_decisions():
    """Testa diferentes cenários de decisão da IA"""

    print("=" * 70)
    print("🤖 TESTE DA NOVA ESTRATÉGIA DA MÁQUINA")
    print("=" * 70)

    # Criar jogador máquina
    machine = Player("Máquina Teste", is_machine=True)
    machine.chips = 1000

    # Cenário 1: Mão premium pré-flop (AA)
    print("\n📍 CENÁRIO 1: Mão Premium Pré-Flop (Ás-Ás)")
    print("-" * 70)
    machine.hand = [
        Card('A', 'Hearts'),
        Card('A', 'Spades')
    ]
    community_cards = []

    decisions = []
    for i in range(5):
        action, amount = machine.make_decision(community_cards, 50, 20, 100)
        decisions.append(action)
        print(f"   Tentativa {i+1}: {action.upper()}" + (f" (valor: {amount})" if amount > 0 else ""))

    fold_count = decisions.count('fold')
    call_count = decisions.count('call')
    raise_count = decisions.count('raise')

    print(f"\n   Estatísticas: {raise_count} raises, {call_count} calls, {fold_count} folds")
    print(f"   ✓ Esperado: Maioria raises (mão muito forte)")

    # Cenário 2: Lixo pré-flop (7-2)
    print("\n📍 CENÁRIO 2: Lixo Pré-Flop (7-2 offsuit)")
    print("-" * 70)
    machine.hand = [
        Card('7', 'Hearts'),
        Card('2', 'Clubs')
    ]
    community_cards = []

    decisions = []
    for i in range(5):
        action, amount = machine.make_decision(community_cards, 100, 20)
        decisions.append(action)
        print(f"   Tentativa {i+1}: {action.upper()}" + (f" (valor: {amount})" if amount > 0 else ""))

    fold_count = decisions.count('fold')
    call_count = decisions.count('call')
    raise_count = decisions.count('raise')

    print(f"\n   Estatísticas: {raise_count} raises, {call_count} calls, {fold_count} folds")
    print(f"   ✓ Esperado: Maioria folds (mão fraca + aposta alta)")

    # Cenário 3: Mão média com draw
    print("\n📍 CENÁRIO 3: Flush Draw (4 cartas do mesmo naipe)")
    print("-" * 70)
    machine.hand = [
        Card('A', 'Hearts'),
        Card('K', 'Hearts')
    ]
    community_cards = [
        Card('Q', 'Hearts'),
        Card('J', 'Hearts'),
        Card('7', 'Clubs')
    ]

    decisions = []
    for i in range(5):
        action, amount = machine.make_decision(community_cards, 50, 20, 100)
        decisions.append(action)
        print(f"   Tentativa {i+1}: {action.upper()}" + (f" (valor: {amount})" if amount > 0 else ""))

    fold_count = decisions.count('fold')
    call_count = decisions.count('call')
    raise_count = decisions.count('raise')

    print(f"\n   Estatísticas: {raise_count} raises, {call_count} calls, {fold_count} folds")
    print(f"   ✓ Esperado: Mix de calls e raises (draw forte)")

    # Cenário 4: Full House (monstro)
    print("\n📍 CENÁRIO 4: Full House (Mão Monstro)")
    print("-" * 70)
    machine.hand = [
        Card('K', 'Hearts'),
        Card('K', 'Diamonds')
    ]
    community_cards = [
        Card('K', 'Spades'),
        Card('7', 'Hearts'),
        Card('7', 'Clubs'),
        Card('2', 'Diamonds'),
        Card('3', 'Spades')
    ]

    decisions = []
    for i in range(5):
        action, amount = machine.make_decision(community_cards, 50, 20, 100)
        decisions.append(action)
        print(f"   Tentativa {i+1}: {action.upper()}" + (f" (valor: {amount})" if amount > 0 else ""))

    fold_count = decisions.count('fold')
    call_count = decisions.count('call')
    raise_count = decisions.count('raise')

    print(f"\n   Estatísticas: {raise_count} raises, {call_count} calls, {fold_count} folds")
    print(f"   ✓ Esperado: Maioria raises, alguns calls (slow play)")

    # Cenário 5: Aposta muito alta vs mão média
    print("\n📍 CENÁRIO 5: Aposta Muito Alta (80% do stack) vs Mão Média")
    print("-" * 70)
    machine.hand = [
        Card('J', 'Hearts'),
        Card('10', 'Spades')
    ]
    community_cards = [
        Card('9', 'Hearts'),
        Card('8', 'Clubs'),
        Card('2', 'Diamonds')
    ]

    decisions = []
    for i in range(5):
        action, amount = machine.make_decision(community_cards, 800, 20, 100)  # 80% do stack, pot=100
        decisions.append(action)
        print(f"   Tentativa {i+1}: {action.upper()}" + (f" (valor: {amount})" if amount > 0 else ""))

    fold_count = decisions.count('fold')
    call_count = decisions.count('call')
    raise_count = decisions.count('raise')

    print(f"\n   Estatísticas: {raise_count} raises, {call_count} calls, {fold_count} folds")
    print(f"   ✓ Esperado: Maioria folds (aposta muito alta para draw)")

    print("\n" + "=" * 70)
    print("✅ TESTE CONCLUÍDO - Verifique se o comportamento está coerente")
    print("=" * 70)
    print("\n💡 DICA: Compare com a versão antiga que SEMPRE dava call!")
    print("💡 Agora a IA toma decisões estratégicas baseadas no contexto.\n")

if __name__ == "__main__":
    test_ai_decisions()
