#!/usr/bin/env python3
"""
Aplicativo aprimorado de Taxas Hold'em para Desktop.

Este script implementa uma versão mais completa do motor de jogo,
incluindo:
  - Definições de cartas e baralho.
  - Distribuição de mãos para jogadores (humano e máquina).
  - Simulação de fases do jogo (pré-flop, flop, turn, river) com apostas.
  - Cálculo de taxas sobre o pote.
  - Registro do histórico de partidas em um arquivo JSON.
  - Atualização do ranking de vitórias em um arquivo JSON.
  - Continuação do jogo com opção de jogar novas partidas e visualização do ranking final.
  - Cartas comunitárias e avaliação de mãos.
  - Decisões da máquina baseadas em probabilidade.
  - Sistema de apostas com raise.
  - Tradução dos naipes e valores para português.
  - Avaliação de mãos mais complexa.
  - Showdown com exibição das mãos.
"""

import random
import json
from typing import List, Optional, Dict, Tuple
import numpy as np

class Card:
    suits_pt = {
        'Hearts': 'Copas',
        'Diamonds': 'Ouros',
        'Clubs': 'Paus',
        'Spades': 'Espadas'
    }
    ranks_pt = {
        '2': '2', '3': '3', '4': '4', '5': '5', '6': '6', '7': '7', '8': '8',
        '9': '9', '10': '10', 'J': 'Valete', 'Q': 'Dama', 'K': 'Rei', 'A': 'Ás'
    }
    suits = ['Hearts', 'Diamonds', 'Clubs', 'Spades']
    ranks = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
    rank_values = {'2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, 
                  '9': 9, '10': 10, 'J': 11, 'Q': 12, 'K': 13, 'A': 14}

    def __init__(self, rank, suit):
        self.rank = rank
        self.suit = suit
        self.value = self.rank_values[rank]

    def __str__(self):
        return f"{self.ranks_pt[self.rank]} de {self.suits_pt[self.suit]}"

class Deck:
    def __init__(self):
        self.cards = [Card(rank, suit) for suit in Card.suits for rank in Card.ranks]
        self.shuffle()

    def shuffle(self):
        random.shuffle(self.cards)

    def draw(self) -> Optional[Card]:
        return self.cards.pop() if self.cards else None

