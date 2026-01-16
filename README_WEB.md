# 🃏 Texas Hold'em Poker - Web Edition

Interface web moderna para jogar Texas Hold'em contra uma IA com aprendizado por reforço.

## ✨ Características

- 🎨 **Interface Web Moderna** - Design responsivo com tema escuro premium
- 🤖 **IA Inteligente** - Oponente com Q-learning que aprende com cada jogada
- 💎 **Gestão de Fichas** - Sistema completo de apostas e conservação de fichas
- 🎯 **Tempo Real** - Atualizações automáticas do estado do jogo
- 📱 **Responsivo** - Funciona em desktop, tablet e mobile

## 🚀 Como Jogar

### Início Rápido

```bash
./start_web.sh
```

Depois abra seu navegador em: **http://localhost:5001**

### Instalação Manual

Se preferir instalar manualmente:

```bash
# 1. Criar ambiente virtual
python3 -m venv .venv

# 2. Ativar ambiente virtual
source .venv/bin/activate

# 3. Instalar dependências
pip install flask flask-cors numpy

# 4. Iniciar servidor
python poker_web.py
```

## 🎮 Como Jogar

1. **Inicie o Servidor** - Execute `./start_web.sh`
2. **Abra o Navegador** - Acesse http://localhost:5001
3. **Nova Mão** - Clique em "🎲 Nova Mão" para começar
4. **Faça sua Jogada** - Escolha entre:
   - ✓ **PAGAR** - Igualar a aposta atual
   - ↑ **AUMENTAR** - Aumentar a aposta
   - ✕ **DESISTIR** - Desistir da mão
5. **Veja o Resultado** - A IA responde automaticamente
6. **Continue Jogando** - Inicie novas mãos até alguém ficar sem fichas!

## 📁 Estrutura do Projeto

```
poker-o3/
├── poker_web.py              # Servidor Flask com API REST
├── poker_app.py              # Lógica do jogo (cartas, jogadores, IA)
├── start_web.sh              # Script de inicialização
├── static/
│   ├── index.html            # Interface principal
│   ├── css/
│   │   └── style.css         # Estilos modernos
│   └── js/
│       ├── cards.js          # Renderização de cartas
│       └── game.js           # Lógica do cliente
└── requirements.txt          # Dependências Python
```

## 🔧 Tecnologias

### Backend
- **Flask** - Framework web Python
- **NumPy** - Computação numérica para IA
- **Q-Learning** - Algoritmo de aprendizado por reforço

### Frontend
- **HTML5** - Estrutura semântica
- **CSS3** - Estilização moderna com animações
- **JavaScript ES6** - Lógica do cliente e comunicação com API

## 🎯 API Endpoints

- `GET /` - Página principal
- `GET /api/game/state` - Estado atual do jogo
- `POST /api/game/new` - Iniciar nova mão
- `POST /api/game/action` - Executar ação (call/raise/fold)
- `GET /api/game/stats` - Estatísticas do jogo

## 🐛 Solução de Problemas

### Porta em Uso
Se a porta 5001 estiver em uso:
```bash
# Matar processo na porta
lsof -ti:5001 | xargs kill -9

# Ou editar poker_web.py e mudar a porta
```

### Dependências Faltando
```bash
source .venv/bin/activate
pip install -r requirements.txt
```

### Servidor Não Inicia
```bash
# Recriar ambiente virtual
rm -rf .venv
python3 -m venv .venv
source .venv/bin/activate
pip install flask flask-cors numpy
```

## 🎨 Capturas de Tela

A interface apresenta:
- 🃏 Cartas renderizadas com símbolos de naipe coloridos
- 💰 Display de fichas em tempo real
- 🎯 Indicador de fase do jogo (Pré-Flop, Flop, Turn, River)
- 🏆 Anúncio de vencedor com overlay
- 📊 Estatísticas de fichas

## 🔮 Próximas Melhorias

- [ ] WebSocket para atualizações em tempo real
- [ ] Input customizado para valor de raise
- [ ] Efeitos sonoros
- [ ] Histórico de mãos
- [ ] Dashboard de estatísticas
- [ ] Suporte multi-jogador
- [ ] Modo torneio

## 📝 Notas

- **Modo Debug Desabilitado** - Para melhor performance no WSL
- **Porta Padrão**: 5001 (evita conflito com outras aplicações)
- **Auto-refresh**: Interface atualiza a cada 2 segundos
- **Conservação de Fichas**: Total sempre 2000 (1000 por jogador)

## 🤝 Contribuindo

Sinta-se à vontade para abrir issues e pull requests!

## 📄 Licença

Este projeto é de código aberto para fins educacionais.

---

**Desenvolvido com ❤️ usando Flask e JavaScript**
