#!/usr/bin/env python3
import os
import socket
import subprocess
import sys

def print_header():
    print("=" * 60)
    print("VERIFICADOR DE CONFIGURAÇÃO DO DISPLAY PARA WSL")
    print("=" * 60)
    print("Este script verifica a configuração do DISPLAY e sugere correções.")
    print("Útil para aplicações gráficas como o Poker GUI no WSL.\n")

def check_vcxsrv():
    print("VERIFICANDO VCXSRV:")
    print("-" * 60)
    
    # Tenta executar xset para verificar se o servidor X está acessível
    try:
        result = subprocess.run(['xset', 'q'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if result.returncode == 0:
            print("✅ Servidor X está acessível!")
            return True
        else:
            print("❌ Servidor X não está acessível.")
            return False
    except Exception as e:
        print(f"❌ Erro ao verificar servidor X: {e}")
        return False

def get_windows_ip():
    print("\nPOSSÍVEIS IPs DO HOST WINDOWS:")
    print("-" * 60)
    ips = []
    
    # Método 1: via ip route
    try:
        result = subprocess.run(['ip', 'route'], capture_output=True, text=True)
        if result.returncode == 0:
            for line in result.stdout.splitlines():
                if 'default via' in line:
                    ip = line.split('default via ')[1].split(' ')[0]
                    print(f"✓ IP via 'ip route': {ip}")
                    ips.append(ip)
    except Exception as e:
        print(f"✗ Não foi possível obter IP via 'ip route': {e}")
    
    # Método 2: via /etc/resolv.conf
    try:
        with open('/etc/resolv.conf', 'r') as f:
            for line in f:
                if 'nameserver' in line:
                    ip = line.strip().split(' ')[1]
                    print(f"✓ IP via '/etc/resolv.conf': {ip}")
                    ips.append(ip)
    except Exception as e:
        print(f"✗ Não foi possível obter IP via '/etc/resolv.conf': {e}")
    
    # Método 3: hostname
    try:
        hostname = socket.gethostname()
        ip = socket.gethostbyname(hostname)
        print(f"✓ IP via hostname: {ip}")
        ips.append(ip)
    except Exception as e:
        print(f"✗ Não foi possível obter IP via hostname: {e}")
    
    return ips

def check_display_var():
    print("\nVARIÁVEL DISPLAY ATUAL:")
    print("-" * 60)
    
    if 'DISPLAY' in os.environ:
        print(f"✓ DISPLAY está definido como: {os.environ['DISPLAY']}")
    else:
        print("✗ DISPLAY não está definido!")
    
    return 'DISPLAY' in os.environ

def suggest_solutions(ips):
    print("\nSOLUÇÕES SUGERIDAS:")
    print("-" * 60)
    
    print("1. Certifique-se de que o VcXsrv está instalado e rodando no Windows:")
    print("   - Baixe em: https://sourceforge.net/projects/vcxsrv/")
    print("   - Execute o XLaunch e marque 'Disable access control'")
    print("   - Permita conexões no Firewall do Windows")
    
    print("\n2. Configure a variável DISPLAY com um dos seguintes comandos:")
    for ip in ips:
        print(f"   export DISPLAY={ip}:0.0")
    
    print("\n   Outros valores comuns para testar:")
    print("   export DISPLAY=:0")
    print("   export DISPLAY=localhost:0.0")
    print("   export DISPLAY=127.0.0.1:0.0")
    
    print("\n3. Depois de configurar o DISPLAY, execute a aplicação:")
    print("   python poker_gui.py")

def main():
    print_header()
    
    vcxsrv_running = check_vcxsrv()
    display_set = check_display_var()
    ips = get_windows_ip()
    
    suggest_solutions(ips)
    
    print("\nRESUMO:")
    print("-" * 60)
    print(f"✓ Servidor X acessível: {'Sim' if vcxsrv_running else 'Não'}")
    print(f"✓ DISPLAY configurado: {'Sim' if display_set else 'Não'}")
    print(f"✓ Possíveis IPs do host Windows: {', '.join(ips) if ips else 'Nenhum encontrado'}")
    
    if vcxsrv_running and display_set:
        print("\n✅ Sua configuração parece correta, mas ainda há problemas.")
        print("   Tente diferentes valores para DISPLAY conforme sugerido acima.")
    else:
        print("\n❌ Sua configuração precisa de ajustes.")
        print("   Siga as soluções sugeridas acima.")

if __name__ == "__main__":
    main()