#!/usr/bin/env python3
import random
import json
from typing import List, Optional, Dict, Tuple
from card import Card

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
        import os
        q_table_path = os.path.join(os.getcwd(), "q_table.json")
        try:
            with open(q_table_path, "r") as f:
                q_tables = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            q_tables = {}
        
        q_tables[self.name] = self.q_table
        with open(q_table_path, "w") as f:
            json.dump(q_tables, f, indent=4)

    def receive_card(self, card: Card):
        if card:
            self.hand.append(card)

    def show_hand(self):
        return ", ".join(str(card) for card in self.hand)

    def get_hand_value(self, community_cards: List[Card]) -> Tuple[str, Tuple[int, ...]]:
        """
        Retorna o nome da mão e uma tupla com valores para comparação.
        A tupla tem formato: (base_value, card1, card2, card3, card4, card5)
        onde card1-5 representam as 5 cartas da melhor mão em ordem de importância.
        """
        all_cards = self.hand + community_cards

        if not all_cards:
            return "Carta Alta", (100, 0, 0, 0, 0, 0)

        # Ordena todas as cartas por valor decrescente
        sorted_cards = sorted(all_cards, key=lambda x: x.value, reverse=True)

        # Conta pares, trincas, quadras
        rank_count: Dict[str, int] = {}
        for card in all_cards:
            rank_count[card.rank] = rank_count.get(card.rank, 0) + 1

        # Verifica flush
        flush_suit = None
        flush_cards = []
        for suit in Card.suits:
            suited_cards = sorted([card for card in all_cards if card.suit == suit],
                                  key=lambda x: x.value, reverse=True)
            if len(suited_cards) >= 5:
                flush_suit = suit
                flush_cards = suited_cards[:5]  # Pega as 5 maiores
                break

        # Função auxiliar para verificar sequências
        def find_straight(cards_list):
            """Retorna a maior sequência encontrada ou None"""
            values = sorted(list(set([c.value for c in cards_list])), reverse=True)

            # Verifica sequências normais (maior para menor)
            for i in range(len(values) - 4):
                if values[i] - values[i+4] == 4:  # Sequência de 5 cartas
                    return [values[i], values[i+1], values[i+2], values[i+3], values[i+4]]

            # Verifica sequência A-2-3-4-5 (wheel)
            if 14 in values and 5 in values and 4 in values and 3 in values and 2 in values:
                return [5, 4, 3, 2, 1]  # A conta como 1 nesse caso

            return None

        # Verifica Royal Flush
        if flush_cards:
            royal_values = {14, 13, 12, 11, 10}
            if set(c.value for c in flush_cards[:5]) == royal_values:
                return "Royal Flush", (1000, 14, 13, 12, 11, 10)

        # Verifica Straight Flush
        if flush_cards:
            straight_values = find_straight(flush_cards)
            if straight_values:
                return "Straight Flush", (900, straight_values[0], straight_values[1],
                                         straight_values[2], straight_values[3], straight_values[4])

        # Quadra (Four of a Kind)
        quads = [rank for rank, count in rank_count.items() if count == 4]
        if quads:
            quad_rank = quads[0]
            quad_value = Card.rank_values[quad_rank]
            # Encontra o melhor kicker
            kickers = sorted([c.value for c in all_cards if c.rank != quad_rank], reverse=True)
            kicker = kickers[0] if kickers else 0
            return "Quadra", (800, quad_value, quad_value, quad_value, quad_value, kicker)

        # Full House
        threes = sorted([rank for rank, count in rank_count.items() if count == 3],
                       key=lambda r: Card.rank_values[r], reverse=True)
        pairs = sorted([rank for rank, count in rank_count.items() if count == 2],
                      key=lambda r: Card.rank_values[r], reverse=True)

        if threes and (pairs or len(threes) >= 2):
            three_value = Card.rank_values[threes[0]]
            # Se temos duas trincas, a segunda vira o par
            if len(threes) >= 2:
                pair_value = Card.rank_values[threes[1]]
            else:
                pair_value = Card.rank_values[pairs[0]]
            return "Full House", (700, three_value, three_value, three_value, pair_value, pair_value)

        # Flush
        if flush_cards:
            return "Flush", (600, flush_cards[0].value, flush_cards[1].value,
                            flush_cards[2].value, flush_cards[3].value, flush_cards[4].value)

        # Sequência (Straight)
        straight_values = find_straight(all_cards)
        if straight_values:
            return "Sequência", (500, straight_values[0], straight_values[1],
                                straight_values[2], straight_values[3], straight_values[4])

        # Trinca (Three of a Kind)
        if threes:
            three_value = Card.rank_values[threes[0]]
            # Encontra os 2 melhores kickers
            kickers = sorted([c.value for c in all_cards if c.rank != threes[0]], reverse=True)
            k1 = kickers[0] if len(kickers) > 0 else 0
            k2 = kickers[1] if len(kickers) > 1 else 0
            return "Trinca", (400, three_value, three_value, three_value, k1, k2)

        # Dois Pares (Two Pair)
        if len(pairs) >= 2:
            high_pair = Card.rank_values[pairs[0]]
            low_pair = Card.rank_values[pairs[1]]
            # Encontra o melhor kicker
            kickers = sorted([c.value for c in all_cards if c.rank not in [pairs[0], pairs[1]]],
                           reverse=True)
            kicker = kickers[0] if kickers else 0
            return "Dois Pares", (300, high_pair, high_pair, low_pair, low_pair, kicker)

        # Par (One Pair)
        if len(pairs) == 1:
            pair_value = Card.rank_values[pairs[0]]
            # Encontra os 3 melhores kickers
            kickers = sorted([c.value for c in all_cards if c.rank != pairs[0]], reverse=True)
            k1 = kickers[0] if len(kickers) > 0 else 0
            k2 = kickers[1] if len(kickers) > 1 else 0
            k3 = kickers[2] if len(kickers) > 2 else 0
            return "Par", (200, pair_value, pair_value, k1, k2, k3)

        # Carta Alta (High Card)
        return "Carta Alta", (100, sorted_cards[0].value, sorted_cards[1].value if len(sorted_cards) > 1 else 0,
                              sorted_cards[2].value if len(sorted_cards) > 2 else 0,
                              sorted_cards[3].value if len(sorted_cards) > 3 else 0,
                              sorted_cards[4].value if len(sorted_cards) > 4 else 0)

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

        # Adiciona bônus para cartas altas (usa a primeira carta da tupla de valor)
        high_card_bonus = hand_value[1] / 14.0 * 0.1 if len(hand_value) > 1 else 0.0
        
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
            performance_factor = 1.0 + (avg_chip_diff * 0.3)  # Reduced performance impact
            win_streak_factor = 1.0 + (min(self.game_sequence['win_streak'] * 0.05, 0.3))  # Reduced win streak bonus
            
            # More aggressive learning rate decay
            time_decay = max(0.3, 1.0 / (1 + 0.001 * self.game_sequence['learning_steps']))  # Faster decay
            
            adaptive_learning_rate = base_learning_rate * performance_factor * win_streak_factor * time_decay
            learning_rate = min(0.3, max(0.01, adaptive_learning_rate))  # Lower maximum learning rate
        else:
            learning_rate = base_learning_rate
        
        # Enhanced temporal difference calculation
        current_q = self.q_table[state][action]
        next_max_q = max(self.q_table[next_state].values())
        
        # Adjust discount factor based on game stage and performance
        base_discount = self.discount_factor
        if hasattr(self, 'chips'):
            chips_ratio = self.chips / 1000  # Normalize by initial chips
            # More conservative long-term planning adjustment
            adjusted_discount = base_discount * (1.0 + (chips_ratio - 1.0) * 0.1)
            discount_factor = min(0.95, max(0.6, adjusted_discount))  # Higher minimum discount
        else:
            discount_factor = base_discount
        
        # Calculate temporal difference with sequence-aware discounting
        temporal_diff = reward + discount_factor * next_max_q - current_q
        
        # Update Q-value with eligibility traces
        if not hasattr(self, 'eligibility_traces'):
            self.eligibility_traces = {}
        
        # Initialize or decay eligibility traces with adaptive decay
        trace_decay = 0.85 if self.game_sequence['hands_played'] < 10 else 0.9  # Reduced trace persistence
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
                    max_update = 0.3  # Reduced maximum update
                    update = max(-max_update, min(max_update, update))
                    self.q_table[s][a] += update

    def make_decision(self, community_cards: List[Card], current_bet: int, min_raise: int) -> Tuple[str, int]:
            if self.is_machine:
                state = self.get_state(community_cards, current_bet)
                
                if state not in self.q_table:
                    # More balanced initial Q-values with randomization
                    hand_strength = self.evaluate_hand_strength(community_cards)
                    position_factor = 1.1 if "late" in state else 0.9  # Reduced position impact
                    texture_factor = 1.1 if "wet" in state or "very_wet" in state else 1.0
                    
                    # Add small random variation to prevent identical initial values
                    random_factor = lambda: random.uniform(-0.05, 0.05)
                    
                    # More conservative base values
                    fold_base = -0.1 - (hand_strength * 0.2) + random_factor()
                    call_base = 0.0 + (hand_strength * 0.3) * position_factor + random_factor()
                    raise_base = -0.05 + (hand_strength * 0.4) * position_factor * texture_factor + random_factor()
                    
                    # More balanced preflop adjustments
                    if len(community_cards) == 0:
                        if hand_strength > 0.7:  # Premium hands
                            fold_base -= 0.1
                            raise_base += 0.2
                        elif hand_strength > 0.5:  # Playable hands
                            call_base += 0.1
                    
                    self.q_table[state] = {
                        'fold': fold_base,
                        'call': call_base,
                        'raise': raise_base
                    }
                
                # Simplified decision making for human games
                if not hasattr(self, 'last_action'):
                    hand_strength = self.evaluate_hand_strength(community_cards)
                    
                    # Base decision on hand strength
                    if hand_strength > 0.8:  # Very strong hand
                        action = 'raise'
                    elif hand_strength > 0.5:  # Decent hand
                        action = 'call'
                    else:  # Weak hand
                        action = 'fold' if current_bet > self.chips * 0.1 else 'call'
                else:
                    # Don't make consecutive raises
                    action = 'call' if self.last_action == 'raise' else 'call'
                
                # Store last action
                self.last_action = action
                
                # Store state and action for Q-value update
                self.last_state = state
                self.last_action = action
                
                if action == "fold":
                    self.folded = True
                    return "fold", 0
                elif action == "raise":
                    raise_amount = min(current_bet + min_raise, self.chips)
                    if raise_amount >= self.chips:
                        raise_amount = self.chips
                        return "raise", raise_amount
                    else:
                        self.chips -= raise_amount
                        return "raise", raise_amount
                else:  # call
                    bet_amount = min(current_bet, self.chips)
                    if bet_amount >= self.chips:
                        bet_amount = self.chips
                    self.chips -= bet_amount
                    
                    # Save Q-table after significant actions
                    if self.is_machine:
                        self.save_q_table()
                    
                    return "call", bet_amount
