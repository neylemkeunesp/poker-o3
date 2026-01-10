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
        '2': '2', '3': '3', '4': '4', '5': '5', '6': 6, '7': 7, '8': 8,
        '9': 9, '10': 10, 'J': 'Valete', 'Q': 'Dama', 'K': 'Rei', 'A': 'Ás'
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

        # Adiciona bônus para cartas altas (extrai apenas o valor adicional, não o base)
        # hand_value tem formato: base + carta_alta (ex: 100 + 14 para Ás)
        # Extrair apenas o valor da carta
        base_values = {"Carta Alta": 100, "Par": 200, "Dois Pares": 300, "Trinca": 400,
                      "Sequência": 500, "Flush": 600, "Full House": 700, "Quadra": 800,
                      "Straight Flush": 900, "Royal Flush": 1000}
        base_value = base_values.get(hand_type, 0)
        card_value = hand_value - base_value  # Extrair apenas o valor adicional
        high_card_bonus = (card_value / 14.0) * 0.05  # Bônus menor e proporcional
        
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
        pot_odds = current_bet / (current_bet + self.chips) if self.chips > 0 else 0
        
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
                'max_chips': self.chips,  # Initialize with starting chips
                'learning_steps': 0
            }
        
        self.game_sequence['learning_steps'] += 1
        
        # Adaptive learning rate based on sequence performance
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
            for a in self.q_table[s]:
                if s in self.eligibility_traces:
                    update = learning_rate * temporal_diff * self.eligibility_traces[s][a]
                    max_update = 0.3  # Reduced maximum update
                    update = max(-max_update, min(max_update, update))
                    self.q_table[s][a] += update

    def make_decision(self, community_cards: List[Card], current_bet: int, min_raise: int) -> Tuple[str, int]:
            if self.is_machine:
                state = self.get_state(community_cards, current_bet)

                # Initialize Q-table for new states
                if state not in self.q_table:
                    hand_strength = self.evaluate_hand_strength(community_cards)
                    position_factor = 1.1 if "late" in state else 0.9
                    texture_factor = 1.1 if "wet" in state or "very_wet" in state else 1.0

                    random_factor = lambda: random.uniform(-0.05, 0.05)

                    fold_base = -0.1 - (hand_strength * 0.2) + random_factor()
                    call_base = 0.0 + (hand_strength * 0.3) * position_factor + random_factor()
                    raise_base = -0.05 + (hand_strength * 0.4) * position_factor * texture_factor + random_factor()

                    if len(community_cards) == 0:
                        if hand_strength > 0.7:
                            fold_base -= 0.1
                            raise_base += 0.2
                        elif hand_strength > 0.5:
                            call_base += 0.1

                    self.q_table[state] = {
                        'fold': fold_base,
                        'call': call_base,
                        'raise': raise_base
                    }

                # ===== ESTRATÉGIA MELHORADA =====
                hand_strength = self.evaluate_hand_strength(community_cards)

                # Calcular pot odds e implied odds
                pot_size = current_bet * 2  # Aproximação do pote atual
                bet_to_call = current_bet

                # Evitar divisão por zero
                if bet_to_call == 0:
                    pot_odds = 0
                else:
                    pot_odds = pot_size / (pot_size + bet_to_call) if (pot_size + bet_to_call) > 0 else 0

                # Fator de risco baseado no tamanho da aposta
                bet_size_ratio = bet_to_call / self.chips if self.chips > 0 else 1

                # Inicializar tracking de ações se necessário
                if not hasattr(self, 'action_history'):
                    self.action_history = []
                if not hasattr(self, 'consecutive_raises'):
                    self.consecutive_raises = 0

                # Usar Q-table com epsilon-greedy (exploração vs exploitação)
                epsilon = max(0.1, 0.3 - (self.game_sequence.get('hands_played', 0) * 0.01))

                if random.random() < epsilon:
                    # Exploração: decisão aleatória ponderada pela força da mão
                    weights = {
                        'fold': max(0.1, 1.0 - hand_strength),
                        'call': max(0.2, hand_strength * 0.8),
                        'raise': max(0.1, hand_strength * 1.2)
                    }
                    total_weight = sum(weights.values())
                    normalized_weights = {k: v/total_weight for k, v in weights.items()}

                    actions = list(normalized_weights.keys())
                    probabilities = list(normalized_weights.values())
                    action = np.random.choice(actions, p=probabilities)
                else:
                    # Exploitação: usar Q-table
                    q_values = self.q_table[state]
                    action = max(q_values, key=q_values.get)

                # ===== AJUSTES ESTRATÉGICOS BASEADOS EM CONTEXTO =====

                # REGRA ESPECIAL: Apostas all-in ou quase (>70%) requerem mãos feitas muito fortes
                if bet_size_ratio > 0.7:
                    # Verificar se tem mão feita forte (não apenas draw)
                    hand_type, hand_value = self.get_hand_value(community_cards)
                    made_hands = ["Flush", "Full House", "Quadra", "Straight Flush", "Royal Flush"]
                    strong_pairs = ["Trinca", "Dois Pares"]

                    if hand_type not in made_hands and hand_type not in strong_pairs:
                        # Não pagar aposta gigante com apenas draws ou pares fracos
                        action = 'fold'

                # 1. FOLD: Desistir com mãos fracas ou apostas muito altas
                if action == 'fold':
                    # Sempre fazer fold com mãos muito fracas e apostas significativas
                    if hand_strength < 0.3 and bet_size_ratio > 0.15:
                        pass  # Manter fold
                    # Considerar pot odds para draws
                    elif hand_strength >= 0.4 and pot_odds > 0.3:
                        action = 'call'  # Pot odds favoráveis, vale a pena ver
                    # Não fazer fold com mãos boas
                    elif hand_strength > 0.6:
                        action = 'call'  # Mão boa demais para desistir

                # 2. CALL: Pagar apostas
                elif action == 'call':
                    # Apostas gigantes (>70% do stack) - apenas para nuts
                    if bet_size_ratio > 0.7:
                        if hand_strength < 0.85:
                            action = 'fold'  # Só continuar com as melhores mãos
                    # Apostas muito altas (>50% do stack) requerem mãos muito fortes
                    elif bet_size_ratio > 0.5 and hand_strength < 0.7:
                        # 80% de chance de fold com aposta gigante e mão não premium
                        if random.random() < 0.8:
                            action = 'fold'
                    # Com mãos muito fortes, considerar raise em vez de call
                    elif hand_strength > 0.75 and bet_size_ratio < 0.3:
                        # 40% de chance de raise com mão forte
                        if random.random() < 0.4:
                            action = 'raise'
                    # Com mãos médias e apostas altas, considerar fold
                    elif hand_strength < 0.4 and bet_size_ratio > 0.25:
                        # 60% de chance de fold com mão fraca e aposta alta
                        if random.random() < 0.6:
                            action = 'fold'
                    # Semi-blefe com draws
                    elif 0.5 < hand_strength < 0.7 and len(community_cards) >= 3 and bet_size_ratio < 0.3:
                        # 25% de chance de raise com draw (apenas se aposta não for muito alta)
                        if random.random() < 0.25:
                            action = 'raise'

                # 3. RAISE: Aumentar aposta
                elif action == 'raise':
                    # Evitar raises consecutivos excessivos
                    if self.consecutive_raises >= 2:
                        action = 'call'  # Não ser muito agressivo
                    # Com mãos fracas, ocasionalmente blefar
                    elif hand_strength < 0.35 and bet_size_ratio < 0.15:
                        # 70% de chance de recuar do raise se mão muito fraca
                        if random.random() < 0.7:
                            action = 'fold' if bet_to_call > 0 else 'call'
                    # Limitar raises com stack baixo
                    elif self.chips < 200 and bet_size_ratio > 0.4:
                        action = 'call'  # Preservar fichas

                # ===== ESTRATÉGIA PRÉ-FLOP ESPECÍFICA =====
                if len(community_cards) == 0:
                    preflop_strength = self.evaluate_preflop_hand()

                    # Mãos premium (AA, KK, QQ, AK): jogar agressivo
                    if preflop_strength > 0.75:
                        if action == 'call' and random.random() < 0.6:
                            action = 'raise'
                    # Mãos especulativas (pares baixos, suited connectors)
                    elif 0.4 < preflop_strength < 0.6:
                        if action == 'raise':
                            action = 'call'  # Ser mais conservador
                        if bet_size_ratio > 0.2:
                            action = 'fold'  # Não pagar muito por mãos especulativas
                    # Lixo (7-2, 8-3, etc)
                    elif preflop_strength < 0.3:
                        if bet_to_call > min_raise:
                            action = 'fold'  # Descartar lixo

                # ===== ESTRATÉGIA PÓS-FLOP =====
                if len(community_cards) >= 3:
                    # Com monstros (full house+), slow play ocasionalmente
                    if hand_strength > 0.85 and random.random() < 0.3:
                        if action == 'raise':
                            action = 'call'  # Slow play para extrair valor

                    # No river, ser mais cauteloso
                    if len(community_cards) == 5:
                        # Não blefar tanto no river
                        if hand_strength < 0.4 and action == 'raise':
                            action = 'fold' if bet_to_call > 0 else 'call'

                # Atualizar histórico de ações
                self.action_history.append(action)
                if action == 'raise':
                    self.consecutive_raises += 1
                else:
                    self.consecutive_raises = 0

                # Limitar histórico a últimas 10 ações
                if len(self.action_history) > 10:
                    self.action_history.pop(0)

                # Store state and action for Q-learning
                self.last_state = state
                self.last_action = action

                # ===== EXECUTAR AÇÃO =====
                if action == "fold":
                    self.folded = True
                    return "fold", 0

                elif action == "raise":
                    # Variar tamanho do raise baseado na situação
                    if hand_strength > 0.8:
                        # Raise grande com mãos fortes (1.5x a 2.5x do mínimo)
                        raise_multiplier = random.uniform(1.5, 2.5)
                    elif hand_strength > 0.6:
                        # Raise médio com mãos boas (1x a 1.5x do mínimo)
                        raise_multiplier = random.uniform(1.0, 1.5)
                    else:
                        # Raise pequeno para blefes (0.8x a 1.2x do mínimo)
                        raise_multiplier = random.uniform(0.8, 1.2)

                    raise_amount = int(min_raise * raise_multiplier)
                    raise_amount = min(raise_amount, self.chips)
                    raise_amount = max(min_raise, raise_amount)  # Nunca menos que o mínimo

                    return "raise", raise_amount

                else:  # call
                    bet_amount = min(current_bet, self.chips)

                    # Save Q-table periodically
                    if self.is_machine and random.random() < 0.1:
                        self.save_q_table()

                    return "call", bet_amount

