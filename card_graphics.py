import tkinter as tk
from PIL import Image, ImageDraw, ImageTk, ImageFont
import os

class CardGraphics:
    def __init__(self):
        self.card_width = 100
        self.card_height = 140
        self.corner_radius = 10
        self.margin = 10
        self.cards = {}
        
        # Colors
        self.red = '#FF0000'
        self.black = '#000000'
        self.white = '#FFFFFF'
        
        # Suit symbols
        self.suit_symbols = {
            'Hearts': '♥',
            'Diamonds': '♦',
            'Clubs': '♣',
            'Spades': '♠'
        }
        
        # Create card images
        self.generate_all_cards()
    
    def round_rectangle(self, draw, xy, radius, fill):
        x1, y1, x2, y2 = xy
        draw.rectangle([x1 + radius, y1, x2 - radius, y2], fill=fill)
        draw.rectangle([x1, y1 + radius, x2, y2 - radius], fill=fill)
        draw.ellipse([x1, y1, x1 + 2*radius, y1 + 2*radius], fill=fill)
        draw.ellipse([x2 - 2*radius, y1, x2, y1 + 2*radius], fill=fill)
        draw.ellipse([x1, y2 - 2*radius, x1 + 2*radius, y2], fill=fill)
        draw.ellipse([x2 - 2*radius, y2 - 2*radius, x2, y2], fill=fill)
    
    def create_card_image(self, rank, suit):
        # Create base image with white background
        image = Image.new('RGB', (self.card_width, self.card_height), self.white)
        draw = ImageDraw.Draw(image)
        
        # Draw rounded rectangle for card border
        self.round_rectangle(draw, 
                           [2, 2, self.card_width-2, self.card_height-2],
                           self.corner_radius, 
                           self.white)
        
        # Determine color based on suit
        color = self.red if suit in ['Hearts', 'Diamonds'] else self.black
        
        try:
            # Try to load a system font
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 20)
            symbol_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 30)
        except OSError:
            # Fallback to default font
            font = ImageFont.load_default()
            symbol_font = ImageFont.load_default()
        
        # Draw rank and suit in top left
        draw.text((self.margin, self.margin), rank, fill=color, font=font)
        draw.text((self.margin, self.margin + 25), 
                 self.suit_symbols[suit], 
                 fill=color, 
                 font=symbol_font)
        
        # Draw large central suit symbol
        draw.text((self.card_width//2 - 15, self.card_height//2 - 15),
                 self.suit_symbols[suit],
                 fill=color,
                 font=symbol_font)
        
        # Draw rank and suit in bottom right (inverted)
        draw.text((self.card_width - 30, self.card_height - 45),
                 rank,
                 fill=color,
                 font=font)
        draw.text((self.card_width - 30, self.card_height - 30),
                 self.suit_symbols[suit],
                 fill=color,
                 font=symbol_font)
        
        # Convert to PhotoImage for tkinter
        photo = ImageTk.PhotoImage(image)
        return photo
    
    def generate_all_cards(self):
        ranks = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
        suits = ['Hearts', 'Diamonds', 'Clubs', 'Spades']
        
        for suit in suits:
            for rank in ranks:
                key = f"{rank}_{suit}"
                self.cards[key] = self.create_card_image(rank, suit)
    
    def get_card_image(self, rank, suit):
        key = f"{rank}_{suit}"
        return self.cards.get(key)
    
    def get_card_back(self):
        # Create back of card with pattern
        image = Image.new('RGB', (self.card_width, self.card_height), self.white)
        draw = ImageDraw.Draw(image)
        
        # Draw rounded rectangle border
        self.round_rectangle(draw, 
                           [2, 2, self.card_width-2, self.card_height-2],
                           self.corner_radius, 
                           '#000080')  # Navy blue back
        
        # Create pattern (simple cross-hatch)
        for i in range(0, self.card_width, 10):
            draw.line([(i, 0), (i, self.card_height)], fill='#0000A0', width=1)
        for i in range(0, self.card_height, 10):
            draw.line([(0, i), (self.card_width, i)], fill='#0000A0', width=1)
        
        return ImageTk.PhotoImage(image)
