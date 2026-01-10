#!/usr/bin/env python3
"""
Versão em texto do jogo de poker, sem depender de gráficos.
Esta versão funciona diretamente no terminal, sem precisar de um servidor X.
"""

import random
import time
import os
from poker_app import Card, Deck, Player, PokerGame, HistoryManager, RankingManager

# Cores ANSI para o terminal
class Colors:
    RESET = "\033[0m"
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    MAGENTA = "\033[95m"
    CYAN = "\033[96m"
    WHITE = "\033[97m"
    BOLD = "\033[1m"
    
    # Cores de fundo
    BG_BLACK = "\033[40m"
    BG_RED = "\033[41m"
    BG_GREEN = "\033[42m"
    BG_YELLOW = "\033[43m"
    BG_BLUE = "\033[44m"
    BG_MAGENTA = "\033[45m"
    BG_CYAN = "\033[46m"
    BG_WHITE = "\033[47m"

# Símbolos para os naipes
SUIT_SYMBOLS = {
    'Hearts': '♥',
    'Diamonds': '♦',
    'Clubs': '♣',
    'Spades': '♠'
}

# Cores para os naipes
SUIT_COLORS = {
    'Hearts': Colors.RED,
    'Diamonds': Colors.RED,
    'Clubs': Colors.WHITE,
    'Spades': Colors.WHITE
}

def clear_screen():
    """Limpa a tela do terminal"""
    os.system('cls' if os.name == 'nt' else 'clear')

def print_card(card):
    """Imprime uma carta com cor"""
    if card is None:
        return "[ ]"
    
    suit_color = SUIT_COLORS.get(card.suit, Colors.WHITE)
    suit_symbol = SUIT_SYMBOLS.get(card.suit, card.suit[0])
    return f"{suit_color}[{card.rank}{suit_symbol}]{Colors.RESET}"

def print_cards(cards):
    """Imprime uma lista de cartas"""
    return " ".join(print_card(card) for card in cards)

def print_hidden_cards(num_cards):
    """Imprime cartas escondidas"""
    return " ".join([f"{Colors.BLUE}[??]{Colors.RESET}" for _ in range(num_cards)])

def print_banner(text):
    """Imprime um banner com texto centralizado"""
    width = 60
    print(f"{Colors.BOLD}{Colors.YELLOW}{'=' * width}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.YELLOW}{text.center(width)}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.YELLOW}{'=' * width}{Colors.RESET}")

def print_phase(phase):
    """Imprime a fase atual do jogo"""
    phases = {
        "pre_flop": "PRÉ-FLOP",
        "flop": "FLOP",
        "turn": "TURN",
        "river": "RIVER",
        "showdown": "SHOWDOWN"
    }
    phase_name = phases.get(phase, phase)
    print(f"{Colors.BOLD}{Colors.CYAN}FASE: {phase_name}{Colors.RESET}")

def print_pot(pot):
    """Imprime o valor do pote"""
    print(f"{Colors.YELLOW}Pote: {pot} chips{Colors.RESET}")

def print_player_info(player, is_current=False):
    """Imprime informações do jogador"""
    prefix = "→ " if is_current else "  "
    if player.folded:
        status = f"{Colors.RED}(Desistiu){Colors.RESET}"
    else:
        status = ""
    
    print(f"{prefix}{Colors.BOLD}{player.name}{Colors.RESET}: {player.chips} chips {status}")

def get_hand_description(hand_type):
    """Retorna uma descrição mais detalhada do tipo de mão"""
    descriptions = {
        "Royal Flush": "Royal Flush (A, K, Q, J, 10 do mesmo naipe)",
        "Straight Flush": "Straight Flush (Sequência do mesmo naipe)",
        "Quadra": "Quadra (Quatro cartas do mesmo valor)",
        "Full House": "Full House (Trinca + Par)",
        "Flush": "Flush (Cinco cartas do mesmo naipe)",
        "Sequência": "Sequência (Cinco cartas em sequência)",
        "Trinca": "Trinca (Três cartas do mesmo valor)",
        "Dois Pares": "Dois Pares (Dois pares diferentes)",
        "Par": "Par (Duas cartas do mesmo valor)",
        "Carta Alta": "Carta Alta (Nenhuma combinação)"
    }
    return descriptions.get(hand_type, hand_type)