class PokerGame:
    def __init__(self, players):
        self.deck = Deck()
        self.community_cards = []
        self.pot = 0
        self.current_bet = 0
        self.min_raise = 20
        self.players = players
        self.history_manager = HistoryManager()
        self.ranking_manager = RankingManager()
        
    def deal_cards(self):
        """Deal initial cards to all players"""
        self.deck = Deck()  # Reset deck
        self.community_cards = []  # Reset community cards
        
        # Deal 2 cards to each player
        for _ in range(2):
            for player in self.players:
                player.receive_card(self.deck.draw())
    
    def deal_community_cards(self, count: int):
        """Deal specified number of community cards"""
        for _ in range(count):
            card = self.deck.draw()
            if card:
                self.community_cards.append(card)
    
    def show_community_cards(self) -> str:
        """Return string representation of community cards"""
        return ", ".join(str(card) for card in self.community_cards)

class HistoryManager:
    def __init__(self):
        self.history_file = "game_history.json"
        self.load_history()

    def load_history(self):
        try:
            with open(self.history_file, "r") as f:
                self.history = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            self.history = []

    def save_history(self):
        with open(self.history_file, "w") as f:
            json.dump(self.history, f, indent=4)

    def record_game(self, game_data):
        self.history.append(game_data)
        self.save_history()

