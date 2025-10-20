# 🚀 Quick Start Guide

Get the Tic-Tac-Toe Multiplayer game running in 5 minutes!

## Prerequisites

- Python 3.9 or higher
- Modern web browser (Chrome, Firefox, Edge)
- Terminal/Command Prompt

## Step-by-Step Instructions

### 1. Install Python Dependencies

Open a terminal and navigate to the project directory:

```bash
cd "d:\GitHub\computer networks 2\Nueva carpeta (2)\backend"
pip install -r requirements.txt
```

**Expected output**: Successfully installed fastapi, python-socketio, sqlalchemy, etc.

### 2. Start the Backend Server

```bash
python run.py
```

**Expected output**:
```
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Database initialized successfully
INFO:     Server started successfully
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

✅ The backend is now running on http://localhost:8000

**Keep this terminal window open!**

### 3. Open the Frontend

Open a **new terminal** window:

```bash
cd "d:\GitHub\computer networks 2\Nueva carpeta (2)\frontend"
python -m http.server 8080
```

**Expected output**:
```
Serving HTTP on :: port 8080 (http://[::]:8080/) ...
```

✅ The frontend is now running on http://localhost:8080

### 4. Play the Game!

Open your browser and go to:
**http://localhost:8080/public/index.html**

#### To Play vs Bot (Single Player):
1. Register a new account
2. You'll be redirected to the lobby
3. Click "Easy Bot", "Medium Bot", or "Hard Bot"
4. Play!

#### To Play vs Another Player (Multiplayer):
1. Open a **second browser window** (or incognito/private mode)
2. Register a **different account**
3. In one window, click "Invite" next to the other player's name
4. In the other window, accept the invitation
5. Play together in real-time!

## 🎮 How to Play

1. **Your Turn**: Click on an empty cell when it's your turn
2. **Objective**: Get 3 in a row (horizontal, vertical, or diagonal)
3. **Forfeit**: Click "Forfeit Game" if you want to give up
4. **Leave**: Click "Leave Game" to return to lobby

## ✅ Verification Checklist

Test these features to verify everything works:

- [ ] Register a new account
- [ ] Login works
- [ ] Can see online players
- [ ] Play vs Easy Bot - Make sure you can make moves
- [ ] Play vs Medium Bot - Make sure bot responds
- [ ] Play vs Hard Bot - Try to beat it! (Hint: you can't, it's perfect)
- [ ] Open two browsers and play multiplayer
- [ ] Invite system works
- [ ] Game board updates in real-time
- [ ] Winning detection works correctly
- [ ] Draw detection works
- [ ] Forfeit works
- [ ] Leaderboard shows your stats
- [ ] Stats update after games

## 🐛 Troubleshooting

### Backend won't start

**Problem**: `ModuleNotFoundError: No module named 'fastapi'`
**Solution**: Run `pip install -r requirements.txt` in the backend folder

**Problem**: `Address already in use`
**Solution**: Port 8000 is busy. Kill the process or change PORT in `.env`

### Frontend shows connection error

**Problem**: "Failed to connect to server"
**Solution**:
1. Check backend is running (terminal shows "Uvicorn running")
2. Try accessing http://localhost:8000 directly - should show JSON message
3. Clear browser cache and reload

### Can't see other players online

**Problem**: Two players logged in but can't see each other
**Solution**:
1. Make sure both are authenticated (check browser console for "Authenticated" message)
2. Refresh the page
3. Check backend terminal for connection logs

### Bot doesn't move

**Problem**: Made a move but bot doesn't respond
**Solution**: Check backend terminal for errors. The bot should move automatically after your move.

### Game board not updating

**Problem**: Made a move but board doesn't update
**Solution**: Check browser console (F12) for errors. Make sure Socket.IO connection is active.

## 🎯 Test Scenarios

### Scenario 1: Quick Bot Game (Easy)
1. Register as "TestUser1"
2. Click "Easy Bot"
3. Play until win/loss/draw
4. Verify result shows correctly

### Scenario 2: Unbeatable Bot (Hard)
1. Click "Hard Bot"
2. Try to win
3. Best case: Draw. The bot is unbeatable!

### Scenario 3: Multiplayer Game
1. Window 1: Register as "Alice"
2. Window 2: Register as "Bob" (incognito mode)
3. Alice invites Bob
4. Bob accepts
5. Play a complete game
6. Verify both players see the same board state
7. Winner/loser shows correctly for both

### Scenario 4: Forfeit
1. Start any game
2. Click "Forfeit Game"
3. Confirm
4. Verify opponent (or bot) wins

### Scenario 5: Stats & Leaderboard
1. Play multiple games (at least 3)
2. Check "Your Stats" section
3. Verify wins/losses/draws count
4. Check leaderboard shows you

## 📊 Expected Test Results

After playing a few games, you should see:

- **Leaderboard**: Top players by ranking points
- **Your Stats**:
  - Total Games: Number of games played
  - Wins/Losses/Draws: Accurate counts
  - Win Rate: Percentage (Wins / Total Games)
  - Ranking Points: ELO-style points (starts at 1000)

## 🔍 Monitoring with Wireshark

Want to see the network traffic?

1. Start Wireshark
2. Capture on "Loopback" interface
3. Filter: `tcp.port == 8000`
4. Play a game
5. Observe:
   - HTTP upgrade to WebSocket
   - JSON messages for moves
   - Real-time communication

## 🎉 Success!

If you can:
1. ✅ Register and login
2. ✅ Play vs bot
3. ✅ Play vs another player
4. ✅ See real-time updates
5. ✅ View stats and leaderboard

**Congratulations! The system is working perfectly!** 🎮🎊

## 🆘 Still Having Issues?

1. Check both terminal windows for error messages
2. Check browser console (F12) for JavaScript errors
3. Verify ports 8000 and 8080 are not blocked by firewall
4. Try restarting both backend and frontend
5. Check [INSTALL.md](INSTALL.md) for detailed installation guide
6. Review logs in `backend/logs/server.log`

## Next Steps

- Read [README.md](README.md) for full documentation
- Try all bot difficulty levels
- Play multiple multiplayer games
- Check the code to understand how it works!
- Monitor network traffic with Wireshark

---

**Have fun playing! 🎮**
