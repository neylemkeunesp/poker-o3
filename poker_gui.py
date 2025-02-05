#!/usr/bin/env python3
import tkinter as tk
from tkinter import ttk, messagebox
import json
import random
from poker_app import Card, Deck, Player, PokerGame, HistoryManager, RankingManager
from card_graphics import CardGraphics

class PokerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Taxas Hold'em Poker")
        self.root.geometry("1024x800")  # Increased height for better fit
        self.root.configure(bg='#1a472a')  # Verde escuro para tema de poker
        
        # Initialize card graphics
        self.card_graphics = CardGraphics()
        self.card_back = self.card_graphics.get_card_back()
        
        # Configuração do estilo
        style = ttk.Style()
        style.configure('TFrame', background='#1a472a')
        style.configure('TLabel', background='#1a472a', foreground='white', anchor='center')
        style.configure('TButton', padding=5)
        
        # Container principal
        self.main_container = ttk.Frame(self.root)
        self.main_container.pack(expand=True, fill='both', padx=20, pady=10)
        
        # Frames principais
        self.setup_frames()
        
        # Componentes da interface
        self.setup_components()
        
        # Inicialização do jogo
        self.player = Player("Jogador 1")
        self.machine = Player("Máquina", is_machine=True)
        self.game = None
        self.current_bet = 50
        
        # Session tracking
        self.hands_played = 0
        self.player_wins = 0
        self.machine_wins = 0
        self.current_streak = 0  # positive for player streak, negative for machine streak
        self.target_chips = 5000  # Win condition
        self.starting_chips = 1000
        
        # Start new session
        self.start_new_session()

    def setup_frames(self):
        # Frame superior para cartas comunitárias
        self.community_frame = ttk.Frame(self.main_container)
        self.community_frame.pack(pady=10, fill='x')
        
        # Frame para imagens das cartas comunitárias
        self.community_cards_frame = ttk.Frame(self.community_frame)
        self.community_cards_frame.pack(pady=10)
        
        # Labels para imagens das cartas comunitárias
        self.community_card_labels = []
        for i in range(5):
            label = ttk.Label(self.community_cards_frame)
            label.pack(side='left', padx=5)
            self.community_card_labels.append(label)
        
        # Frame central para cartas do oponente
        self.opponent_frame = ttk.Frame(self.main_container)
        self.opponent_frame.pack(pady=10, fill='x')
        
        # Frame para imagens das cartas do oponente
        self.opponent_cards_frame = ttk.Frame(self.opponent_frame)
        self.opponent_cards_frame.pack(pady=10)
        
        # Labels para imagens das cartas do oponente
        self.opponent_card_labels = []
        for i in range(2):
            label = ttk.Label(self.opponent_cards_frame)
            label.pack(side='left', padx=5)
            self.opponent_card_labels.append(label)
        
        # Frame para informações do jogo
        self.info_frame = ttk.Frame(self.main_container)
        self.info_frame.pack(pady=10, fill='x')
        
        # Frame para cartas do jogador
        self.player_frame = ttk.Frame(self.main_container)
        self.player_frame.pack(pady=10, fill='x')
        
        # Frame para imagens das cartas do jogador
        self.player_cards_frame = ttk.Frame(self.player_frame)
        self.player_cards_frame.pack(pady=10)
        
        # Labels para imagens das cartas do jogador
        self.player_card_labels = []
        for i in range(2):
            label = ttk.Label(self.player_cards_frame)
            label.pack(side='left', padx=5)
            self.player_card_labels.append(label)
        
        # Frame para log do jogo
        self.log_frame = ttk.Frame(self.main_container)
        self.log_frame.pack(pady=10, fill='both', expand=True)
        
        # Text widget para log
        self.log_text = tk.Text(self.log_frame, height=6, bg='#0f2819', fg='white', wrap=tk.WORD)
        self.log_text.pack(fill='both', expand=True, padx=10)
        
        # Frame para controles
        self.control_frame = ttk.Frame(self.main_container)
        self.control_frame.pack(pady=5, fill='x', side='bottom')

    def log_message(self, message):
        """Add a message to the game log"""
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)  # Scroll to bottom
        self.root.update()

    def setup_components(self):
        # Labels para cartas comunitárias
        self.community_label = ttk.Label(
            self.community_frame,
            text="Cartas Comunitárias",
            font=('Arial', 14, 'bold')
        )
        self.community_label.pack(anchor='center')
        
        # Labels para cartas do oponente
        self.opponent_label = ttk.Label(
            self.opponent_frame,
            text="Máquina",
            font=('Arial', 14, 'bold')
        )
        self.opponent_label.pack(anchor='center')
        
        # Labels para informações do jogo
        info_container = ttk.Frame(self.info_frame)
        info_container.pack(anchor='center')
        
        self.pot_label = ttk.Label(
            info_container,
            text="Pote: 0",
            font=('Arial', 12)
        )
        self.pot_label.pack(side='left', padx=10)
        
        self.bet_label = ttk.Label(
            info_container,
            text="Aposta Atual: 50",
            font=('Arial', 12)
        )
        self.bet_label.pack(side='left', padx=10)
        
        self.chips_label = ttk.Label(
            info_container,
            text="Seus Chips: 1000",
            font=('Arial', 12)
        )
        self.chips_label.pack(side='left', padx=10)
        
        # Labels para cartas do jogador
        self.player_label = ttk.Label(
            self.player_frame,
            text="Suas Cartas",
            font=('Arial', 14, 'bold')
        )
        self.player_label.pack(anchor='center')
        
        # Container para botões
        button_container = ttk.Frame(self.control_frame)
        button_container.pack(anchor='center', pady=5)
        
        # Botões de controle
        self.call_button = ttk.Button(
            button_container,
            text="Call",
            command=self.call_action,
            width=15
        )
        self.call_button.pack(side='left', padx=5)
        
        self.raise_button = ttk.Button(
            button_container,
            text="Raise",
            command=self.raise_action,
            width=15
        )
        self.raise_button.pack(side='left', padx=5)
        
        self.fold_button = ttk.Button(
            button_container,
            text="Fold",
            command=self.fold_action,
            width=15
        )
        self.fold_button.pack(side='left', padx=5)
        
        self.new_game_button = ttk.Button(
            button_container,
            text="Próxima Mão",
            command=self.new_hand,
            width=15
        )
        self.new_game_button.pack(side='left', padx=5)
        
        self.new_session_button = ttk.Button(
            button_container,
            text="Nova Sessão",
            command=self.start_new_session,
            width=15
        )
        self.new_session_button.pack(side='left', padx=5)

    def start_new_session(self):
        """Start a new poker session"""
        # Reset session stats
        self.hands_played = 0
        self.player_wins = 0
        self.machine_wins = 0
        self.current_streak = 0
        
        # Reset player states with starting chips
        self.player.chips = self.starting_chips
        self.machine.chips = self.starting_chips
        
        # Clear log
        self.log_text.delete(1.0, tk.END)
        
        # Log session start
        self.log_message("=== Nova Sessão de Poker ===")
        self.log_message(f"Objetivo: Alcançar {self.target_chips} chips")
        self.log_message(f"Jogador 1: {self.player.chips} chips")
        self.log_message(f"Máquina: {self.machine.chips} chips\n")
        
        # Start first hand
        self.new_hand()

    def new_hand(self):
        """Start a new hand within the current session"""
        # Reset hand states
        self.player.hand = []
        self.player.folded = False
        self.machine.hand = []
        self.machine.folded = False
        
        # Initialize new game
        self.game = PokerGame([self.player, self.machine])
        self.current_bet = 50  # Small blind + big blind
        
        # Deal initial cards
        self.game.deal_cards()
        
        # Log hand start
        self.log_message("\n=== Nova Mão ===")
        self.log_message(f"Jogador 1: {self.player.chips} chips")
        self.log_message(f"Máquina: {self.machine.chips} chips")
        
        # Update display and enable buttons
        self.update_display()
        self.enable_buttons()

    def update_display(self):
        # Atualiza cartas comunitárias
        for i, label in enumerate(self.community_card_labels):
            if i < len(self.game.community_cards):
                card = self.game.community_cards[i]
                image = self.card_graphics.get_card_image(card.rank, card.suit)
                label.configure(image=image)
                label._image = image  # Keep a reference
            else:
                label.configure(image='')
                label._image = None
        
        # Atualiza cartas do oponente
        for i, label in enumerate(self.opponent_card_labels):
            if i < len(self.machine.hand):
                # Only show machine's cards if game ended naturally (all community cards revealed) and no one folded
                if self.game and len(self.game.community_cards) == 5 and not any(p.folded for p in self.game.players):
                    card = self.machine.hand[i]
                    image = self.card_graphics.get_card_image(card.rank, card.suit)
                else:
                    image = self.card_back
                label.configure(image=image)
                label._image = image
            else:
                label.configure(image='')
                label._image = None
        
        # Atualiza informações do jogo
        self.pot_label.config(text=f"Pote: {self.game.pot}")
        self.bet_label.config(text=f"Aposta Atual: {self.current_bet}")
        self.chips_label.config(text=f"Seus Chips: {self.player.chips}")
        
        # Atualiza cartas do jogador
        for i, label in enumerate(self.player_card_labels):
            if i < len(self.player.hand):
                card = self.player.hand[i]
                image = self.card_graphics.get_card_image(card.rank, card.suit)
                label.configure(image=image)
                label._image = image
            else:
                label.configure(image='')
                label._image = None

    def call_action(self):
        bet_amount = min(self.current_bet, self.player.chips)
        self.player.chips -= bet_amount
        self.game.pot += bet_amount
        
        self.log_message(f"Jogador: Call {bet_amount}")
        
        # Update game state before machine action
        self.update_display()
        
        # Ação da máquina
        self.machine_action()
        
        # Check if machine folded
        if self.machine.folded:
            self.end_hand("Jogador 1")
            return
            
        self.update_display()
        self.check_game_state()

    def raise_action(self):
        raise_amount = self.current_bet + self.game.min_raise
        if raise_amount <= self.player.chips:
            self.player.chips -= raise_amount
            self.game.pot += raise_amount
            self.current_bet = raise_amount
            
            self.log_message(f"Jogador: Raise para {raise_amount}")
            
            # Update game state before machine action
            self.update_display()
            
            # Ação da máquina
            self.machine_action()
            
            # Check if machine folded
            if self.machine.folded:
                self.end_hand("Jogador 1")
                return
                
            self.update_display()
            self.check_game_state()
        else:
            self.log_message("⚠️ Chips insuficientes para raise!")

    def fold_action(self):
        self.player.folded = True
        self.log_message("Jogador: Fold")
        self.end_hand("Máquina")
        self.disable_buttons()

    def machine_action(self):
        action, amount = self.machine.make_decision(self.game.community_cards, self.current_bet, self.game.min_raise)
        
        if action == "fold":
            self.machine.folded = True
            self.log_message("Máquina: Fold")
            return
        elif action == "raise":
            self.machine.chips -= amount
            self.game.pot += amount
            self.current_bet = amount
            self.log_message(f"Máquina: Raise para {amount}")
        else:  # call
            bet_amount = min(self.current_bet, self.machine.chips)
            self.machine.chips -= bet_amount
            self.game.pot += bet_amount
            self.log_message(f"Máquina: Call {bet_amount}")

    def check_game_state(self):
        # Only proceed if both players have acted
        if self.player.folded or self.machine.folded:
            return
            
        # Verifica se é hora de revelar novas cartas comunitárias
        if len(self.game.community_cards) == 0:
            self.game.deal_community_cards(3)  # Flop
            self.log_message("\n=== Flop ===")
            self.current_bet = self.game.min_raise  # Reset bet for new round
        elif len(self.game.community_cards) == 3:
            self.game.deal_community_cards(1)  # Turn
            self.log_message("\n=== Turn ===")
            self.current_bet = self.game.min_raise  # Reset bet for new round
        elif len(self.game.community_cards) == 4:
            self.game.deal_community_cards(1)  # River
            self.log_message("\n=== River ===")
            self.current_bet = self.game.min_raise  # Reset bet for new round
            self.end_hand()
        
        self.update_display()

    def end_hand(self, winner_by_fold=None):
        """End the current hand and update session stats"""
        if winner_by_fold:
            winner_name = winner_by_fold
            self.log_message(f"\n🏆 {winner_name} vence por desistência!")
        else:
            # Determina o vencedor baseado nas mãos
            player_type, player_value = self.player.get_hand_value(self.game.community_cards)
            machine_type, machine_value = self.machine.get_hand_value(self.game.community_cards)
            
            result = f"\nJogador 1 tem {player_type}\nMáquina tem {machine_type}\n"
            
            if player_value > machine_value:
                winner_name = "Jogador 1"
                self.player.chips += self.game.pot
            else:
                winner_name = "Máquina"
                self.machine.chips += self.game.pot
            
            result += f"🏆 {winner_name} vence!"
            self.log_message(result)
        
        # Update session stats
        self.hands_played += 1
        if winner_name == "Jogador 1":
            self.player_wins += 1
            self.current_streak = max(1, self.current_streak + 1)
        else:
            self.machine_wins += 1
            self.current_streak = min(-1, self.current_streak - 1)
        
        # Registra o resultado
        self.game.history_manager.record_game({
            "winner": winner_name,
            "pot": self.game.pot,
            "community_cards": self.game.show_community_cards(),
            "player_hand": self.player.show_hand(),
            "machine_hand": self.machine.show_hand()
        })
        
        # Atualiza o ranking
        self.game.ranking_manager.update_ranking(winner_name)
        
        # Show session stats
        self.log_message(f"\n=== Estatísticas da Sessão ===")
        self.log_message(f"Mãos jogadas: {self.hands_played}")
        self.log_message(f"Vitórias do Jogador: {self.player_wins}")
        self.log_message(f"Vitórias da Máquina: {self.machine_wins}")
        streak_owner = "Jogador" if self.current_streak > 0 else "Máquina"
        streak_count = abs(self.current_streak)
        if streak_count > 1:
            self.log_message(f"🔥 {streak_owner} está em uma sequência de {streak_count} vitórias!")
        
        # Show chips
        self.log_message(f"\nJogador 1: {self.player.chips} chips")
        self.log_message(f"Máquina: {self.machine.chips} chips")
        
        # Check if session should end
        if self.player.chips <= 0:
            self.log_message("\n🏆 Máquina vence a sessão! Jogador ficou sem chips.")
            self.disable_all_buttons()
            return
        elif self.machine.chips <= 0:
            self.log_message("\n🏆 Jogador vence a sessão! Máquina ficou sem chips.")
            self.disable_all_buttons()
            return
        elif self.player.chips >= self.target_chips:
            self.log_message(f"\n🏆 Jogador vence a sessão! Alcançou {self.target_chips} chips!")
            self.disable_all_buttons()
            return
        elif self.machine.chips >= self.target_chips:
            self.log_message(f"\n🏆 Máquina vence a sessão! Alcançou {self.target_chips} chips!")
            self.disable_all_buttons()
            return
        
        # Continue to next hand
        self.log_message("\nPressione 'Próxima Mão' para continuar")
        self.new_game_button.config(state='normal')
        self.call_button.config(state='disabled')
        self.raise_button.config(state='disabled')
        self.fold_button.config(state='disabled')

    def enable_buttons(self):
        self.call_button.config(state='normal')
        self.raise_button.config(state='normal')
        self.fold_button.config(state='normal')
        self.new_game_button.config(state='disabled')

    def disable_buttons(self):
        self.call_button.config(state='disabled')
        self.raise_button.config(state='disabled')
        self.fold_button.config(state='disabled')

    def disable_all_buttons(self):
        self.disable_buttons()
        self.new_game_button.config(state='disabled')
        self.new_session_button.config(state='normal')

if __name__ == "__main__":
    root = tk.Tk()
    app = PokerGUI(root)
    root.mainloop()
