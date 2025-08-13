// --- simple client-side blackjack demo ---

const SUITS = ["spades","hearts","diamonds","clubs"];
const RANKS = ["A","2","3","4","5","6","7","8","9","10","J","Q","K"];

let deck = [];
let dealer = [];
let player = [];
let gameOver = false;

const dealerBox = document.getElementById("dealer-cards");
const playerBox = document.getElementById("player-cards");
const dealerScoreEl = document.getElementById("dealer-score");
const playerScoreEl = document.getElementById("player-score");

document.getElementById("hit-btn").addEventListener("click", onHit);
document.getElementById("stand-btn").addEventListener("click", onStand);
document.getElementById("restart-btn").addEventListener("click", startGame);
document.getElementById("howtoplay-btn").addEventListener("click", ()=> modal(true));
document.getElementById("close-modal").addEventListener("click", ()=> modal(false));

function modal(show){
  const m = document.getElementById("howtoplay-modal");
  if (show) m.removeAttribute("hidden"); else m.setAttribute("hidden","hidden");
}

function buildDeck(){
  const d = [];
  for (const s of SUITS){
    for (const r of RANKS){
      d.push({rank:r, suit:s});
    }
  }
  return shuffle(d);
}

function shuffle(a){
  for (let i=a.length-1;i>0;i--){
    const j = Math.floor(Math.random()* (i+1));
    [a[i],a[j]] = [a[j],a[i]];
  }
  return a;
}

function cardValue(card){
  if (["J","Q","K"].includes(card.rank)) return 10;
  if (card.rank === "A") return 11; // treat as 11 first, fix later
  return Number(card.rank);
}

function handValue(hand){
  let total = 0, aces = 0;
  for (const c of hand){
    total += cardValue(c);
    if (c.rank === "A") aces++;
  }
  while (total > 21 && aces){ total -= 10; aces--; }
  return total;
}

// maps to /static/cards/king_of_hearts.svg, etc.
function cardSrc(card){
  const rankName = (
    card.rank === "A" ? "ace" :
    card.rank === "J" ? "jack" :
    card.rank === "Q" ? "queen" :
    card.rank === "K" ? "king" : card.rank
  ).toLowerCase();
  return `/static/cards/${rankName}_of_${card.suit}.svg`;
}

function drawCard(who){
  const c = deck.pop();
  who.push(c);
  return c;
}

function render(){
  // clear
  dealerBox.innerHTML = "";
  playerBox.innerHTML = "";

  for (const c of dealer){
    const img = document.createElement("img");
    img.src = cardSrc(c);
    img.alt = `${c.rank} of ${c.suit}`;
    dealerBox.appendChild(img);
  }
  for (const c of player){
    const img = document.createElement("img");
    img.src = cardSrc(c);
    img.alt = `${c.rank} of ${c.suit}`;
    playerBox.appendChild(img);
  }

  dealerScoreEl.textContent = `Score: ${handValue(dealer)}`;
  playerScoreEl.textContent = `Score: ${handValue(player)}`;
}

function startGame(){
  gameOver = false;
  deck = buildDeck();
  dealer = [];
  player = [];
  drawCard(player); drawCard(dealer); drawCard(player); drawCard(dealer);
  render();
}

function onHit(){
  if (gameOver) return;
  drawCard(player);
  render();
  if (handValue(player) >= 21) onStand();
}

function onStand(){
  if (gameOver) return;
  // dealer draws to 17+
  while (handValue(dealer) < 17) drawCard(dealer);
  render();
  const ps = handValue(player), ds = handValue(dealer);
  let msg = "";
  if (ps > 21) msg = "You bust. Dealer wins.";
  else if (ds > 21) msg = "Dealer busts. You win!";
  else if (ps > ds) msg = "You win!";
  else if (ps < ds) msg = "Dealer wins.";
  else msg = "Push (tie).";
  alert(msg);
  gameOver = true;
}

// kick off
window.addEventListener("DOMContentLoaded", startGame);
