// Main game logic and API integration

class PokerGame {
    constructor() {
        this.baseUrl = '';
        this.updateInterval = null;
        this.currentState = null;
    }

    /**
     * Initialize the game
     */
    async init() {
        console.log('Initializing poker game...');
        await this.updateGameState();
        this.startAutoUpdate();
    }

    /**
     * Fetch current game state from API
     */
    async getGameState() {
        try {
            const response = await fetch(`${this.baseUrl}/api/game/state`);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return await response.json();
        } catch (error) {
            console.error('Error fetching game state:', error);
            this.showMessage('Erro ao conectar com o servidor', 'error');
            return null;
        }
    }

    /**
     * Start a new hand
     */
    async newHand() {
        try {
            const response = await fetch(`${this.baseUrl}/api/game/new`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' }
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            this.showMessage('Nova mão iniciada!', 'success');
            await this.updateGameState();
            this.enableButtons();
        } catch (error) {
            console.error('Error starting new hand:', error);
            this.showMessage('Erro ao iniciar nova mão', 'error');
        }
    }

    /**
     * Perform a game action
     */
    async performAction(action, amount = 0) {
        try {
            this.disableButtons();

            const response = await fetch(`${this.baseUrl}/api/game/action`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ action, amount })
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();

            if (data.error) {
                this.showMessage(data.error, 'error');
                this.enableButtons();
                return;
            }

            // Show machine action
            if (data.machine_action) {
                const actionText = {
                    'call': 'pagou',
                    'raise': 'aumentou',
                    'fold': 'desistiu'
                }[data.machine_action] || data.machine_action;

                this.showMessage(`Máquina ${actionText}`, 'info');
            }

            await this.updateGameState();

            // Check if game is over
            if (this.currentState && this.currentState.game_over) {
                this.showWinner(this.currentState.winner);
                this.disableButtons();
            } else {
                this.enableButtons();
            }

        } catch (error) {
            console.error('Error performing action:', error);
            this.showMessage('Erro ao executar ação', 'error');
            this.enableButtons();
        }
    }

    /**
     * Update the UI with current game state
     */
    async updateGameState() {
        const state = await this.getGameState();
        if (!state) return;

        this.currentState = state;

        // Update phase
        const phaseText = {
            'waiting': 'AGUARDANDO',
            'preflop': 'PRÉ-FLOP',
            'flop': 'FLOP',
            'turn': 'TURN',
            'river': 'RIVER',
            'showdown': 'SHOWDOWN'
        }[state.phase] || state.phase.toUpperCase();

        document.getElementById('gamePhase').textContent = phaseText;

        // Update chips
        document.getElementById('playerChips').textContent = state.player.chips;
        document.getElementById('machineChips').textContent = state.machine.chips;
        document.getElementById('pot').textContent = state.pot;
        document.getElementById('currentBet').textContent = state.current_bet;
        document.getElementById('totalChips').textContent =
            state.player.chips + state.machine.chips + state.pot;

        // Update cards
        if (state.player && state.player.hand) {
            renderCards('playerHand', state.player.hand, false);

            // Update hand strength
            const strength = getHandStrength(state.player.hand, state.community_cards);
            document.getElementById('handStrength').textContent = strength;
        }

        // Machine cards (show backs unless game is over)
        if (state.game_over && state.machine && state.machine.hand) {
            // Show machine cards at showdown
            renderCards('machineHand', state.machine.hand, false);
        } else if (state.machine && state.machine.hand_count > 0) {
            // Show card backs
            const backs = Array(state.machine.hand_count).fill({});
            renderCards('machineHand', backs, true);
        } else {
            renderCards('machineHand', [], false);
        }

        // Community cards
        renderCards('communityCards', state.community_cards || [], false);

        // Update button states
        if (state.game_over || !state.initialized) {
            this.disableButtons();
        } else {
            this.enableButtons();
        }
    }

    /**
     * Show winner announcement
     */
    showWinner(winner) {
        const overlay = document.getElementById('winnerOverlay');
        const text = document.getElementById('winnerText');

        if (winner === 'Empate') {
            text.textContent = '🤝 EMPATE!';
        } else {
            text.textContent = `🏆 ${winner.toUpperCase()} VENCEU!`;
        }

        overlay.style.display = 'flex';
    }

    /**
     * Hide winner announcement
     */
    hideWinner() {
        document.getElementById('winnerOverlay').style.display = 'none';
    }

    /**
     * Show temporary message
     */
    showMessage(message, type = 'info') {
        const messageBox = document.getElementById('messageBox');
        messageBox.textContent = message;
        messageBox.style.display = 'block';

        // Auto-hide after 3 seconds
        setTimeout(() => {
            messageBox.style.display = 'none';
        }, 3000);
    }

    /**
     * Enable action buttons
     */
    enableButtons() {
        document.getElementById('callBtn').disabled = false;
        document.getElementById('raiseBtn').disabled = false;
        document.getElementById('foldBtn').disabled = false;
    }

    /**
     * Disable action buttons
     */
    disableButtons() {
        document.getElementById('callBtn').disabled = true;
        document.getElementById('raiseBtn').disabled = true;
        document.getElementById('foldBtn').disabled = true;
    }

    /**
     * Start auto-updating game state
     */
    startAutoUpdate() {
        // Update every 2 seconds
        this.updateInterval = setInterval(() => {
            this.updateGameState();
        }, 2000);
    }

    /**
     * Stop auto-updating
     */
    stopAutoUpdate() {
        if (this.updateInterval) {
            clearInterval(this.updateInterval);
            this.updateInterval = null;
        }
    }
}

// Global game instance
const game = new PokerGame();

// Global functions for HTML onclick handlers
function newHand() {
    game.newHand();
}

function newGame() {
    window.location.reload();
}

function performAction(action) {
    if (action === 'raise') {
        // For now, use a fixed raise amount
        // TODO: Add UI for custom raise amount
        const raiseAmount = 50;
        game.performAction(action, raiseAmount);
    } else {
        game.performAction(action);
    }
}

function hideWinner() {
    game.hideWinner();
}

// Initialize game when page loads
document.addEventListener('DOMContentLoaded', () => {
    console.log('Page loaded, initializing game...');
    game.init();
});

// Cleanup on page unload
window.addEventListener('beforeunload', () => {
    game.stopAutoUpdate();
});
