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
        self.root.title("Texas Hold'em Poker")
        self.root.geometry("1178x920")  # Increased size by 15% for better fit
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
        self.betting_round_complete = False  # New flag to track betting round completion
        
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
        
        # Text widget para log com estilo melhorado
        self.log_text = tk.Text(
            self.log_frame,
            height=4,  # Altura reduzida
            bg='#0a1f12',  # Verde mais escuro para melhor contraste
            fg='#e0e0e0',  # Cinza claro para melhor legibilidade
            wrap=tk.WORD,
            font=('Consolas', 10),  # Fonte monoespaçada para melhor leitura
            padx=8,  # Padding interno horizontal
            pady=5,  # Padding interno vertical
            relief='solid',  # Borda sólida
            borderwidth=1  # Borda fina
        )
        self.log_text.pack(fill='both', expand=True, padx=15, pady=5)
        
        # Configurar tags para diferentes tipos de mensagens
        self.log_text.tag_configure('header', font=('Consolas', 10, 'bold'))
        self.log_text.tag_configure('winner', foreground='#90EE90')  # Verde claro
        self.log_text.tag_configure('chips', foreground='#FFD700')   # Dourado
        
        # Frame para controles
        self.control_frame = ttk.Frame(self.main_container)
        self.control_frame.pack(pady=5, fill='x', side='bottom')

    def log_message(self, message, tag=None):
        """Add a message to the game log with optional formatting"""
        # Aplicar tags específicas baseado no conteúdo da mensagem
        if message.startswith('==='):
            self.log_text.insert(tk.END, message + "\n", 'header')
        elif '🏆' in message:
            self.log_text.insert(tk.END, message + "\n", 'winner')
        elif 'chips' in message.lower() or '💰' in message:
            self.log_text.insert(tk.END, message + "\n", 'chips')
        else:
            self.log_text.insert(tk.END, message + "\n", tag)
            
        self.log_text.see(tk.END)  # Scroll to bottom
        self.root.update()
        
    def log_chip_state(self, action):
        """Log the current state of all chips and verify conservation"""
        total = self.player.chips + self.machine.chips + self.game.pot
        message = f"\n[{action}]\n"
        message += f"Jogador: {self.player.chips} chips\n"
        message += f"Máquina: {self.machine.chips} chips\n"
        message += f"Pote: {self.game.pot} chips\n"
        message += f"Total: {total} chips"
        if total != 2000:
            message += f" ⚠️ ERRO: Total deveria ser 2000!"
        self.log_message(message)

    def setup_components(self):
        # Labels para cartas comunitárias
        self.community_label = ttk.Label(
            self.community_frame,
            text="Cartas Comunitárias",
            font=('Arial', 14, 'bold')
        )
        self.community_label.pack(anchor='center')

        # Add Stats button
        self.stats_button = ttk.Button(
            self.community_frame,
            text="Estatísticas",
            command=self.show_statistics,
            width=15
        )
        self.stats_button.pack(side='right', padx=5)
        
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
        
        # Reset player states with starting chips and statistics
        for player in [self.player, self.machine]:
            player.chips = self.starting_chips
            player.game_sequence = {
                'hands_played': 0,
                'total_chip_diff': 0,
                'win_streak': 0,
                'max_chips': self.starting_chips,
                'learning_steps': 0,
                'hand_frequencies': {
                    'Royal Flush': 0,
                    'Straight Flush': 0,
                    'Quadra': 0,
                    'Full House': 0,
                    'Flush': 0,
                    'Sequência': 0,
                    'Trinca': 0,
                    'Dois Pares': 0,
                    'Par': 0,
                    'Carta Alta': 0
                },
                'total_winnings': 0,
                'total_losses': 0,
                'best_hand': None,
                'biggest_pot_won': 0
            }
        
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
        self.betting_round_complete = False  # Reset betting round flag
        
        # Log hand start
        self.log_message("\n=== Nova Mão ===")
        self.log_message(f"Jogador 1: {self.player.chips} chips")
        self.log_message(f"Máquina: {self.machine.chips} chips")
        
        # Initialize new game
        self.game = PokerGame([self.player, self.machine])
        
        # Set up blinds
        small_blind = 25
        big_blind = 50
        
        # Log initial state
        self.log_message("\nEstado inicial da mão:")
        self.log_chip_state("Início da mão")
        
        # Post blinds and update chips
        self.player.chips -= small_blind  # Player is small blind
        self.machine.chips -= big_blind   # Machine is big blind
        self.game.pot = small_blind + big_blind
        self.current_bet = big_blind
        
        # Log state after blinds
        self.log_message("\nDepois dos blinds:")
        self.log_chip_state("Blinds postados")
        
        # Update hands played counter
        self.player.game_sequence['hands_played'] += 1
        self.machine.game_sequence['hands_played'] += 1
        
        # Update chip difference tracking
        self.player.game_sequence['total_chip_diff'] = self.player.chips - self.starting_chips
        self.machine.game_sequence['total_chip_diff'] = self.machine.chips - self.starting_chips
        
        # Update max chips tracking
        self.player.game_sequence['max_chips'] = max(self.player.game_sequence['max_chips'], self.player.chips)
        self.machine.game_sequence['max_chips'] = max(self.machine.game_sequence['max_chips'], self.machine.chips)
        
        # Log blinds
        self.log_message(f"Jogador 1 posta small blind: {small_blind}")
        self.log_message(f"Máquina posta big blind: {big_blind}")
        
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
                # Only show machine's cards if game ended naturally (all community cards revealed), betting is complete, and no one folded
                if (self.game and len(self.game.community_cards) == 5 and 
                    self.betting_round_complete and not any(p.folded for p in self.game.players)):
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
        # Log before state
        self.log_message(f"\nAntes do Call/Check:")
        self.log_chip_state("Estado Inicial")
        
        if self.current_bet > 0:
            # Calculate how much more the player needs to add to match the current bet
            player_current_bet = self.starting_chips - self.player.chips
            additional_bet = self.current_bet - player_current_bet
            
            if additional_bet > 0 and additional_bet <= self.player.chips:
                self.player.chips -= additional_bet
                self.game.pot += additional_bet
                self.log_message(f"Jogador: Call {additional_bet}")
                self.log_chip_state("Jogador Call")
        else:
            self.log_message("Jogador: Check")
            self.log_chip_state("Jogador Check")
        
        # Update game state before machine action
        self.update_display()
        
        # Ação da máquina
        self.machine_action()
        
        # Check if machine folded
        if self.machine.folded:
            self.end_hand("Jogador 1")
            return
            
        self.betting_round_complete = True  # Mark betting round as complete after both players have acted
        self.update_display()
        self.check_game_state()

    def raise_action(self):
        # Calculate total amount needed (current bet + raise)
        player_current_bet = self.starting_chips - self.player.chips
        additional_bet = self.current_bet - player_current_bet
        total_amount = additional_bet + self.game.min_raise
        
        if total_amount <= self.player.chips:
            self.player.chips -= total_amount
            self.game.pot += total_amount
            self.current_bet = self.current_bet + self.game.min_raise
            
            self.log_message(f"Jogador: Raise para {total_amount}")
            self.log_chip_state("Jogador Raise")
            
            # Update game state before machine action
            self.update_display()
            
            # Ação da máquina
            self.machine_action()
            
            # Check if machine folded
            if self.machine.folded:
                self.end_hand("Jogador 1")
                return
            
            self.betting_round_complete = True  # Mark betting round as complete after both players have acted
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
        # Store initial state
        initial_machine_chips = self.machine.chips
        initial_pot = self.game.pot
        
        # Log before state
        self.log_message(f"\nAntes do Call/Check da Máquina:")
        self.log_chip_state("Estado Inicial")
        
        action, amount = self.machine.make_decision(self.game.community_cards, self.current_bet, self.game.min_raise)
        
        if action == "fold":
            self.machine.folded = True
            self.log_message("Máquina: Fold")
            return
        elif action == "raise":
            if amount <= initial_machine_chips:  # Can afford raise
                # Calculate total amount needed (current bet + raise)
                total_amount = self.game.min_raise
                
                if total_amount <= initial_machine_chips:
                    self.machine.chips = initial_machine_chips - total_amount
                    self.game.pot = initial_pot + total_amount
                    self.current_bet = self.current_bet + self.game.min_raise
                    
                    self.log_message(f"Máquina: Raise para {total_amount}")
                    self.log_chip_state("Máquina Raise")
                    self.betting_round_complete = False  # Reset if machine raises
        else:  # call
            if self.current_bet > 0:
                # Calculate how much more the machine needs to add to match the current bet
                bet_to_call = min(self.current_bet, initial_machine_chips)
                
                if bet_to_call > 0:
                    self.machine.chips = initial_machine_chips - bet_to_call
                    self.game.pot = initial_pot + bet_to_call
                    self.log_message(f"Máquina: Call {bet_to_call}")
                    self.log_chip_state("Máquina Call")
            else:
                self.log_message("Máquina: Check")
                self.log_chip_state("Máquina Check")

    def check_game_state(self):
        # Only proceed if both players have acted
        if self.player.folded or self.machine.folded:
            return
            
        # Only proceed to next stage if betting round is complete
        if not self.betting_round_complete:
            return
            
        # Verifica se é hora de revelar novas cartas comunitárias
        if len(self.game.community_cards) == 0:
            # Log state before dealing flop
            self.log_message("\nAntes do Flop:")
            self.log_chip_state("Estado antes do Flop")
            
            self.game.deal_community_cards(3)  # Flop
            self.log_message("\n=== Flop ===")
            self.current_bet = 0  # Reset bet for new round
            self.betting_round_complete = False  # Reset for new betting round
            
            # Log state after dealing flop
            self.log_chip_state("Estado após o Flop")
        elif len(self.game.community_cards) == 3:
            # Log state before dealing turn
            self.log_message("\nAntes do Turn:")
            self.log_chip_state("Estado antes do Turn")
            
            self.game.deal_community_cards(1)  # Turn
            self.log_message("\n=== Turn ===")
            self.current_bet = 0  # Reset bet for new round
            self.betting_round_complete = False  # Reset for new betting round
            
            # Log state after dealing turn
            self.log_chip_state("Estado após o Turn")
        elif len(self.game.community_cards) == 4:
            # Log state before dealing river
            self.log_message("\nAntes do River:")
            self.log_chip_state("Estado antes do River")
            
            self.game.deal_community_cards(1)  # River
            self.log_message("\n=== River ===")
            self.current_bet = 0  # Reset bet for new round
            self.betting_round_complete = False  # Reset for new betting round
            
            # Log state after dealing river
            self.log_chip_state("Estado após o River")
        elif len(self.game.community_cards) == 5:
            self.end_hand()  # Only end hand after River betting is complete
        
        self.update_display()

    def end_hand(self, winner_by_fold=None):
        """End the current hand and update session stats"""
        print("end_hand called")
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
            else:
                winner_name = "Máquina"

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

        # Award the pot and update statistics
        print(f"\n💰 Antes do pagamento - Jogador 1: {self.player.chips}, Máquina: {self.machine.chips}, Pote: {self.game.pot}")
        if winner_name == "Jogador 1":
            pot_amount = self.game.pot
            self.player.chips += pot_amount
            self.player.game_sequence['total_winnings'] += pot_amount
            self.machine.game_sequence['total_losses'] += pot_amount
            if pot_amount > self.player.game_sequence['biggest_pot_won']:
                self.player.game_sequence['biggest_pot_won'] = pot_amount
            self.game.pot = 0  # Zero the pot after distributing
            self.log_chip_state("Jogador vence o pote")
        else:
            pot_amount = self.game.pot
            self.machine.chips += pot_amount
            self.machine.game_sequence['total_winnings'] += pot_amount
            self.player.game_sequence['total_losses'] += pot_amount
            if pot_amount > self.machine.game_sequence['biggest_pot_won']:
                self.machine.game_sequence['biggest_pot_won'] = pot_amount
            self.game.pot = 0  # Zero the pot after distributing
            self.log_chip_state("Máquina vence o pote")

        print(f"\n💰 Depois do pagamento - Jogador 1: {self.player.chips}, Máquina: {self.machine.chips}, Pote: {self.game.pot}")
        # Log chip counts after pot is awarded
        self.log_message(f"\n💰 Depois do pagamento - Jogador 1: {self.player.chips}, Máquina: {self.machine.chips} chips")

        # Registra o resultado com estatísticas detalhadas
        self.game.history_manager.record_game({
            "winner": winner_name,
            "pot": self.game.pot,
            "community_cards": self.game.show_community_cards(),
            "player_hand": self.player.show_hand(),
            "machine_hand": self.machine.show_hand(),
            "player_stats": {
                "hand_frequencies": self.player.game_sequence['hand_frequencies'],
                "total_winnings": self.player.game_sequence['total_winnings'],
                "total_losses": self.player.game_sequence['total_losses'],
                "best_hand": self.player.game_sequence['best_hand'],
                "biggest_pot_won": self.player.game_sequence['biggest_pot_won']
            },
            "machine_stats": {
                "hand_frequencies": self.machine.game_sequence['hand_frequencies'],
                "total_winnings": self.machine.game_sequence['total_winnings'],
                "total_losses": self.machine.game_sequence['total_losses'],
                "best_hand": self.machine.game_sequence['best_hand'],
                "biggest_pot_won": self.machine.game_sequence['biggest_pot_won']
            }
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

        # Update display to reflect chip changes
        self.update_display()

        # Check if session should end
        if self.player.chips <= 0:
            self.log_message("\n🏆 Máquina vence a sessão! Jogador ficou sem chips.")
            self.disable_all_buttons()
            return
        if self.machine.chips <= 0:
            self.log_message("\n🏆 Jogador vence a sessão! Máquina ficou sem chips.")
            self.disable_all_buttons()
            return
        if self.player.chips >= self.target_chips:
            self.log_message(f"\n🏆 Jogador vence a sessão! Alcançou {self.target_chips} chips!")
            self.disable_all_buttons()
            return
        if self.machine.chips >= self.target_chips:
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
        
    def show_statistics(self):
        """Show detailed player statistics in a new window"""
        stats_window = tk.Toplevel(self.root)
        stats_window.title("Estatísticas do Jogador")
        stats_window.geometry("600x400")
        stats_window.configure(bg='#1a472a')
        
        # Create notebook for tabs
        notebook = ttk.Notebook(stats_window)
        notebook.pack(expand=True, fill='both', padx=10, pady=10)
        
        # Player tab
        player_frame = ttk.Frame(notebook)
        notebook.add(player_frame, text='Jogador 1')
        
        # Machine tab
        machine_frame = ttk.Frame(notebook)
        notebook.add(machine_frame, text='Máquina')
        
        # Add statistics to each tab
        for player, frame in [('Jogador 1', player_frame), ('Máquina', machine_frame)]:
            player_obj = self.player if player == 'Jogador 1' else self.machine
            stats = player_obj.game_sequence
            
            # Create scrollable frame
            canvas = tk.Canvas(frame, bg='#1a472a')
            scrollbar = ttk.Scrollbar(frame, orient="vertical", command=canvas.yview)
            scrollable_frame = ttk.Frame(canvas)
            
            scrollable_frame.bind(
                "<Configure>",
                lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
            )
            
            canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
            canvas.configure(yscrollcommand=scrollbar.set)
            
            # Basic stats
            ttk.Label(scrollable_frame, text="Estatísticas Básicas", font=('Arial', 12, 'bold')).pack(pady=5)
            ttk.Label(scrollable_frame, text=f"Mãos Jogadas: {stats['hands_played']}").pack()
            ttk.Label(scrollable_frame, text=f"Ganhos Totais: {stats['total_winnings']}").pack()
            ttk.Label(scrollable_frame, text=f"Perdas Totais: {stats['total_losses']}").pack()
            
            # Best hand
            if stats['best_hand']:
                hand_type, value = stats['best_hand']
                ttk.Label(scrollable_frame, text=f"Melhor Mão: {hand_type} ({value})").pack()
            
            ttk.Label(scrollable_frame, text=f"Maior Pote Ganho: {stats['biggest_pot_won']}").pack()
            
            # Hand frequencies
            ttk.Label(scrollable_frame, text="\nFrequência de Mãos", font=('Arial', 12, 'bold')).pack(pady=5)
            for hand_type, freq in stats['hand_frequencies'].items():
                ttk.Label(scrollable_frame, text=f"{hand_type}: {freq}").pack()
            
            # Pack scrollbar and canvas
            scrollbar.pack(side="right", fill="y")
            canvas.pack(side="left", fill="both", expand=True)

if __name__ == "__main__":
    try:
        print("Iniciando aplicação...")
        import os
        os.environ['DISPLAY'] = ':0'  # Usa a configuração que funcionou
        root = tk.Tk()
        app = PokerGUI(root)
        print("Interface gráfica inicializada")
        print("Iniciando loop principal...")
        root.mainloop()
    except Exception as e:
        print(f"Erro ao iniciar aplicação: {e}")
        print("\nPor favor, certifique-se de que:")
        print("1. VcXsrv está instalado e rodando no Windows")
        print("2. XLaunch foi configurado com 'Disable access control'")
        print("3. Firewall do Windows permite conexões do WSL")
        import traceback
        traceback.print_exc()
