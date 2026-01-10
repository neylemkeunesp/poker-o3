import tkinter as tkpp
from PIL import Image, ImageDraw, ImageFont
import os
import tempfile
import shutil

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
        
        # Create temporary directory for card images
        self.temp_dir = tempfile.mkdtemp(prefix="poker_cards_")
        print(f"Criando diretório temporário para imagens: {self.temp_dir}")
        
        # Create card images
        self.generate_all_cards()
    
    def __del__(self):
        # Clean up temporary directory when object is destroyed
        try:
            shutil.rmtree(self.temp_dir)
            print(f"Removendo diretório temporário: {self.temp_dir}")
        except:
            pass
    
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
        
        # Try different system font locations
        font_paths = [
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",  # Linux
            "/System/Library/Fonts/Supplemental/Arial Bold.ttf",      # macOS
            "C:\\Windows\\Fonts\\arialbd.ttf"                        # Windows
        ]
        
        font = None
        for font_path in font_paths:
            try:
                if os.path.exists(font_path):
                    font = ImageFont.truetype(font_path, 20)
                    symbol_font = ImageFont.truetype(font_path, 30)
                    break
            except OSError:
                continue
        
        if font is None:
            # Fallback to default font if no system fonts are available
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
        
        # Save image to temporary file
        filename = os.path.join(self.temp_dir, f"{rank}_{suit}.png")
        image.save(filename)
        
        # Load image with tk.PhotoImage
        photo = tk.PhotoImage(file=filename)
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
        
        # Save image to temporary file
        filename = os.path.join(self.temp_dir, "card_back.png")
        image.save(filename)
        
        # Load image with tk.PhotoImage
        photo = tk.PhotoImage(file=filename)
        return photo