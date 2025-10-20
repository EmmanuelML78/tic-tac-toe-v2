if (!Storage.isAuthenticated()) {
  alert("Session expired or not logged in. Please login again.");
  window.location.href = "index.html";
  throw new Error("Not authenticated");
}

const userInfo = Storage.getUserInfo();

if (!userInfo || !userInfo.userId || !userInfo.username) {
  alert("Invalid session data. Please login again.");
  Storage.clearAll();
  window.location.href = "index.html";
  throw new Error("Invalid user info");
}

let socket = null;
let currentInvitations = [];

document.getElementById(
  "username-display"
).textContent = `Welcome, ${userInfo.username}!`;

document.getElementById("logout-btn").addEventListener("click", () => {
  Storage.clearAll();
  if (socket) {
    socket.disconnect();
  }
  window.location.href = "index.html";
});

function initSocket() {
  showLoading();

  const token = Storage.getToken();

  socket = io(CONFIG.SOCKET_URL, {
    transports: ["websocket", "polling"],
    auth: {
      token: token,
    },
    query: {
      token: token,
    },
  });

  socket.on("connect", () => {
    socket.emit("authenticate", {
      token: token,
    });
  });

  socket.on("authenticated", (data) => {
    hideLoading();
    Notification.success("Connected to game server!");
    loadLeaderboard();
    loadUserStats();
  });

  socket.on("auth_error", (data) => {
    hideLoading();
    Notification.error("Authentication failed: " + data.message);
    setTimeout(() => {
      Storage.clearAll();
      window.location.href = "index.html";
    }, 2000);
  });

  socket.on("online_users", (data) => {
    updateOnlineUsers(data.users);
  });

  socket.on("invitation_received", (data) => {
    handleInvitationReceived(data);
  });

  socket.on("invitation_sent", (data) => {
    Notification.success(`Invitation sent to ${data.to_username}`);
  });

  socket.on("game_started", (data) => {
    localStorage.setItem("current_game", JSON.stringify(data));
    window.location.href = "game.html";
  });

  socket.on("error", (data) => {
    Notification.error(data.message);
  });

  socket.on("disconnect", () => {
    Notification.error("Disconnected from server");
  });
}

function updateOnlineUsers(users) {
  const list = document.getElementById("online-users-list");
  document.getElementById("online-count").textContent = users.length;

  if (users.length === 0) {
    list.innerHTML = '<p class="text-center">No other players online</p>';
    return;
  }

  list.innerHTML = "";

  users.forEach((user) => {
    if (user.id == userInfo.userId) return;

    const userItem = document.createElement("div");
    userItem.className = "user-item";

    const status = user.in_game
      ? '<span class="user-status in-game">In Game</span>'
      : '<span class="user-status">Available</span>';

    userItem.innerHTML = `
            <div>
                <span class="user-name">${user.username}</span>
                ${status}
            </div>
            <button class="btn btn-primary"
                    onclick="invitePlayer(${user.id})"
                    ${user.in_game ? "disabled" : ""}>
                Invite
            </button>
        `;

    list.appendChild(userItem);
  });
}

function invitePlayer(targetUserId) {
  if (!socket) return;

  socket.emit("invite_player", {
    target_user_id: targetUserId,
  });
}

function handleInvitationReceived(data) {
  currentInvitations.push(data);
  updateInvitationsList();
  Notification.info(`${data.from_username} invited you to play!`, 5000);
}

function updateInvitationsList() {
  const list = document.getElementById("invitations-list");

  if (currentInvitations.length === 0) {
    list.innerHTML = '<p class="text-center">No pending invitations</p>';
    return;
  }

  list.innerHTML = "";

  currentInvitations.forEach((invitation) => {
    const invItem = document.createElement("div");
    invItem.className = "invitation-item";
    invItem.innerHTML = `
            <p><strong>${invitation.from_username}</strong> wants to play with you!</p>
            <div class="invitation-actions">
                <button class="btn btn-secondary" onclick="acceptInvitation(${invitation.invitation_id})">
                    Accept
                </button>
                <button class="btn btn-danger" onclick="rejectInvitation(${invitation.invitation_id})">
                    Reject
                </button>
            </div>
        `;
    list.appendChild(invItem);
  });
}

