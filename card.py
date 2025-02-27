#!/usr/bin/env python3

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
