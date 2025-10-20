/**
 * Game functionality
 */

// Check authentication
if (!Storage.isAuthenticated()) {
  window.location.href = "index.html";
}

// Get game data from localStorage
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

console.log("Game data:", gameData);
console.log("My symbol:", mySymbol);

// Initialize game UI
function initGameUI() {
  // Set player names
  document.getElementById("player1-name").textContent =
    gameData.player1.username;
  document.getElementById("player2-name").textContent =
    gameData.player2.username;

  // Update board
  updateBoard(currentBoard);

  // Update turn
  updateTurn(currentTurn);

  // Forfeit button handler
  document.getElementById("forfeit-btn").addEventListener("click", forfeitGame);

  // Cell click handlers
  const cells = document.querySelectorAll(".cell");
  cells.forEach((cell) => {
    cell.addEventListener("click", () => {
      if (gameOver) return;

      const index = parseInt(cell.getAttribute("data-index"));
      makeMove(index);
    });
  });
}

// Initialize Socket.IO
function initSocket() {
  showLoading();

  socket = io(CONFIG.SOCKET_URL, {
    transports: ["websocket", "polling"],
  });

  socket.on("connect", () => {
    console.log("Connected to server");
    socket.emit("authenticate", {
      token: Storage.getToken(),
    });
  });

  socket.on("authenticated", () => {
    console.log("Authenticated");

    // Join the game room after authentication
    console.log("Joining game room:", gameData.game_id);
    socket.emit("join_game", {
      game_id: gameData.game_id,
    });
  });

  socket.on("game_joined", (data) => {
    console.log("Successfully joined game:", data);
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
    console.error("Socket error:", data);
    Notification.error(data.message);

    // If not authenticated error, try to reconnect
    if (data.message === "Not authenticated") {
      console.log("Re-authenticating...");
      socket.emit("authenticate", {
        token: Storage.getToken(),
      });
    }
  });

  socket.on("disconnect", () => {
    Notification.error("Disconnected from server");
  });
}

// Update board display
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

    // Disable filled cells
    if (symbol !== "-") {
      cell.classList.add("disabled");
    }
  });

  currentBoard = board;
}

// Update turn display
function updateTurn(turnUserId) {
  currentTurn = turnUserId;

  const isMyTurn = turnUserId == userInfo.userId;

  // Update turn display
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

  // Update player indicators
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

  // Enable/disable cells
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

// Make a move
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

  // Send move to server
  socket.emit("make_move", {
    game_id: gameData.game_id,
    position: position,
  });
}

// Handle move made
function handleMoveMade(data) {
  console.log("Move made:", data);
  console.log("  - game_over:", data.game_over);
  console.log("  - result:", data.result);
  console.log("  - winner_id:", data.winner_id);
  console.log("  - board:", data.board);

  // Update board
  updateBoard(data.board);

  // Update turn
  if (!data.game_over) {
    updateTurn(data.current_turn);
  } else {
    console.log("🎮 GAME OVER DETECTED! Setting gameOver = true");
  }

  // Check if game over
  if (data.game_over) {
    gameOver = true;
    console.log("🎮 Calling handleGameOver with data:", data);
    handleGameOver(data);
  }
}

// Handle game over
function handleGameOver(data) {
  console.log("Game over:", data);

  const modal = document.getElementById("game-over-modal");
  const title = document.getElementById("game-result-title");
  const message = document.getElementById("game-result-message");

  // Highlight winning line if exists
  if (data.winning_line) {
    data.winning_line.forEach((index) => {
      const cell = document.querySelector(`.cell[data-index="${index}"]`);
      cell.classList.add("winning");
    });
  }

  // Determine result message
  if (data.result === "win") {
    if (data.winner_id == userInfo.userId) {
      title.textContent = "🎉 Victory!";
      title.style.color = "#4caf50"; // Secondary color (green)
      message.textContent = "Congratulations! You won the game!";
    } else {
      title.textContent = "😔 Defeat";
      title.style.color = "#f44336"; // Danger color (red)
      message.textContent = "Better luck next time!";
    }
  } else if (data.result === "draw") {
    title.textContent = "🤝 Draw";
    title.style.color = "#ff9800"; // Warning color (orange)
    message.textContent = "It's a tie! Good game!";
  }

  // Show modal
  setTimeout(() => {
    modal.style.display = "flex";
  }, 1000);
}

// Handle game forfeited
function handleGameForfeited(data) {
  console.log("Game forfeited:", data);

  gameOver = true;

  const modal = document.getElementById("game-over-modal");
  const title = document.getElementById("game-result-title");
  const message = document.getElementById("game-result-message");

  if (data.forfeited_by == userInfo.userId) {
    title.textContent = "🏳️ You Forfeited";
    title.style.color = "#f44336"; // Danger color (red)
    message.textContent = "You have left the game.";
  } else {
    title.textContent = "🎉 Victory!";
    title.style.color = "#4caf50"; // Secondary color (green)
    message.textContent = "Opponent forfeited. You win!";
  }

  modal.style.display = "flex";
}

// Forfeit game
function forfeitGame() {
  if (gameOver) return;

  if (confirm("Are you sure you want to forfeit? This will count as a loss.")) {
    socket.emit("forfeit_game", {
      game_id: gameData.game_id,
    });
  }
}

// Return to lobby
function returnToLobby() {
  localStorage.removeItem("current_game");
  window.location.href = "lobby.html";
}

// Initialize on page load
window.addEventListener("DOMContentLoaded", () => {
  initGameUI();
  initSocket();
});

// Prevent accidental page close
window.addEventListener("beforeunload", (e) => {
  if (!gameOver) {
    e.preventDefault();
    e.returnValue =
      "Game is still in progress. Are you sure you want to leave?";
  }
});