function acceptInvitation(invitationId) {
  if (!socket) return;

  socket.emit("accept_invitation", {
    invitation_id: invitationId,
  });

  currentInvitations = currentInvitations.filter(
    (inv) => inv.invitation_id !== invitationId
  );
  updateInvitationsList();
}

function rejectInvitation(invitationId) {
  if (!socket) return;

  socket.emit("reject_invitation", {
    invitation_id: invitationId,
  });

  currentInvitations = currentInvitations.filter(
    (inv) => inv.invitation_id !== invitationId
  );
  updateInvitationsList();
  Notification.info("Invitation rejected");
}

function playVsBot(difficulty) {
  if (!socket) return;

  socket.emit("play_vs_bot", {
    difficulty: difficulty,
  });
}

async function loadLeaderboard() {
  try {
    const token = Storage.getToken();

    const response = await fetch(`${CONFIG.API_URL}/api/stats/leaderboard`, {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || "Failed to load leaderboard");
    }

    const data = await response.json();
    displayLeaderboard(data);
  } catch (error) {
    const list = document.getElementById("leaderboard-list");
    list.innerHTML = `<p class="text-center" style="color: var(--danger-color);">Error loading leaderboard</p>`;
  }
}

function displayLeaderboard(data) {
  const list = document.getElementById("leaderboard-list");

  if (data.length === 0) {
    list.innerHTML = '<p class="text-center">No players yet</p>';
    return;
  }

  list.innerHTML = "";

  data.forEach((player) => {
    const item = document.createElement("div");
    item.className = "leaderboard-item";

    const medal =
      player.rank === 1
        ? "🥇"
        : player.rank === 2
        ? "🥈"
        : player.rank === 3
        ? "🥉"
        : "";

    item.innerHTML = `
            <span class="rank">${medal || `#${player.rank}`}</span>
            <div class="player-info">
                <span class="player-name">${player.username}</span>
                <span class="player-stats">W: ${player.wins} | L: ${
      player.losses
    } | D: ${player.draws} | WR: ${player.win_rate}%</span>
            </div>
            <span class="points">${player.ranking_points} pts</span>
        `;

    list.appendChild(item);
  });
}

async function loadUserStats() {
  try {
    const token = Storage.getToken();

    const response = await fetch(`${CONFIG.API_URL}/api/stats`, {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || "Failed to load stats");
    }

    const data = await response.json();
    displayUserStats(data);
  } catch (error) {
    const container = document.getElementById("user-stats");
    container.innerHTML = `<p class="text-center" style="color: var(--danger-color);">Error loading stats</p>`;
  }
}

function displayUserStats(stats) {
  const container = document.getElementById("user-stats");

  container.innerHTML = `
        <div class="stat-row">
            <span class="stat-label">Total Games:</span>
            <span class="stat-value">${stats.total_games}</span>
        </div>
        <div class="stat-row">
            <span class="stat-label">Wins:</span>
            <span class="stat-value" style="color: var(--secondary-color);">${stats.wins}</span>
        </div>
        <div class="stat-row">
            <span class="stat-label">Losses:</span>
            <span class="stat-value" style="color: var(--danger-color);">${stats.losses}</span>
        </div>
        <div class="stat-row">
            <span class="stat-label">Draws:</span>
            <span class="stat-value" style="color: var(--warning-color);">${stats.draws}</span>
        </div>
        <div class="stat-row">
            <span class="stat-label">Win Rate:</span>
            <span class="stat-value">${stats.win_rate}%</span>
        </div>
        <div class="stat-row">
            <span class="stat-label">Current Streak:</span>
            <span class="stat-value">${stats.current_streak}</span>
        </div>
        <div class="stat-row">
            <span class="stat-label">Ranking Points:</span>
            <span class="stat-value">${stats.ranking_points}</span>
        </div>
    `;
}

window.addEventListener("DOMContentLoaded", () => {
  initSocket();
});
