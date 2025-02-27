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

    def get_hand_value(self, community_cards: List[Card]) -> Tuple[str, int]:
        all_cards = self.hand + community_cards

        if not all_cards:
            return "Carta Alta", 100  # Return a default value if there are no cards
        
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