class RankingManager:
    def __init__(self):
        self.ranking_file = "ranking.json"
        self.load_ranking()

    def load_ranking(self):
        try:
            with open(self.ranking_file, "r") as f:
                self.ranking = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            self.ranking = {}

    def save_ranking(self):
        with open(self.ranking_file, "w") as f:
            json.dump(self.ranking, f, indent=4)

    def update_ranking(self, winner_name):
        if winner_name not in self.ranking:
            self.ranking[winner_name] = 0
        self.ranking[winner_name] += 1
        self.save_ranking()

class Game:
    """Legacy class for machine vs machine games"""
    def __init__(self):
        self.deck = Deck()
        self.community_cards = []
        self.pot = 0
        self.current_bet = 0
        self.min_raise = 20
        
    def play_machine_vs_machine(self, num_games: int):
        self.player1 = Player("Máquina 1", is_machine=True)
        self.player2 = Player("Máquina 2", is_machine=True)
        
        for game in range(num_games):
            print(f"\n=== Jogo {game + 1} de {num_games} ===")
            
            # Create a PokerGame instance for this round
            poker_game = PokerGame([self.player1, self.player2])
            
            # Deal cards
            poker_game.deal_cards()
            
            # Set positions
            self.player1.position = "early"
            self.player2.position = "late"
            
            # Pre-flop
            print("\n=== Pré-Flop ===")
            self._betting_round([self.player1, self.player2])
            
            if not self.player1.folded and not self.player2.folded:
                # Flop
                print("\n=== Flop ===")
                poker_game.deal_community_cards(3)
                self.community_cards = poker_game.community_cards
                self._betting_round([self.player1, self.player2])
            
            if not self.player1.folded and not self.player2.folded:
                # Turn
                print("\n=== Turn ===")
                poker_game.deal_community_cards(1)
                self.community_cards = poker_game.community_cards
                self._betting_round([self.player1, self.player2])
            
            if not self.player1.folded and not self.player2.folded:
                # River
                print("\n=== River ===")
                poker_game.deal_community_cards(1)
                self.community_cards = poker_game.community_cards
                self._betting_round([self.player1, self.player2])
            
            # Showdown
            self._showdown([self.player1, self.player2])
            
            # Save Q-tables
            self.player1.save_q_table()
            self.player2.save_q_table()
    
    def _betting_round(self, players: List[Player]):
        self.current_bet = 0
        for player in players:
            if not player.folded:
                action, amount = player.make_decision(self.community_cards, self.current_bet, self.min_raise)
                if action == "raise":
                    self.current_bet = amount
                self.pot += amount
    
    def _showdown(self, players: List[Player]):
        active_players = [p for p in players if not p.folded]
        
        if not active_players:
            print("\n❌ Todos os jogadores desistiram!")
            return
        
        if len(active_players) == 1:
            winner = active_players[0]
            print(f"\n🏆 {winner.name} vence o pote de {self.pot} chips!")
            winner.chips += self.pot
            return
        
        # Compare hands - now using tuple comparison for proper tie-breaking
        hand_values = [(p, p.get_hand_value(self.community_cards)) for p in active_players]
        if hand_values:  # Only proceed if there are hands to compare
            # x[1] is (hand_name, hand_value_tuple), so x[1][1] is the tuple we compare
            best_value = max(hand_values, key=lambda x: x[1][1])
            # Find all players with the exact same hand value tuple
            winners = [p for p, v in hand_values if v[1] == best_value[1][1]]
        
        # Award the pot without any chip rebalancing
        print(f"\n💰 Antes da redistribuição - Jogador 1: {players[0].chips}, Máquina: {players[1].chips}, Pote: {self.pot}")
        if len(winners) == 1:
            winner = winners[0]
            print(f"\n🏆 {winner.name} vence {self.pot} chips com {best_value[1][0]}!")
            winner.chips += self.pot
        else:
            # Split pot among winners
            split_amount = self.pot // len(winners)
            for winner in winners:
                print(f"\n🏆 {winner.name} vence {split_amount} chips com {best_value[1][0]}!")
                winner.chips += split_amount

        self.pot = 0  # Clear the pot after distribution
        print("end_hand called")
