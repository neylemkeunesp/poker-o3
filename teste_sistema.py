#!/usr/bin/env python3
"""
Teste usando o Python do sistema (não do ambiente virtual)
Este script deve ser executado com o Python do sistema, não com o Python do ambiente virtual.
"""

import os
import sys
import tkinter as tk
from PIL import Image, ImageTk

def main():
    print("=== Teste de PIL/Pillow com Tkinter usando Python do sistema ===")
    print(f"Python: {sys.version}")
    print(f"Tkinter: {tk.TkVersion}")
    
    try:
        import PIL
        print(f"PIL/Pillow: {PIL.__version__}")
        print(f"PIL.__file__: {PIL.__file__}")
    except ImportError:
        print("PIL/Pillow não está instalado")
        return
    
    print("\nTentando criar uma janela Tkinter com uma imagem...")
    try:
        # Cria a janela principal
        root = tk.Tk()
        root.title("Teste PIL/Pillow com Tkinter")
        root.geometry("300x200")
        
        # Cria uma imagem simples
        image = Image.new('RGB', (100, 100), color='red')
        
        # Converte para PhotoImage
        photo = ImageTk.PhotoImage(image)
        
        # Usa a imagem em um label
        label = tk.Label(root, image=photo)
        label.image = photo  # Mantém uma referência
        label.pack(pady=20)
        
        # Adiciona um texto
        text = tk.Label(root, text="Se você vê um quadrado vermelho,\no PIL/Pillow está funcionando com o Tkinter!")
        text.pack(pady=10)
        
        print("✅ Sucesso! A janela deve estar visível agora.")
        print("Feche a janela para encerrar o teste.")
        
        # Inicia o loop principal
        root.mainloop()
        return True
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    main()