#!/usr/bin/env python3
"""
Teste da estratégia de raise variável
Demonstra como o sizing muda baseado em contexto
"""

from player import Player
from card import Card


def test_raise_sizing():
    """Testa o sizing de raise em diferentes situações"""

    print("=" * 80)
    print("🎯 TESTE DE ESTRATÉGIA DE RAISE VARIÁVEL")
    print("=" * 80)

    # Criar jogador máquina
    machine = Player("IA", is_machine=True)
    machine.chips = 1000
    machine.position = "late"

    # === CENÁRIO 1: Mão Premium Pré-Flop ===
    print("\n📍 CENÁRIO 1: Mão Premium Pré-Flop (A♠A♥)")
    print("-" * 80)
    machine.hand = [Card('A', 'Spades'), Card('A', 'Hearts')]
    community = []

    print(f"   Pot: 100 | Current Bet: 20 | Min Raise: 20")
    raise_amounts = []
    for i in range(5):
        size = machine.calculate_raise_size(community, 20, 20, 100)
        raise_amounts.append(size)
        print(f"   Tentativa {i+1}: Raise para {size} fichas ({(size/100)*100:.0f}% do pot)")

    avg = sum(raise_amounts) / len(raise_amounts)
    print(f"\n   ✓ Média: {avg:.0f} fichas ({(avg/100)*100:.0f}% do pot)")
    print(f"   ✓ Esperado: 75-130% do pot (mão forte + pré-flop)")

    # === CENÁRIO 2: Flush Completo no Flop ===
    print("\n📍 CENÁRIO 2: Flush Completo no Flop (Mão Muito Forte)")
    print("-" * 80)
    machine.hand = [Card('A', 'Hearts'), Card('K', 'Hearts')]
    community = [
        Card('Q', 'Hearts'),
        Card('J', 'Hearts'),
        Card('9', 'Hearts')
    ]

    print(f"   Pot: 200 | Current Bet: 50 | Min Raise: 50")
    raise_amounts = []
    for i in range(5):
        size = machine.calculate_raise_size(community, 50, 50, 200)
        raise_amounts.append(size)
        pot_percent = ((size - 50) / 200) * 100
        print(f"   Tentativa {i+1}: Raise para {size} fichas (raise de {size-50}, {pot_percent:.0f}% do pot)")

    avg = sum(raise_amounts) / len(raise_amounts)
    avg_raise = avg - 50
    print(f"\n   ✓ Média do raise: {avg_raise:.0f} fichas ({(avg_raise/200)*100:.0f}% do pot)")
    print(f"   ✓ Esperado: 75-100% do pot (proteger mão forte)")

    # === CENÁRIO 3: Draw no Flop (Mesa Wet) ===
    print("\n📍 CENÁRIO 3: Flush Draw no Flop (Mesa Very Wet)")
    print("-" * 80)
    machine.hand = [Card('A', 'Hearts'), Card('K', 'Hearts')]
    community = [
        Card('Q', 'Hearts'),
        Card('J', 'Hearts'),
        Card('9', 'Spades')  # 4 cartas do mesmo naipe
    ]

    print(f"   Pot: 150 | Current Bet: 30 | Min Raise: 30")
    raise_amounts = []
    for i in range(5):
        size = machine.calculate_raise_size(community, 30, 30, 150)
        raise_amounts.append(size)
        pot_percent = ((size - 30) / 150) * 100
        print(f"   Tentativa {i+1}: Raise para {size} fichas (raise de {size-30}, {pot_percent:.0f}% do pot)")

    avg = sum(raise_amounts) / len(raise_amounts)
    avg_raise = avg - 30
    print(f"\n   ✓ Média do raise: {avg_raise:.0f} fichas ({(avg_raise/150)*100:.0f}% do pot)")
    print(f"   ✓ Esperado: 50-90% do pot (semi-bluff agressivo)")

    # === CENÁRIO 4: Par Médio em Mesa Seca ===
    print("\n📍 CENÁRIO 4: Par Médio em Mesa Seca")
    print("-" * 80)
    machine.hand = [Card('9', 'Hearts'), Card('9', 'Diamonds')]
    community = [
        Card('K', 'Spades'),
        Card('7', 'Clubs'),
        Card('2', 'Hearts')
    ]

    print(f"   Pot: 120 | Current Bet: 25 | Min Raise: 25")
    raise_amounts = []
    for i in range(5):
        size = machine.calculate_raise_size(community, 25, 25, 120)
        raise_amounts.append(size)
        pot_percent = ((size - 25) / 120) * 100
        print(f"   Tentativa {i+1}: Raise para {size} fichas (raise de {size-25}, {pot_percent:.0f}% do pot)")

    avg = sum(raise_amounts) / len(raise_amounts)
    avg_raise = avg - 25
    print(f"\n   ✓ Média do raise: {avg_raise:.0f} fichas ({(avg_raise/120)*100:.0f}% do pot)")
    print(f"   ✓ Esperado: 30-50% do pot (mão média, mesa seca)")

    # === CENÁRIO 5: Bluff no River (Mesa Paired) ===
    print("\n📍 CENÁRIO 5: Bluff Potencial no River (Mão Fraca, Mesa Pareada)")
    print("-" * 80)
    machine.hand = [Card('7', 'Hearts'), Card('6', 'Diamonds')]
    community = [
        Card('A', 'Spades'),
        Card('A', 'Clubs'),
        Card('K', 'Hearts'),
        Card('Q', 'Diamonds'),
        Card('2', 'Spades')
    ]

    print(f"   Pot: 300 | Current Bet: 50 | Min Raise: 50")
    raise_amounts = []
    for i in range(5):
        size = machine.calculate_raise_size(community, 50, 50, 300)
        raise_amounts.append(size)
        pot_percent = ((size - 50) / 300) * 100
        print(f"   Tentativa {i+1}: Raise para {size} fichas (raise de {size-50}, {pot_percent:.0f}% do pot)")

    avg = sum(raise_amounts) / len(raise_amounts)
    avg_raise = avg - 50
    print(f"\n   ✓ Média do raise: {avg_raise:.0f} fichas ({(avg_raise/300)*100:.0f}% do pot)")
    print(f"   ✓ Esperado: 20-70% do pot (bluff sizing, 15% chance de overbet)")

    # === CENÁRIO 6: Short Stack com Mão Boa ===
    print("\n📍 CENÁRIO 6: Short Stack (250 fichas) com Mão Boa")
    print("-" * 80)
    machine.chips = 250  # Short stack
    machine.hand = [Card('Q', 'Hearts'), Card('Q', 'Diamonds')]
    community = [
        Card('J', 'Spades'),
        Card('9', 'Clubs'),
        Card('2', 'Hearts')
    ]

    print(f"   Pot: 100 | Current Bet: 30 | Min Raise: 30 | Stack: 250")
    raise_amounts = []
    allin_count = 0
    for i in range(10):  # Mais tentativas para ver all-ins
        size = machine.calculate_raise_size(community, 30, 30, 100)
        raise_amounts.append(size)
        is_allin = size == machine.chips
        if is_allin:
            allin_count += 1
        status = " ⚠️ ALL-IN" if is_allin else ""
        print(f"   Tentativa {i+1}: Raise para {size} fichas{status}")

    print(f"\n   ✓ All-ins: {allin_count}/10 ({(allin_count/10)*100:.0f}%)")
    print(f"   ✓ Esperado: Alta frequência de all-in (short stack + mão boa)")

    # === CENÁRIO 7: Big Stack com Nuts no River ===
    print("\n📍 CENÁRIO 7: Big Stack (2500 fichas) com Nuts no River")
    print("-" * 80)
    machine.chips = 2500  # Big stack
    machine.hand = [Card('A', 'Spades'), Card('K', 'Spades')]
    community = [
        Card('Q', 'Spades'),
        Card('J', 'Spades'),
        Card('10', 'Spades'),
        Card('5', 'Hearts'),
        Card('2', 'Clubs')
    ]

    print(f"   Pot: 400 | Current Bet: 80 | Min Raise: 80 | Stack: 2500")
    raise_amounts = []
    overbet_count = 0
    for i in range(10):
        size = machine.calculate_raise_size(community, 80, 80, 400)
        raise_amounts.append(size)
        raise_size = size - 80
        is_overbet = raise_size > 400
        if is_overbet:
            overbet_count += 1
        status = " 🔥 OVERBET" if is_overbet else ""
        pot_percent = (raise_size / 400) * 100
        print(f"   Tentativa {i+1}: Raise para {size} (raise de {raise_size}, {pot_percent:.0f}% pot){status}")

    avg = sum(raise_amounts) / len(raise_amounts)
    avg_raise = avg - 80
    print(f"\n   ✓ Média do raise: {avg_raise:.0f} fichas ({(avg_raise/400)*100:.0f}% do pot)")
    print(f"   ✓ Overbets: {overbet_count}/10 ({(overbet_count/10)*100:.0f}%)")
    print(f"   ✓ Esperado: 90-120% do pot, alguns overbets (nuts + river)")

    # === RESUMO ===
    print("\n" + "=" * 80)
    print("✅ TESTE CONCLUÍDO")
    print("=" * 80)
    print("\n📊 CARACTERÍSTICAS DA ESTRATÉGIA DE RAISE VARIÁVEL:")
    print("   • Sizing baseado em força da mão (0.8+: 75-100%, 0.6-0.8: 50-75%, etc)")
    print("   • Pré-flop: +30% sizing (reduz campo)")
    print("   • Turn: +10% sizing (menos cartas por vir)")
    print("   • River com nuts: +20% sizing (value bet)")
    print("   • Mesa wet: +20% com mãos fortes (proteção)")
    print("   • Mesa dry: -15% em bluffs (mais barato)")
    print("   • Late position: -5% sizing (vantagem posicional)")
    print("   • Short stack (<30%): 2x multiplier + all-in frequente")
    print("   • Big stack (>200%): +15% sizing (pressure)")
    print("   • Bluff ocasional (15%) com sizing de value bet")
    print("   • All-in estratégico em situações específicas")
    print("\n💡 Agora a IA varia o raise de 25% a 150%+ do pot conforme contexto!")
    print("💡 Muito mais imprevisível e estratégica que o min-raise fixo anterior.\n")


if __name__ == "__main__":
    test_raise_sizing()
