#!/usr/bin/env python3
"""
Teste simples do Tkinter
Este script cria uma janela básica do Tkinter para verificar se a biblioteca está funcionando corretamente.
"""

import os
import tkinter as tk
from tkinter import ttk
import sys

def print_info():
    """Imprime informações sobre o ambiente"""
    print("=== Informações do Ambiente ===")
    print(f"Python: {sys.version}")
    print(f"Tkinter: {tk.TkVersion}")
    print(f"DISPLAY: {os.environ.get('DISPLAY', 'Não definido')}")
    print("=" * 30)

def main():
    """Função principal que cria uma janela Tkinter simples"""
    print_info()
    
    print("Tentando criar uma janela Tkinter...")
    try:
        # Cria a janela principal
        root = tk.Tk()
        root.title("Teste do Tkinter")
        root.geometry("400x300")
        
        # Adiciona um frame
        frame = ttk.Frame(root, padding="10")
        frame.pack(fill=tk.BOTH, expand=True)
        
        # Adiciona um label
        label = ttk.Label(
            frame, 
            text="Tkinter está funcionando!",
            font=("Arial", 16)
        )
        label.pack(pady=20)
        
        # Adiciona um botão
        button = ttk.Button(
            frame,
            text="Fechar",
            command=root.destroy
        )
        button.pack(pady=10)
        
        print("✅ Janela Tkinter criada com sucesso!")
        print("Se você consegue ver a janela, o Tkinter está funcionando corretamente.")
        print("Feche a janela para encerrar o teste.")
        
        # Inicia o loop principal
        root.mainloop()
        
        print("Teste concluído com sucesso!")
        return True
    except Exception as e:
        print(f"❌ Erro ao criar janela Tkinter: {e}")
        print("\nPossíveis soluções:")
        print("1. Verifique se o servidor X está rodando (VcXsrv no Windows)")
        print("2. Configure a variável DISPLAY corretamente:")
        print("   export DISPLAY=<IP-do-Windows>:0.0")
        print("3. Execute o script check_display.py para diagnóstico")
        return False

if __name__ == "__main__":
    main()