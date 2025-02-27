#!/usr/bin/env python3
from deck import Deck
from player import Player
from poker_game import PokerGame
from typing import List

class Game:
    """Legacy class for machine vs machine games"""
    def __init__(self):
        self.deck = Deck()
        self.community_cards = []
        self.pot = 0
        self.current_bet = 0
        self.min_raise = 20
        
    def play_machine_vs_machine(self, num_games: int):
        self.player1 = Player("Máquina 1", is_machine=True)
        self.player2 = Player("Máquina 2", is_machine=True)
        
        for game in range(num_games):
            print(f"\n=== Jogo {game + 1} de {num_games} ===")
            
            # Create a PokerGame instance for this round
            poker_game = PokerGame([self.player1, self.player2])
            
            # Deal cards
            poker_game.deal_cards()
            
            # Set positions
            self.player1.position = "early"
            self.player2.position = "late"
            
            # Pre-flop
            print("\n=== Pré-Flop ===")
            self._betting_round([self.player1, self.player2])
            
            if not self.player1.folded and not self.player2.folded:
                # Flop
                print("\n=== Flop ===")
                poker_game.deal_community_cards(3)
                self.community_cards = poker_game.community_cards
                self._betting_round([self.player1, self.player2])
            
            if not self.player1.folded and not self.player2.folded:
                # Turn
                print("\n=== Turn ===")
                poker_game.deal_community_cards(1)
                self.community_cards = poker_game.community_cards
                self._betting_round([self.player1, self.player2])
            
            if not self.player1.folded and not self.player2.folded:
                # River
                print("\n=== River ===")
                poker_game.deal_community_cards(1)
                self.community_cards = poker_game.community_cards
                self._betting_round([self.player1, self.player2])
            
            # Showdown
            self._showdown([self.player1, self.player2])
            
            # Save Q-tables
            self.player1.save_q_table()
            self.player2.save_q_table()
    
    def _betting_round(self, players: List[Player]):
        self.current_bet = 0
        for player in players:
            if not player.folded:
                action, amount = player.make_decision(self.community_cards, self.current_bet, self.min_raise)
                if action == "raise":
                    self.current_bet = amount
                self.pot += amount
    
    def _showdown(self, players: List[Player]):
        active_players = [p for p in players if not p.folded]
        
        if not active_players:
            print("\n❌ Todos os jogadores desistiram!")
            return
        
        if len(active_players) == 1:
            winner = active_players[0]
            print(f"\n🏆 {winner.name} vence o pote de {self.pot} chips!")
            winner.chips += self.pot
            return
        
        # Compare hands
        hand_values = [(p, p.get_hand_value(self.community_cards)) for p in active_players]
        if hand_values:  # Only proceed if there are hands to compare
            best_value = max(hand_values, key=lambda x: x[1][1])
            winners = [p for p, v in hand_values if v[1] == best_value[1][1]]
        
        # Award the pot and ensure total chips remain 2000
        if len(winners) == 1:
            winner = winners[0]
            print(f"\n🏆 {winner.name} vence {self.pot} chips com {best_value[1][0]}!")
            winner.chips += self.pot

            # Ensure total chips remain 2000
            other_players = [p for p in players if p != winner]
            if not other_players:
                print("\n⚠️  Não há outro jogador para transferir fichas.")
                return
            other_player = other_players[0]

            # Calculate how many chips the winner has over 1000
            excess_chips = winner.chips - 1000

            # If the winner has more than 1000 chips, transfer the excess to the other player
            if excess_chips > 0 and other_player.chips < 1000:
                transfer_amount = min(excess_chips, 1000 - other_player.chips)
                winner.chips -= transfer_amount
                other_player.chips += transfer_amount
                print(f"\n⚖️  {transfer_amount} chips transferidos de {winner.name} para {other_player.name} para manter o total de 2000.")
            else:
                print("\ni️  Nenhuma transferência de fichas necessária.")
        else:
            # Split pot among winners
            split_amount = self.pot // len(winners)
            for winner in winners:
                print(f"\n🏆 {winner.name} vence {split_amount} chips com {best_value[1][0]}!")
                winner.chips += split_amount

            # Ensure total chips remain 2000 after split
            for winner in winners:
                excess_chips = winner.chips - 1000
                if excess_chips > 0:
                    # Distribute excess chips among other players (excluding winners)
                    remaining_players = [p for p in players if p not in winners]
                    if remaining_players:
                        transfer_amount = min(excess_chips, 1000 - remaining_players[0].chips)
                        winner.chips -= transfer_amount
                        remaining_players[0].chips += transfer_amount
                        print(f"\n⚖️  {transfer_amount} chips transferidos de {winner.name} para {remaining_players[0].name} para manter o total de 2000.")
                    else:
                        # If no other players, return chips to the pot (shouldn't happen)
                        self.pot += excess_chips
                        winner.chips -= excess_chips
                        print(f"\n⚠️  {excess_chips} chips retornados ao pote de {winner.name} (situação inesperada).")
                else:
                    print("\ni️  Nenhuma transferência de fichas necessária.")

def main():
    print("Bem-vindo ao Poker Texas Hold'em!")
    print("\nEscolha o modo de jogo:")
    print("1. Humano vs Máquina")
    print("2. Máquina vs Máquina")
    
    mode = input("\nDigite sua escolha (1-2): ")
    
    game = Game()
    
    if mode == "2":
        num_games = int(input("\nQuantos jogos simular? "))
        game.play_machine_vs_machine(num_games)
    else:
        print("Modo não implementado ainda.")

if __name__ == "__main__":
    main()
