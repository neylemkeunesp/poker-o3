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
        self.root.title("🃏 Texas Hold'em Poker - Premium Edition")
        self.root.geometry("1500x1000")  # Aumentado para acomodar cartas maiores
        self.root.configure(bg='#0d1b2a')  # Dark blue-black background

        # Initialize card graphics
        self.card_graphics = CardGraphics()
        self.card_back = self.card_graphics.get_card_back()

        # Modern color palette
        self.colors = {
            'bg_dark': '#0d1b2a',
            'bg_medium': '#1b263b',
            'bg_light': '#415a77',
            'accent_gold': '#ffd60a',
            'accent_blue': '#4cc9f0',
            'accent_green': '#06ffa5',
            'accent_red': '#ff006e',
            'text_white': '#ffffff',
            'text_gray': '#a8b2c1',
            'table_felt': '#0f5132',
            'card_shadow': '#000814'
        }

        # Configure modern style
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TFrame', background=self.colors['bg_dark'])
        style.configure('TLabel',
                       background=self.colors['bg_dark'],
                       foreground=self.colors['text_white'],
                       font=('Segoe UI', 10))

        # Custom button styles with modern look
        style.configure('Action.TButton',
                       font=('Segoe UI', 11, 'bold'),
                       borderwidth=0,
                       relief='flat',
                       padding=10)

        style.map('Action.TButton',
                 background=[('active', self.colors['bg_light']), ('!active', self.colors['bg_medium'])],
                 foreground=[('active', self.colors['text_white']), ('!active', self.colors['text_white'])])

        style.configure('Call.TButton',
                       background=self.colors['accent_green'],
                       foreground='#000000')
        style.configure('Raise.TButton',
                       background=self.colors['accent_blue'],
                       foreground='#000000')
        style.configure('Fold.TButton',
                       background=self.colors['accent_red'],
                       foreground='#ffffff')

        # Create canvas and scrollbar for scrolling capability
        self.canvas = tk.Canvas(self.root, bg=self.colors['bg_dark'], highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self.root, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas, style='TFrame')

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        # Pack scrollbar and canvas
        self.scrollbar.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)

        # Bind mouse wheel for scrolling
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        self.canvas.bind_all("<Button-4>", self._on_mousewheel)  # Linux scroll up
        self.canvas.bind_all("<Button-5>", self._on_mousewheel)  # Linux scroll down

        # Main container (inside scrollable frame)
        self.main_container = ttk.Frame(self.scrollable_frame, style='TFrame')
        self.main_container.pack(expand=True, fill='both', padx=20, pady=10)
        
        # Set up frames and components
        self.setup_frames()
        self.setup_components()
        
        # Game initialization
        self.player = Player("Jogador 1")
        self.machine = Player("Máquina", is_machine=True)
        self.game = None
        self.current_bet = 50
        self.betting_round_complete = False  # Flag to track betting round completion
        
        # Bet tracking
        self.player_bet_in_round = 0
        self.machine_bet_in_round = 0
        
        # Session tracking
        self.hands_played = 0
        self.player_wins = 0
        self.machine_wins = 0
        self.current_streak = 0  # positive for player streak, negative for machine streak
        self.target_chips = 5000  # Win condition
        self.starting_chips = 1000
        
        # Store game messages
        self.message_history = []
        
        # Start a new game session
        self.start_new_session()

    def setup_frames(self):
        """Set up all frames in the interface"""
        # Top section: Game phase banner with gradient effect
        self.phase_banner_frame = tk.Frame(
            self.main_container,
            bg=self.colors['bg_medium'],
            height=80,
            relief=tk.FLAT,
            bd=0
        )
        self.phase_banner_frame.pack(fill='x', pady=(0, 15))

        # Add decorative border
        border_frame = tk.Frame(
            self.phase_banner_frame,
            bg=self.colors['accent_gold'],
            height=3
        )
        border_frame.pack(fill='x', side='bottom')

        # Phase indicator with modern styling
        self.phase_label = tk.Label(
            self.phase_banner_frame,
            text="✦ FASE: PRÉ-FLOP ✦",
            font=('Segoe UI', 18, 'bold'),
            fg=self.colors['accent_gold'],
            bg=self.colors['bg_medium']
        )
        self.phase_label.pack(fill='both', expand=True, pady=8)

        # Winner announcement frame (initially hidden) with celebratory styling
        self.winner_frame = tk.Frame(
            self.main_container,
            bg=self.colors['bg_medium'],
            height=60,
            relief=tk.RIDGE,
            bd=3,
            highlightbackground=self.colors['accent_gold'],
            highlightthickness=3
        )
        self.winner_frame.pack(fill='x', pady=(0, 8))
        self.winner_frame.pack_forget()  # Initially hidden

        self.winner_label = tk.Label(
            self.winner_frame,
            text="",
            font=('Segoe UI', 20, 'bold'),
            fg=self.colors['accent_gold'],
            bg=self.colors['bg_medium']
        )
        self.winner_label.pack(fill='both', expand=True, pady=8)

        # Opponent section with modern card layout
        self.opponent_section = tk.Frame(
            self.main_container,
            bg=self.colors['bg_medium'],
            relief=tk.FLAT,
            bd=5,
            padx=15,
            pady=10
        )
        self.opponent_section.pack(fill='x', pady=8)

        # Opponent info and cards
        self.opponent_info = tk.Frame(self.opponent_section, bg=self.colors['bg_medium'])
        self.opponent_info.pack(side='left', padx=20)

        self.machine_name_label = tk.Label(
            self.opponent_info,
            text="🤖 MÁQUINA AI",
            font=('Segoe UI', 16, 'bold'),
            fg=self.colors['accent_red'],
            bg=self.colors['bg_medium']
        )
        self.machine_name_label.pack(anchor='w', pady=(0, 8))

        # Modern chip display for opponent
        self.machine_chips_box = tk.Frame(
            self.opponent_info,
            bg=self.colors['bg_light'],
            relief=tk.FLAT,
            bd=0,
            padx=15,
            pady=8
        )
        self.machine_chips_box.pack(anchor='w')

        # Add subtle border effect
        tk.Frame(
            self.machine_chips_box,
            bg=self.colors['accent_red'],
            height=2
        ).pack(side='top', fill='x')

        self.machine_chips_display = tk.Label(
            self.machine_chips_box,
            text="💎 1000",
            font=('Segoe UI', 15, 'bold'),
            fg=self.colors['accent_gold'],
            bg=self.colors['bg_light']
        )
        self.machine_chips_display.pack(anchor='w', pady=(3,0))
        
        # Opponent cards container with title
        self.opponent_cards_container = tk.Frame(self.opponent_section, bg=self.colors['bg_medium'])
        self.opponent_cards_container.pack(side='right', padx=20)

        # Label above opponent cards
        self.opponent_cards_title = tk.Label(
            self.opponent_cards_container,
            text="🤖 CARTAS DA MÁQUINA",
            font=('Segoe UI', 13, 'bold'),
            fg=self.colors['accent_red'],
            bg=self.colors['bg_medium']
        )
        self.opponent_cards_title.pack(pady=(0, 8))

        # Opponent cards frame
        self.opponent_cards_frame = tk.Frame(self.opponent_cards_container, bg=self.colors['bg_medium'])
        self.opponent_cards_frame.pack()

        # Opponent card labels
        self.opponent_card_labels = []
        for i in range(2):
            label = ttk.Label(self.opponent_cards_frame, background=self.colors['bg_medium'])
            label.pack(side='left', padx=10)  # Aumentado de 5 para 10 para acomodar cartas maiores
            self.opponent_card_labels.append(label)

        # Community cards section with premium styling
        self.community_section = tk.Frame(
            self.main_container,
            bg=self.colors['bg_dark']
        )
        self.community_section.pack(fill='x', pady=10)
        
        # Info bar with pot and bet
        info_bar = tk.Frame(self.community_section, bg=self.colors['bg_medium'], pady=10)
        info_bar.pack(side='top', pady=10)

        # Pot display - Premium styling
        self.pot_frame = tk.Frame(info_bar, bg=self.colors['bg_medium'])
        self.pot_frame.pack(side='left', padx=20)

        self.pot_label = tk.Label(
            self.pot_frame,
            text="💰 POTE TOTAL",
            font=('Segoe UI', 12, 'bold'),
            fg=self.colors['text_gray'],
            bg=self.colors['bg_medium']
        )
        self.pot_label.pack()

        self.pot_box = tk.Frame(
            self.pot_frame,
            bg=self.colors['bg_light'],
            relief=tk.FLAT,
            bd=0,
            padx=20,
            pady=12
        )
        self.pot_box.pack(pady=(5,0))

        # Decorative top border for pot
        tk.Frame(
            self.pot_box,
            bg=self.colors['accent_gold'],
            height=3
        ).pack(side='top', fill='x')

        self.pot_display = tk.Label(
            self.pot_box,
            text="0",
            font=('Segoe UI', 22, 'bold'),
            fg=self.colors['accent_gold'],
            bg=self.colors['bg_light']
        )
        self.pot_display.pack(pady=(5,0))

        # Current bet display - Modern styling
        self.current_bet_frame = tk.Frame(info_bar, bg=self.colors['bg_medium'])
        self.current_bet_frame.pack(side='left', padx=20)

        self.current_bet_label = tk.Label(
            self.current_bet_frame,
            text="🎯 APOSTA ATUAL",
            font=('Segoe UI', 12, 'bold'),
            fg=self.colors['text_gray'],
            bg=self.colors['bg_medium']
        )
        self.current_bet_label.pack()

        self.current_bet_box = tk.Frame(
            self.current_bet_frame,
            bg=self.colors['bg_light'],
            relief=tk.FLAT,
            bd=0,
            padx=20,
            pady=12
        )
        self.current_bet_box.pack(pady=(5,0))

        # Decorative top border for bet
        tk.Frame(
            self.current_bet_box,
            bg=self.colors['accent_blue'],
            height=3
        ).pack(side='top', fill='x')

        self.current_bet_display = tk.Label(
            self.current_bet_box,
            text="50",
            font=('Segoe UI', 22, 'bold'),
            fg=self.colors['accent_blue'],
            bg=self.colors['bg_light']
        )
        self.current_bet_display.pack(pady=(5,0))

        # Total chips display - Conservation verification
        self.total_chips_frame = tk.Frame(info_bar, bg=self.colors['bg_medium'])
        self.total_chips_frame.pack(side='left', padx=20)

        self.total_chips_label = tk.Label(
            self.total_chips_frame,
            text="🔢 TOTAL EM JOGO",
            font=('Segoe UI', 12, 'bold'),
            fg=self.colors['text_gray'],
            bg=self.colors['bg_medium']
        )
        self.total_chips_label.pack()

        self.total_chips_box = tk.Frame(
            self.total_chips_frame,
            bg=self.colors['bg_light'],
            relief=tk.FLAT,
            bd=0,
            padx=20,
            pady=12
        )
        self.total_chips_box.pack(pady=(5,0))

        # Decorative top border for total
        self.total_chips_border = tk.Frame(
            self.total_chips_box,
            bg=self.colors['accent_green'],
            height=3
        )
        self.total_chips_border.pack(side='top', fill='x')

        self.total_chips_display = tk.Label(
            self.total_chips_box,
            text="2000",
            font=('Segoe UI', 22, 'bold'),
            fg=self.colors['accent_green'],
            bg=self.colors['bg_light']
        )
        self.total_chips_display.pack(pady=(5,0))

        # Community cards frame with premium felt table
        self.community_cards_label = tk.Label(
            self.community_section,
            text="♠ CARTAS COMUNITÁRIAS ♥",
            font=('Segoe UI', 14, 'bold'),
            fg=self.colors['text_white'],
            bg=self.colors['bg_dark']
        )
        self.community_cards_label.pack(pady=(20, 10))

        self.community_cards_frame = tk.Frame(self.community_section, bg=self.colors['bg_dark'])
        self.community_cards_frame.pack(pady=10)

        # Premium poker table background with elevated design
        table_outer = tk.Frame(
            self.community_cards_frame,
            bg=self.colors['bg_light'],
            relief=tk.RAISED,
            bd=3
        )
        table_outer.pack(padx=5, pady=5)

        self.table_bg = tk.Frame(
            table_outer,
            bg=self.colors['table_felt'],
            width=850,  # Aumentado de 600 para 850 para acomodar cartas maiores
            height=240,  # Aumentado de 180 para 240 para altura das cartas
            padx=15,
            pady=15
        )
        self.table_bg.pack()
        self.table_bg.pack_propagate(False)

        # Decorative corners
        for pos in ['nw', 'ne', 'sw', 'se']:
            corner = tk.Frame(
                self.table_bg,
                bg=self.colors['accent_gold'],
                width=3,
                height=3
            )
            if 'n' in pos:
                corner.place(relx=0 if 'w' in pos else 1, rely=0, anchor=pos)
            else:
                corner.place(relx=0 if 'w' in pos else 1, rely=1, anchor=pos)

        # Community card labels
        self.community_card_container = tk.Frame(self.table_bg, bg=self.colors['table_felt'])
        self.community_card_container.pack(expand=True, fill='both')

        self.community_card_labels = []
        for i in range(5):
            label = ttk.Label(self.community_card_container, background=self.colors['table_felt'])
            label.pack(side='left', padx=10)  # Aumentado de 6 para 10 para melhor espaçamento
            self.community_card_labels.append(label)
        
        # Player section with modern styling
        self.player_section = tk.Frame(
            self.main_container,
            bg=self.colors['bg_medium'],
            relief=tk.FLAT,
            bd=5,
            padx=15,
            pady=15
        )
        self.player_section.pack(fill='x', pady=(20, 10))

        # Container for player info (left side)
        self.player_info = tk.Frame(self.player_section, bg=self.colors['bg_medium'])
        self.player_info.pack(side='left', padx=20)

        self.player_name_label = tk.Label(
            self.player_info,
            text="👤 VOCÊ",
            font=('Segoe UI', 16, 'bold'),
            fg=self.colors['accent_green'],
            bg=self.colors['bg_medium']
        )
        self.player_name_label.pack(anchor='w', pady=(0, 8))

        # Premium chip display for player
        self.player_chips_box = tk.Frame(
            self.player_info,
            bg=self.colors['bg_light'],
            relief=tk.FLAT,
            bd=0,
            padx=15,
            pady=8
        )
        self.player_chips_box.pack(anchor='w')

        # Add subtle border effect
        tk.Frame(
            self.player_chips_box,
            bg=self.colors['accent_green'],
            height=2
        ).pack(side='top', fill='x')

        self.player_chips_display = tk.Label(
            self.player_chips_box,
            text="💎 1000",
            font=('Segoe UI', 15, 'bold'),
            fg=self.colors['accent_gold'],
            bg=self.colors['bg_light']
        )
        self.player_chips_display.pack(anchor='w', pady=(3,0))

        # Container for player cards (right side) - text above cards
        self.player_cards_container = tk.Frame(self.player_section, bg=self.colors['bg_medium'])
        self.player_cards_container.pack(side='right', padx=20)

        # Label above cards - mais visível
        self.player_cards_title = tk.Label(
            self.player_cards_container,
            text="👤 SUAS CARTAS",
            font=('Segoe UI', 13, 'bold'),
            fg=self.colors['accent_green'],  # Verde destaque igual ao nome
            bg=self.colors['bg_medium']
        )
        self.player_cards_title.pack(pady=(0, 8))

        # Cards frame
        self.player_cards_frame = tk.Frame(self.player_cards_container, bg=self.colors['bg_medium'])
        self.player_cards_frame.pack()

        self.player_card_labels = []
        for i in range(2):
            label = ttk.Label(self.player_cards_frame, background=self.colors['bg_medium'])
            label.pack(side='left', padx=10)  # Aumentado de 5 para 10 para acomodar cartas maiores
            self.player_card_labels.append(label)
        
        # Player action buttons with modern design
        self.action_buttons_frame = tk.Frame(
            self.main_container,
            bg=self.colors['bg_dark'],
            pady=15
        )
        self.action_buttons_frame.pack(fill='x', pady=8)

        # Player's hand strength indicator - Premium card
        self.hand_strength_frame = tk.Frame(
            self.action_buttons_frame,
            bg=self.colors['bg_medium'],
            padx=20,
            pady=12,
            relief=tk.FLAT
        )
        self.hand_strength_frame.pack(side='left', padx=20)

        tk.Frame(
            self.hand_strength_frame,
            bg=self.colors['accent_green'],
            height=2
        ).pack(side='top', fill='x')

        self.hand_strength_label = tk.Label(
            self.hand_strength_frame,
            text="🎴 SUA MÃO:",
            font=('Segoe UI', 11, 'bold'),
            fg=self.colors['text_gray'],
            bg=self.colors['bg_medium']
        )
        self.hand_strength_label.pack(anchor='w', pady=(5,2))

        self.hand_type_display = tk.Label(
            self.hand_strength_frame,
            text="-",
            font=('Segoe UI', 16, 'bold'),
            fg=self.colors['accent_green'],
            bg=self.colors['bg_medium']
        )
        self.hand_type_display.pack(anchor='w')

        # Control buttons - Premium modern design
        self.button_container = tk.Frame(self.action_buttons_frame, bg=self.colors['bg_dark'])
        self.button_container.pack(side='right', padx=20)

        # Call button with green theme
        call_btn_frame = tk.Frame(self.button_container, bg=self.colors['accent_green'], relief=tk.FLAT, bd=0)
        call_btn_frame.pack(side='left', padx=5)

        self.call_button = tk.Button(
            call_btn_frame,
            text="✓ PAGAR",
            command=self.call_action,
            font=('Segoe UI', 12, 'bold'),
            bg=self.colors['accent_green'],
            fg='#000000',
            activebackground='#05dd8e',
            activeforeground='#000000',
            relief=tk.FLAT,
            bd=0,
            padx=25,
            pady=12,
            cursor='hand2'
        )
        self.call_button.pack()

        # Raise button with blue theme
        raise_btn_frame = tk.Frame(self.button_container, bg=self.colors['accent_blue'], relief=tk.FLAT, bd=0)
        raise_btn_frame.pack(side='left', padx=5)

        self.raise_button = tk.Button(
            raise_btn_frame,
            text="↑ AUMENTAR",
            command=self.raise_action,
            font=('Segoe UI', 12, 'bold'),
            bg=self.colors['accent_blue'],
            fg='#000000',
            activebackground='#3bb0d9',
            activeforeground='#000000',
            relief=tk.FLAT,
            bd=0,
            padx=25,
            pady=12,
            cursor='hand2'
        )
        self.raise_button.pack()

        # Fold button with red theme
        fold_btn_frame = tk.Frame(self.button_container, bg=self.colors['accent_red'], relief=tk.FLAT, bd=0)
        fold_btn_frame.pack(side='left', padx=5)

        self.fold_button = tk.Button(
            fold_btn_frame,
            text="✕ DESISTIR",
            command=self.fold_action,
            font=('Segoe UI', 12, 'bold'),
            bg=self.colors['accent_red'],
            fg='#ffffff',
            activebackground='#e0005d',
            activeforeground='#ffffff',
            relief=tk.FLAT,
            bd=0,
            padx=25,
            pady=12,
            cursor='hand2'
        )
        self.fold_button.pack()
        
        # Hand progress indicators with modern timeline
        self.progress_frame = tk.Frame(
            self.main_container,
            bg=self.colors['bg_medium'],
            pady=15
        )
        self.progress_frame.pack(fill='x', pady=8)

        self.hand_progress_label = tk.Label(
            self.progress_frame,
            text="📊 PROGRESSO DA MÃO",
            font=('Segoe UI', 12, 'bold'),
            fg=self.colors['text_white'],
            bg=self.colors['bg_medium']
        )
        self.hand_progress_label.pack(anchor='w', padx=20, pady=(0,10))

        self.hand_progress_container = tk.Frame(self.progress_frame, bg=self.colors['bg_medium'])
        self.hand_progress_container.pack(fill='x', padx=40, pady=10)

        self.hand_stages = ["Pré-Flop", "Flop", "Turn", "River", "Showdown"]
        self.hand_stage_indicators = []

        # Create modern progress indicators for each stage
        for i, stage in enumerate(self.hand_stages):
            stage_frame = tk.Frame(self.hand_progress_container, bg=self.colors['bg_medium'])
            stage_frame.pack(side='left', expand=True, fill='x')

            # Visual connection line
            if i > 0:
                line_frame = tk.Frame(stage_frame, bg=self.colors['bg_light'], height=3)
                line_frame.pack(fill='x', pady=12)

            # Stage indicator circle
            indicator = tk.Label(
                stage_frame,
                text="●",
                font=('Segoe UI', 20),
                fg=self.colors['bg_light'],
                bg=self.colors['bg_medium']
            )
            indicator.pack(anchor='center')

            # Stage name
            name_label = tk.Label(
                stage_frame,
                text=stage,
                font=('Segoe UI', 9, 'bold'),
                fg=self.colors['text_gray'],
                bg=self.colors['bg_medium']
            )
            name_label.pack(anchor='center', pady=(2,0))

            self.hand_stage_indicators.append((indicator, name_label))

        # Bottom navigation buttons
        self.nav_buttons_frame = tk.Frame(self.main_container, bg='#1a472a')
        self.nav_buttons_frame.pack(fill='x', pady=10)
        
        self.new_hand_button = ttk.Button(
            self.nav_buttons_frame,
            text="Próxima Mão",
            command=self.new_hand,
            width=20
        )
        self.new_hand_button.pack(side='left', padx=10)
        
        self.new_session_button = ttk.Button(
            self.nav_buttons_frame,
            text="Nova Sessão",
            command=self.start_new_session,
            width=20
        )
        self.new_session_button.pack(side='left', padx=10)
        
        # Information buttons
        self.info_button = ttk.Button(
            self.nav_buttons_frame,
            text="Regras do Jogo",
            command=self.show_game_info,
            width=20
        )
        self.info_button.pack(side='right', padx=10)
        
        self.stats_button = ttk.Button(
            self.nav_buttons_frame,
            text="Estatísticas",
            command=self.show_statistics,
            width=20
        )
        self.stats_button.pack(side='right', padx=10)

    def setup_components(self):
        """Configure additional UI components and event handlers"""
        # Initial state of buttons
        self.disable_buttons()
        self.new_hand_button.config(state='disabled')

    def log_message(self, message):
        """Add a message to the game log"""
        # Store message in history
        self.message_history.append(message)

        # Print to console for debugging
        print(message)

        # Update hand stats if needed
        self.update_game_info(message)
        
    def log_chip_state(self, action):
        """Log the current state of all chips"""
        total = self.player.chips + self.machine.chips + self.game.pot
        expected_total = self.starting_chips * 2  # Should always be 2000 for 2 players

        message = f"\n[{action}]\n"
        message += f"Jogador: {self.player.chips} chips\n"
        message += f"Máquina: {self.machine.chips} chips\n"
        message += f"Pote: {self.game.pot} chips\n"
        message += f"Total: {total} chips"

        if total != expected_total:
            difference = total - expected_total
            message += f"\n⚠️⚠️⚠️ ERRO DE CONSERVAÇÃO DE FICHAS! ⚠️⚠️⚠️"
            message += f"\nEsperado: {expected_total} chips"
            message += f"\nEncontrado: {total} chips"
            message += f"\nDiferença: {difference:+d} chips"

        self.log_message(message)

        # Update chip displays
        self.update_chip_displays()
        
    def update_chip_displays(self):
        """Update all chip displays in the UI with modern styling"""
        self.player_chips_display.config(text=f"💎 {self.player.chips}")
        self.machine_chips_display.config(text=f"💎 {self.machine.chips}")

        # Calculate total chips in play
        if self.game is not None:
            total = self.player.chips + self.machine.chips + self.game.pot
            self.pot_display.config(text=f"{self.game.pot}")
            self.current_bet_display.config(text=f"{self.current_bet}")
        else:
            total = self.player.chips + self.machine.chips
            self.pot_display.config(text="0")
            self.current_bet_display.config(text="0")

        # Update total display and change color if there's an error
        expected_total = self.starting_chips * 2
        self.total_chips_display.config(text=f"{total}")

        if total != expected_total:
            # Red for error
            self.total_chips_display.config(fg=self.colors['accent_red'])
            self.total_chips_border.config(bg=self.colors['accent_red'])
        else:
            # Green for correct
            self.total_chips_display.config(fg=self.colors['accent_green'])
            self.total_chips_border.config(bg=self.colors['accent_green'])
        
    def update_game_info(self, message):
        """Update game state indicators based on log messages"""
        # Update hand type displays
        if "Jogador 1 tem " in message and "\n" in message:
            hand_type = message.split("Jogador 1 tem ")[1].split("\n")[0]
            self.hand_type_display.config(text=hand_type)
            
        # Update game progress
        if "=== Flop ===" in message:
            self.update_progress_indicators(1)  # Flop
        elif "=== Turn ===" in message:
            self.update_progress_indicators(2)  # Turn
        elif "=== River ===" in message:
            self.update_progress_indicators(3)  # River
        elif "🏆" in message and "vence" in message:
            self.update_progress_indicators(4)  # Showdown
        elif "=== Nova Mão ===" in message:
            self.update_progress_indicators(0)  # Pre-flop
            self.hand_type_display.config(text="-")
            
    def update_progress_indicators(self, stage_index):
        """Update the hand progress indicators with modern styling"""
        # Update stage indicators
        for i, (indicator, label) in enumerate(self.hand_stage_indicators):
            if i < stage_index:
                # Completed stage
                indicator.config(text="✓", fg=self.colors['accent_green'])
                label.config(fg=self.colors['accent_green'])
            elif i == stage_index:
                # Current stage
                indicator.config(text="●", fg=self.colors['accent_gold'])
                label.config(fg=self.colors['accent_gold'])
            else:
                # Future stage
                indicator.config(text="○", fg=self.colors['bg_light'])
                label.config(fg=self.colors['text_gray'])

        # Update phase banner with modern styling
        phases = ["PRÉ-FLOP", "FLOP", "TURN", "RIVER", "SHOWDOWN"]
        phase_icons = ["🎴", "🃏", "🎯", "🎲", "🏆"]

        if 0 <= stage_index < len(phases):
            self.phase_label.config(
                text=f"{phase_icons[stage_index]} FASE: {phases[stage_index]} {phase_icons[stage_index]}"
            )

            # Modern color scheme for each phase
            phase_colors = {
                0: self.colors['accent_gold'],    # Pre-flop
                1: self.colors['accent_green'],   # Flop
                2: self.colors['accent_blue'],    # Turn
                3: self.colors['accent_red'],     # River
                4: self.colors['accent_gold'],    # Showdown
            }

            fg_color = phase_colors.get(stage_index, self.colors['accent_gold'])
            self.phase_label.config(fg=fg_color)

    def update_display(self):
        """Update all card displays"""
        # Update community cards
        for i, label in enumerate(self.community_card_labels):
            if i < len(self.game.community_cards):
                card = self.game.community_cards[i]
                image = self.card_graphics.get_card_image(card.rank, card.suit)
                label.configure(image=image)
                label._image = image  # Keep a reference
            else:
                label.configure(image='')
                label._image = None
        
        # Update opponent cards (legacy, hidden frame)
        for i, label in enumerate(self.opponent_card_labels):
            if i < len(self.machine.hand):
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
        
        # Update player cards (legacy, hidden frame)
        for i, label in enumerate(self.player_card_labels):
            if i < len(self.player.hand):
                card = self.player.hand[i]
                image = self.card_graphics.get_card_image(card.rank, card.suit)
                label.configure(image=image)
                label._image = image
            else:
                label.configure(image='')
                label._image = None

        # Update chip displays
        self.update_chip_displays()

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
        
        # Clear log and history
        self.message_history.clear()

        # Reset hand stats and progress
        self.hand_type_display.config(text="-")
        self.update_progress_indicators(0)  # Reset progress
        
        # Hide winner frame if visible
        if hasattr(self, 'winner_frame') and self.winner_frame is not None:
            self.winner_frame.pack_forget()
        
        # Update chip displays immediately
        self.update_chip_displays()

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
        
        # Hide winner frame if visible
        if hasattr(self, 'winner_frame') and self.winner_frame is not None:
            self.winner_frame.pack_forget()
        
        # Reset phase to PRE-FLOP
        self.update_progress_indicators(0)
        
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
        
        # Reset round bets
        self.player_bet_in_round = 0
        self.machine_bet_in_round = 0
        
        # Post blinds and update chips
        self.player.chips -= small_blind  # Player is small blind
        self.machine.chips -= big_blind   # Machine is big blind
        self.game.pot = small_blind + big_blind
        self.current_bet = big_blind
        
        # Update round bets
        self.player_bet_in_round = small_blind
        self.machine_bet_in_round = big_blind
        
        # Log blinds
        self.log_message(f"Jogador 1 posta small blind: {small_blind}")
        self.log_message(f"Máquina posta big blind: {big_blind}")
        self.log_chip_state("Blinds postados")

        # Update chip displays after blinds
        self.update_chip_displays()

        # Update statistics
        self.player.game_sequence['hands_played'] += 1
        self.machine.game_sequence['hands_played'] += 1
        self.player.game_sequence['total_chip_diff'] = self.player.chips - self.starting_chips
        self.machine.game_sequence['total_chip_diff'] = self.machine.chips - self.starting_chips
        self.player.game_sequence['max_chips'] = max(self.player.game_sequence['max_chips'], self.player.chips)
        self.machine.game_sequence['max_chips'] = max(self.machine.game_sequence['max_chips'], self.machine.chips)
        
        # Deal initial cards
        self.game.deal_cards()
        
        # Update display and enable buttons
        self.update_display()
        self.enable_buttons()
        self.new_hand_button.config(state='disabled')

    def call_action(self):
        """Player chooses to call/check"""
        # Log state before action
        self.log_message(f"\nAntes do Call/Check:")
        self.log_chip_state("Estado Inicial")
        
        # Calculate call amount
        additional_bet = self.machine_bet_in_round - self.player_bet_in_round
        
        if additional_bet > 0:
            # Call (match the current bet)
            if additional_bet <= self.player.chips:
                self.player.chips -= additional_bet
                self.game.pot += additional_bet
                self.player_bet_in_round += additional_bet
                self.log_message(f"Jogador: Call {additional_bet} (Total na rodada: {self.player_bet_in_round})")
                self.log_chip_state("Jogador Call")
            else:
                # All-in call
                all_in_amount = self.player.chips
                self.player.chips = 0
                self.game.pot += all_in_amount
                self.player_bet_in_round += all_in_amount
                self.log_message(f"Jogador: All-in Call {all_in_amount} (Total na rodada: {self.player_bet_in_round})")
                self.log_chip_state("Jogador All-in")
        else:
            # Check (no additional bet)
            self.log_message(f"Jogador: Check (Total na rodada: {self.player_bet_in_round})")
            self.log_chip_state("Jogador Check")
        
        # Update UI before machine action
        self.update_chip_displays()
        self.update_display()
        
        # Machine's turn
        self.machine_action()
        
        # Check if machine folded
        if self.machine.folded:
            self.end_hand("Jogador 1")
            return
            
        # Betting round complete after both players have acted
        self.betting_round_complete = True
        self.update_display()
        self.check_game_state()

    def raise_action(self):
        """Player chooses to raise"""
        # First match the current bet, then add the raise amount
        call_amount = self.machine_bet_in_round - self.player_bet_in_round
        raise_amount = self.game.min_raise
        total_amount = call_amount + raise_amount
        
        if total_amount <= self.player.chips:
            # Standard raise
            self.player.chips -= total_amount
            self.game.pot += total_amount
            self.player_bet_in_round += total_amount
            self.current_bet = self.player_bet_in_round
            
            self.log_message(f"Jogador: Raise para {total_amount} (Total na rodada: {self.player_bet_in_round})")
            self.log_chip_state("Jogador Raise")

            # Update UI before machine action
            self.update_chip_displays()
            self.update_display()
            
            # Machine's turn
            self.machine_action()
            
            # Check if machine folded
            if self.machine.folded:
                self.end_hand("Jogador 1")
                return
            
            # Betting round complete after both players have acted
            self.betting_round_complete = True
            self.update_display()
            self.check_game_state()
        elif self.player.chips > call_amount:
            # Not enough for full raise, but can do a smaller raise
            available_raise = self.player.chips - call_amount
            total_amount = call_amount + available_raise
            
            self.player.chips = 0  # All-in
            self.game.pot += total_amount
            self.player_bet_in_round += total_amount
            self.current_bet = self.player_bet_in_round
            
            self.log_message(f"Jogador: All-in Raise para {total_amount} (Total na rodada: {self.player_bet_in_round})")
            self.log_chip_state("Jogador All-in Raise")
            
            # Update UI and continue game
            self.update_display()
            self.machine_action()
            
            if self.machine.folded:
                self.end_hand("Jogador 1")
                return
                
            self.betting_round_complete = True
            self.update_display()
            self.check_game_state()
        else:
            # Not enough chips even for the call - must go all-in with call
            self.log_message("⚠️ Chips insuficientes para raise! Use Call para all-in.")

    def fold_action(self):
        """Player chooses to fold"""
        self.player.folded = True
        self.log_message("Jogador: Fold")
        self.end_hand("Máquina")
        self.disable_buttons()
        self.new_hand_button.config(state='normal')

    def machine_action(self):
        """Handle machine's betting action"""
        # Log state before action
        self.log_message(f"\nAntes da ação da Máquina:")
        self.log_chip_state("Estado Inicial")

        # Get machine's decision
        action, amount = self.machine.make_decision(self.game.community_cards, self.current_bet, self.game.min_raise)

        if action == "fold":
            # Machine folds
            self.machine.folded = True
            self.log_message("Máquina: Fold")
            self.update_chip_displays()
            return
        elif action == "raise":
            # Calculate call and raise amounts
            call_amount = self.player_bet_in_round - self.machine_bet_in_round
            raise_amount = self.game.min_raise
            total_amount = call_amount + raise_amount

            if total_amount <= self.machine.chips:
                # Standard raise
                self.machine.chips -= total_amount
                self.game.pot += total_amount
                self.machine_bet_in_round += total_amount
                self.current_bet = self.machine_bet_in_round

                self.log_message(f"Máquina: Raise para {total_amount} (Total na rodada: {self.machine_bet_in_round})")
                self.log_chip_state("Máquina Raise")
                self.betting_round_complete = False  # Reset flag as player needs to act again
            else:
                # All-in raise
                all_in_amount = self.machine.chips
                self.machine.chips = 0
                self.game.pot += all_in_amount
                self.machine_bet_in_round += all_in_amount
                self.current_bet = self.machine_bet_in_round

                self.log_message(f"Máquina: All-in Raise para {all_in_amount} (Total na rodada: {self.machine_bet_in_round})")
                self.log_chip_state("Máquina All-in")
                self.betting_round_complete = False  # Reset flag
        else:  # call/check
            # Calculate call amount
            call_amount = self.player_bet_in_round - self.machine_bet_in_round

            if call_amount > 0:
                if call_amount <= self.machine.chips:
                    # Standard call
                    self.machine.chips -= call_amount
                    self.game.pot += call_amount
                    self.machine_bet_in_round += call_amount

                    self.log_message(f"Máquina: Call {call_amount} (Total na rodada: {self.machine_bet_in_round})")
                    self.log_chip_state("Máquina Call")
                else:
                    # All-in call
                    all_in_amount = self.machine.chips
                    self.machine.chips = 0
                    self.game.pot += all_in_amount
                    self.machine_bet_in_round += all_in_amount

                    self.log_message(f"Máquina: All-in Call {all_in_amount} (Total na rodada: {self.machine_bet_in_round})")
                    self.log_chip_state("Máquina All-in")
            else:
                # Check (bet already matched)
                self.log_message(f"Máquina: Check (Total na rodada: {self.machine_bet_in_round})")
                self.log_chip_state("Máquina Check")

        # Update chip displays after machine action
        self.update_chip_displays()

    def check_game_state(self):
        """Check game state and advance to next phase if needed"""
        # Only proceed if no one folded
        if self.player.folded or self.machine.folded:
            return
            
        # Only proceed to next stage if betting round is complete
        if not self.betting_round_complete:
            return
            
        # Determine next phase based on current community cards
        if len(self.game.community_cards) == 0:
            # Deal the flop (first 3 community cards)
            self.log_message("\nAntes do Flop:")
            self.log_chip_state("Estado antes do Flop")
            
            self.game.deal_community_cards(3)  # Deal 3 cards for the flop
            self.log_message("\n=== Flop ===")
            
            # Reset bets for new round
            self.current_bet = 0
            self.player_bet_in_round = 0
            self.machine_bet_in_round = 0
            self.betting_round_complete = False
            
            # Log state after dealing flop
            self.log_chip_state("Estado após o Flop")
        elif len(self.game.community_cards) == 3:
            # Deal the turn (4th community card)
            self.log_message("\nAntes do Turn:")
            self.log_chip_state("Estado antes do Turn")
            
            self.game.deal_community_cards(1)  # Deal 1 card for the turn
            self.log_message("\n=== Turn ===")
            
            # Reset bets for new round
            self.current_bet = 0
            self.player_bet_in_round = 0
            self.machine_bet_in_round = 0
            self.betting_round_complete = False
            
            # Log state after dealing turn
            self.log_chip_state("Estado após o Turn")
        elif len(self.game.community_cards) == 4:
            # Deal the river (5th community card)
            self.log_message("\nAntes do River:")
            self.log_chip_state("Estado antes do River")
            
            self.game.deal_community_cards(1)  # Deal 1 card for the river
            self.log_message("\n=== River ===")
            
            # Reset bets for new round
            self.current_bet = 0
            self.player_bet_in_round = 0
            self.machine_bet_in_round = 0
            self.betting_round_complete = False
            
            # Log state after dealing river
            self.log_chip_state("Estado após o River")
        elif len(self.game.community_cards) == 5:
            # All community cards dealt, betting complete - go to showdown
            self.end_hand()
        
        # Update UI
        self.update_display()

    def end_hand(self, winner_by_fold=None):
        """End the current hand and update session stats"""
        # Determine the winner
        if winner_by_fold:
            winner_name = winner_by_fold
            winner_hand_type = None
        else:
            # Evaluate both player's hands
            player_type, player_value = self.player.get_hand_value(self.game.community_cards)
            machine_type, machine_value = self.machine.get_hand_value(self.game.community_cards)
            
            # Display hand results
            result = f"\nJogador 1 tem {player_type}\nMáquina tem {machine_type}\n"
            
            if player_value > machine_value:
                winner_name = "Jogador 1"
                winner_hand_type = player_type
            else:
                winner_name = "Máquina"
                winner_hand_type = machine_type
                
            result += f"🏆 {winner_name} vence!"
            self.log_message(result)
        
        # Show winner banner
        if self.winner_frame is not None:
            self.winner_frame.pack(fill='x', pady=(0, 10))
            
            if self.winner_label is not None:
                if winner_by_fold:
                    self.winner_label.config(
                        text=f"🏆 {winner_name} VENCE POR DESISTÊNCIA! 🏆",
                        fg="#FFD700" if winner_name == "Jogador 1" else "#FF6347"
                    )
                    self.log_message(f"\n🏆 {winner_name} vence por desistência!")
                else:
                    self.winner_label.config(
                        text=f"🏆 {winner_name} VENCE COM {winner_hand_type}! 🏆",
                        fg="#FFD700" if winner_name == "Jogador 1" else "#FF6347"
                    )

        # Update session stats
        self.hands_played += 1
        if winner_name == "Jogador 1":
            self.player_wins += 1
            self.current_streak = max(1, self.current_streak + 1)
        else:
            self.machine_wins += 1
            self.current_streak = min(-1, self.current_streak - 1)

        # Award the pot to the winner
        if winner_name == "Jogador 1":
            pot_amount = self.game.pot
            self.player.chips += pot_amount
            self.player.game_sequence['total_winnings'] += pot_amount
            self.machine.game_sequence['total_losses'] += pot_amount
            if pot_amount > self.player.game_sequence['biggest_pot_won']:
                self.player.game_sequence['biggest_pot_won'] = pot_amount
            self.game.pot = 0  # Clear the pot
            self.log_chip_state("Jogador vence o pote")
        else:
            pot_amount = self.game.pot
            self.machine.chips += pot_amount
            self.machine.game_sequence['total_winnings'] += pot_amount
            self.player.game_sequence['total_losses'] += pot_amount
            if pot_amount > self.machine.game_sequence['biggest_pot_won']:
                self.machine.game_sequence['biggest_pot_won'] = pot_amount
            self.game.pot = 0  # Clear the pot
            self.log_chip_state("Máquina vence o pote")

        # Update chip displays after pot is awarded
        self.update_chip_displays()

        # Log chip counts after pot is awarded
        self.log_message(f"\n💰 Depois do pagamento - Jogador 1: {self.player.chips}, Máquina: {self.machine.chips} chips")

        # Record game results
        self.game.history_manager.record_game({
            "winner": winner_name,
            "pot": pot_amount,
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

        # Update ranking
        self.game.ranking_manager.update_ranking(winner_name)

        # Show session stats
        self.log_message(f"\n=== Estatísticas da Sessão ===")
        self.log_message(f"Mãos jogadas: {self.hands_played}")
        self.log_message(f"Vitórias do Jogador: {self.player_wins}")
        self.log_message(f"Vitórias da Máquina: {self.machine_wins}")
        
        # Show streak if applicable
        streak_owner = "Jogador" if self.current_streak > 0 else "Máquina"
        streak_count = abs(self.current_streak)
        if streak_count > 1:
            self.log_message(f"🔥 {streak_owner} está em uma sequência de {streak_count} vitórias!")

        # Update UI
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
        self.new_hand_button.config(state='normal')
        self.disable_buttons()

    def enable_buttons(self):
        """Enable player action buttons"""
        self.call_button.config(state='normal')
        self.raise_button.config(state='normal')
        self.fold_button.config(state='normal')
        self.new_hand_button.config(state='disabled')

    def disable_buttons(self):
        """Disable player action buttons"""
        self.call_button.config(state='disabled')
        self.raise_button.config(state='disabled')
        self.fold_button.config(state='disabled')

    def disable_all_buttons(self):
        """Disable all game control buttons except new session"""
        self.disable_buttons()
        self.new_hand_button.config(state='disabled')
        self.new_session_button.config(state='normal')
        
    def show_game_info(self):
        """Show game rules and information"""
        info_window = tk.Toplevel(self.root)
        info_window.title("Informações sobre o Poker Texas Hold'em")
        info_window.geometry("700x500")
        info_window.configure(bg='#1a472a')
        
        # Create tabbed interface
        notebook = ttk.Notebook(info_window)
        notebook.pack(expand=True, fill='both', padx=10, pady=10)
        
        # Rules tab
        rules_frame = ttk.Frame(notebook)
        notebook.add(rules_frame, text='Regras Básicas')
        
        # Hand values tab
        hands_frame = ttk.Frame(notebook)
        notebook.add(hands_frame, text='Valores das Mãos')
        
        # Tips tab
        tips_frame = ttk.Frame(notebook)
        notebook.add(tips_frame, text='Dicas')
        
        # Rules content
        rules_content = tk.Text(rules_frame, wrap=tk.WORD, bg='#233729', fg='white', padx=10, pady=10)
        rules_content.pack(fill='both', expand=True)
        rules_content.insert(tk.END, """
REGRAS BÁSICAS DO POKER TEXAS HOLD'EM

O Texas Hold'em é uma variante do poker onde cada jogador recebe duas cartas privativas (hole cards) e cinco cartas comunitárias são reveladas no centro da mesa.

OBJETIVO:
Formar a melhor mão de cinco cartas possível usando suas duas cartas privativas e as cinco cartas comunitárias.

FASES DO JOGO:

1. PRÉ-FLOP:
   - Cada jogador recebe duas cartas viradas para baixo
   - Apostas iniciais são feitas (small blind e big blind)
   - Jogadores decidem se continuam na mão (call/raise) ou desistem (fold)

2. FLOP:
   - Três cartas comunitárias são reveladas
   - Nova rodada de apostas

3. TURN:
   - Uma quarta carta comunitária é revelada
   - Nova rodada de apostas

4. RIVER:
   - A quinta e última carta comunitária é revelada
   - Rodada final de apostas

5. SHOWDOWN:
   - Os jogadores que não desistiram revelam suas cartas
   - O jogador com a melhor mão vence o pote

AÇÕES POSSÍVEIS:
- FOLD: Desistir da mão e perder as apostas já feitas
- CHECK: Passar a vez sem apostar (só possível se ninguém apostou antes)
- CALL: Igualar a aposta atual
- RAISE: Aumentar a aposta atual
        """)
        rules_content.config(state='disabled')  # Make read-only
        
        # Hand values content
        hands_content = tk.Text(hands_frame, wrap=tk.WORD, bg='#233729', fg='white', padx=10, pady=10)
        hands_content.pack(fill='both', expand=True)
        hands_content.insert(tk.END, """
VALORES DAS MÃOS (DO MAIS ALTO PARA O MAIS BAIXO):

1. ROYAL FLUSH:
   As cinco cartas mais altas do mesmo naipe (10, J, Q, K, A)
   Ex: 10♥ J♥ Q♥ K♥ A♥

2. STRAIGHT FLUSH:
   Cinco cartas em sequência do mesmo naipe
   Ex: 5♠ 6♠ 7♠ 8♠ 9♠

3. QUADRA (FOUR OF A KIND):
   Quatro cartas do mesmo valor
   Ex: A♥ A♦ A♣ A♠ 7♦

4. FULL HOUSE:
   Uma trinca e um par
   Ex: K♥ K♦ K♣ 10♥ 10♠

5. FLUSH:
   Cinco cartas do mesmo naipe (não em sequência)
   Ex: 2♣ 5♣ 7♣ J♣ K♣

6. SEQUÊNCIA (STRAIGHT):
   Cinco cartas em sequência (não do mesmo naipe)
   Ex: 7♥ 8♦ 9♠ 10♣ J♥

7. TRINCA (THREE OF A KIND):
   Três cartas do mesmo valor
   Ex: Q♥ Q♦ Q♠ 4♣ 9♥

8. DOIS PARES (TWO PAIR):
   Dois pares diferentes
   Ex: 8♥ 8♣ 3♦ 3♠ A♥

9. PAR (ONE PAIR):
   Duas cartas do mesmo valor
   Ex: 10♥ 10♠ 6♦ 4♣ A♠

10. CARTA ALTA (HIGH CARD):
    Quando nenhuma das combinações acima é formada
    Ex: A♥ J♦ 8♣ 6♠ 2♥
        """)
        hands_content.config(state='disabled')  # Make read-only
        
        # Tips content
        tips_content = tk.Text(tips_frame, wrap=tk.WORD, bg='#233729', fg='white', padx=10, pady=10)
        tips_content.pack(fill='both', expand=True)
        tips_content.insert(tk.END, """
DICAS PARA INICIANTES:

1. SEJA SELETIVO COM SUAS MÃOS INICIAIS:
   - Pares altos (AA, KK, QQ, JJ) são sempre boas mãos para jogar
   - Cartas altas do mesmo naipe (AK, AQ, KQ) também são boas opções
   - Evite jogar mãos fracas como 7-2 ou 8-3 de naipes diferentes

2. POSIÇÃO É IMPORTANTE:
   - Jogar por último dá vantagem, pois você já viu as ações dos outros jogadores
   - Seja mais conservador em posições iniciais
   - Seja mais agressivo em posições tardias

3. LEIA O FLOP:
   - Avalie se o flop melhorou sua mão ou não
   - Considere as possíveis mãos que seus oponentes podem ter
   - Não tenha medo de desistir se o flop não ajudou sua mão

4. GERENCIE SEUS CHIPS:
   - Não arrisque todos os seus chips em mãos marginais
   - Faça apostas proporcionais ao pote
   - Saiba quando desistir para preservar seus chips

5. OBSERVE SEUS OPONENTES:
   - Preste atenção aos padrões de aposta
   - Identifique jogadores agressivos e passivos
   - Adapte sua estratégia de acordo com o estilo dos oponentes

6. SEJA PACIENTE:
   - O poker é um jogo de decisões a longo prazo
   - Nem todas as mãos serão vencedoras
   - Espere pelas oportunidades certas para maximizar seus ganhos
        """)
        tips_content.config(state='disabled')  # Make read-only
    
    def show_statistics(self):
        """Show detailed player statistics"""
        stats_window = tk.Toplevel(self.root)
        stats_window.title("Estatísticas do Jogador")
        stats_window.geometry("600x400")
        stats_window.configure(bg='#1a472a')
        
        # Create tabbed interface
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
            ttk.Label(scrollable_frame, text=f"Mãos Jogadas: {stats['hands_played']}").pack(anchor='w', padx=10)
            ttk.Label(scrollable_frame, text=f"Ganhos Totais: {stats['total_winnings']}").pack(anchor='w', padx=10)
            ttk.Label(scrollable_frame, text=f"Perdas Totais: {stats['total_losses']}").pack(anchor='w', padx=10)
            
            # Best hand
            if stats['best_hand']:
                hand_type, value = stats['best_hand']
                ttk.Label(scrollable_frame, text=f"Melhor Mão: {hand_type} ({value})").pack(anchor='w', padx=10)
            
            ttk.Label(scrollable_frame, text=f"Maior Pote Ganho: {stats['biggest_pot_won']}").pack(anchor='w', padx=10)
            
            # Hand frequencies
            ttk.Label(scrollable_frame, text="\nFrequência de Mãos", font=('Arial', 12, 'bold')).pack(pady=5)
            for hand_type, freq in stats['hand_frequencies'].items():
                ttk.Label(scrollable_frame, text=f"{hand_type}: {freq}").pack(anchor='w', padx=10)
            
            # Pack scrollbar and canvas
            scrollbar.pack(side="right", fill="y")
            canvas.pack(side="left", fill="both", expand=True)

    def _on_mousewheel(self, event):
        """Handle mouse wheel scrolling"""
        if event.num == 5 or event.delta < 0:
            # Scroll down (Linux: Button-5, Windows/Mac: negative delta)
            self.canvas.yview_scroll(1, "units")
        elif event.num == 4 or event.delta > 0:
            # Scroll up (Linux: Button-4, Windows/Mac: positive delta)
            self.canvas.yview_scroll(-1, "units")

if __name__ == "__main__":
    try:
        print("Iniciando aplicação...")
        import os
        import socket
        
        # Verifica se o usuário definiu manualmente o DISPLAY
        if 'DISPLAY' in os.environ:
            print(f"Usando DISPLAY definido pelo usuário: {os.environ['DISPLAY']}")
        else:
            # Tenta obter o IP do host Windows a partir do WSL
            try:
                # Método 1: Tenta obter o IP do host Windows usando o comando ip route
                try:
                    import subprocess
                    result = subprocess.run(['ip', 'route'], capture_output=True, text=True)
                    if result.returncode == 0:
                        # Procura pela rota padrão
                        for line in result.stdout.splitlines():
                            if 'default via' in line:
                                # O IP após "default via" é geralmente o IP do host Windows
                                wsl2_host_ip = line.split('default via ')[1].split(' ')[0]
                                os.environ['DISPLAY'] = f'{wsl2_host_ip}:0.0'
                                print(f"Configurando DISPLAY via ip route: {os.environ['DISPLAY']}")
                                break
                except Exception as e:
                    print(f"Não foi possível obter o IP via ip route: {e}")
                    
                # Método 2: Obtém o IP do host Windows do arquivo /etc/resolv.conf
                if 'DISPLAY' not in os.environ:
                    with open('/etc/resolv.conf', 'r') as f:
                        for line in f:
                            if 'nameserver' in line:
                                wsl2_host_ip = line.strip().split(' ')[1]
                                os.environ['DISPLAY'] = f'{wsl2_host_ip}:0.0'
                                print(f"Configurando DISPLAY via resolv.conf: {os.environ['DISPLAY']}")
                                break
            except:
                try:
                    # Método alternativo - tenta obter o hostname
                    hostname = socket.gethostname()
                    ip_addr = socket.gethostbyname(hostname)
                    os.environ['DISPLAY'] = f'{ip_addr}:0.0'
                    print(f"Configurando DISPLAY via hostname: {os.environ['DISPLAY']}")
                except:
                    # Fallback para configurações comuns
                    print("Não foi possível determinar o IP automaticamente")
                    print("Tentando configurações alternativas para DISPLAY")
                    
                    # Tenta várias configurações comuns para o DISPLAY
                    display_options = [
                        ':0',                  # Display local padrão
                        '127.0.0.1:0.0',       # Localhost
                        'localhost:0.0',       # Localhost por nome
                        '172.17.0.1:0.0',      # IP comum do Docker host
                        '192.168.1.1:0.0',     # IP comum de rede local
                        # IPs específicos para WSL
                        '172.21.0.1:0.0',      # Possível IP do WSL
                        '172.22.0.1:0.0',      # Possível IP do WSL
                        '172.23.0.1:0.0',      # Possível IP do WSL
                        '172.24.0.1:0.0',      # Possível IP do WSL
                        '172.25.0.1:0.0',      # Possível IP do WSL
                        '172.26.0.1:0.0',      # Possível IP do WSL
                        '172.27.0.1:0.0',      # Possível IP do WSL
                        '172.28.0.1:0.0',      # Possível IP do WSL
                        '172.29.0.1:0.0',      # Possível IP do WSL
                        '172.30.0.1:0.0',      # Possível IP do WSL
                        '172.31.0.1:0.0'       # Possível IP do WSL
                    ]
            
                    # Try each option until one works
                    for display in display_options:
                        try:
                            print(f"Tentando DISPLAY={display}")
                            os.environ['DISPLAY'] = display
                            # Test if display works by creating a temporary widget
                            test_root = tk.Tk()
                            test_root.withdraw()
                            test_root.destroy()
                            print(f"DISPLAY={display} funcionou!")
                            break
                        except Exception as e:
                            print(f"Falha com DISPLAY={display}: {e}")
                            continue
        
        # Additional configuration for PIL/Tkinter
        os.environ['PYTHONUNBUFFERED'] = '1'  # Ensure immediate output
        
        # Check if X server is accessible
        print("Verificando se o servidor X (VcXsrv) está acessível...")
        try:
            import subprocess
            # Try to run a simple X11 command to check if the server is responding
            subprocess.run(['xset', 'q'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
            print("Servidor X está acessível!")
        except Exception as e:
            print(f"AVISO: Servidor X pode não estar acessível: {e}")
            print("Continuando mesmo assim, mas pode falhar se o VcXsrv não estiver configurado corretamente.")
        
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
        print("\nDica: Você pode definir manualmente o DISPLAY usando:")
        print("   export DISPLAY=<IP-do-Windows>:0.0")
        print("   Exemplo: export DISPLAY=192.168.1.100:0.0")
        print("   Depois execute novamente: python poker_gui.py")
        print("\nPara verificar sua configuração, execute o script de diagnóstico:")
        print("   python check_display.py")
        print("   Este script verificará sua configuração e sugerirá correções.")
        import traceback
        traceback.print_exc()