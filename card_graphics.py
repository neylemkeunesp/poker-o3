import tkinter as tk
from PIL import Image, ImageDraw, ImageTk, ImageFont
import os

class CardGraphics:
    def __init__(self):
        # Tamanho maior para melhor visibilidade
        self.card_width = 140  # Era 80, agora 140 (75% maior)
        self.card_height = 196  # Era 112, agora 196 (75% maior)
        self.corner_radius = 12
        self.margin = 12
        self.cards = {}
        self._card_back = None  # Lazy load card back

        # Colors - cores mais vibrantes
        self.red = '#DC143C'  # Crimson vermelho mais forte
        self.black = '#000000'
        self.white = '#FFFFFF'
        self.card_bg = '#F8F9FA'  # Branco levemente cinza para contraste

        # Suit symbols
        self.suit_symbols = {
            'Hearts': '♥',
            'Diamonds': '♦',
            'Clubs': '♣',
            'Spades': '♠'
        }

        # Tentar carregar fontes melhores
        self.rank_font_large = None
        self.rank_font_small = None
        self.suit_font_large = None
        self.suit_font_small = None

        self._load_fonts()

        # Don't pre-generate all cards - create on demand to save memory

    def _load_fonts(self):
        """Carregar fontes com fallback para fonte padrão"""
        try:
            # Tentar fontes do sistema
            self.rank_font_large = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 36)
            self.rank_font_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 28)
            self.suit_font_large = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 60)
            self.suit_font_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 32)
        except:
            try:
                # Fallback para Arial (Windows/WSL)
                self.rank_font_large = ImageFont.truetype("arial.ttf", 36)
                self.rank_font_small = ImageFont.truetype("arial.ttf", 28)
                self.suit_font_large = ImageFont.truetype("arial.ttf", 60)
                self.suit_font_small = ImageFont.truetype("arial.ttf", 32)
            except:
                # Usar fonte padrão se nenhuma estiver disponível
                self.rank_font_large = ImageFont.load_default()
                self.rank_font_small = ImageFont.load_default()
                self.suit_font_large = ImageFont.load_default()
                self.suit_font_small = ImageFont.load_default()

    def create_card_image(self, rank, suit):
        # Criar carta com alta resolução e contraste
        image = Image.new('RGB', (self.card_width, self.card_height), self.card_bg)
        draw = ImageDraw.Draw(image)

        # Borda mais grossa e com cantos arredondados
        # Criar máscara para cantos arredondados
        mask = Image.new('L', (self.card_width, self.card_height), 0)
        mask_draw = ImageDraw.Draw(mask)
        mask_draw.rounded_rectangle(
            [0, 0, self.card_width, self.card_height],
            radius=self.corner_radius,
            fill=255
        )

        # Aplicar máscara
        rounded_card = Image.new('RGB', (self.card_width, self.card_height), self.white)
        rounded_card.paste(image, (0, 0), mask)
        image = rounded_card
        draw = ImageDraw.Draw(image)

        # Borda preta grossa
        draw.rounded_rectangle(
            [0, 0, self.card_width-1, self.card_height-1],
            radius=self.corner_radius,
            outline=self.black,
            width=3
        )

        # Determinar cor baseado no naipe
        color = self.red if suit in ['Hearts', 'Diamonds'] else self.black

        # Desenhar rank e naipe no canto superior esquerdo
        draw.text(
            (self.margin, self.margin),
            rank,
            fill=color,
            font=self.rank_font_small
        )
        draw.text(
            (self.margin, self.margin + 35),
            self.suit_symbols[suit],
            fill=color,
            font=self.suit_font_small
        )

        # Desenhar símbolo grande no centro
        # Calcular posição centralizada
        center_x = self.card_width // 2
        center_y = self.card_height // 2

        # Usar textbbox para centralizar corretamente
        bbox = draw.textbbox((0, 0), self.suit_symbols[suit], font=self.suit_font_large)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]

        draw.text(
            (center_x - text_width // 2, center_y - text_height // 2),
            self.suit_symbols[suit],
            fill=color,
            font=self.suit_font_large
        )

        # Desenhar rank e naipe no canto inferior direito (invertido)
        # Calcular posições do canto inferior direito
        bbox_rank = draw.textbbox((0, 0), rank, font=self.rank_font_small)
        bbox_suit = draw.textbbox((0, 0), self.suit_symbols[suit], font=self.suit_font_small)

        rank_width = bbox_rank[2] - bbox_rank[0]
        suit_width = bbox_suit[2] - bbox_suit[0]

        # Criar imagem temporária para o canto invertido
        corner_img = Image.new('RGBA', (50, 80), (0, 0, 0, 0))
        corner_draw = ImageDraw.Draw(corner_img)
        corner_draw.text((5, 5), rank, fill=color, font=self.rank_font_small)
        corner_draw.text((5, 40), self.suit_symbols[suit], fill=color, font=self.suit_font_small)

        # Rotacionar 180 graus
        corner_img = corner_img.rotate(180)

        # Colar no canto inferior direito
        image.paste(corner_img, (self.card_width - 50, self.card_height - 80), corner_img)

        # Convert to PhotoImage for tkinter
        photo = ImageTk.PhotoImage(image)
        return photo
    
    def get_card_image(self, rank, suit):
        """Lazy load cards - only create when needed"""
        key = f"{rank}_{suit}"
        if key not in self.cards:
            self.cards[key] = self.create_card_image(rank, suit)
        return self.cards[key]
    
    def get_card_back(self):
        """Lazy load card back - only create once when needed"""
        if self._card_back is None:
            # Criar verso da carta com padrão elegante
            base_color = '#1E3A8A'  # Azul escuro
            pattern_color = '#3B82F6'  # Azul médio
            border_color = '#FBBF24'  # Dourado

            image = Image.new('RGB', (self.card_width, self.card_height), base_color)
            draw = ImageDraw.Draw(image)

            # Criar máscara para cantos arredondados
            mask = Image.new('L', (self.card_width, self.card_height), 0)
            mask_draw = ImageDraw.Draw(mask)
            mask_draw.rounded_rectangle(
                [0, 0, self.card_width, self.card_height],
                radius=self.corner_radius,
                fill=255
            )

            # Aplicar máscara
            rounded_back = Image.new('RGB', (self.card_width, self.card_height), base_color)
            rounded_back.paste(image, (0, 0), mask)
            image = rounded_back
            draw = ImageDraw.Draw(image)

            # Borda dourada grossa
            draw.rounded_rectangle(
                [0, 0, self.card_width-1, self.card_height-1],
                radius=self.corner_radius,
                outline=border_color,
                width=4
            )

            # Padrão de linhas diagonais mais denso
            for i in range(0, self.card_width + self.card_height, 12):
                draw.line([(i, 0), (0, i)], fill=pattern_color, width=2)
                draw.line([(self.card_width, i), (i, self.card_height)], fill=pattern_color, width=2)

            # Adicionar um retângulo interno decorativo
            margin_inner = 15
            draw.rounded_rectangle(
                [margin_inner, margin_inner,
                 self.card_width - margin_inner, self.card_height - margin_inner],
                radius=8,
                outline=border_color,
                width=2
            )

            # Desenhar símbolo de cartas no centro (opcional)
            center_x = self.card_width // 2
            center_y = self.card_height // 2

            # Desenhar símbolo de naipe no centro
            try:
                draw.text(
                    (center_x - 15, center_y - 20),
                    "🃏",
                    fill='#FBBF24',
                    font=self.suit_font_large
                )
            except:
                # Se a fonte não suportar emoji, desenhar um padrão simples
                draw.ellipse(
                    [center_x - 20, center_y - 20, center_x + 20, center_y + 20],
                    fill=pattern_color,
                    outline=border_color,
                    width=2
                )

            self._card_back = ImageTk.PhotoImage(image)

        return self._card_back
