#\!/usr/bin/env python3
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
        self.root.geometry("1024x700")  # Reduced window size to fit common screens
        self.root.minsize(800, 600)  # Set minimum window size
        self.root.configure(bg='#1a472a')  # Dark green poker theme
        
        # Initialize card graphics
        self.card_graphics = CardGraphics()
        self.card_back = self.card_graphics.get_card_back()
        
        # Set default window size to be taller to better show scrolling
        self.root.geometry("1024x720")  # Increased height slightly
        
        # Configure style
        style = ttk.Style()
        style.configure('TFrame', background='#1a472a')
        style.configure('TLabel', background='#1a472a', foreground='white', anchor='center')
        style.configure('TButton', padding=5)
        
        # Custom button styles
        style.configure('Action.TButton', font=('Arial', 12, 'bold'))
        style.configure('Call.TButton', background='#4caf50')
        style.configure('Raise.TButton', background='#2196f3')
        style.configure('Fold.TButton', background='#f44336')
        
        # Create a main frame to hold the canvas and scrollbar
        self.main_frame = tk.Frame(self.root)
        self.main_frame.pack(fill="both", expand=True)
        
        # Create canvas with scrollbar for vertical scrolling
        self.main_canvas = tk.Canvas(self.main_frame, bg='#1a472a')
        self.main_scrollbar = ttk.Scrollbar(self.main_frame, orient="vertical", command=self.main_canvas.yview)
        
        # Configure scrollbar and canvas
        self.main_canvas.configure(yscrollcommand=self.main_scrollbar.set)
        
        # Pack scrollbar and canvas
        self.main_scrollbar.pack(side="right", fill="y")
        self.main_canvas.pack(side="left", fill="both", expand=True)
        
        # Create a frame inside the canvas which will contain all elements
        self.main_container = ttk.Frame(self.main_canvas, style='TFrame')
        
        # Add this frame to the canvas
        self.canvas_frame = self.main_canvas.create_window((0, 0), window=self.main_container, anchor="nw")
        
        # Configure the container frame to expand to canvas width
        def _configure_canvas(event):
            # Update the width of the frame to fill the canvas
            canvas_width = event.width
            self.main_canvas.itemconfig(self.canvas_frame, width=canvas_width)
            
        self.main_canvas.bind('<Configure>', _configure_canvas)
        
        # Configure main container to resize and update scrollregion
        def _configure_scroll_region(event):
            # Update the scrollregion to encompass all content
            self.main_canvas.configure(scrollregion=self.main_canvas.bbox("all"))
            
        self.main_container.bind("<Configure>", _configure_scroll_region)
        
        # Add padding to main container
        self.main_container.pack(expand=True, fill='both', padx=20, pady=10)
        
        # Configure enhanced mousewheel scrolling to work in more environments
        def _bind_mousewheel(event):
            self.main_canvas.bind_all("<MouseWheel>", self._on_mousewheel_windows)        # Windows
            self.main_canvas.bind_all("<Button-4>", self._on_mousewheel_linux_up)         # Linux up
            self.main_canvas.bind_all("<Button-5>", self._on_mousewheel_linux_down)       # Linux down
            
        def _unbind_mousewheel(event):
            self.main_canvas.unbind_all("<MouseWheel>")
            self.main_canvas.unbind_all("<Button-4>")
            self.main_canvas.unbind_all("<Button-5>")
            
        # Bind and unbind mousewheel when entering/leaving the canvas
        self.main_canvas.bind("<Enter>", _bind_mousewheel)
        self.main_canvas.bind("<Leave>", _unbind_mousewheel)
        
        # Initially bind mousewheel to ensure it works at startup
        self.main_canvas.bind_all("<MouseWheel>", self._on_mousewheel_windows)
        self.main_canvas.bind_all("<Button-4>", self._on_mousewheel_linux_up)
        self.main_canvas.bind_all("<Button-5>", self._on_mousewheel_linux_down)
        
        # Add keyboard navigation bindings
        self.root.bind("<Prior>", lambda event: self.main_canvas.yview_scroll(-10, "units"))  # Page Up
        self.root.bind("<Next>", lambda event: self.main_canvas.yview_scroll(10, "units"))    # Page Down
        self.root.bind("<Home>", lambda event: self.main_canvas.yview_moveto(0))              # Home
        self.root.bind("<End>", lambda event: self.main_canvas.yview_moveto(1.0))             # End
        
        # Use arrow keys for scrolling too
        self.root.bind("<Up>", lambda event: self.main_canvas.yview_scroll(-1, "units"))
        self.root.bind("<Down>", lambda event: self.main_canvas.yview_scroll(1, "units"))
        
        # Add a scroll instruction banner
        self.scroll_instruction = tk.Frame(self.main_container, bg='#0a3a1a', padx=10, pady=5)
        self.scroll_instruction.pack(fill='x', pady=(0, 10))
        
        scroll_label = tk.Label(
            self.scroll_instruction,
            text="↕️ ROLE A TELA PARA VER TODO O CONTEÚDO ↕️",
            font=('Arial', 12, 'bold'),
            fg='#FFFFFF',
            bg='#0a3a1a'
        )
        scroll_label.pack(fill='x')
        
        # Add scroll up/down buttons inside instruction banner
        scroll_buttons = tk.Frame(self.scroll_instruction, bg='#0a3a1a')
        scroll_buttons.pack(pady=5)
        
        scroll_up = ttk.Button(
            scroll_buttons,
            text="⬆️ Rolar para Cima",
            command=lambda: self.main_canvas.yview_scroll(-10, "units"),
            width=20
        )
        scroll_up.pack(side='left', padx=10)
        
        scroll_down = ttk.Button(
            scroll_buttons,
            text="⬇️ Rolar para Baixo",
            command=lambda: self.main_canvas.yview_scroll(10, "units"),
            width=20
        )
        scroll_down.pack(side='left', padx=10)
        
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
        # Top section: Game phase banner
        self.phase_banner_frame = tk.Frame(
            self.main_container,
            bg='#0a1f12',
            height=60
        )
        self.phase_banner_frame.pack(fill='x', pady=(0, 10))
        
        # Phase indicator
        self.phase_label = tk.Label(
            self.phase_banner_frame,
            text="FASE: PRÉ-FLOP",
            font=('Arial', 18, 'bold'),
            fg='#FFD700',
            bg='#0a1f12'
        )
        self.phase_label.pack(fill='both', expand=True, pady=10)
        
        # Winner announcement frame (initially hidden)
        self.winner_frame = tk.Frame(
            self.main_container,
            bg='#0a1f12',
            height=60
        )
        self.winner_frame.pack(fill='x', pady=(0, 10))
        self.winner_frame.pack_forget()  # Initially hidden
        
        self.winner_label = tk.Label(
            self.winner_frame,
            text="",
            font=('Arial', 22, 'bold'),
            fg='#FFD700',
            bg='#0a1f12'
        )
        self.winner_label.pack(fill='both', expand=True, pady=10)
        
        # Opponent section
        self.opponent_section = tk.Frame(self.main_container, bg='#1a472a')
        self.opponent_section.pack(fill='x', pady=10)
        
        # Opponent info and cards
        self.opponent_info = tk.Frame(self.opponent_section, bg='#1a472a')
        self.opponent_info.pack(side='left', padx=20)
        
        self.machine_name_label = tk.Label(
            self.opponent_info, 
            text="MÁQUINA", 
            font=('Arial', 14, 'bold'),
            fg='white', 
            bg='#1a472a'
        )
        self.machine_name_label.pack(anchor='w', pady=(0, 5))
        
        self.machine_chips_box = tk.Frame(
            self.opponent_info,
            bg='#233729',
            highlightbackground='#FF6347',  # Red for opponent
            highlightthickness=2,
            padx=10,
            pady=5
        )
        self.machine_chips_box.pack(anchor='w')
        
        self.machine_chips_display = tk.Label(
            self.machine_chips_box,
            text="1000 💰",
            font=('Arial', 14, 'bold'),
            fg='#FFD700',
            bg='#233729'
        )
        self.machine_chips_display.pack(anchor='w')
        
        # Opponent cards frame
        self.opponent_cards_frame = tk.Frame(self.opponent_section, bg='#1a472a')
        self.opponent_cards_frame.pack(side='right', padx=20)
        
        # Opponent card labels
        self.opponent_card_labels = []
        for i in range(2):
            label = ttk.Label(self.opponent_cards_frame)
            label.pack(side='left', padx=5)
            self.opponent_card_labels.append(label)
        
        # Community cards section
        self.community_section = tk.Frame(self.main_container, bg='#1a472a')
        self.community_section.pack(fill='x', pady=20)
        
        # Pot display
        self.pot_frame = tk.Frame(self.community_section, bg='#1a472a')
        self.pot_frame.pack(side='top', pady=10)
        
        self.pot_label = tk.Label(
            self.pot_frame,
            text="POTE ATUAL",
            font=('Arial', 14, 'bold'),
            fg='white',
            bg='#1a472a'
        )
        self.pot_label.pack()
        
        self.pot_box = tk.Frame(
            self.pot_frame,
            bg='#233729',
            highlightbackground='#FF9900',
            highlightthickness=3,
            padx=15,
            pady=10
        )
        self.pot_box.pack()
        
        self.pot_display = tk.Label(
            self.pot_box,
            text="0 💰",
            font=('Arial', 18, 'bold'),
            fg='#FF9900',
            bg='#233729'
        )
        self.pot_display.pack()
        
        # Current bet display
        self.current_bet_frame = tk.Frame(self.community_section, bg='#1a472a')
        self.current_bet_frame.pack(side='top', pady=5)
        
        self.current_bet_label = tk.Label(
            self.current_bet_frame,
            text="APOSTA ATUAL",
            font=('Arial', 12),
            fg='white',
            bg='#1a472a'
        )
        self.current_bet_label.pack()
        
        self.current_bet_box = tk.Frame(
            self.current_bet_frame,
            bg='#233729',
            highlightbackground='#90EE90',
            highlightthickness=2,
            padx=10,
            pady=5
        )
        self.current_bet_box.pack()
        
        self.current_bet_display = tk.Label(
            self.current_bet_box,
            text="50 💰",
            font=('Arial', 14, 'bold'),
            fg='#90EE90',
            bg='#233729'
        )
        self.current_bet_display.pack()
        
        # Community cards frame
        self.community_cards_label = tk.Label(
            self.community_section,
            text="CARTAS COMUNITÁRIAS",
            font=('Arial', 14, 'bold'),
            fg='white', 
            bg='#1a472a'
        )
        self.community_cards_label.pack(pady=(20, 10))
        
        self.community_cards_frame = tk.Frame(self.community_section, bg='#1a472a')
        self.community_cards_frame.pack(pady=10)
        
        # Table background for community cards - green felt
        self.table_bg = tk.Frame(
            self.community_cards_frame,
            bg='#0a3b0a',
            width=550,
            height=160,
            padx=10,
            pady=10,
            relief=tk.RIDGE,
            borderwidth=3
        )
        self.table_bg.pack()
        self.table_bg.pack_propagate(False)  # Maintain the size
        
        # Community card labels
        self.community_card_container = tk.Frame(self.table_bg, bg='#0a3b0a')
        self.community_card_container.pack(expand=True, fill='both')
        
        self.community_card_labels = []
        for i in range(5):
            label = ttk.Label(self.community_card_container, background='#0a3b0a')
            label.pack(side='left', padx=5)
            self.community_card_labels.append(label)
        
        # Player section
        self.player_section = tk.Frame(self.main_container, bg='#1a472a')
        self.player_section.pack(fill='x', pady=(20, 10))
        
        # Player cards
        self.player_cards_frame = tk.Frame(self.player_section, bg='#1a472a')
        self.player_cards_frame.pack(side='right', padx=20)
        
        self.player_card_labels = []
        for i in range(2):
            label = ttk.Label(self.player_cards_frame)
            label.pack(side='left', padx=5)
            self.player_card_labels.append(label)
        
        # Player info
        self.player_info = tk.Frame(self.player_section, bg='#1a472a')
        self.player_info.pack(side='left', padx=20)
        
        self.player_name_label = tk.Label(
            self.player_info, 
            text="JOGADOR 1", 
            font=('Arial', 14, 'bold'),
            fg='white', 
            bg='#1a472a'
        )
        self.player_name_label.pack(anchor='w', pady=(0, 5))
        
        self.player_chips_box = tk.Frame(
            self.player_info,
            bg='#233729',
            highlightbackground='#FFD700',  # Gold for player
            highlightthickness=2,
            padx=10,
            pady=5
        )
        self.player_chips_box.pack(anchor='w')
        
        self.player_chips_display = tk.Label(
            self.player_chips_box,
            text="1000 💰",
            font=('Arial', 14, 'bold'),
            fg='#FFD700',
            bg='#233729'
        )
        self.player_chips_display.pack(anchor='w')
        
        # Player action buttons
        self.action_buttons_frame = tk.Frame(self.main_container, bg='#1a472a')
        self.action_buttons_frame.pack(fill='x', pady=10)
        
        # Player's hand strength indicator
        self.hand_strength_frame = tk.Frame(self.action_buttons_frame, bg='#1a472a')
        self.hand_strength_frame.pack(side='left', padx=20)
        
        self.hand_strength_label = tk.Label(
            self.hand_strength_frame,
            text="SUA MÃO:",
            font=('Arial', 12),
            fg='white',
            bg='#1a472a'
        )
        self.hand_strength_label.pack(anchor='w')
        
        self.hand_type_display = tk.Label(
            self.hand_strength_frame,
            text="-",
            font=('Arial', 14, 'bold'),
            fg='#90EE90',
            bg='#1a472a'
        )
        self.hand_type_display.pack(anchor='w')
        
        # Control buttons - improved styling
        self.button_container = tk.Frame(self.action_buttons_frame, bg='#1a472a')
        self.button_container.pack(side='right', padx=20)
        
        self.call_button = ttk.Button(
            self.button_container,
            text="CALL",
            command=self.call_action,
            style='Action.TButton',
            width=16
        )
        self.call_button.pack(side='left', padx=8)
        
        self.raise_button = ttk.Button(
            self.button_container,
            text="RAISE",
            command=self.raise_action,
            style='Action.TButton',
            width=16
        )
        self.raise_button.pack(side='left', padx=8)
        
        self.fold_button = ttk.Button(
            self.button_container,
            text="FOLD",
            command=self.fold_action,
            style='Action.TButton',
            width=16
        )
        self.fold_button.pack(side='left', padx=8)
        
        # Hand progress indicators
        self.progress_frame = tk.Frame(self.main_container, bg='#1a472a')
        self.progress_frame.pack(fill='x', pady=10)
        
        self.hand_progress_label = tk.Label(
            self.progress_frame,
            text="PROGRESSO DA MÃO:",
            font=('Arial', 12),
            fg='white',
            bg='#1a472a'
        )
        self.hand_progress_label.pack(anchor='w', padx=20)
        
        self.hand_progress_container = tk.Frame(self.progress_frame, bg='#1a472a')
        self.hand_progress_container.pack(fill='x', padx=20, pady=5)
        
        self.hand_stages = ["Pré-Flop", "Flop", "Turn", "River", "Showdown"]
        self.hand_stage_indicators = []
        
        # Create progress indicators for each stage
        for i, stage in enumerate(self.hand_stages):
            stage_frame = tk.Frame(self.hand_progress_container, bg='#1a472a')
            stage_frame.pack(side='left', expand=True, fill='x')
            
            # Visual connection line
            if i > 0:
                line_frame = tk.Frame(stage_frame, bg='#444444', height=2)
                line_frame.pack(fill='x', pady=10)
            
            # Stage indicator
            indicator = tk.Label(
                stage_frame,
                text="○",
                font=('Arial', 18),
                fg='#888888',
                bg='#1a472a'
            )
            indicator.pack(anchor='center')
            
            # Stage name
            name_label = tk.Label(
                stage_frame,
                text=stage,
                font=('Arial', 10),
                fg='#888888',
                bg='#1a472a'
            )
            name_label.pack(anchor='center')
            
            self.hand_stage_indicators.append((indicator, name_label))
        
        # Game action history
        self.history_frame = tk.Frame(self.main_container, bg='#0a1f12')
        self.history_frame.pack(fill='both', expand=True, pady=10)
        
        self.history_label = tk.Label(
            self.history_frame,
            text="HISTÓRICO DE AÇÕES",
            font=('Arial', 12, 'bold'),
            fg='white',
            bg='#0a1f12'
        )
        self.history_label.pack(pady=5)
        
        # Scrollable history view
        self.history_canvas = tk.Canvas(
            self.history_frame,
            bg='#0a1f12',
            highlightthickness=0
        )
        self.history_scrollbar = ttk.Scrollbar(
            self.history_frame,
            orient="vertical",
            command=self.history_canvas.yview
        )
        
        self.history_scrollable_frame = ttk.Frame(self.history_canvas)
        
        self.history_scrollable_frame.bind(
            "<Configure>",
            lambda e: self.history_canvas.configure(scrollregion=self.history_canvas.bbox("all"))
        )
        
        self.history_canvas.create_window(
            (0, 0),
            window=self.history_scrollable_frame,
            anchor="nw",
            width=self.history_canvas.winfo_width()
        )
        self.history_canvas.configure(yscrollcommand=self.history_scrollbar.set)
        
        self.history_scrollbar.pack(side="right", fill="y")
        self.history_canvas.pack(side="left", fill="both", expand=True)
        
        # Fix scrollbar visibility issue - make sure it extends throughout the window
        self.main_scrollbar.lift()  # Bring scrollbar to front
        
        # Bottom navigation buttons
        self.nav_buttons_frame = tk.Frame(self.main_container, bg='#1a472a')
        self.nav_buttons_frame.pack(fill='x', pady=10)
        
        # Add scroll navigation buttons for easier interface navigation
        self.scroll_buttons_frame = tk.Frame(self.main_container, bg='#1a472a')
        self.scroll_buttons_frame.pack(fill='x', pady=5)
        
        # Create scroll navigation buttons
        self.scroll_top_button = ttk.Button(
            self.scroll_buttons_frame,
            text="⬆️ Topo",
            command=lambda: self.scroll_to_view(0),
            width=12
        )
        self.scroll_top_button.pack(side='left', padx=5)
        
        self.scroll_cards_button = ttk.Button(
            self.scroll_buttons_frame,
            text="🃏 Cartas",
            command=lambda: self.scroll_to_view(0.3),
            width=12
        )
        self.scroll_cards_button.pack(side='left', padx=5)
        
        self.scroll_player_button = ttk.Button(
            self.scroll_buttons_frame,
            text="👤 Jogador",
            command=lambda: self.scroll_to_view(0.4),
            width=12
        )
        self.scroll_player_button.pack(side='left', padx=5)
        
        self.scroll_log_button = ttk.Button(
            self.scroll_buttons_frame,
            text="📜 Histórico",
            command=lambda: self.scroll_to_view(0.8),
            width=12
        )
        self.scroll_log_button.pack(side='left', padx=5)
        
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
        
        # Add a bottom scroll instruction for clarity
        self.bottom_scroll_frame = tk.Frame(self.main_container, bg='#0a3a1a', padx=10, pady=5)
        self.bottom_scroll_frame.pack(fill='x', pady=10)
        
        bottom_scroll_label = tk.Label(
            self.bottom_scroll_frame,
            text="↕️ ROLE A TELA PARA VER TODO O CONTEÚDO ↕️",
            font=('Arial', 12, 'bold'),
            fg='#FFFFFF',
            bg='#0a3a1a'
        )
        bottom_scroll_label.pack(fill='x')
        
        # Add scroll buttons inside bottom instruction banner
        bottom_scroll_buttons = tk.Frame(self.bottom_scroll_frame, bg='#0a3a1a')
        bottom_scroll_buttons.pack(pady=5)
        
        bottom_scroll_up = ttk.Button(
            bottom_scroll_buttons,
            text="⬆️ Rolar para Cima",
            command=lambda: self.main_canvas.yview_scroll(-10, "units"),
            width=20
        )
        bottom_scroll_up.pack(side='left', padx=10)
        
        bottom_scroll_down = ttk.Button(
            bottom_scroll_buttons,
            text="⬇️ Rolar para Baixo",
            command=lambda: self.main_canvas.yview_scroll(10, "units"),
            width=20
        )
        bottom_scroll_down.pack(side='left', padx=10)

    def _on_mousewheel_windows(self, event):
        """Handle mousewheel scrolling in Windows"""
        self.main_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        
    def _on_mousewheel_linux_up(self, event):
        """Handle mousewheel scrolling up in Linux"""
        self.main_canvas.yview_scroll(-1, "units")
        
    def _on_mousewheel_linux_down(self, event):
        """Handle mousewheel scrolling down in Linux"""
        self.main_canvas.yview_scroll(1, "units")
            
    def setup_components(self):
        """Configure additional UI components and event handlers"""
        # Initial state of buttons
        self.disable_buttons()
        self.new_hand_button.config(state='disabled')

    def log_message(self, message):
        """Add a message to the game log with formatting"""
        # Store message in history
        self.message_history.append(message)
        
        # Determine icon and colors based on message content
        icon = "🔄"  # Default icon
        bg_color = "#0a1f12"  # Default background
        fg_color = "#e0e0e0"  # Default text color
        
        # Apply specific styling based on message content
        if message.startswith('==='):
            icon = "📌"
            bg_color = "#1a3a2a"
        elif '🏆' in message:
            icon = "🏆"
            bg_color = "#2a3a1a"
            fg_color = "#90EE90"  # Light green
        elif 'chips' in message.lower() or '💰' in message:
            icon = "💰"
            bg_color = "#3a2a1a"
            fg_color = "#FFD700"  # Gold
        elif 'Jogador: Call' in message or 'Máquina: Call' in message:
            icon = "✅"
        elif 'Jogador: Raise' in message or 'Máquina: Raise' in message:
            icon = "⬆️"
        elif 'Fold' in message:
            icon = "❌"
        elif 'Flop' in message:
            icon = "🃏"
        elif 'Turn' in message:
            icon = "🃏"
        elif 'River' in message:
            icon = "🃏"
            
        # Create message frame
        message_frame = tk.Frame(
            self.history_scrollable_frame,
            background=bg_color,
            padx=5,
            pady=3
        )
        message_frame.pack(fill='x', pady=2, padx=5)
        
        # Add icon
        icon_label = tk.Label(
            message_frame,
            text=icon,
            font=('Arial', 12),
            foreground=fg_color,
            background=bg_color
        )
        icon_label.pack(side='left', padx=5)
        
        # Add message text
        text_label = tk.Label(
            message_frame,
            text=message,
            wraplength=800,
            foreground=fg_color,
            background=bg_color,
            justify='left',
            anchor='w'
        )
        text_label.pack(side='left', padx=5, fill='x', expand=True)
        
        # Scroll history canvas to bottom
        self.history_canvas.update_idletasks()
        self.history_canvas.yview_moveto(1.0)
        
        # If this is an important message (like a phase change or winning), 
        # scroll the main window to show the game log
        if message.startswith('===') or '🏆' in message:
            self.scroll_to_view(0.9)  # Scroll to see game log area
            
        self.root.update()
        
        # Update hand stats if needed
        self.update_game_info(message)
        
    def log_chip_state(self, action):
        """Log the current state of all chips"""
        total = self.player.chips + self.machine.chips + self.game.pot
        message = f"\n[{action}]\n"
        message += f"Jogador: {self.player.chips} chips\n"
        message += f"Máquina: {self.machine.chips} chips\n"
        message += f"Pote: {self.game.pot} chips\n"
        message += f"Total: {total} chips"
        if total != 2000:
            message += f" ⚠️ ERRO: Total deveria ser 2000\!"
            # Fix chip total if there's an error
            self.fix_chip_conservation()
        self.log_message(message)
        
        # Update chip displays
        self.update_chip_displays()
        
    def fix_chip_conservation(self):
        """Ensure total chips in play equals the starting amount (2000)"""
        total = self.player.chips + self.machine.chips + self.game.pot
        if total != 2000:
            # Add a note about the correction
            self.log_message("⚠️ Corrigindo conservação de chips...")
            
            # Calculate deficit
            deficit = 2000 - total
            
            # If deficit is positive, add to pot
            if deficit > 0:
                self.game.pot += deficit
                self.log_message(f"Adicionado {deficit} chips ao pote")
            # If deficit is negative, remove from pot if possible
            elif deficit < 0 and self.game.pot >= abs(deficit):
                self.game.pot -= abs(deficit)
                self.log_message(f"Removido {abs(deficit)} chips do pote")
            # If can't remove from pot, adjust player chips
            elif deficit < 0:
                remaining = abs(deficit) - self.game.pot
                self.game.pot = 0
                # Distribute remaining correction between players
                player_adjustment = remaining // 2
                self.player.chips -= player_adjustment
                self.machine.chips -= (remaining - player_adjustment)
                self.log_message(f"Ajustado chips dos jogadores: {player_adjustment} cada")
            
            # Verify correction
            new_total = self.player.chips + self.machine.chips + self.game.pot
            self.log_message(f"Total corrigido: {new_total} chips")
        
    def update_chip_displays(self):
        """Update all chip displays in the UI"""
        self.player_chips_display.config(text=f"{self.player.chips} 💰")
        self.machine_chips_display.config(text=f"{self.machine.chips} 💰")
        self.pot_display.config(text=f"{self.game.pot} 💰")
        self.current_bet_display.config(text=f"{self.current_bet} 💰")
        
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
        """Update the hand progress indicators"""
        # Update stage indicators
        for i, (indicator, label) in enumerate(self.hand_stage_indicators):
            if i <= stage_index:
                # Current/completed stage
                indicator.config(text="●", fg="#FFD700")  # Gold
                label.config(fg="#FFD700")
            else:
                # Future stage
                indicator.config(text="○", fg="#888888")
                label.config(fg="#888888")
                
        # Update phase banner
        phases = ["PRÉ-FLOP", "FLOP", "TURN", "RIVER", "SHOWDOWN"]
        if 0 <= stage_index < len(phases):
            self.phase_label.config(text=f"FASE: {phases[stage_index]}")
            
            # Different colors for each phase
            colors = {
                0: ("#FFD700", "#0a1f12"),  # Gold on dark green (Pre-flop)
                1: ("#90EE90", "#0a1f12"),  # Light green on dark green (Flop)
                2: ("#87CEEB", "#0a1f12"),  # Light blue on dark green (Turn)
                3: ("#FFA07A", "#0a1f12"),  # Light salmon on dark green (River)
                4: ("#FF6347", "#0a1f12"),  # Tomato on dark green (Showdown)
            }
            
            fg_color, bg_color = colors.get(stage_index, ("#FFFFFF", "#0a1f12"))
            self.phase_label.config(fg=fg_color, bg=bg_color)
            self.phase_banner_frame.config(bg=bg_color)

    def scroll_to_view(self, y_position=None):
        """Scroll the main canvas to a specific position or default to middle view"""
        self.main_canvas.update_idletasks()  # Ensure canvas is updated
        if y_position is None:
            # Default to middle view
            self.main_canvas.yview_moveto(0.3)
        else:
            # Scroll to specific position
            self.main_canvas.yview_moveto(y_position)
            
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
        
        # Update opponent cards
        for i, label in enumerate(self.opponent_card_labels):
            if i < len(self.machine.hand):
                # Only show machine's cards at showdown if no one folded
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
        
        # Update player cards
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
            player.current_bet = 0  # Reset current bet
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
        
        for widget in self.history_scrollable_frame.winfo_children():
            widget.destroy()
            
        # Reset hand stats and progress
        self.hand_type_display.config(text="-")
        self.update_progress_indicators(0)  # Reset progress
        
        # Hide winner frame if visible
        if hasattr(self, 'winner_frame') and self.winner_frame is not None:
            self.winner_frame.pack_forget()
        
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
        self.player.current_bet = 0  # Reset current bet for this hand
        self.machine.hand = []
        self.machine.folded = False
        self.machine.current_bet = 0  # Reset current bet for this hand
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
        
        # Update round bets and player tracking
        self.player_bet_in_round = small_blind
        self.machine_bet_in_round = big_blind
        self.player.current_bet = small_blind
        self.machine.current_bet = big_blind
        
        # Log blinds
        self.log_message(f"Jogador 1 posta small blind: {small_blind}")
        self.log_message(f"Máquina posta big blind: {big_blind}")
        self.log_chip_state("Blinds postados")
        
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
        
        # Scroll to see player's cards
        self.scroll_to_view(0.4)

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
                # Update player's current_bet for consistency
                self.player.current_bet = self.player_bet_in_round
                self.log_message(f"Jogador: Call {additional_bet} (Total na rodada: {self.player_bet_in_round})")
                self.log_chip_state("Jogador Call")
            else:
                # All-in call
                all_in_amount = self.player.chips
                self.player.chips = 0
                self.game.pot += all_in_amount
                self.player_bet_in_round += all_in_amount
                # Update player's current_bet for consistency
                self.player.current_bet = self.player_bet_in_round
                self.log_message(f"Jogador: All-in Call {all_in_amount} (Total na rodada: {self.player_bet_in_round})")
                self.log_chip_state("Jogador All-in")
        else:
            # Check (no additional bet)
            self.log_message(f"Jogador: Check (Total na rodada: {self.player_bet_in_round})")
            self.log_chip_state("Jogador Check")
        
        # Update UI before machine action
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
            
            # Update player's current_bet for consistency
            self.player.current_bet = self.player_bet_in_round
            
            self.log_message(f"Jogador: Raise para {total_amount} (Total na rodada: {self.player_bet_in_round})")
            self.log_chip_state("Jogador Raise")
            
            # Update UI before machine action
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
            
            # Update player's current_bet for consistency
            self.player.current_bet = self.player_bet_in_round
            
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
            self.log_message("⚠️ Chips insuficientes para raise\! Use Call para all-in.")

    def fold_action(self):
        """Player chooses to fold"""
        self.player.folded = True
        self.log_message("Jogador: Fold")
        self.end_hand("Máquina")
        self.disable_buttons()
        self.new_hand_button.config(state='normal')

    def machine_action(self):
        """Handle machine's betting action"""
        # Scroll to see machine's area
        self.scroll_to_view(0.15)
        # Store initial state
        initial_machine_chips = self.machine.chips
        initial_pot = self.game.pot
        
        # Log state before action
        self.log_message(f"\nAntes da ação da Máquina:")
        self.log_chip_state("Estado Inicial")
        
        # Get machine's decision
        action, amount = self.machine.make_decision(self.game.community_cards, self.player_bet_in_round, self.game.min_raise)
        
        if action == "fold":
            # Machine folds
            self.machine.folded = True
            self.log_message("Máquina: Fold")
            return
        elif action == "raise":
            # Machine raises
            if amount <= initial_machine_chips:
                # Calculate call and raise amounts
                call_amount = self.player_bet_in_round - self.machine_bet_in_round
                raise_amount = amount - call_amount  # Use the actual raise amount returned by AI
                total_amount = call_amount + raise_amount
                
                if total_amount <= initial_machine_chips:
                    # Standard raise
                    self.machine.chips = initial_machine_chips - total_amount
                    self.game.pot = initial_pot + total_amount
                    self.machine_bet_in_round += total_amount
                    self.current_bet = self.machine_bet_in_round
                    # Update machine's current_bet for consistency
                    self.machine.current_bet = self.machine_bet_in_round
                    
                    self.log_message(f"Máquina: Raise para {total_amount} (Total na rodada: {self.machine_bet_in_round})")
                    self.log_chip_state("Máquina Raise")
                    self.betting_round_complete = False  # Reset flag as player needs to act again
                else:
                    # All-in raise
                    self.machine.chips = 0
                    self.game.pot = initial_pot + initial_machine_chips
                    self.machine_bet_in_round += initial_machine_chips
                    self.current_bet = self.machine_bet_in_round
                    # Update machine's current_bet for consistency
                    self.machine.current_bet = self.machine_bet_in_round
                    
                    self.log_message(f"Máquina: All-in Raise para {initial_machine_chips} (Total na rodada: {self.machine_bet_in_round})")
                    self.log_chip_state("Máquina All-in")
                    self.betting_round_complete = False  # Reset flag
        else:  # call/check
            if self.current_bet > 0:
                # Calculate call amount
                call_amount = self.player_bet_in_round - self.machine_bet_in_round
                
                if call_amount > 0:
                    if call_amount <= initial_machine_chips:
                        # Standard call
                        self.machine.chips = initial_machine_chips - call_amount
                        self.game.pot = initial_pot + call_amount
                        self.machine_bet_in_round += call_amount
                        # Update machine's current_bet for consistency
                        self.machine.current_bet = self.machine_bet_in_round
                        
                        self.log_message(f"Máquina: Call {call_amount} (Total na rodada: {self.machine_bet_in_round})")
                        self.log_chip_state("Máquina Call")
                    else:
                        # All-in call
                        self.machine.chips = 0
                        self.game.pot = initial_pot + initial_machine_chips
                        self.machine_bet_in_round += initial_machine_chips
                        # Update machine's current_bet for consistency
                        self.machine.current_bet = self.machine_bet_in_round
                        
                        self.log_message(f"Máquina: All-in Call {initial_machine_chips} (Total na rodada: {self.machine_bet_in_round})")
                        self.log_chip_state("Máquina All-in")
                else:
                    # Check (bet already matched)
                    self.log_message(f"Máquina: Check (Total na rodada: {self.machine_bet_in_round})")
                    self.log_chip_state("Máquina Check")
            else:
                # Check (no bet to match)
                self.log_message(f"Máquina: Check (Total na rodada: {self.machine_bet_in_round})")
                self.log_chip_state("Máquina Check")

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
            self.player.current_bet = 0
            self.machine.current_bet = 0
            self.betting_round_complete = False
            
            # Log state after dealing flop
            self.log_chip_state("Estado após o Flop")
            
            # Scroll to see community cards
            self.scroll_to_view(0.3)
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
            self.player.current_bet = 0
            self.machine.current_bet = 0
            self.betting_round_complete = False
            
            # Log state after dealing turn
            self.log_chip_state("Estado após o Turn")
            
            # Scroll to see community cards
            self.scroll_to_view(0.3)
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
            self.player.current_bet = 0
            self.machine.current_bet = 0
            self.betting_round_complete = False
            
            # Log state after dealing river
            self.log_chip_state("Estado após o River")
            
            # Scroll to see community cards
            self.scroll_to_view(0.3)
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
                
            result += f"🏆 {winner_name} vence\!"
            self.log_message(result)
        
        # Show winner banner
        if self.winner_frame is not None:
            self.winner_frame.pack(fill='x', pady=(0, 10))
            
            if self.winner_label is not None:
                if winner_by_fold:
                    self.winner_label.config(
                        text=f"🏆 {winner_name} VENCE POR DESISTÊNCIA\! 🏆",
                        fg="#FFD700" if winner_name == "Jogador 1" else "#FF6347"
                    )
                    self.log_message(f"\n🏆 {winner_name} vence por desistência\!")
                else:
                    self.winner_label.config(
                        text=f"🏆 {winner_name} VENCE COM {winner_hand_type}\! 🏆",
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
            self.log_message(f"🔥 {streak_owner} está em uma sequência de {streak_count} vitórias\!")

        # Update UI
        self.update_display()

        # Check if session should end
        if self.player.chips <= 0:
            self.log_message("\n🏆 Máquina vence a sessão\! Jogador ficou sem chips.")
            self.disable_all_buttons()
            return
        if self.machine.chips <= 0:
            self.log_message("\n🏆 Jogador vence a sessão\! Máquina ficou sem chips.")
            self.disable_all_buttons()
            return
        if self.player.chips >= self.target_chips:
            self.log_message(f"\n🏆 Jogador vence a sessão\! Alcançou {self.target_chips} chips\!")
            self.disable_all_buttons()
            return
        if self.machine.chips >= self.target_chips:
            self.log_message(f"\n🏆 Máquina vence a sessão\! Alcançou {self.target_chips} chips\!")
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
                            print(f"DISPLAY={display} funcionou\!")
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
            print("Servidor X está acessível\!")
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
