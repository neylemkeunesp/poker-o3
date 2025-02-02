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
        
        # Inicia novo jogo
        self.new_game()

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
        
        # Frame para controles
        self.control_frame = ttk.Frame(self.main_container)
        self.control_frame.pack(pady=5, fill='x', side='bottom')

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
            text="Novo Jogo",
            command=self.new_game,
            width=15
        )
        self.new_game_button.pack(side='left', padx=5)

    def new_game(self):
        # Reset player states
        self.player.hand = []
        self.player.chips = 1000
        self.player.folded = False
        self.machine.hand = []
        self.machine.chips = 1000
        self.machine.folded = False
        
        # Initialize new game
        self.game = PokerGame([self.player, self.machine])
        self.current_bet = 50
        
        # Deal initial cards
        self.game.deal_cards()
        
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
        
        # Ação da máquina
        self.machine_action()
        
        self.update_display()
        self.check_game_state()

    def raise_action(self):
        raise_amount = self.current_bet + self.game.min_raise
        if raise_amount <= self.player.chips:
            self.player.chips -= raise_amount
            self.game.pot += raise_amount
            self.current_bet = raise_amount
            
            # Ação da máquina
            self.machine_action()
            
            self.update_display()
            self.check_game_state()
        else:
            messagebox.showwarning("Aviso", "Chips insuficientes para raise!")

    def fold_action(self):
        self.player.folded = True
        self.end_game("Máquina")

    def machine_action(self):
        try:
            hand_type, value = self.machine.get_hand_value(self.game.community_cards)
            
            # Probabilidade de continuar baseada no valor da mão
            prob_table = {
                "Quadra": 0.95,
                "Full House": 0.9,
                "Flush": 0.85,
                "Sequência": 0.8,
                "Trinca": 0.75,
                "Dois Pares": 0.7,
                "Par": 0.6,
                "Carta Alta": 0.3
            }
            
            prob = prob_table.get(hand_type, 0.3)
            
            # No início do jogo, maior chance de continuar
            if not self.game.community_cards:
                prob = max(prob, 0.7)
            
            if random.random() < prob:
                # Call
                bet_amount = min(self.current_bet, self.machine.chips)
                self.machine.chips -= bet_amount
                self.game.pot += bet_amount
                messagebox.showinfo("Ação da Máquina", "Máquina: Call")
            else:
                # Fold
                self.machine.folded = True
                self.end_game("Jogador 1")
        except ValueError:
            # Se não houver cartas para avaliar, sempre call no início
            bet_amount = min(self.current_bet, self.machine.chips)
            self.machine.chips -= bet_amount
            self.game.pot += bet_amount
            messagebox.showinfo("Ação da Máquina", "Máquina: Call")

    def check_game_state(self):
        # Verifica se é hora de revelar novas cartas comunitárias
        if len(self.game.community_cards) == 0:
            self.game.deal_community_cards(3)  # Flop
        elif len(self.game.community_cards) == 3:
            self.game.deal_community_cards(1)  # Turn
        elif len(self.game.community_cards) == 4:
            self.game.deal_community_cards(1)  # River
            self.end_game()
        
        self.update_display()

    def end_game(self, winner_by_fold=None):
        if winner_by_fold:
            winner_name = winner_by_fold
            messagebox.showinfo("Fim do Jogo", f"{winner_name} vence por desistência!")
        else:
            # Determina o vencedor baseado nas mãos
            player_type, player_value = self.player.get_hand_value(self.game.community_cards)
            machine_type, machine_value = self.machine.get_hand_value(self.game.community_cards)
            
            result = f"Jogador 1 tem {player_type}\nMáquina tem {machine_type}\n\n"
            
            if player_value > machine_value:
                winner_name = "Jogador 1"
                self.player.chips += self.game.pot
            else:
                winner_name = "Máquina"
                self.machine.chips += self.game.pot
            
            result += f"{winner_name} vence!"
            messagebox.showinfo("Fim do Jogo", result)
        
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
        
        # Desabilita os botões de ação
        self.disable_buttons()
        
        # Mostra o ranking
        with open("ranking.json", "r") as f:
            rankings = json.load(f)
        ranking_text = "Ranking:\n" + "\n".join(f"{name}: {wins}" for name, wins in rankings.items())
        messagebox.showinfo("Ranking", ranking_text)

    def enable_buttons(self):
        self.call_button.config(state='normal')
        self.raise_button.config(state='normal')
        self.fold_button.config(state='normal')

    def disable_buttons(self):
        self.call_button.config(state='disabled')
        self.raise_button.config(state='disabled')
        self.fold_button.config(state='disabled')

if __name__ == "__main__":
    root = tk.Tk()
    app = PokerGUI(root)
    root.mainloop()