class Player:
    def __init__(self, name, is_machine=False):
        self.name = name
        self.is_machine = is_machine
        self.hand: List[Card] = []
        self.chips = 1000
        self.current_bet = 0
        self.folded = False
        self.learning_rate = 0.1
        self.discount_factor = 0.9
        self.position = None  # Will be set by the game
        
        # Initialize game sequence tracking
        self.game_sequence = {
            'hands_played': 0,
            'total_chip_diff': 0,
            'win_streak': 0,
            'max_chips': self.chips,  # Initialize with starting chips
            'learning_steps': 0
        }
        
        # Carrega Q-table existente se for uma máquina
        if self.is_machine:
            self.q_table = self.load_q_table()
        else:
            self.q_table = {}

    def load_q_table(self) -> Dict:
        """Carrega a Q-table do arquivo."""
        try:
            with open("q_table.json", "r") as f:
                q_tables = json.load(f)
                return q_tables.get(self.name, {})
        except (FileNotFoundError, json.JSONDecodeError):
            return {}

    def save_q_table(self):
        """Salva a Q-table no arquivo."""
        try:
            with open("q_table.json", "r") as f:
                q_tables = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            q_tables = {}
        
        q_tables[self.name] = self.q_table
        
        with open("q_table.json", "w") as f:
            json.dump(q_tables, f, indent=4)

    def receive_card(self, card: Card):
        if card:
            self.hand.append(card)

    def show_hand(self):
        return ", ".join(str(card) for card in self.hand)

    def get_hand_value(self, community_cards: List[Card]) -> Tuple[str, int]:
        all_cards = self.hand + community_cards
        
        # Verifica sequência
        values = sorted([card.value for card in all_cards])
        straight = False
        straight_high = 0
        
        # Verifica sequência normal
        for i in range(len(values) - 4):
            if values[i:i+5] == list(range(values[i], values[i]+5)):
                straight = True
                straight_high = values[i+4]
                break
        
        # Verifica sequência A-5 (Ás baixo)
        if not straight and 14 in values:  # Se tem Ás
            values_with_low_ace = sorted([1 if v == 14 else v for v in values])
            for i in range(len(values_with_low_ace) - 4):
                if values_with_low_ace[i:i+5] == list(range(values_with_low_ace[i], values_with_low_ace[i]+5)):
                    straight = True
                    straight_high = values_with_low_ace[i+4]
                    break
        
        # Verifica flush e straight flush
        flush_suit = None
        flush = False
        for suit in Card.suits:
            suited_cards = [card for card in all_cards if card.suit == suit]
            if len(suited_cards) >= 5:
                flush = True
                flush_suit = suit
                # Verifica Royal Flush
                royal_values = {'10', 'J', 'Q', 'K', 'A'}
                royal_cards = [card for card in suited_cards if card.rank in royal_values]
                if len(royal_cards) == 5:
                    return "Royal Flush", 1000  # Valor alto para garantir que vence todas as outras mãos
                break

        # Verifica straight flush
        if flush:
            suited_cards = sorted([card for card in all_cards if card.suit == flush_suit], key=lambda x: x.value)
            if len(suited_cards) >= 5:  # Precisa de pelo menos 5 cartas do mesmo naipe
                # Verifica sequência normal
                for i in range(len(suited_cards) - 4):
                    values = [c.value for c in suited_cards[i:i+5]]
                    if values == list(range(min(values), max(values) + 1)) and len(values) == 5:
                        return "Straight Flush", 900 + max(values)
                
                # Verifica sequência A-5 em flush
                if 14 in [c.value for c in suited_cards]:  # Se tem Ás
                    ace_low_values = []
                    for c in suited_cards:
                        if c.value == 14:
                            ace_low_values.append(1)
                        else:
                            ace_low_values.append(c.value)
                    ace_low_values.sort()
                    
                    for i in range(len(ace_low_values) - 4):
                        values = ace_low_values[i:i+5]
                        if values == list(range(min(values), max(values) + 1)) and len(values) == 5:
                            return "Straight Flush", 900 + max(values)

        # Conta pares, trincas, quadras
        rank_count: Dict[str, int] = {}
        for card in all_cards:
            rank_count[card.rank] = rank_count.get(card.rank, 0) + 1
        
        # Quadra (valor base 800)
        for rank, count in rank_count.items():
            if count == 4:
                return "Quadra", 800 + Card.rank_values[rank]
        
        # Full house (valor base 700)
        has_three = False
        has_pair = False
        three_value = 0
        for rank, count in rank_count.items():
            if count == 3:
                has_three = True
                three_value = Card.rank_values[rank]
            elif count == 2:
                has_pair = True
        if has_three and has_pair:
            return "Full House", 700 + three_value
        
        # Flush (valor base 600)
        if flush:
            return "Flush", 600 + max(card.value for card in all_cards)
        
        # Sequência (valor base 500)
        if straight:
            return "Sequência", 500 + straight_high
        
        # Trinca (valor base 400)
        if has_three:
            return "Trinca", 400 + three_value
        
        # Dois pares (valor base 300)
        pairs = [(rank, count) for rank, count in rank_count.items() if count == 2]
        if len(pairs) >= 2:
            return "Dois Pares", 300 + max(Card.rank_values[rank] for rank, _ in pairs)
        
        # Par (valor base 200)
        if len(pairs) == 1:
            return "Par", 200 + Card.rank_values[pairs[0][0]]
        
        # Carta alta (valor base 100)
        return "Carta Alta", 100 + max(card.value for card in all_cards)

    def evaluate_preflop_hand(self) -> float:
        """
        Avalia a força da mão inicial no pré-flop.
        """
        if len(self.hand) != 2:
            return 0.0
            
        card1, card2 = self.hand
        
        # Par na mão
        if card1.rank == card2.rank:
            return 0.5 + (card1.value / 14.0) * 0.5  # Pares altos são melhores
            
        # Cartas do mesmo naipe (suited)
        suited = card1.suit == card2.suit
        
        # Conectores (cartas sequenciais)
        gap = abs(card1.value - card2.value)
        connected = gap == 1
        
        # Pontuação base pela força das cartas
        high_card = max(card1.value, card2.value) / 14.0
        low_card = min(card1.value, card2.value) / 14.0
        
        # Combina os fatores
        score = (
            0.4 * high_card +           # 40% baseado na carta mais alta
            0.2 * low_card +            # 20% baseado na carta mais baixa
            0.2 * (1.0 if suited else 0.0) +  # 20% bônus para suited
            0.2 * (1.0 if connected else max(0, 1 - gap/5))  # 20% bônus para conectores
        )
        
        return score

    def evaluate_hand_strength(self, community_cards: List[Card]) -> float:
        """
        Avalia a força da mão em uma escala de 0 a 1.
        """
        # No pré-flop, usa avaliação específica
        if not community_cards:
            return self.evaluate_preflop_hand()
            
        hand_type, hand_value = self.get_hand_value(community_cards)
        
        # Pontuação base pela força da mão
        hand_scores = {
            "Carta Alta": 0.1,
            "Par": 0.3,
            "Dois Pares": 0.5,
            "Trinca": 0.7,
            "Sequência": 0.8,
            "Flush": 0.85,
            "Full House": 0.9,
            "Quadra": 0.95,
            "Straight Flush": 0.98,
            "Royal Flush": 1.0
        }
        
        # Adiciona bônus para cartas altas
        high_card_bonus = hand_value / 14.0 * 0.1
        
        # Adiciona bônus para draws
        draw_bonus = 0.0
        if len(community_cards) >= 3:
            # Verifica flush draw
            suits = [card.suit for card in self.hand + community_cards]
            for suit in Card.suits:
                if suits.count(suit) == 4:
                    draw_bonus = max(draw_bonus, 0.2)
                    
            # Verifica straight draw
            values = sorted([card.value for card in self.hand + community_cards])
            for i in range(len(values) - 3):
                if values[i:i+4] == list(range(values[i], values[i]+4)):
                    draw_bonus = max(draw_bonus, 0.15)
        
        return min(1.0, hand_scores.get(hand_type, 0.0) + high_card_bonus + draw_bonus)

    def get_state(self, community_cards: List[Card], current_bet: int) -> str:
        """
        Creates a more detailed state representation including:
        - Game phase
        - Hand strength
        - Position
        - Stack sizes
        - Pot odds
        - Previous actions
        - Opponent patterns
        """
        # Basic state components
        hand_strength = self.evaluate_hand_strength(community_cards)
        chips_ratio = self.chips / 1000
        bet_ratio = current_bet / self.chips if self.chips > 0 else 1
        pot_odds = current_bet / (current_bet + self.chips) if current_bet > 0 else 0
        
        # Game phase with more detail
        if len(community_cards) == 0:
            phase = "preflop"
            board_texture = "none"
        elif len(community_cards) == 3:
            phase = "flop"
            board_texture = self._evaluate_board_texture(community_cards)
        elif len(community_cards) == 4:
            phase = "turn"
            board_texture = self._evaluate_board_texture(community_cards)
        else:
            phase = "river"
            board_texture = self._evaluate_board_texture(community_cards)
            
        # Use position that was set by the game
        position = self.position if self.position else "unknown"
        
        # Opponent modeling - track opponent's aggression frequency
        if hasattr(self, 'opponent_stats'):
            opp_aggression = self.opponent_stats.get('aggression_frequency', 0.5)
        else:
            self.opponent_stats = {'aggression_frequency': 0.5, 'fold_frequency': 0.5}
            opp_aggression = 0.5
            
        # Combine all factors into state representation
        state = (f"{phase}_{board_texture}_{position}_"
                f"{hand_strength:.2f}_{chips_ratio:.2f}_"
                f"{bet_ratio:.2f}_{pot_odds:.2f}_"
                f"{opp_aggression:.2f}")
        return state
        
    def _evaluate_board_texture(self, community_cards: List[Card]) -> str:
        """
        Evaluates the board texture (dry, wet, paired, etc.)
        """
        if not community_cards:
            return "none"
            
        # Count suits and ranks
        suits = [card.suit for card in community_cards]
        ranks = [card.value for card in community_cards]
        
        # Check for flush draws
        flush_draw = any(suits.count(suit) >= 3 for suit in set(suits))
        
        # Check for straight draws
        sorted_ranks = sorted(ranks)
        straight_draw = False
        for i in range(len(sorted_ranks) - 2):
            if sorted_ranks[i+2] - sorted_ranks[i] <= 4:
                straight_draw = True
                break
                
        # Check for paired board
        paired = len(set(ranks)) < len(ranks)
        
        # Determine texture
        if paired:
            return "paired"
        elif flush_draw and straight_draw:
            return "very_wet"
        elif flush_draw or straight_draw:
            return "wet"
        else:
            return "dry"

    def update_q_value(self, state: str, action: str, reward: float, next_state: str):
        """
        Updates Q-value with sequence-aware learning and adaptive parameters
        """
        if state not in self.q_table:
            self.q_table[state] = {'fold': 0, 'call': 0, 'raise': 0}
        
        if next_state not in self.q_table:
            self.q_table[next_state] = {'fold': 0, 'call': 0, 'raise': 0}
        
        # Initialize game sequence if not exists
        if not hasattr(self, 'game_sequence'):
            self.game_sequence = {
                'hands_played': 0,
                'total_chip_diff': 0,
                'win_streak': 0,
                'max_chips': self.chips,
                'learning_steps': 0
            }
        
        self.game_sequence['learning_steps'] += 1
        
        # Adaptive learning rate based on sequence performance
        base_learning_rate = self.learning_rate
        if self.game_sequence['hands_played'] > 0:
            # Adjust learning rate based on performance trend
            avg_chip_diff = self.game_sequence['total_chip_diff'] / self.game_sequence['hands_played']
            performance_factor = 1.0 + (avg_chip_diff * 0.5)  # Increase learning when performing well
            win_streak_factor = 1.0 + (min(self.game_sequence['win_streak'] * 0.1, 0.5))  # Bonus for win streaks
            
            # Decay learning rate over time but maintain minimum
            time_decay = max(0.5, 1.0 / (1 + 0.0005 * self.game_sequence['learning_steps']))
            
            adaptive_learning_rate = base_learning_rate * performance_factor * win_streak_factor * time_decay
            learning_rate = min(0.5, max(0.01, adaptive_learning_rate))  # Keep between 0.01 and 0.5
        else:
            learning_rate = base_learning_rate
        
        # Enhanced temporal difference calculation
        current_q = self.q_table[state][action]
        next_max_q = max(self.q_table[next_state].values())
        
        # Adjust discount factor based on game stage and performance
        base_discount = self.discount_factor
        if hasattr(self, 'chips'):
            chips_ratio = self.chips / 1000  # Normalize by initial chips
            # Increase long-term planning when ahead, more immediate rewards when behind
            adjusted_discount = base_discount * (1.0 + (chips_ratio - 1.0) * 0.2)
            discount_factor = min(0.99, max(0.5, adjusted_discount))
        else:
            discount_factor = base_discount
        
        # Calculate temporal difference with sequence-aware discounting
        temporal_diff = reward + discount_factor * next_max_q - current_q
        
        # Update Q-value with eligibility traces
        if not hasattr(self, 'eligibility_traces'):
            self.eligibility_traces = {}
        
        # Initialize or decay eligibility traces with adaptive decay
        trace_decay = 0.9 if self.game_sequence['hands_played'] < 10 else 0.95  # More persistent traces later in game
        for s in self.q_table:
            if s not in self.eligibility_traces:
                self.eligibility_traces[s] = {'fold': 0, 'call': 0, 'raise': 0}
            for a in self.eligibility_traces[s]:
                self.eligibility_traces[s][a] *= trace_decay
        
        # Set eligibility trace for current state-action pair
        if state not in self.eligibility_traces:
            self.eligibility_traces[state] = {'fold': 0, 'call': 0, 'raise': 0}
        self.eligibility_traces[state][action] = 1.0
        
        # Update all state-action pairs according to their eligibility
        for s in self.q_table:
            for a in self.q_table[s]:
                if s in self.eligibility_traces:
                    update = learning_rate * temporal_diff * self.eligibility_traces[s][a]
                    
                    # Limit the magnitude of updates to prevent instability
                    max_update = 0.5  # Maximum allowed update
                    update = max(-max_update, min(max_update, update))
                    
                    self.q_table[s][a] += update

    def make_decision(self, community_cards: List[Card], current_bet: int, min_raise: int) -> Tuple[str, int]:
            if self.is_machine:
                state = self.get_state(community_cards, current_bet)
                
                if state not in self.q_table:
                    # Strategic initial Q-values
                    hand_strength = self.evaluate_hand_strength(community_cards)
                    position_factor = 1.2 if "late" in state else 0.8  # Increased position impact
                    texture_factor = 1.2 if "wet" in state or "very_wet" in state else 1.0
                    
                    # Base values that encourage more action with strong hands
                    fold_base = -0.2 - (hand_strength * 0.3)  # Stronger penalty for folding good hands
                    call_base = 0.0 + (hand_strength * 0.4) * position_factor  # More reward for calling with good hands
                    raise_base = -0.1 + (hand_strength * 0.5) * position_factor * texture_factor  # Aggressive with very strong hands
                    
                    # Adjust for preflop play
                    if len(community_cards) == 0:
                        if hand_strength > 0.7:  # Premium hands
                            fold_base -= 0.2
                            raise_base += 0.3
                        elif hand_strength > 0.5:  # Playable hands
                            call_base += 0.2
                    
                    self.q_table[state] = {
                        'fold': fold_base,
                        'call': call_base,
                        'raise': raise_base
                    }
                
                # Dynamic exploration strategy
                hand_strength = self.evaluate_hand_strength(community_cards)
                
                # Exploration rates based on game stage
                base_epsilon = 0.15  # Lower base exploration
                phase_factor = 1.0 if len(community_cards) == 0 else 0.8  # More consistent preflop play
                position_factor = 1.2 if "late" in state else 0.8  # Increased position impact
                stack_factor = float(state.split('_')[4])  # chips_ratio
                
                # Exploration rate that considers hand strength more strongly
                epsilon = min(0.4, (base_epsilon * phase_factor * position_factor * 
                         (1 - hand_strength * 0.8) * stack_factor))  # More hand-strength dependent
                
                # Initialize opponent stats with total_actions
                if not hasattr(self, 'opponent_stats'):
                    self.opponent_stats = {
                        'aggression_frequency': 0.5,
                        'fold_frequency': 0.5,
                        'raise_frequency': 0.5,
                        'action_history': [],
                        'total_actions': 0
                    }
                elif 'total_actions' not in self.opponent_stats:
                    self.opponent_stats['total_actions'] = 0
                
                if random.random() < epsilon:
                    # Strategic action weights based on situation and position
                    if hand_strength > 0.8:  # Premium hands (AA, KK, QQ, AKs)
                        if "late" in state:
                            weights = {'fold': 0, 'call': 1, 'raise': 5}  # Very aggressive in position
                        else:
                            weights = {'fold': 0, 'call': 2, 'raise': 4}  # Aggressive out of position
                    elif hand_strength > 0.6:  # Strong hands (JJ, TT, AQs, AJs)
                        if "late" in state:
                            weights = {'fold': 0, 'call': 2, 'raise': 3}  # Aggressive in position
                        else:
                            weights = {'fold': 1, 'call': 3, 'raise': 2}  # More cautious out of position
                    elif hand_strength > 0.4:  # Playable hands (99, 88, ATs, KQs)
                        if "late" in state:
                            weights = {'fold': 1, 'call': 3, 'raise': 2}  # Position allows more aggression
                        else:
                            weights = {'fold': 2, 'call': 3, 'raise': 1}  # Mostly call out of position
                    elif hand_strength > 0.2:  # Marginal hands (77, A9s, KJs)
                        if "late" in state:
                            weights = {'fold': 2, 'call': 3, 'raise': 1}  # Mostly call in position
                        else:
                            weights = {'fold': 3, 'call': 2, 'raise': 0}  # Often fold out of position
                    else:  # Weak hands
                        if "late" in state:
                            weights = {'fold': 3, 'call': 1, 'raise': 0}  # Sometimes play in position
                        else:
                            weights = {'fold': 4, 'call': 1, 'raise': 0}  # Almost always fold
                            
                    # Adjust weights based on board texture
                    if "very_wet" in state:
                        # More cautious on very coordinated boards
                        weights['raise'] = max(0, weights['raise'] - 1)
                        weights['call'] += 1
                    elif "paired" in state:
                        # More aggressive on paired boards with strong hands
                        if hand_strength > 0.6:
                            weights['raise'] += 1
                            weights['fold'] = max(0, weights['fold'] - 1)
                    
                    # More conservative adjustments based on opponent tendencies
                    if self.opponent_stats['total_actions'] > 10:  # Only adjust if we have enough data
                        if self.opponent_stats['aggression_frequency'] > 0.7:
                            weights['raise'] *= 0.8  # More defensive against aggressive opponents
                            weights['call'] *= 1.2
                        elif self.opponent_stats['fold_frequency'] > 0.7:
                            weights['raise'] *= 1.2  # Slightly more aggressive against tight opponents
                    
                    actions = list(weights.keys())
                    weights = list(weights.values())
                    action = random.choices(actions, weights=weights)[0]
                    
                    # Update opponent stats
                    self.opponent_stats['total_actions'] += 1
                    if action == 'raise':
                        self.opponent_stats['aggression_frequency'] = (
                            (self.opponent_stats['aggression_frequency'] * (self.opponent_stats['total_actions'] - 1) + 1) / 
                            self.opponent_stats['total_actions']
                        )
                    elif action == 'fold':
                        self.opponent_stats['fold_frequency'] = (
                            (self.opponent_stats['fold_frequency'] * (self.opponent_stats['total_actions'] - 1) + 1) / 
                            self.opponent_stats['total_actions']
                        )
                else:
                    # Strategic action selection
                    q_values = self.q_table[state]
                    max_q = max(q_values.values())
                    best_actions = [a for a, q in q_values.items() if q == max_q]
                    
                    # Break ties based on multiple factors
                    if len(best_actions) > 1:
                        if "late" in state and hand_strength > 0.5:
                            action = 'raise' if 'raise' in best_actions else best_actions[0]
                        elif "wet" in state or "very_wet" in state:
                            action = 'call' if 'call' in best_actions else best_actions[0]
                        else:
                            action = best_actions[0]
                    else:
                        action = best_actions[0]
                    
                    # Update opponent stats
                    self.opponent_stats['total_actions'] += 1
                    if action == 'raise':
                        self.opponent_stats['aggression_frequency'] = (
                            (self.opponent_stats['aggression_frequency'] * (self.opponent_stats['total_actions'] - 1) + 1) / 
                            self.opponent_stats['total_actions']
                        )
                    elif action == 'fold':
                        self.opponent_stats['fold_frequency'] = (
                            (self.opponent_stats['fold_frequency'] * (self.opponent_stats['total_actions'] - 1) + 1) / 
                            self.opponent_stats['total_actions']
                        )
                
                # Store state and action for Q-value update
                self.last_state = state
                self.last_action = action
                
                if action == "fold":
                    self.folded = True
                    print(f"\n❌ {self.name} folds!")
                    return "fold", 0
                elif action == "raise":
                    raise_amount = min(current_bet + min_raise, self.chips)
                    if raise_amount >= self.chips:
                        raise_amount = self.chips
                        print(f"\n🔥 {self.name} está ALL-IN!")
                        print(f"► Apostou seus últimos {raise_amount} chips!")
                        return "raise", raise_amount
                    else:
                        print(f"\n💰 {self.name} aumenta para {raise_amount} chips!")
                        self.chips -= raise_amount
                        return "raise", raise_amount
                else:  # call
                    bet_amount = min(current_bet, self.chips)
                    if bet_amount >= self.chips:
                        bet_amount = self.chips
                        print(f"\n🔥 {self.name} está ALL-IN!")
                        print(f"► Apostou seus últimos {bet_amount} chips!")
                    else:
                        print(f"\n✅ {self.name} pagou {bet_amount} chips")
                    self.chips -= bet_amount
                    return "call", bet_amount
                    
            else:
                # Método atual para jogadores humanos
                while True:
                    try:
                        print(f"\n🎮 SUA VEZ ({self.name})!")
                        print("-" * 40)
                        print(f"🎴 Suas cartas: {self.show_hand()}")
                        if len(community_cards) > 0:
                            print(f"🎴 Mesa: {', '.join(str(c) for c in community_cards)}")
                            hand_type, _ = self.get_hand_value(community_cards)
                            print(f"🃏 Seu melhor jogo: {hand_type}")
                        print(f"💰 Aposta atual: {current_bet}")
                        print(f"💰 Seus chips: {self.chips}")
                        print("-" * 40)
                        
                        # Mostra opções disponíveis
                        print("\nOpções disponíveis:")
                        if self.chips == 0:
                            print("❌ Você não tem mais chips para apostar!")
                            return "fold", 0
                        
                        if current_bet >= self.chips:
                            print("1. (a) 🔥 ALL-IN com", self.chips, "chips")
                            print("2. (f) ❌ Fold")
                            action = input("\nEscolha sua ação: ").lower()
                            if action == 'a' or action == '1':
                                return "call", self.chips  # All-in
                            return "fold", 0
                        
                        print(f"1. (c) ✅ Call: {current_bet} chips")
                        if current_bet + min_raise <= self.chips:
                            print(f"2. (r) 💰 Raise: mínimo {current_bet + min_raise} chips")
                        else:
                            print("2. (r) 💰 Raise: indisponível (chips insuficientes)")
                        print("3. (a) 🔥 ALL-IN com", self.chips, "chips")
                        print("4. (f) ❌ Fold")
                        
                        action = input("\nEscolha sua ação: ").lower()
                        
                        if action in ['c', '1']:
                            bet_amount = min(current_bet, self.chips)
                            return "call", bet_amount
                        elif action in ['r', '2']:
                            if current_bet + min_raise <= self.chips:
                                raise_amount = current_bet + min_raise
                                print(f"\nValor mínimo para raise: {raise_amount}")
                                print(f"Seus chips disponíveis: {self.chips}")
                                try:
                                    amount = int(input("Digite o valor do raise (ou 0 para cancelar): "))
                                    if amount == 0:
                                        continue
                                    if amount >= raise_amount and amount <= self.chips:
                                        return "raise", amount
                                    else:
                                        print("❌ Valor inválido!")
                                except ValueError:
                                    print("❌ Valor inválido!")
                            else:
                                print("❌ Chips insuficientes para raise!")
                        elif action in ['a', '3']:
                            return "raise", self.chips  # All-in
                        elif action in ['f', '4']:
                            return "fold", 0
                    except KeyboardInterrupt:
                        return "fold", 0
            
            return "fold", 0

