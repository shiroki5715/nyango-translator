// Memory Match Game Logic
const emojiList = ["🍎", "🍌", "🍇", "🍒", "🍑", "🥝", "🍍", "🍉"];
let deck;
let flipped = [];
let lock = false;
let moves = 0;
let startTime;
let timerInterval;

const gameContainer = document.getElementById("game");
const movesSpan = document.getElementById("moves");
const timeSpan  = document.getElementById("time");
const restartBtn = document.getElementById("restart");
restartBtn.addEventListener("click", restart);

function shuffle(array) {
  return array.sort(() => Math.random() - 0.5);
}

function startTimer() {
  startTime = Date.now();
  timerInterval = setInterval(() => {
    const seconds = Math.floor((Date.now() - startTime) / 1000);
    timeSpan.textContent = `時間: ${seconds}s`;
  }, 1000);
}

function stopTimer() {
  clearInterval(timerInterval);
}

function createCards() {
  gameContainer.innerHTML = "";
  deck.forEach((emoji) => {
    const card = document.createElement("div");
    card.className =
      "card perspective w-20 h-24 sm:w-24 sm:h-28 cursor-pointer";
    card.innerHTML = `
      <div class="inner w-full h-full">
        <div class="front absolute inset-0 bg-gray-700 rounded-lg flex items-center justify-center text-3xl">?</div>
        <div class="back absolute inset-0 bg-gray-800 rounded-lg flex items-center justify-center text-3xl">${emoji}</div>
      </div>`;
    card.addEventListener("click", () => flipCard(card, emoji));
    gameContainer.appendChild(card);
  });
}

function flipCard(card, emoji) {
  if (lock || card.classList.contains("matched") || flipped[0] === card) return;
  card.querySelector(".inner").classList.add("rotate-y-180");
  flipped.push({ card, emoji });

  if (flipped.length === 2) {
    moves++;
    movesSpan.textContent = `手数: ${moves}`;
    checkMatch();
  }
}

function checkMatch() {
  lock = true;
  const [first, second] = flipped;

  if (first.emoji === second.emoji) {
    first.card.classList.add("matched");
    second.card.classList.add("matched");
    flipped = [];
    lock = false;
    if (document.querySelectorAll(".matched").length === deck.length) {
      stopTimer();
      setTimeout(() =>
        alert(
          `クリア！\n手数: ${moves}\n時間: ${timeSpan.textContent.replace("時間: ", "")}`
        ),
        300
      );
    }
  } else {
    setTimeout(() => {
      first.card.querySelector(".inner").classList.remove("rotate-y-180");
      second.card.querySelector(".inner").classList.remove("rotate-y-180");
      flipped = [];
      lock = false;
    }, 800);
  }
}

function restart() {
  stopTimer();
  moves = 0;
  movesSpan.textContent = "手数: 0";
  timeSpan.textContent = "時間: 0s";
  flipped = [];
  lock = false;
  deck = shuffle([...emojiList, ...emojiList]);
  createCards();
  startTimer();
}

// 初期化
restart();