class PokerTextUI:
    def __init__(self):
        self.player = Player("Jogador 1")
        self.machine = Player("Máquina", is_machine=True)
        self.game = None
        self.current_bet = 50
        self.betting_round_complete = False
        
        # Rastreamento de apostas na mão atual
        self.player_bet_in_round = 0
        self.machine_bet_in_round = 0
        
        # Session tracking
        self.hands_played = 0
        self.player_wins = 0
        self.machine_wins = 0
        self.current_streak = 0
        self.target_chips = 5000
        self.starting_chips = 1000
        
        # Histórico de mensagens
        self.messages = []
        
    def log_message(self, message, color=None):
        """Adiciona uma mensagem ao histórico"""
        if color:
            message = f"{color}{message}{Colors.RESET}"
        self.messages.append(message)
        if len(self.messages) > 10:
            self.messages.pop(0)
    
    def display_game_state(self):
        """Exibe o estado atual do jogo"""
        clear_screen()
        
        # Banner do jogo
        print_banner("TEXAS HOLD'EM POKER")
        print()
        
        # Fase atual
        if self.game:
            phase = "pre_flop"
            if len(self.game.community_cards) == 3:
                phase = "flop"
            elif len(self.game.community_cards) == 4:
                phase = "turn"
            elif len(self.game.community_cards) == 5:
                phase = "showdown" if self.betting_round_complete else "river"
            
            print_phase(phase)
            print()
        
        # Informações dos jogadores
        print_player_info(self.machine)
        if self.game and not self.machine.folded and self.betting_round_complete and len(self.game.community_cards) == 5:
            print(f"Mão da máquina: {print_cards(self.machine.hand)}")
        else:
            print(f"Mão da máquina: {print_hidden_cards(2)}")
        print()
        
        # Cartas comunitárias
        print(f"{Colors.BOLD}Cartas Comunitárias:{Colors.RESET}")
        if self.game:
            if self.game.community_cards:
                print(print_cards(self.game.community_cards))
            else:
                print("Nenhuma carta revelada ainda")
        else:
            print("Jogo não iniciado")
        print()
        
        # Informações do jogador
        print_player_info(self.player, True)
        if self.game and self.player.hand:
            print(f"Sua mão: {print_cards(self.player.hand)}")
        print()
        
        # Pote e apostas
        if self.game:
            print_pot(self.game.pot)
            print(f"Aposta atual: {self.current_bet}")
            print(f"{Colors.YELLOW}Apostas nesta rodada: Jogador: {self.player_bet_in_round}, Máquina: {self.machine_bet_in_round}{Colors.RESET}")
        print()
        
        # Histórico de mensagens
        print(f"{Colors.BOLD}Histórico:{Colors.RESET}")
        for msg in self.messages:
            print(msg)
        print()
        
        # Comandos disponíveis
        self.display_available_commands()
    
    def display_available_commands(self):
        """Exibe os comandos disponíveis para o jogador"""
        print(f"{Colors.BOLD}Comandos:{Colors.RESET}")
        
        if not self.game:
            print("(N) Nova sessão")
            return
        
        if self.betting_round_complete and len(self.game.community_cards) == 5:
            print("(P) Próxima mão")
            print("(N) Nova sessão")
            return
        
        if not self.betting_round_complete:
            print("(C) Call/Check")
            print("(R) Raise")
            print("(F) Fold")
        else:
            print("Aguardando próxima fase...")
    
    def start_new_session(self):
        """Inicia uma nova sessão de poker"""
        # Reset session stats
        self.hands_played = 0
        self.player_wins = 0
        self.machine_wins = 0
        self.current_streak = 0
        
        # Reset player states
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
        
        # Clear messages
        self.messages = []
        
        # Log session start
        self.log_message("=== Nova Sessão de Poker ===", Colors.GREEN)
        self.log_message(f"Objetivo: Alcançar {self.target_chips} chips", Colors.YELLOW)
        
        # Start first hand
        self.new_hand()
    
    def new_hand(self):
        """Inicia uma nova mão"""
        # Reset hand states
        self.player.hand = []
        self.player.folded = False
        self.machine.hand = []
        self.machine.folded = False
        self.betting_round_complete = False
        
        # Log hand start
        self.log_message("\n=== Nova Mão ===", Colors.GREEN)
        
        # Initialize new game
        self.game = PokerGame([self.player, self.machine])
        
        # Set up blinds
        small_blind = 25
        big_blind = 50
        
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
        
        # Log blinds
        self.log_message(f"Jogador 1 posta small blind: {small_blind}", Colors.YELLOW)
        self.log_message(f"Máquina posta big blind: {big_blind}", Colors.YELLOW)
        
        # Deal initial cards
        self.game.deal_cards()
        
        # Update display
        self.display_game_state()
    
    def call_action(self):
        """Jogador faz call/check"""
        if self.current_bet > 0:
            # Calculate how much more the player needs to add to match the current bet
            additional_bet = self.machine_bet_in_round - self.player_bet_in_round
            
            if additional_bet > 0 and additional_bet <= self.player.chips:
                self.player.chips -= additional_bet
                self.game.pot += additional_bet
                self.player_bet_in_round += additional_bet
                self.log_message(f"Jogador: Call {additional_bet} (Total na rodada: {self.player_bet_in_round})", Colors.CYAN)
        else:
            self.log_message(f"Jogador: Check (Total na rodada: {self.player_bet_in_round})", Colors.CYAN)
        
        # Machine action
        self.machine_action()
        
        # Check if machine folded
        if self.machine.folded:
            self.end_hand("Jogador 1")
            return
        
        self.betting_round_complete = True
        self.check_game_state()
        self.display_game_state()
    
    def raise_action(self):
        """Jogador faz raise"""
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
            
            self.log_message(f"Jogador: Raise para {total_amount} (Total na rodada: {self.player_bet_in_round})", Colors.CYAN)
            
            # Machine action
            self.machine_action()
            
            # Check if machine folded
            if self.machine.folded:
                self.end_hand("Jogador 1")
                return
            
            self.betting_round_complete = True
            self.check_game_state()
        else:
            self.log_message("⚠️ Chips insuficientes para raise!", Colors.RED)
        
        self.display_game_state()
    
    def fold_action(self):
        """Jogador desiste"""
        self.player.folded = True
        self.log_message("Jogador: Fold", Colors.RED)
        self.end_hand("Máquina")
        self.display_game_state()
    
    def machine_action(self):
        """Ação da máquina"""
        # Store initial state
        initial_machine_chips = self.machine.chips
        initial_pot = self.game.pot
        
        action, amount = self.machine.make_decision(self.game.community_cards, self.current_bet, self.game.min_raise)
        
        if action == "fold":
            self.machine.folded = True
            self.log_message("Máquina: Fold", Colors.RED)
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
                    
                    self.log_message(f"Máquina: Raise para {total_amount} (Total na rodada: {self.machine_bet_in_round})", Colors.MAGENTA)
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
                    self.log_message(f"Máquina: Call {call_amount} (Total na rodada: {self.machine_bet_in_round})", Colors.MAGENTA)
            else:
                self.log_message(f"Máquina: Check (Total na rodada: {self.machine_bet_in_round})", Colors.MAGENTA)
    
    def check_game_state(self):
        """Verifica o estado do jogo e avança para a próxima fase se necessário"""
        # Only proceed if both players have acted
        if self.player.folded or self.machine.folded:
            return
        
        # Only proceed to next stage if betting round is complete
        if not self.betting_round_complete:
            return
        
        # Verifica se é hora de revelar novas cartas comunitárias
        if len(self.game.community_cards) == 0:
            self.game.deal_community_cards(3)  # Flop
            self.log_message("\n=== Flop ===", Colors.GREEN)
            self.current_bet = 0  # Reset bet for new round
            self.player_bet_in_round = 0  # Reset player bet for new round
            self.machine_bet_in_round = 0  # Reset machine bet for new round
            self.betting_round_complete = False  # Reset for new betting round
        elif len(self.game.community_cards) == 3:
            self.game.deal_community_cards(1)  # Turn
            self.log_message("\n=== Turn ===", Colors.GREEN)
            self.current_bet = 0  # Reset bet for new round
            self.player_bet_in_round = 0  # Reset player bet for new round
            self.machine_bet_in_round = 0  # Reset machine bet for new round
            self.betting_round_complete = False  # Reset for new betting round
        elif len(self.game.community_cards) == 4:
            self.game.deal_community_cards(1)  # River
            self.log_message("\n=== River ===", Colors.GREEN)
            self.current_bet = 0  # Reset bet for new round
            self.player_bet_in_round = 0  # Reset player bet for new round
            self.machine_bet_in_round = 0  # Reset machine bet for new round
            self.betting_round_complete = False  # Reset for new betting round
        elif len(self.game.community_cards) == 5:
            self.end_hand()  # Only end hand after River betting is complete
    
    def end_hand(self, winner_by_fold=None):
        """Finaliza a mão atual"""
        if winner_by_fold:
            winner_name = winner_by_fold
            self.log_message(f"\n🏆 {winner_name} vence por desistência!", Colors.GREEN)
        else:
            # Determina o vencedor baseado nas mãos
            player_type, player_value = self.player.get_hand_value(self.game.community_cards)
            machine_type, machine_value = self.machine.get_hand_value(self.game.community_cards)
            
            result = f"\nJogador 1 tem {get_hand_description(player_type)}\n"
            result += f"Máquina tem {get_hand_description(machine_type)}\n"
            
            if player_value > machine_value:
                winner_name = "Jogador 1"
            else:
                winner_name = "Máquina"
            
            result += f"🏆 {winner_name} vence!"
            self.log_message(result, Colors.GREEN)
        
        # Update session stats
        self.hands_played += 1
        if winner_name == "Jogador 1":
            self.player_wins += 1
            self.current_streak = max(1, self.current_streak + 1)
        else:
            self.machine_wins += 1
            self.current_streak = min(-1, self.current_streak - 1)
        
        # Award the pot
        if winner_name == "Jogador 1":
            pot_amount = self.game.pot
            self.player.chips += pot_amount
            self.player.game_sequence['total_winnings'] += pot_amount
            self.machine.game_sequence['total_losses'] += pot_amount
            if pot_amount > self.player.game_sequence['biggest_pot_won']:
                self.player.game_sequence['biggest_pot_won'] = pot_amount
            self.game.pot = 0  # Zero the pot after distributing
        else:
            pot_amount = self.game.pot
            self.machine.chips += pot_amount
            self.machine.game_sequence['total_winnings'] += pot_amount
            self.player.game_sequence['total_losses'] += pot_amount
            if pot_amount > self.machine.game_sequence['biggest_pot_won']:
                self.machine.game_sequence['biggest_pot_won'] = pot_amount
            self.game.pot = 0  # Zero the pot after distributing
        
        # Log chip counts after pot is awarded
        self.log_message(f"\n💰 Depois do pagamento - Jogador 1: {self.player.chips}, Máquina: {self.machine.chips} chips", Colors.YELLOW)
        
        # Show session stats
        self.log_message(f"\n=== Estatísticas da Sessão ===", Colors.CYAN)
        self.log_message(f"Mãos jogadas: {self.hands_played}", Colors.CYAN)
        self.log_message(f"Vitórias do Jogador: {self.player_wins}", Colors.CYAN)
        self.log_message(f"Vitórias da Máquina: {self.machine_wins}", Colors.CYAN)
        
        # Check if session should end
        if self.player.chips <= 0:
            self.log_message("\n🏆 Máquina vence a sessão! Jogador ficou sem chips.", Colors.RED)
            return
        if self.machine.chips <= 0:
            self.log_message("\n🏆 Jogador vence a sessão! Máquina ficou sem chips.", Colors.GREEN)
            return
        if self.player.chips >= self.target_chips:
            self.log_message(f"\n🏆 Jogador vence a sessão! Alcançou {self.target_chips} chips!", Colors.GREEN)
            return
        if self.machine.chips >= self.target_chips:
            self.log_message(f"\n🏆 Máquina vence a sessão! Alcançou {self.target_chips} chips!", Colors.RED)
            return
    
    def run(self):
        """Executa o jogo"""
        self.start_new_session()
        
        while True:
            # Exibe o estado atual do jogo
            self.display_game_state()
            
            # Obtém a ação do jogador
            action = input("Digite sua ação: ").strip().upper()
            
            if action == 'Q':
                print("Saindo do jogo...")
                break
            
            if not self.game:
                if action == 'N':
                    self.start_new_session()
                continue
            
            if self.betting_round_complete and len(self.game.community_cards) == 5:
                if action == 'P':
                    self.new_hand()
                elif action == 'N':
                    self.start_new_session()
                continue
            
            if not self.betting_round_complete:
                if action == 'C':
                    self.call_action()
                elif action == 'R':
                    self.raise_action()
                elif action == 'F':
                    self.fold_action()

if __name__ == "__main__":
    try:
        # Verifica se o terminal suporta cores ANSI
        if os.name == 'nt':
            os.system('color')
        
        print("Iniciando versão em texto do jogo de poker...")
        game = PokerTextUI()
        game.run()
    except KeyboardInterrupt:
        print("\nJogo interrompido pelo usuário.")
    except Exception as e:
        print(f"Erro ao executar o jogo: {e}")
        import traceback
        traceback.print_exc()