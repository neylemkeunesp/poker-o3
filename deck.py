#!/usr/bin/env python3
import random
from card import Card
from typing import Optional

class Deck:
    def __init__(self):
        self.cards = [Card(rank, suit) for suit in Card.suits for rank in Card.ranks]
        self.shuffle()

    def shuffle(self):
        random.shuffle(self.cards)

    def draw(self) -> Optional[Card]:
        return self.cards.pop() if self.cards else None