class HistoryManager:
    def __init__(self, history_file="history.json"):
        self.history_file = history_file
        try:
            with open(self.history_file, "r") as f:
                self.games = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            self.games = []

    def record_game(self, game_data):
        self.games.append(game_data)
        self.save_history()

    def save_history(self):
        with open(self.history_file, "w") as f:
            json.dump(self.games, f, indent=4)

class RankingManager:
    def __init__(self, ranking_file="ranking.json"):
        self.ranking_file = ranking_file
        try:
            with open(self.ranking_file, "r") as f:
                self.rankings = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            self.rankings = {}

    def update_ranking(self, winner_name):
        self.rankings[winner_name] = self.rankings.get(winner_name, 0) + 1
        self.save_ranking()

    def save_ranking(self):
        with open(self.ranking_file, "w") as f:
            json.dump(self.rankings, f, indent=4)

class PokerGame:
    def __init__(self, players):
        self.deck = Deck()
        self.players = players
        self.history_manager = HistoryManager()
        self.ranking_manager = RankingManager()
        self.current_state = "pre-flop"
        self.community_cards: List[Card] = []
        self.pot = 0
        self.current_bet = 50  # Aposta inicial
        self.min_raise = 50    # Valor mínimo para raise
        
        # Set player positions
        for i, player in enumerate(players):
            player.position = "early" if i == 0 else "late"

    def deal_cards(self):
        # Distribuir 2 cartas para cada jogador, simulando o pré-flop
        for player in self.players:
            player.hand = []
            player.receive_card(self.deck.draw())
            player.receive_card(self.deck.draw())

    def deal_community_cards(self, count: int):
        for _ in range(count):
            card = self.deck.draw()
            if card:
                self.community_cards.append(card)

    def show_community_cards(self):
        return ", ".join(str(card) for card in self.community_cards)

    def betting_round(self) -> int:
        round_pot = 0
        active_players = [p for p in self.players if not p.folded]
        
        for player in active_players:
            print(f"\n👤 {player.name}")
            print(f"💰 Chips: {player.chips}")
            if len(self.community_cards) > 0:
                hand_type, _ = player.get_hand_value(self.community_cards)
                print(f"🃏 Melhor jogo: {hand_type}")
                print(f"🎴 Cartas na mão: {player.show_hand()}")
                print(f"🎴 Mesa: {self.show_community_cards()}")
            else:
                print(f"🎴 Cartas na mão: {player.show_hand()}")
            print("-" * 40)
            
            # Verifica situação de all-in
            if player.chips == 0:
                player.folded = True
                print(f"❌ {player.name} não tem mais chips e está fora!")
                continue
            
            # Se o jogador não tem chips suficientes para a aposta mínima
            is_all_in = player.chips <= self.current_bet
            if is_all_in:
                print(f"\n🔥 SITUAÇÃO DE ALL-IN!")
                print(f"► Aposta necessária: {self.current_bet}")
                print(f"► Chips disponíveis: {player.chips}")
            
            action, bet_amount = player.make_decision(self.community_cards, self.current_bet, self.min_raise)
            
            if action == "fold":
                player.folded = True
                print(f"\n❌ {player.name} folds!")
            elif action == "raise":
                if bet_amount >= player.chips:  # All-in
                    bet_amount = player.chips
                    print(f"\n🔥 {player.name} está ALL-IN!")
                    print(f"► Apostou seus últimos {bet_amount} chips!")
                else:
                    print(f"\n💰 {player.name} aumenta para {bet_amount} chips!")
                
                player.chips -= bet_amount
                round_pot += bet_amount
                self.current_bet = bet_amount
                
                # Se alguém deu raise, precisa dar chance dos outros igualarem
                for other_player in [p for p in active_players if p != player and not p.folded]:
                    print(f"\n👤 {other_player.name}")
                    print(f"💰 Chips: {other_player.chips}")
                    print("-" * 40)
                    
                    # Verifica situação de all-in do outro jogador
                    if other_player.chips == 0:
                        other_player.folded = True
                        print(f"❌ {other_player.name} não tem mais chips e está fora!")
                        continue
                    
                    is_all_in = other_player.chips <= self.current_bet
                    if is_all_in:
                        print(f"\n🔥 SITUAÇÃO DE ALL-IN!")
                        print(f"► Aposta necessária: {self.current_bet}")
                        print(f"► Chips disponíveis: {other_player.chips}")
                    
                    response, response_amount = other_player.make_decision(self.community_cards, self.current_bet, self.min_raise)
                    if response == "fold":
                        other_player.folded = True
                        print(f"\n❌ {other_player.name} folds!")
                    else:  # call
                        if response_amount >= other_player.chips:  # All-in
                            response_amount = other_player.chips
                            print(f"\n🔥 {other_player.name} está ALL-IN!")
                            print(f"► Apostou seus últimos {response_amount} chips!")
                        else:
                            print(f"\n✅ {other_player.name} pagou {response_amount} chips")
                        
                        other_player.chips -= response_amount
                        round_pot += response_amount
            else:  # call
                if bet_amount >= player.chips:  # All-in
                    bet_amount = player.chips
                    print(f"\n🔥 {player.name} está ALL-IN!")
                    print(f"► Apostou seus últimos {bet_amount} chips!")
                else:
                    print(f"\n✅ {player.name} pagou {bet_amount} chips")
                
                player.chips -= bet_amount
                round_pot += bet_amount
        
        return round_pot

    def determine_winner(self) -> Optional[Player]:
        active_players = [p for p in self.players if not p.folded]
        if not active_players:
            return None
            
        if len(active_players) == 1:
            winner = active_players[0]
            print(f"\n🏆 {winner.name} vence por desistência!")
            return winner
        
        print("\n" + "="*20 + " SHOWDOWN " + "="*20)
        max_hand = ("", -1)
        winner = None
        
        # Mostra as mãos de todos os jogadores ativos
        print("\n📊 RESULTADO FINAL DAS MÃOS:")
        for player in active_players:
            hand_type, value = player.get_hand_value(self.community_cards)
            print("\n" + "-" * 40)
            print(f"👤 {player.name}:")
            print(f"🃏 MELHOR JOGO: {hand_type}")
            print(f"🎴 Cartas na mão: {player.show_hand()}")
            print(f"🎴 Cartas da mesa: {self.show_community_cards()}")
            print("-" * 40)
            
            # Atualiza o vencedor se esta mão for melhor
            if value > max_hand[1]:
                max_hand = (hand_type, value)
                winner = player
        
        if winner:
            print(f"\n🏆 {winner.name} vence a mão!")
            print(f"🃏 Melhor jogo: {max_hand[0]}")
            print(f"🎴 Cartas do vencedor: {winner.show_hand()}")
            print(f"🎴 Cartas da mesa: {self.show_community_cards()}")
        
        return winner

    def play(self):
        print("\n" + "="*50)
        print("           INICIANDO NOVA MÃO")
        print("="*50)
        
        self.deal_cards()
        print("\n🎴 MÃOS INICIAIS:")
        print("-"*30)
        for player in self.players:
            print(f"► {player.name}: {player.show_hand()}")

        # Pré-flop
        print("\n" + "="*20 + " PRÉ-FLOP " + "="*20)
        self.pot += self.betting_round()
        
        # Se todos menos um jogador desistiram, termina o jogo
        if len([p for p in self.players if not p.folded]) <= 1:
            winner = self.determine_winner()
            if winner:
                print(f"\n🏆 {winner.name} vence por desistência!")
        else:
            # Flop
            print("\n" + "="*22 + " FLOP " + "="*22)
            self.deal_community_cards(3)
            print("\n🎴 CARTAS COMUNITÁRIAS:")
            print("-"*30)
            print(f"► {self.show_community_cards()}")
            self.pot += self.betting_round()
            
            if len([p for p in self.players if not p.folded]) > 1:
                # Turn
                print("\n" + "="*22 + " TURN " + "="*22)
                self.deal_community_cards(1)
                print("\n🎴 CARTAS COMUNITÁRIAS:")
                print("-"*30)
                print(f"► {self.show_community_cards()}")
                self.pot += self.betting_round()
                
                if len([p for p in self.players if not p.folded]) > 1:
                    # River
                    print("\n" + "="*22 + " RIVER " + "="*22)
                    self.deal_community_cards(1)
                    print("\n🎴 CARTAS COMUNITÁRIAS:")
                    print("-"*30)
                    print(f"► {self.show_community_cards()}")
                    self.pot += self.betting_round()

        # Calcula taxa e pagamento
        fee = self.pot * 0.10  # Taxa de 10%
        payout = self.pot - fee

        # Determina o vencedor
        winner = self.determine_winner()
        if winner:
            winner.chips += payout
            self.ranking_manager.update_ranking(winner.name)
            
            # Atualiza Q-values para máquinas baseado no resultado
            for player in self.players:
                if player.is_machine:
                    # Find opponent
                    opponent = next(p for p in self.players if p != player)
                    
                    # Calculate chip difference relative to opponent
                    chips_diff = (player.chips - opponent.chips) / 1000  # Normalize by initial chips
                    
                    # Track game sequence performance
                    if not hasattr(player, 'game_sequence'):
                        player.game_sequence = {
                            'hands_played': 0,
                            'total_chip_diff': 0,
                            'win_streak': 0,
                            'max_chips': player.chips,
                            'learning_steps': 0
                        }
                    
                    player.game_sequence['hands_played'] += 1
                    player.game_sequence['total_chip_diff'] += chips_diff
                    
                    if player == winner:
                        player.game_sequence['win_streak'] += 1
                    else:
                        player.game_sequence['win_streak'] = 0
                    
                    player.game_sequence['max_chips'] = max(player.game_sequence['max_chips'], player.chips)
                    
                    # Calculate sequence-based metrics
                    avg_chip_diff = player.game_sequence['total_chip_diff'] / player.game_sequence['hands_played']
                    win_streak_bonus = min(0.1 * player.game_sequence['win_streak'], 0.3)  # Cap at 0.3
                    chip_retention = player.chips / player.game_sequence['max_chips']
                    
                    # Hand strength and position factors
                    hand_strength = player.evaluate_hand_strength(self.community_cards)
                    position_multiplier = 1.1 if player.position == "late" else 0.9
                    
                    # Action-based components
                    action_reward = 0.0
                    if hasattr(player, 'last_action'):
                        if player.last_action == 'raise':
                            if chips_diff > 0:  # Reward aggressive play when ahead
                                action_reward = 0.2
                            else:  # Smaller reward when behind to encourage comebacks
                                action_reward = 0.1
                        elif player.last_action == 'fold':
                            action_reward = 0.1 if chips_diff < -0.3 else -0.1  # Reward conservative play when significantly behind
                    
                    # Combine rewards with emphasis on chip difference and sequence performance
                    reward = (
                        0.4 * chips_diff +           # Current hand performance
                        0.2 * avg_chip_diff +        # Long-term performance
                        0.15 * win_streak_bonus +    # Consecutive wins bonus
                        0.15 * chip_retention +      # Bankroll management
                        0.1 * action_reward          # Action-specific reward
                    ) * position_multiplier
                    
                    # Estado final é o estado atual
                    final_state = player.get_state(self.community_cards, self.current_bet)
                    
                    # Atualiza Q-value para a última ação
                    if hasattr(player, 'last_state') and hasattr(player, 'last_action'):
                        player.update_q_value(player.last_state, player.last_action, reward, final_state)
            
            result = {
                "winner": winner.name,
                "state": self.current_state,
                "total_pot": self.pot,
                "fee": fee,
                "payout": payout,
                "community_cards": self.show_community_cards(),
                "players": [{
                    "name": p.name,
                    "hand": p.show_hand(),
                    "chips": p.chips,
                    "folded": p.folded
                } for p in self.players]
            }
            self.history_manager.record_game(result)
            print("\n📊 RESULTADO DA PARTIDA:")
            print("-"*40)
            print(f"🏆 Vencedor: {result['winner']}")
            print(f"💰 Pote total: {result['total_pot']}")
            print(f"💸 Taxa: {result['fee']}")
            print(f"💵 Pagamento: {result['payout']}")
            print(f"🎴 Mesa final: {result['community_cards']}")
            print("\n👥 JOGADORES:")
            for p in result['players']:
                print(f"► {p['name']}:")
                print(f"  Cartas: {p['hand']}")
                print(f"  Chips: {p['chips']}")
                print(f"  Status: {'Desistiu' if p['folded'] else 'Jogou até o fim'}")
                print()

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
        "Máquina 1": {"wins": 0, "chips_won": 0, "folds": 0},
        "Máquina 2": {"wins": 0, "chips_won": 0, "folds": 0}
    }
    
    for game_num in range(1, num_games + 1):
        print(f"\n📊 Progresso: Jogo {game_num}/{num_games}")
        print(f"💰 Chips - Máquina 1: {machine1.chips}, Máquina 2: {machine2.chips}")
        
        # Reset chips para cada novo jogo para manter consistência
        machine1.chips = 1000
        machine2.chips = 1000
        
        game = PokerGame([machine1, machine2])
        game.play()
        
        # Registra estatísticas
        if machine1.folded:
            stats["Máquina 1"]["folds"] += 1
        if machine2.folded:
            stats["Máquina 2"]["folds"] += 1
            
        if machine1.chips > machine2.chips:
            stats["Máquina 1"]["wins"] += 1
            stats["Máquina 1"]["chips_won"] += (machine1.chips - 1000)
        else:
            stats["Máquina 2"]["wins"] += 1
            stats["Máquina 2"]["chips_won"] += (machine2.chips - 1000)
            
        # Salva Q-tables após cada jogo
        machine1.save_q_table()
        machine2.save_q_table()
    
    # Exibe resultados finais
    print("\n" + "="*50)
    print("           RESULTADOS DO TESTE")
    print("="*50)
    
    for machine, results in stats.items():
        win_rate = (results["wins"] / num_games) * 100
        avg_chips = results["chips_won"] / num_games
        fold_rate = (results["folds"] / num_games) * 100
        print(f"\n► {machine}:")
        print(f"  Vitórias: {results['wins']} ({win_rate:.1f}%)")
        print(f"  Média de chips ganhos por jogo: {avg_chips:.1f}")
        print(f"  Desistências: {results['folds']} ({fold_rate:.1f}%)")

