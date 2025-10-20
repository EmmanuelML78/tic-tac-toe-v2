if (!Storage.isAuthenticated()) {
  window.location.href = "index.html";
}

const gameDataStr = localStorage.getItem("current_game");
if (!gameDataStr) {
  Notification.error("No game data found");
  setTimeout(() => {
    window.location.href = "lobby.html";
  }, 2000);
}

const gameData = JSON.parse(gameDataStr);
const userInfo = Storage.getUserInfo();
let socket = null;
let currentBoard = gameData.board || "---------";
let currentTurn = gameData.current_turn;
let mySymbol = gameData.player1.id == userInfo.userId ? "X" : "O";
let gameOver = false;

function initGameUI() {
  document.getElementById("player1-name").textContent =
    gameData.player1.username;
  document.getElementById("player2-name").textContent =
    gameData.player2.username;

  updateBoard(currentBoard);
  updateTurn(currentTurn);

  document.getElementById("forfeit-btn").addEventListener("click", forfeitGame);

  const cells = document.querySelectorAll(".cell");
  cells.forEach((cell) => {
    cell.addEventListener("click", () => {
      if (gameOver) return;

      const index = parseInt(cell.getAttribute("data-index"));
      makeMove(index);
    });
  });
}

function initSocket() {
  showLoading();

  socket = io(CONFIG.SOCKET_URL, {
    transports: ["websocket", "polling"],
  });

  socket.on("connect", () => {
    socket.emit("authenticate", {
      token: Storage.getToken(),
    });
  });

  socket.on("authenticated", () => {
    socket.emit("join_game", {
      game_id: gameData.game_id,
    });
  });

  socket.on("game_joined", (data) => {
    hideLoading();
    Notification.success("Connected to game!");
  });

  socket.on("move_made", (data) => {
    handleMoveMade(data);
  });

  socket.on("game_forfeited", (data) => {
    handleGameForfeited(data);
  });

  socket.on("error", (data) => {
    Notification.error(data.message);

    if (data.message === "Not authenticated") {
      socket.emit("authenticate", {
        token: Storage.getToken(),
      });
    }
  });

  socket.on("disconnect", () => {
    Notification.error("Disconnected from server");
  });
}

function updateBoard(board) {
  const cells = document.querySelectorAll(".cell");

  cells.forEach((cell, index) => {
    const symbol = board[index];
    cell.textContent = symbol === "-" ? "" : symbol;
    cell.className = "cell";

    if (symbol === "X") {
      cell.classList.add("x");
    } else if (symbol === "O") {
      cell.classList.add("o");
    }

    if (symbol !== "-") {
      cell.classList.add("disabled");
    }
  });

  currentBoard = board;
}

function updateTurn(turnUserId) {
  currentTurn = turnUserId;

  const isMyTurn = turnUserId == userInfo.userId;

  const turnDisplay = document.getElementById("turn-display");
  if (isMyTurn) {
    turnDisplay.textContent = `Your turn! (${mySymbol})`;
    turnDisplay.style.background = "#c8e6c9";
  } else {
    const opponentName =
      gameData.player1.id == turnUserId
        ? gameData.player1.username
        : gameData.player2.username;
    turnDisplay.textContent = `${opponentName}'s turn...`;
    turnDisplay.style.background = "#fff9c4";
  }

  const player1Info = document.getElementById("player1-info");
  const player2Info = document.getElementById("player2-info");
  const player1Turn = document.getElementById("player1-turn");
  const player2Turn = document.getElementById("player2-turn");

  player1Info.classList.remove("active");
  player2Info.classList.remove("active");
  player1Turn.classList.remove("active");
  player2Turn.classList.remove("active");

  if (turnUserId == gameData.player1.id) {
    player1Info.classList.add("active");
    player1Turn.classList.add("active");
    player1Turn.textContent = "👉 Your turn!";
  } else {
    player2Info.classList.add("active");
    player2Turn.classList.add("active");
    player2Turn.textContent = "👉 Your turn!";
  }

  const cells = document.querySelectorAll(".cell");
  cells.forEach((cell) => {
    if (cell.textContent === "") {
      if (isMyTurn && !gameOver) {
        cell.classList.remove("disabled");
      } else {
        cell.classList.add("disabled");
      }
    }
  });
}

function makeMove(position) {
  if (gameOver) return;

  if (currentTurn != userInfo.userId) {
    Notification.error("Not your turn!");
    return;
  }

  if (currentBoard[position] !== "-") {
    Notification.error("Cell already taken!");
    return;
  }

  socket.emit("make_move", {
    game_id: gameData.game_id,
    position: position,
  });
}

function handleMoveMade(data) {
  updateBoard(data.board);

  if (!data.game_over) {
    updateTurn(data.current_turn);
  }

  if (data.game_over) {
    gameOver = true;
    handleGameOver(data);
  }
}

function handleGameOver(data) {

  const modal = document.getElementById("game-over-modal");
  const title = document.getElementById("game-result-title");
  const message = document.getElementById("game-result-message");

  if (data.winning_line) {
    data.winning_line.forEach((index) => {
      const cell = document.querySelector(`.cell[data-index="${index}"]`);
      cell.classList.add("winning");
    });
  }

  if (data.result === "win") {
    if (data.winner_id == userInfo.userId) {
      title.textContent = "Congratulations, victory is yours!";
      title.style.color = "#4caf50";
      message.textContent = "Congratulations! You won the game!";
    } else {
      title.textContent = "😔 Oh you've lost";
      title.style.color = "#f44336";
      message.textContent = "Better luck next time!";
    }
  } else if (data.result === "You're good, you tied") {
    title.textContent = "🤝 Draw";
    title.style.color = "#ff9800";
    message.textContent = "It's a tie! Good game!";
  }

  setTimeout(() => {
    modal.style.display = "flex";
  }, 1000);
}

function handleGameForfeited(data) {

  gameOver = true;

  const modal = document.getElementById("game-over-modal");
  const title = document.getElementById("game-result-title");
  const message = document.getElementById("game-result-message");

  if (data.forfeited_by == userInfo.userId) {
    title.textContent = "🏳️ You Forfeited";
    title.style.color = "#f44336";
    message.textContent = "You have left the game.";
  } else {
    title.textContent = "🎉 Congratulations, victory is yours!!";
    title.style.color = "#4caf50";
    message.textContent = "Opponent forfeited. You win!";
  }

  modal.style.display = "flex";
}

function forfeitGame() {
  if (gameOver) return;

  if (confirm("Are you sure you want to forfeit? This will count as a loss.")) {
    socket.emit("forfeit_game", {
      game_id: gameData.game_id,
    });
  }
}

function returnToLobby() {
  localStorage.removeItem("current_game");
  window.location.href = "lobby.html";
}

window.addEventListener("DOMContentLoaded", () => {
  initGameUI();
  initSocket();
});

window.addEventListener("beforeunload", (e) => {
  if (!gameOver) {
    e.preventDefault();
    e.returnValue =
      "Game is still in progress. Are you sure you want to leave?";
  }
});
