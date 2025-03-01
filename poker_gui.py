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
        self.root.geometry("1280x1024")  # Larger window to ensure all elements are visible
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
        
        # Rastreamento de apostas na mão atual
        self.player_bet_in_round = 0
        self.machine_bet_in_round = 0
        
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
        # Banner para fase das apostas
        self.phase_banner_frame = tk.Frame(
            self.main_container,
            bg='#0a1f12',  # Verde escuro
            height=40
        )
        self.phase_banner_frame.pack(fill='x', pady=(0, 5))
        
        # Label para mostrar a fase atual
        self.phase_label = tk.Label(
            self.phase_banner_frame,
            text="FASE: PRÉ-FLOP",
            font=('Arial', 16, 'bold'),
            fg='#FFD700',  # Dourado
            bg='#0a1f12'   # Verde escuro
        )
        self.phase_label.pack(fill='both', expand=True)
        
        # Frame superior para cartas comunitárias
        self.community_frame = ttk.Frame(self.main_container)
        self.community_frame.pack(pady=5, fill='x')
        
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
        
        # Frame para botões
        self.control_frame = ttk.Frame(self.main_container)
        self.control_frame.pack(pady=5, fill='x', side='bottom')
        
        # Frame para painel de informações do jogo (com altura limitada)
        self.info_panel_frame = ttk.Frame(self.main_container)
        self.info_panel_frame.pack(pady=5, fill='both', expand=True)
        
        # Definir altura para o painel de informações
        self.info_panel_frame.config(height=230)  # Aumentado para mostrar mais conteúdo
        
        # Criar notebook para abas de informações
        self.info_notebook = ttk.Notebook(self.info_panel_frame)
        self.info_notebook.pack(fill='both', expand=True, padx=15, pady=5)
        
        # Aba de histórico de ações
        self.action_history_frame = ttk.Frame(self.info_notebook)
        self.info_notebook.add(self.action_history_frame, text="Histórico de Ações")
        
        # Aba de estatísticas da mão atual
        self.hand_stats_frame = ttk.Frame(self.info_notebook)
        self.info_notebook.add(self.hand_stats_frame, text="Estatísticas da Mão")
        
        # Aba de chips e apostas
        self.chips_frame = ttk.Frame(self.info_notebook)
        self.info_notebook.add(self.chips_frame, text="Estatísticas")
        
        # Configurar o frame de histórico de ações
        self.action_history_canvas = tk.Canvas(
            self.action_history_frame,
            bg='#0a1f12',
            highlightthickness=0,
            height=180  # Aumentado para mostrar mais mensagens
        )
        self.action_history_scrollbar = ttk.Scrollbar(
            self.action_history_frame,
            orient="vertical",
            command=self.action_history_canvas.yview
        )
        self.action_history_scrollable_frame = ttk.Frame(self.action_history_canvas)
        
        self.action_history_scrollable_frame.bind(
            "<Configure>",
            lambda e: self.action_history_canvas.configure(scrollregion=self.action_history_canvas.bbox("all"))
        )
        
        self.action_history_canvas.create_window(
            (0, 0),
            window=self.action_history_scrollable_frame,
            anchor="nw"
        )
        self.action_history_canvas.configure(yscrollcommand=self.action_history_scrollbar.set)
        
        self.action_history_scrollbar.pack(side="right", fill="y")
        self.action_history_canvas.pack(side="left", fill="both", expand=True)
        
        # Configurar o frame de estatísticas da mão
        self.hand_stats_content = ttk.Frame(self.hand_stats_frame)
        self.hand_stats_content.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Estatísticas da mão atual
        self.player_hand_type_label = ttk.Label(
            self.hand_stats_content,
            text="Sua mão: -",
            font=('Arial', 12, 'bold')
        )
        self.player_hand_type_label.pack(anchor='w', pady=5)
        
        self.machine_hand_type_label = ttk.Label(
            self.hand_stats_content,
            text="Mão da máquina: -",
            font=('Arial', 12, 'bold')
        )
        self.machine_hand_type_label.pack(anchor='w', pady=5)
        
        self.hand_progress_label = ttk.Label(
            self.hand_stats_content,
            text="Progresso da mão:",
            font=('Arial', 12)
        )
        self.hand_progress_label.pack(anchor='w', pady=5)
        
        # Barra de progresso da mão
        self.hand_progress_frame = ttk.Frame(self.hand_stats_content)
        self.hand_progress_frame.pack(fill='x', pady=5)
        
        self.hand_stages = ["Pré-Flop", "Flop", "Turn", "River", "Showdown"]
        self.hand_stage_labels = []
        
        for stage in self.hand_stages:
            stage_frame = ttk.Frame(self.hand_progress_frame)
            stage_frame.pack(side='left', expand=True, fill='x')
            
            stage_indicator = ttk.Label(
                stage_frame,
                text="○",
                font=('Arial', 14),
                foreground='#888888'
            )
            stage_indicator.pack(anchor='center')
            
            stage_label = ttk.Label(
                stage_frame,
                text=stage,
                font=('Arial', 9)
            )
            stage_label.pack(anchor='center')
            
            self.hand_stage_labels.append((stage_indicator, stage_label))
        
        # Configurar o frame de chips e apostas
        self.chips_content = ttk.Frame(self.chips_frame)
        self.chips_content.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Visualização de chips
        self.player_chips_frame = ttk.Frame(self.chips_content)
        self.player_chips_frame.pack(fill='x', pady=10)
        
        self.player_chips_label = ttk.Label(
            self.player_chips_frame,
            text="Seus Chips:",
            font=('Arial', 12)
        )
        self.player_chips_label.pack(side='left', padx=5)
        
        self.player_chips_value = ttk.Label(
            self.player_chips_frame,
            text="1000",
            font=('Arial', 12, 'bold'),
            foreground='#FFD700'  # Dourado
        )
        self.player_chips_value.pack(side='left', padx=5)
        
        self.player_chips_progress = ttk.Progressbar(
            self.player_chips_frame,
            orient='horizontal',
            length=200,
            mode='determinate'
        )
        self.player_chips_progress.pack(side='left', padx=10, expand=True, fill='x')
        
        # Visualização de chips da máquina
        self.machine_chips_frame = ttk.Frame(self.chips_content)
        self.machine_chips_frame.pack(fill='x', pady=10)
        
        self.machine_chips_label = ttk.Label(
            self.machine_chips_frame,
            text="Chips da Máquina:",
            font=('Arial', 12)
        )
        self.machine_chips_label.pack(side='left', padx=5)
        
        self.machine_chips_value = ttk.Label(
            self.machine_chips_frame,
            text="1000",
            font=('Arial', 12, 'bold'),
            foreground='#FFD700'  # Dourado
        )
        self.machine_chips_value.pack(side='left', padx=5)
        
        self.machine_chips_progress = ttk.Progressbar(
            self.machine_chips_frame,
            orient='horizontal',
            length=200,
            mode='determinate'
        )
        self.machine_chips_progress.pack(side='left', padx=10, expand=True, fill='x')
        
        # Visualização do pote
        self.pot_frame = ttk.Frame(self.chips_content)
        self.pot_frame.pack(fill='x', pady=10)
        
        self.pot_label = ttk.Label(
            self.pot_frame,
            text="Pote Atual:",
            font=('Arial', 12)
        )
        self.pot_label.pack(side='left', padx=5)
        
        self.pot_value = ttk.Label(
            self.pot_frame,
            text="0",
            font=('Arial', 14, 'bold'),
            foreground='#FFD700'  # Dourado
        )
        self.pot_value.pack(side='left', padx=5)
        
        # Histórico de mensagens (invisível, apenas para armazenar)
        self.message_history = []

    def add_chip_displays(self):
        """Adiciona caixas de texto para exibir chips dos jogadores e o pote"""
        # Remover elementos antigos, se existirem
        for widget in self.info_frame.winfo_children():
            widget.destroy()
            
        # Frame superior com chips da máquina e pote
        top_chips_frame = tk.Frame(self.info_frame, bg='#1a472a')
        top_chips_frame.pack(fill='x', pady=5)
        
        # Box de chips da máquina
        self.machine_chips_box = tk.Frame(
            top_chips_frame,
            bg='#233729',
            highlightbackground='#FFD700',
            highlightthickness=2,
            padx=10,
            pady=5
        )
        self.machine_chips_box.pack(side='left', padx=20)
        
        tk.Label(
            self.machine_chips_box,
            text="MÁQUINA",
            font=('Arial', 10, 'bold'),
            fg='white',
            bg='#233729'
        ).pack(anchor='w')
        
        self.machine_chips_display = tk.Label(
            self.machine_chips_box,
            text="1000 💰",
            font=('Arial', 14, 'bold'),
            fg='#FFD700',
            bg='#233729'
        )
        self.machine_chips_display.pack(anchor='w')
        
        # Box do pote
        self.pot_box = tk.Frame(
            top_chips_frame,
            bg='#233729',
            highlightbackground='#FF9900',
            highlightthickness=2,
            padx=10,
            pady=5
        )
        self.pot_box.pack(side='right', padx=20)
        
        tk.Label(
            self.pot_box,
            text="POTE",
            font=('Arial', 10, 'bold'),
            fg='white',
            bg='#233729'
        ).pack(anchor='e')
        
        self.pot_display = tk.Label(
            self.pot_box,
            text="0 💰",
            font=('Arial', 14, 'bold'),
            fg='#FF9900',
            bg='#233729'
        )
        self.pot_display.pack(anchor='e')
        
        # Frame inferior com chips do jogador e aposta atual
        bottom_chips_frame = tk.Frame(self.info_frame, bg='#1a472a')
        bottom_chips_frame.pack(fill='x', pady=5)
        
        # Box de chips do jogador
        self.player_chips_box = tk.Frame(
            bottom_chips_frame,
            bg='#233729',
            highlightbackground='#FFD700',
            highlightthickness=2,
            padx=10,
            pady=5
        )
        self.player_chips_box.pack(side='left', padx=20)
        
        tk.Label(
            self.player_chips_box,
            text="SEUS CHIPS",
            font=('Arial', 10, 'bold'),
            fg='white',
            bg='#233729'
        ).pack(anchor='w')
        
        self.player_chips_display = tk.Label(
            self.player_chips_box,
            text="1000 💰",
            font=('Arial', 14, 'bold'),
            fg='#FFD700',
            bg='#233729'
        )
        self.player_chips_display.pack(anchor='w')
        
        # Box de aposta atual
        self.current_bet_box = tk.Frame(
            bottom_chips_frame,
            bg='#233729',
            highlightbackground='#90EE90',
            highlightthickness=2,
            padx=10,
            pady=5
        )
        self.current_bet_box.pack(side='right', padx=20)
        
        tk.Label(
            self.current_bet_box,
            text="APOSTA ATUAL",
            font=('Arial', 10, 'bold'),
            fg='white',
            bg='#233729'
        ).pack(anchor='e')
        
        self.current_bet_display = tk.Label(
            self.current_bet_box,
            text="50 💰",
            font=('Arial', 14, 'bold'),
            fg='#90EE90',
            bg='#233729'
        )
        self.current_bet_display.pack(anchor='e')

    def setup_components(self):
        # Adiciona displays de chips em text boxes
        self.add_chip_displays()
        
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
        
        # Cria referências vazias para compatibilidade
        self.pot_label = ttk.Label(text="")
        self.bet_label = ttk.Label(text="")
        self.chips_label = ttk.Label(text="")
        
        # Labels para cartas do jogador
        self.player_label = ttk.Label(
            self.player_frame,
            text="Suas Cartas",
            font=('Arial', 14, 'bold')
        )
        self.player_label.pack(anchor='center')
        
        # Container para botões
        button_container = ttk.Frame(self.control_frame)
        button_container.pack(anchor='center', pady=10)  # Increased padding
        
        # Botões de controle - com tamanhos maiores
        self.call_button = ttk.Button(
            button_container,
            text="Call",
            command=self.call_action,
            width=16  # Increased width
        )
        self.call_button.pack(side='left', padx=8)  # Increased padding
        
        self.raise_button = ttk.Button(
            button_container,
            text="Raise",
            command=self.raise_action,
            width=16  # Increased width
        )
        self.raise_button.pack(side='left', padx=8)  # Increased padding
        
        self.fold_button = ttk.Button(
            button_container,
            text="Fold",
            command=self.fold_action,
            width=16  # Increased width
        )
        self.fold_button.pack(side='left', padx=8)  # Increased padding
        
        self.new_game_button = ttk.Button(
            button_container,
            text="Próxima Mão",
            command=self.new_hand,
            width=16  # Increased width
        )
        self.new_game_button.pack(side='left', padx=8)  # Increased padding
        
        self.new_session_button = ttk.Button(
            button_container,
            text="Nova Sessão",
            command=self.start_new_session,
            width=16  # Increased width
        )
        self.new_session_button.pack(side='left', padx=8)  # Increased padding

    def log_message(self, message, tag=None):
        """Add a message to the game log with optional formatting"""
        # Armazenar a mensagem no histórico
        self.message_history.append((message, tag))
        
        # Determinar o ícone e cor baseado no conteúdo da mensagem
        icon = "🔄"  # Ícone padrão
        bg_color = "#0a1f12"  # Cor de fundo padrão
        fg_color = "#e0e0e0"  # Cor de texto padrão
        
        if message.startswith('==='):
            icon = "📌"
            bg_color = "#1a3a2a"
        elif '🏆' in message:
            icon = "🏆"
            bg_color = "#2a3a1a"
            fg_color = "#90EE90"  # Verde claro
        elif 'chips' in message.lower() or '💰' in message:
            icon = "💰"
            bg_color = "#3a2a1a"
            fg_color = "#FFD700"  # Dourado
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
            
        # Criar um frame para a mensagem (usando tk.Frame em vez de ttk.Frame para facilitar a configuração de cores)
        message_frame = tk.Frame(
            self.action_history_scrollable_frame,
            background=bg_color,
            padx=5,
            pady=2
        )
        message_frame.pack(fill='x', pady=2, padx=5)
        
        # Adicionar ícone
        icon_label = tk.Label(
            message_frame,
            text=icon,
            font=('Arial', 12),
            foreground=fg_color,
            background=bg_color
        )
        icon_label.pack(side='left', padx=5)
        
        # Adicionar texto da mensagem
        text_label = tk.Label(
            message_frame,
            text=message,
            wraplength=400,
            foreground=fg_color,
            background=bg_color,
            justify='left',
            anchor='w'
        )
        text_label.pack(side='left', padx=5, fill='x', expand=True)
        
        # Rolar para o final
        self.action_history_canvas.update_idletasks()
        self.action_history_canvas.yview_moveto(1.0)
        self.root.update()
        
        # Atualizar estatísticas da mão se necessário
        self.update_hand_stats(message)
        
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
        
        # Atualizar visualização de chips
        self.update_chips_display()
        
    def update_chips_display(self):
        """Atualiza a visualização de chips em todos os locais"""
        # Atualizar valores de chips nos novos displays
        if hasattr(self, 'player_chips_display'):
            self.player_chips_display.config(text=f"{self.player.chips} 💰")
        if hasattr(self, 'machine_chips_display'):
            self.machine_chips_display.config(text=f"{self.machine.chips} 💰")
        if hasattr(self, 'pot_display'):
            self.pot_display.config(text=f"{self.game.pot} 💰")
        if hasattr(self, 'current_bet_display'):
            self.current_bet_display.config(text=f"{self.current_bet} 💰")
        
        # Atualizar valores nas estatísticas (tab)
        self.player_chips_value.config(text=str(self.player.chips))
        self.machine_chips_value.config(text=str(self.machine.chips))
        self.pot_value.config(text=str(self.game.pot))
        
        # Atualizar barras de progresso
        target = self.target_chips
        self.player_chips_progress['value'] = (self.player.chips / target) * 100
        self.machine_chips_progress['value'] = (self.machine.chips / target) * 100
        
    def update_hand_stats(self, message):
        """Atualiza as estatísticas da mão atual baseado nas mensagens de log"""
        # Atualizar tipo de mão do jogador
        if "Jogador 1 tem " in message and "\n" in message:
            hand_type = message.split("Jogador 1 tem ")[1].split("\n")[0]
            self.player_hand_type_label.config(text=f"Sua mão: {hand_type}")
            
        # Atualizar tipo de mão da máquina
        if "Máquina tem " in message and "\n" in message:
            hand_type = message.split("Máquina tem ")[1].split("\n")[0]
            self.machine_hand_type_label.config(text=f"Mão da máquina: {hand_type}")
            
        # Atualizar progresso da mão
        if "=== Flop ===" in message:
            self.update_hand_progress(1)  # Flop
        elif "=== Turn ===" in message:
            self.update_hand_progress(2)  # Turn
        elif "=== River ===" in message:
            self.update_hand_progress(3)  # River
        elif "🏆" in message and "vence" in message:
            self.update_hand_progress(4)  # Showdown
        elif "=== Nova Mão ===" in message:
            self.update_hand_progress(0)  # Pré-Flop
            
    def update_phase_banner(self, stage_index):
        """Atualiza o banner com a fase atual do jogo"""
        phases = ["PRÉ-FLOP", "FLOP", "TURN", "RIVER", "SHOWDOWN"]
        if 0 <= stage_index < len(phases):
            self.phase_label.config(text=f"FASE: {phases[stage_index]}")
            
            # Cores diferentes para cada fase
            colors = {
                0: ("#FFD700", "#0a1f12"),  # Dourado sobre verde escuro (Pré-Flop)
                1: ("#90EE90", "#0a1f12"),  # Verde claro sobre verde escuro (Flop)
                2: ("#87CEEB", "#0a1f12"),  # Azul claro sobre verde escuro (Turn)
                3: ("#FFA07A", "#0a1f12"),  # Salmão sobre verde escuro (River)
                4: ("#FF6347", "#0a1f12"),  # Tomate sobre verde escuro (Showdown)
            }
            
            fg_color, bg_color = colors.get(stage_index, ("#FFFFFF", "#0a1f12"))
            self.phase_label.config(fg=fg_color, bg=bg_color)
            self.phase_banner_frame.config(bg=bg_color)
    
    def update_hand_progress(self, stage_index):
        """Atualiza os indicadores de progresso da mão"""
        # Resetar todos os indicadores para não selecionados
        for i, (indicator, label) in enumerate(self.hand_stage_labels):
            if i <= stage_index:
                # Estágio atual ou anterior
                indicator.config(text="●", foreground="#FFD700")  # Dourado
                label.config(foreground="#FFD700")
            else:
                # Estágio futuro
                indicator.config(text="○", foreground="#888888")
                label.config(foreground="#888888")
                
        # Atualizar o banner da fase
        self.update_phase_banner(stage_index)

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
        
        # Atualiza informações do jogo nos textboxes
        self.update_chips_display()
        
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
        # Limpar histórico de mensagens
        self.message_history.clear()
        
        # Limpar widgets de histórico de ações
        for widget in self.action_history_scrollable_frame.winfo_children():
            widget.destroy()
            
        # Resetar estatísticas da mão
        self.player_hand_type_label.config(text="Sua mão: -")
        self.machine_hand_type_label.config(text="Mão da máquina: -")
        self.update_hand_progress(0)  # Resetar progresso da mão
        
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
        
        # Inicializar o banner de fase para PRÉ-FLOP
        self.update_phase_banner(0)
        
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
        
        # Reset apostas da rodada
        self.player_bet_in_round = 0
        self.machine_bet_in_round = 0
        
        # Post blinds and update chips
        self.player.chips -= small_blind  # Player is small blind
        self.machine.chips -= big_blind   # Machine is big blind
        self.game.pot = small_blind + big_blind
        self.current_bet = big_blind
        
        # Atualiza apostas da rodada
        self.player_bet_in_round = small_blind
        self.machine_bet_in_round = big_blind
        
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

    def call_action(self):
        # Log before state
        self.log_message(f"\nAntes do Call/Check:")
        self.log_chip_state("Estado Inicial")
        
        if self.current_bet > 0:
            # Calculate how much more the player needs to add to match the current bet
            additional_bet = self.machine_bet_in_round - self.player_bet_in_round
            
            if additional_bet > 0 and additional_bet <= self.player.chips:
                self.player.chips -= additional_bet
                self.game.pot += additional_bet
                self.player_bet_in_round += additional_bet
                self.log_message(f"Jogador: Call {additional_bet} (Total na rodada: {self.player_bet_in_round})")
                self.log_chip_state("Jogador Call")
        else:
            self.log_message(f"Jogador: Check (Total na rodada: {self.player_bet_in_round})")
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
        # Primeiro, o jogador precisa igualar a aposta atual
        call_amount = self.machine_bet_in_round - self.player_bet_in_round
        # Depois, adiciona o valor do raise
        raise_amount = self.game.min_raise
        total_amount = call_amount + raise_amount
        
        if total_amount <= self.player.chips:
            self.player.chips -= total_amount
            self.game.pot += total_amount
            self.player_bet_in_round += total_amount
            self.current_bet = self.player_bet_in_round
            
            self.log_message(f"Jogador: Raise para {total_amount} (Total na rodada: {self.player_bet_in_round})")
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
                # Primeiro, a máquina precisa igualar a aposta atual
                call_amount = self.player_bet_in_round - self.machine_bet_in_round
                # Depois, adiciona o valor do raise
                raise_amount = self.game.min_raise
                total_amount = call_amount + raise_amount
                
                if total_amount <= initial_machine_chips:
                    self.machine.chips = initial_machine_chips - total_amount
                    self.game.pot = initial_pot + total_amount
                    self.machine_bet_in_round += total_amount
                    self.current_bet = self.machine_bet_in_round
                    
                    self.log_message(f"Máquina: Raise para {total_amount} (Total na rodada: {self.machine_bet_in_round})")
                    self.log_chip_state("Máquina Raise")
                    self.betting_round_complete = False  # Reset if machine raises
        else:  # call
            if self.current_bet > 0:
                # Calculate how much more the machine needs to add to match the current bet
                call_amount = self.player_bet_in_round - self.machine_bet_in_round
                
                if call_amount > 0:
                    call_amount = min(call_amount, initial_machine_chips)
                    self.machine.chips = initial_machine_chips - call_amount
                    self.game.pot = initial_pot + call_amount
                    self.machine_bet_in_round += call_amount
                    self.log_message(f"Máquina: Call {call_amount} (Total na rodada: {self.machine_bet_in_round})")
                    self.log_chip_state("Máquina Call")
            else:
                self.log_message(f"Máquina: Check (Total na rodada: {self.machine_bet_in_round})")
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
            self.player_bet_in_round = 0  # Reset player bet for new round
            self.machine_bet_in_round = 0  # Reset machine bet for new round
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
            
            # Tenta cada opção até uma funcionar
            for display in display_options:
                try:
                    print(f"Tentando DISPLAY={display}")
                    os.environ['DISPLAY'] = display
                    # Testa se o display funciona criando um widget temporário
                    test_root = tk.Tk()
                    test_root.withdraw()
                    test_root.destroy()
                    print(f"DISPLAY={display} funcionou!")
                    break
                except Exception as e:
                    print(f"Falha com DISPLAY={display}: {e}")
                    continue
        
        # Configuração adicional para o PIL/Tkinter
        os.environ['PYTHONUNBUFFERED'] = '1'  # Garante saída imediata
        
        # Verifica se o servidor X está acessível
        print("Verificando se o servidor X (VcXsrv) está acessível...")
        try:
            import subprocess
            # Tenta executar um comando simples do X11 para verificar se o servidor está respondendo
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