if __name__ == "__main__":
    try:
        print("\n" + "="*50)
        print("           TAXAS HOLD'EM")
        print("="*50)
        print("\n💫 Bem-vindo ao Taxas Hold'em!")
        print("🎮 Escolha o modo de jogo:")
        print("1. Jogador vs Máquina")
        print("2. Teste Máquina vs Máquina")
        
        mode = input("\nDigite o número do modo desejado (1 ou 2): ")
        
        if mode == "2":
            try:
                games_input = input("Digite o número de jogos para testar (recomendado: 100): ")
                num_games = int(games_input) if games_input.strip() else 100
                run_machine_vs_machine_test(num_games)
            except ValueError:
                print("\n❌ Valor inválido! Usando valor padrão de 100 jogos.")
                run_machine_vs_machine_test(100)
        else:
            print("\n🎮 O jogo continuará até que um dos jogadores perca todos os seus chips.")
            player1 = Player("Jogador 1")
            machine_player = Player("Máquina", is_machine=True)
            hand_number = 1
            
            try:
                while player1.chips > 0 and machine_player.chips > 0:
                    print(f"\n" + "="*50)
                    print(f"             MÃO #{hand_number}")
                    print("="*50)
                    print(f"\n💰 CHIPS ATUAIS:")
                    print("-"*30)
                    print(f"► Jogador 1: {player1.chips}")
                    print(f"► Máquina: {machine_player.chips}")
                    
                    game = PokerGame([player1, machine_player])
                    game.play()
                    hand_number += 1
                    
                    # Reset para próxima mão
                    player1.folded = False
                    machine_player.folded = False
                    
                    try:
                        input("\n⏩ Pressione Enter para continuar ou Ctrl+C para sair...")
                    except KeyboardInterrupt:
                        print("\n❌ Interrupção detectada. Encerrando jogo...")
                        break
                
                # Determina o vencedor do jogo
                print("\n" + "="*50)
                print("           FIM DO JOGO")
                print("="*50)
                
                if player1.chips <= 0:
                    print(f"\n🏆 Jogo encerrado! A Máquina venceu após {hand_number-1} mãos!")
                elif machine_player.chips <= 0:
                    print(f"\n🏆 Jogo encerrado! O Jogador 1 venceu após {hand_number-1} mãos!")
                else:
                    print("\n❌ Jogo interrompido pelo usuário.")
                
                # Salva a Q-table da máquina ao final do jogo
                machine_player.save_q_table()
            except KeyboardInterrupt:
                print("\n❌ Interrupção detectada. Encerrando jogo...")
                machine_player.save_q_table()
            
    except KeyboardInterrupt:
        print("\n❌ Interrupção detectada. Encerrando jogo...")
    finally:
        rm = RankingManager()
        print("\n📊 RANKING FINAL:")
        print("-"*30)
        rankings = rm.rankings
        sorted_rankings = sorted(rankings.items(), key=lambda x: x[1], reverse=True)
        for name, wins in sorted_rankings:
            print(f"► {name}: {wins} vitórias")
