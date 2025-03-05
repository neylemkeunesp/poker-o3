#!/usr/bin/env python3
import os
import tkinter as tk
import subprocess
import time
import sys

def test_display(display_value):
    """Testa se uma configuração de DISPLAY funciona"""
    print(f"\nTestando DISPLAY={display_value}")
    os.environ['DISPLAY'] = display_value
    
    try:
        # Tenta criar uma janela Tkinter
        root = tk.Tk()
        root.geometry("300x200")
        root.title(f"Teste DISPLAY={display_value}")
        
        # Adiciona um label com a configuração
        label = tk.Label(root, text=f"DISPLAY={display_value} FUNCIONA!", font=("Arial", 14))
        label.pack(pady=20)
        
        # Adiciona instruções
        instructions = tk.Label(root, text="Feche esta janela para testar a próxima configuração", font=("Arial", 10))
        instructions.pack(pady=10)
        
        # Adiciona um botão para fechar
        button = tk.Button(root, text="Fechar", command=root.destroy)
        button.pack(pady=10)
        
        print(f"✅ SUCESSO! DISPLAY={display_value} funciona!")
        print("Uma janela de teste deve ter aparecido. Feche-a para continuar.")
        
        root.mainloop()
        return True
    except Exception as e:
        print(f"❌ FALHA: {e}")
        return False

def get_possible_displays():
    """Retorna uma lista de possíveis configurações de DISPLAY"""
    displays = []
    
    # Configurações básicas
    displays.append(':0')
    displays.append(':0.0')
    
    # Localhost
    displays.append('localhost:0.0')
    displays.append('127.0.0.1:0.0')
    
    # Tenta obter o IP do host Windows via ip route
    try:
        result = subprocess.run(['ip', 'route'], capture_output=True, text=True)
        if result.returncode == 0:
            for line in result.stdout.splitlines():
                if 'default via' in line:
                    ip = line.split('default via ')[1].split(' ')[0]
                    displays.append(f'{ip}:0.0')
    except:
        pass
    
    # Tenta obter o IP do host Windows via /etc/resolv.conf
    try:
        with open('/etc/resolv.conf', 'r') as f:
            for line in f:
                if 'nameserver' in line:
                    ip = line.strip().split(' ')[1]
                    displays.append(f'{ip}:0.0')
    except:
        pass
    
    # IPs comuns para WSL
    for i in range(21, 32):
        displays.append(f'172.{i}.0.1:0.0')
    
    # Outros IPs comuns
    displays.append('192.168.1.1:0.0')
    displays.append('192.168.0.1:0.0')
    
    return displays

def main():
    print("=== Teste de Configuração do DISPLAY para WSL ===")
    print("Este script testa várias configurações de DISPLAY para encontrar uma que funcione.")
    print("Para cada configuração, tentaremos abrir uma janela Tkinter.")
    print("Se a janela aparecer, significa que a configuração funciona!")
    print("\nCertifique-se de que:")
    print("1. VcXsrv está instalado e rodando no Windows")
    print("2. XLaunch foi configurado com 'Disable access control'")
    print("3. Firewall do Windows permite conexões do WSL")
    
    input("\nPressione Enter para começar os testes...")
    
    displays = get_possible_displays()
    working_displays = []
    
    for display in displays:
        if test_display(display):
            working_displays.append(display)
    
    print("\n=== Resultados ===")
    if working_displays:
        print(f"Encontramos {len(working_displays)} configurações de DISPLAY que funcionam:")
        for display in working_displays:
            print(f"  export DISPLAY={display}")
        
        print("\nPara usar uma dessas configurações, execute:")
        print(f"  export DISPLAY={working_displays[0]}")
        print("  python poker_gui.py")
    else:
        print("Não encontramos nenhuma configuração de DISPLAY que funcione.")
        print("Verifique se o VcXsrv está rodando corretamente e tente novamente.")
    
    print("\nSe você quiser testar uma configuração específica, execute:")
    print("  python test_display.py IP:0.0")
    print("  Exemplo: python test_display.py 192.168.1.100:0.0")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        # Se um argumento foi fornecido, testa apenas essa configuração
        test_display(sys.argv[1])
    else:
        # Caso contrário, testa todas as configurações
        main()