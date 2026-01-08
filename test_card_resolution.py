#!/usr/bin/env python3
"""
Teste visual da resolução das cartas
Mostra algumas cartas de exemplo para verificar a qualidade
"""

import tkinter as tk
from card_graphics import CardGraphics

def test_cards():
    root = tk.Tk()
    root.title("Teste de Resolução das Cartas - Melhorada para Miopia")
    root.geometry("900x600")
    root.configure(bg='#0d1b2a')

    # Título
    title = tk.Label(
        root,
        text="🃏 Cartas em Alta Resolução - Otimizadas para Visibilidade 🃏",
        font=('Arial', 18, 'bold'),
        fg='#FFD700',
        bg='#0d1b2a',
        pady=20
    )
    title.pack()

    # Info
    info = tk.Label(
        root,
        text="Tamanho: 140x196 pixels | Fontes: 28-60px | Cores vibrantes",
        font=('Arial', 12),
        fg='#90EE90',
        bg='#0d1b2a'
    )
    info.pack()

    # Frame para as cartas
    cards_frame = tk.Frame(root, bg='#1b263b', pady=20)
    cards_frame.pack(pady=20, padx=20)

    # Criar instância do CardGraphics
    card_graphics = CardGraphics()

    # Exemplos de cartas
    cards = [
        ('A', 'Spades'),
        ('K', 'Hearts'),
        ('Q', 'Diamonds'),
        ('J', 'Clubs'),
        ('10', 'Hearts')
    ]

    # Título das cartas
    cards_title = tk.Label(
        cards_frame,
        text="Exemplos de Cartas:",
        font=('Arial', 14, 'bold'),
        fg='#FFFFFF',
        bg='#1b263b'
    )
    cards_title.pack(pady=(0, 10))

    # Frame para cartas de frente
    front_frame = tk.Frame(cards_frame, bg='#1b263b')
    front_frame.pack(pady=10)

    # Mostrar cartas
    for rank, suit in cards:
        img = card_graphics.get_card_image(rank, suit)
        label = tk.Label(front_frame, image=img, bg='#1b263b')
        label.image = img  # Keep reference
        label.pack(side='left', padx=8)

    # Frame para verso
    back_frame = tk.Frame(cards_frame, bg='#1b263b')
    back_frame.pack(pady=20)

    back_title = tk.Label(
        back_frame,
        text="Verso da Carta:",
        font=('Arial', 14, 'bold'),
        fg='#FFFFFF',
        bg='#1b263b'
    )
    back_title.pack()

    # Mostrar verso
    back_img = card_graphics.get_card_back()
    back_label = tk.Label(back_frame, image=back_img, bg='#1b263b')
    back_label.image = back_img
    back_label.pack(pady=10)

    # Informações técnicas
    specs = tk.Label(
        root,
        text="✓ Cantos arredondados | ✓ Bordas grossas | ✓ Símbolo central grande\n"
             "✓ Cores vibrantes | ✓ Alto contraste | ✓ Texto legível",
        font=('Arial', 11),
        fg='#87CEEB',
        bg='#0d1b2a',
        justify='center'
    )
    specs.pack(pady=10)

    # Botão de fechar
    close_btn = tk.Button(
        root,
        text="✓ Fechar",
        command=root.destroy,
        font=('Arial', 12, 'bold'),
        bg='#28a745',
        fg='white',
        padx=30,
        pady=10,
        relief=tk.FLAT
    )
    close_btn.pack(pady=20)

    root.mainloop()

if __name__ == "__main__":
    print("Iniciando teste de resolução das cartas...")
    print("Aguarde a janela abrir...")
    test_cards()
