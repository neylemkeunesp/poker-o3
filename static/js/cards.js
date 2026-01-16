// Card rendering utilities

const SUITS = {
    'Hearts': '♥',
    'Diamonds': '♦',
    'Clubs': '♣',
    'Spades': '♠'
};

const SUIT_COLORS = {
    'Hearts': 'red',
    'Diamonds': 'red',
    'Clubs': 'black',
    'Spades': 'black'
};

const RANK_DISPLAY = {
    '2': '2', '3': '3', '4': '4', '5': '5', '6': '6',
    '7': '7', '8': '8', '9': '9', '10': '10',
    'J': 'J', 'Q': 'Q', 'K': 'K', 'A': 'A'
};

/**
 * Create a card element
 * @param {Object} card - Card object with rank and suit
 * @returns {HTMLElement} Card element
 */
function createCard(card) {
    const cardEl = document.createElement('div');
    cardEl.className = 'card';

    if (!card || !card.rank || !card.suit) {
        cardEl.classList.add('card-placeholder');
        return cardEl;
    }

    const suit = SUITS[card.suit] || card.suit;
    const rank = RANK_DISPLAY[card.rank] || card.rank;
    const color = SUIT_COLORS[card.suit] || 'black';

    cardEl.classList.add(`card-${color}`);

    // Card content
    cardEl.innerHTML = `
        <div style="position: absolute; top: 8px; left: 8px; font-size: 1.2rem;">
            ${rank}<br>${suit}
        </div>
        <div style="font-size: 3rem;">
            ${suit}
        </div>
        <div style="position: absolute; bottom: 8px; right: 8px; font-size: 1.2rem; transform: rotate(180deg);">
            ${rank}<br>${suit}
        </div>
    `;

    return cardEl;
}

/**
 * Create a card back element
 * @returns {HTMLElement} Card back element
 */
function createCardBack() {
    const cardEl = document.createElement('div');
    cardEl.className = 'card card-back';
    return cardEl;
}

/**
 * Render cards in a container
 * @param {string} containerId - ID of the container element
 * @param {Array} cards - Array of card objects
 * @param {boolean} showBack - Whether to show card backs
 */
function renderCards(containerId, cards, showBack = false) {
    const container = document.getElementById(containerId);
    if (!container) return;

    container.innerHTML = '';

    if (!cards || cards.length === 0) {
        // Show placeholders
        const numPlaceholders = containerId === 'communityCards' ? 5 : 2;
        for (let i = 0; i < numPlaceholders; i++) {
            container.appendChild(createCard(null));
        }
        return;
    }

    cards.forEach(card => {
        if (showBack) {
            container.appendChild(createCardBack());
        } else {
            container.appendChild(createCard(card));
        }
    });

    // Fill remaining slots with placeholders for community cards
    if (containerId === 'communityCards') {
        const remaining = 5 - cards.length;
        for (let i = 0; i < remaining; i++) {
            container.appendChild(createCard(null));
        }
    }
}

/**
 * Get hand strength description
 * @param {Array} playerHand - Player's hand
 * @param {Array} communityCards - Community cards
 * @returns {string} Hand strength description
 */
function getHandStrength(playerHand, communityCards) {
    // This is a simplified version - the actual evaluation is done server-side
    if (!playerHand || playerHand.length === 0) {
        return '-';
    }

    if (!communityCards || communityCards.length === 0) {
        // Pre-flop: just show the cards
        const ranks = playerHand.map(c => RANK_DISPLAY[c.rank]).join(', ');
        return `${ranks}`;
    }

    // Post-flop: server should provide this info
    return 'Avaliando...';
}
