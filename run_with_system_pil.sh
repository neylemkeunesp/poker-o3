#!/bin/bash
# Script para executar o poker_gui.py com acesso aos módulos PIL do sistema

# Verifica se o VcXsrv está acessível
echo "Verificando conexão com o servidor X..."
xset q &>/dev/null
if [ $? -ne 0 ]; then
    echo "⚠️ Aviso: Não foi possível conectar ao servidor X (VcXsrv)"
    echo "Certifique-se de que:"
    echo "1. VcXsrv está instalado e rodando no Windows"
    echo "2. XLaunch foi configurado com 'Disable access control'"
    echo "3. Firewall do Windows permite conexões do WSL"
    echo ""
    
    # Tenta obter o IP do host Windows
    echo "Possíveis IPs do host Windows:"
    
    # Via ip route
    DEFAULT_ROUTE=$(ip route | grep default | awk '{print $3}')
    if [ ! -z "$DEFAULT_ROUTE" ]; then
        echo "- $DEFAULT_ROUTE (via ip route)"
        SUGGESTED_IP=$DEFAULT_ROUTE
    fi
    
    # Via /etc/resolv.conf
    NAMESERVER=$(grep nameserver /etc/resolv.conf | awk '{print $2}')
    if [ ! -z "$NAMESERVER" ]; then
        echo "- $NAMESERVER (via /etc/resolv.conf)"
        SUGGESTED_IP=$NAMESERVER
    fi
    
    # Sugestão para configurar o DISPLAY
    if [ ! -z "$SUGGESTED_IP" ]; then
        echo ""
        echo "Tente configurar o DISPLAY com:"
        echo "export DISPLAY=$SUGGESTED_IP:0.0"
    fi
    
    echo ""
    echo "Pressione Enter para continuar mesmo assim, ou Ctrl+C para cancelar..."
    read
fi

# Ativa o ambiente virtual
source .venv/bin/activate

# Adiciona o diretório de pacotes do sistema ao PYTHONPATH
# Isso permite que o Python do ambiente virtual encontre os módulos PIL do sistema
export PYTHONPATH="/usr/lib/python3/dist-packages:$PYTHONPATH"

# Exibe informações sobre o ambiente
echo "=== Informações do Ambiente ==="
echo "DISPLAY: $DISPLAY"
echo "Python: $(which python)"
echo "PYTHONPATH: $PYTHONPATH"
echo "==============================="
echo ""

# Executa o poker_gui.py
echo "Executando poker_gui.py com acesso aos módulos PIL do sistema..."
python poker_gui.py