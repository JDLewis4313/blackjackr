

// ---------------- SHUFFLE ANIMATION ---------------- //
const shuffleBtn = document.getElementById('shuffle-btn');
const shuffleContainer = document.querySelector('.shuffle-container');

function shuffleCards() {
    if (!shuffleContainer) return;

    // Reset and apply shuffle class
    shuffleContainer.classList.remove('stacked');
    shuffleContainer.classList.add('shuffle');

    setTimeout(() => {
        shuffleContainer.classList.remove('shuffle');
        shuffleContainer.classList.add('stacked');
    }, 800); // Give time for animation
}

// Auto shuffle every 3 seconds
if (shuffleContainer) {
    window.addEventListener('load', () => {
        shuffleCards();
        setInterval(shuffleCards, 3000);
    });
}

if (shuffleBtn) shuffleBtn.addEventListener('click', shuffleCards);


// ---------------- MODALS ---------------- //
const modals = document.querySelectorAll('.modal');
const loginBtn = document.getElementById('login-btn');
const signupBtn = document.getElementById('signup-btn');
const howToPlayBtn = document.getElementById('howtoplay-btn');
const closeButtons = document.querySelectorAll('.close-btn');

loginBtn?.addEventListener('click', () => document.getElementById('login-modal').style.display = 'flex');
signupBtn?.addEventListener('click', () => document.getElementById('signup-modal').style.display = 'flex');
howToPlayBtn?.addEventListener('click', () => document.getElementById('howtoplay-modal').style.display = 'flex');

closeButtons.forEach(btn => btn.addEventListener('click', () => modals.forEach(m => m.style.display = 'none')));
window.addEventListener('click', (e) => modals.forEach(m => { if (e.target === m) m.style.display = 'none'; }));

// ---------------- BLACKJACK GAME LOGIC ---------------- //
const dealerCardsContainer = document.getElementById('dealer-cards');
const playerCardsContainer = document.getElementById('player-cards');
const dealerScoreDisplay = document.getElementById('dealer-score');
const playerScoreDisplay = document.getElementById('player-score');

const hitBtn = document.getElementById('hit-btn');
const standBtn = document.getElementById('stand-btn');
const restartBtn = document.getElementById('restart-btn');

const suits = ['hearts', 'spades', 'diamonds', 'clubs'];
const values = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K'];
let deck = [];
let playerCards = [];
let dealerCards = [];

// Initialize Game
function initializeGame() {
    deck = createDeck();
    shuffleDeck(deck);
    playerCards = [drawCard(), drawCard()];
    dealerCards = [drawCard(), drawCard()];
    renderCards(playerCardsContainer, playerCards);
    renderCards(dealerCardsContainer, dealerCards);
    updateScores();
}

function createDeck() {
    const newDeck = [];
    for (let suit of suits) {
        for (let value of values) {
            newDeck.push({ suit, value });
        }
    }
    return newDeck;
}

function shuffleDeck(d) {
    for (let i = d.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [d[i], d[j]] = [d[j], d[i]];
    }
}

function drawCard() { return deck.pop(); }

function renderCards(container, cards) {
    if (!container) return;
    container.innerHTML = '';
    cards.forEach(card => {
        const img = document.createElement('img');
        img.src = `Cards/${card.value.toLowerCase()}_of_${card.suit}.svg`;
        img.alt = `${card.value} of ${card.suit}`;
        container.appendChild(img);
    });
}

function calculateScore(cards) {
    let total = 0;
    let aces = 0;
    cards.forEach(card => {
        if (['J', 'Q', 'K'].includes(card.value)) total += 10;
        else if (card.value === 'A') { total += 11; aces++; }
        else total += parseInt(card.value);
    });
    while (total > 21 && aces > 0) { total -= 10; aces--; }
    return total;
}

function updateScores() {
    if (dealerScoreDisplay) dealerScoreDisplay.textContent = `Score: ${calculateScore(dealerCards)}`;
    if (playerScoreDisplay) playerScoreDisplay.textContent = `Score: ${calculateScore(playerCards)}`;
}

hitBtn?.addEventListener('click', () => {
    playerCards.push(drawCard());
    renderCards(playerCardsContainer, playerCards);
    updateScores();
    if (calculateScore(playerCards) > 21) {
        alert('You Bust! Dealer Wins.');
        disableControls();
    }
});

standBtn?.addEventListener('click', () => dealerTurn());

function dealerTurn() {
    while (calculateScore(dealerCards) < 17) {
        dealerCards.push(drawCard());
        renderCards(dealerCardsContainer, dealerCards);
        updateScores();
    }
    checkWinner();
}

function checkWinner() {
    const playerScore = calculateScore(playerCards);
    const dealerScore = calculateScore(dealerCards);
    let message;

    if (dealerScore > 21 || playerScore > dealerScore) {
        message = 'You Win!';
    } else if (playerScore < dealerScore) {
        message = 'Dealer Wins!';
    } else {
        message = 'It\'s a Tie!';
    }

    alert(message);
    disableControls();
}

restartBtn?.addEventListener('click', () => {
    enableControls();
    initializeGame();
});

function disableControls() {
    if (hitBtn) hitBtn.disabled = true;
    if (standBtn) standBtn.disabled = true;
}

function enableControls() {
    if (hitBtn) hitBtn.disabled = false;
    if (standBtn) standBtn.disabled = false;
}

if (playerCardsContainer && dealerCardsContainer) {
    initializeGame();
}

// ---------------- HIGH SCORE STORAGE (future backend integration) ---------------- //
// Placeholder, can integrate later.
