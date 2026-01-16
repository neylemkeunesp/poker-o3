#!/bin/bash
# Script para iniciar o servidor web do poker

echo "=============================================="
echo "🃏 TEXAS HOLD'EM POKER - WEB SERVER"
echo "=============================================="
echo ""

# Verificar se o ambiente virtual existe
if [ ! -d ".venv" ]; then
    echo "❌ Ambiente virtual não encontrado!"
    echo "Criando ambiente virtual..."
    python3 -m venv .venv
fi

# Ativar ambiente virtual
echo "📦 Ativando ambiente virtual..."
source .venv/bin/activate

# Instalar dependências
echo "📥 Verificando dependências..."
pip install -q flask flask-cors numpy 2>/dev/null

echo ""
echo "=============================================="
echo "🌐 Iniciando servidor em http://localhost:5001"
echo "=============================================="
echo ""
echo "✨ Abra seu navegador e acesse:"
echo "   http://localhost:5001"
echo ""
echo "⌨️  Pressione Ctrl+C para parar o servidor"
echo ""
echo "=============================================="
echo ""

# Iniciar servidor
python poker_web.py
