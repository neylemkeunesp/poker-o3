#!/usr/bin/env python3
"""
Script para testar estratégias de máquinas competindo entre si no jogo de Poker Hold'em.
"""

import random
from poker_app import Player, Game

def run_machine_vs_machine_test(num_games=100):
    """
    Executa um teste de estratégia entre duas máquinas por um número específico de jogos.
    """
    print("\n" + "="*50)
    print("     TESTE DE ESTRATÉGIA MÁQUINA VS MÁQUINA")
    print("="*50)
    
    machine1 = Player("Máquina 1", is_machine=True)
    machine2 = Player("Máquina 2", is_machine=True)
    
    stats = {
        "Máquina 1": {"vitórias": 0, "chips_ganhos": 0},
        "Máquina 2": {"vitórias": 0, "chips_ganhos": 0}
    }
    
    for jogo_num in range(1, num_games + 1):
        print(f"\n📊 Progresso: Jogo {jogo_num}/{num_games}")
        print(f"💰 Chips - Máquina 1: {machine1.chips}, Máquina 2: {machine2.chips}")
        
        # Resetar chips para cada novo jogo para manter consistência
        machine1.chips = 1000
        machine2.chips = 1000
        
        game = Game()
        game.play_machine_vs_machine(1)  # Play one game at a time
        
        # Get the machines from the game since it creates its own
        game_machine1 = next(p for p in [game.player1, game.player2] if p.name == "Máquina 1")
        game_machine2 = next(p for p in [game.player1, game.player2] if p.name == "Máquina 2")
        
        # Registrar estatísticas
        if game_machine1.chips > game_machine2.chips:
            stats["Máquina 1"]["vitórias"] += 1
            stats["Máquina 1"]["chips_ganhos"] += (game_machine1.chips - 1000)
        else:
            stats["Máquina 2"]["vitórias"] += 1
            stats["Máquina 2"]["chips_ganhos"] += (game_machine2.chips - 1000)
    
    # Exibir resultados finais
    print("\n" + "="*50)
    print("           RESULTADOS DO TESTE")
    print("="*50)
    
    for maquina, resultados in stats.items():
        taxa_vitoria = (resultados["vitórias"] / num_games) * 100
        media_chips = resultados["chips_ganhos"] / num_games
        print(f"\n► {maquina}:")
        print(f"  Vitórias: {resultados['vitórias']} ({taxa_vitoria:.1f}%)")
        print(f"  Média de chips ganhos por jogo: {media_chips:.1f}")

if __name__ == "__main__":
    try:
        num_games_input = input("Digite o número de jogos para testar (recomendado: 100): ")
        num_games = int(num_games_input)
        run_machine_vs_machine_test(num_games)
    except ValueError:
        print("❌ Entrada inválida! Por favor, insira um número inteiro.")
    except KeyboardInterrupt:
        print("\n❌ Teste interrompido pelo usuário.")
