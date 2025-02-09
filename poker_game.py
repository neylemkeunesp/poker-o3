#!/usr/bin/env python3
from deck import Deck
from history_manager import HistoryManager
from ranking_manager import RankingManager
from typing import List

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
