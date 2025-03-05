#!/usr/bin/env python3
"""
Teste da integração entre PIL/Pillow e Tkinter
Este script verifica se o PIL/Pillow está corretamente integrado com o Tkinter,
testando especificamente a funcionalidade ImageTk que causa o erro "PyImagingPhoto".
"""

import os
import sys
import tkinter as tk
from tkinter import ttk
import traceback

def print_info():
    """Imprime informações sobre o ambiente"""
    print("=== Informações do Ambiente ===")
    print(f"Python: {sys.version}")
    print(f"Tkinter: {tk.TkVersion}")
    print(f"DISPLAY: {os.environ.get('DISPLAY', 'Não definido')}")
    
    # Verifica se PIL está instalado
    try:
        import PIL
        print(f"PIL/Pillow: {PIL.__version__}")
    except ImportError:
        print("PIL/Pillow: Não instalado")
    
    print("=" * 30)

def test_basic_tkinter():
    """Testa a funcionalidade básica do Tkinter"""
    print("\n1. Testando funcionalidade básica do Tkinter...")
    try:
        root = tk.Tk()
        root.withdraw()  # Esconde a janela
        root.update()
        root.destroy()
        print("✅ Tkinter básico está funcionando!")
        return True
    except Exception as e:
        print(f"❌ Erro no Tkinter básico: {e}")
        return False

def test_pil_import():
    """Testa a importação do PIL/Pillow"""
    print("\n2. Testando importação do PIL/Pillow...")
    try:
        from PIL import Image
        print("✅ PIL.Image importado com sucesso!")
        
        from PIL import ImageTk
        print("✅ PIL.ImageTk importado com sucesso!")
        return True
    except ImportError as e:
        print(f"❌ Erro ao importar PIL: {e}")
        print("\nSolução: Instale o PIL/Pillow com:")
        print("sudo apt-get install python3-pil python3-pil.imagetk")
        return False
    except Exception as e:
        print(f"❌ Erro desconhecido: {e}")
        return False

def test_pil_tkinter_integration():
    """Testa a integração entre PIL e Tkinter"""
    print("\n3. Testando integração PIL/Pillow com Tkinter...")
    try:
        from PIL import Image, ImageTk
        
        # Cria a janela principal primeiro
        print("   Criando janela Tkinter...")
        root = tk.Tk()
        root.withdraw()  # Esconde a janela
        
        # Cria uma imagem simples
        image = Image.new('RGB', (100, 100), color='red')
        
        # Tenta converter para PhotoImage
        print("   Tentando criar um ImageTk.PhotoImage...")
        photo = ImageTk.PhotoImage(image)
        
        # Tenta usar a imagem em um widget Tkinter
        print("   Tentando usar a imagem em um widget Tkinter...")
        label = tk.Label(root, image=photo)
        label.image = photo  # Mantém uma referência
        
        root.update()
        root.destroy()
        
        print("✅ Integração PIL/Pillow com Tkinter funcionando corretamente!")
        return True
    except tk.TclError as e:
        if "invalid command name \"PyImagingPhoto\"" in str(e):
            print("❌ Erro específico detectado: invalid command name \"PyImagingPhoto\"")
            print("\nEste é exatamente o erro que ocorre na aplicação de poker.")
            print("Solução: Instale o pacote python3-pil.imagetk:")
            print("sudo apt-get install python3-pil.imagetk")
        else:
            print(f"❌ Erro Tcl/Tk: {e}")
        return False
    except Exception as e:
        print(f"❌ Erro ao testar integração: {e}")
        traceback.print_exc()
        return False

def main():
    """Função principal que executa todos os testes"""
    print_info()
    
    # Executa os testes em sequência
    tkinter_ok = test_basic_tkinter()
    pil_ok = test_pil_import()
    
    if tkinter_ok and pil_ok:
        integration_ok = test_pil_tkinter_integration()
    else:
        print("\n⚠️ Pulando teste de integração devido a falhas anteriores.")
        integration_ok = False
    
    # Resumo dos resultados
    print("\n=== RESUMO DOS TESTES ===")
    print(f"Tkinter básico: {'✅ OK' if tkinter_ok else '❌ Falha'}")
    print(f"Importação PIL: {'✅ OK' if pil_ok else '❌ Falha'}")
    print(f"Integração PIL-Tkinter: {'✅ OK' if integration_ok else '❌ Falha'}")
    
    if not (tkinter_ok and pil_ok and integration_ok):
        print("\nSoluções recomendadas:")
        print("1. Instale os pacotes necessários:")
        print("   sudo apt-get install python3-pil python3-pil.imagetk")
        print("2. Configure o servidor X corretamente:")
        print("   export DISPLAY=<IP-do-Windows>:0.0")
        print("3. Execute o script check_display.py para diagnóstico")
    else:
        print("\n✅ Todos os testes passaram! A integração PIL/Pillow com Tkinter está funcionando corretamente.")

if __name__ == "__main__":
    main()