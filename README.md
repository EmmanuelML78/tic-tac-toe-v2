# 🎮 Tic-Tac-Toe Multiplayer - Capstone Project

Network Multiplayer Tic-Tac-Toe Game developed for Computer Networks 2 course at Jala University.

## 📋 Project Overview

A real-time multiplayer tic-tac-toe game built with client-server architecture, featuring:

- **Real-time gameplay** using WebSockets (Socket.IO)
- **User authentication** with JWT tokens and bcrypt password hashing
- **Bot AI** with 3 difficulty levels (Easy, Medium, Hard) using Minimax algorithm
- **Leaderboard and statistics** tracking with ELO-based ranking system
- **Reconnection support** to resume games after disconnection
- **Event-driven architecture** with game manager acting as event bus
- **Comprehensive logging** to database and files
- **Secure communication** with support for SSL/TLS

## ✨ Features Implemented

### Base Requirements ✅
1. ✅ User registration and authentication (secure password storage with bcrypt)
2. ✅ Display online users in real-time
3. ✅ Create games and invite other players
4. ✅ Accept/reject game invitations
5. ✅ Turn-based gameplay with real-time board synchronization
6. ✅ Game result display (win/loss/draw)
7. ✅ Forfeit game functionality
8. ✅ Server event logging (connections, games, errors) persisted to database

### Optional Requirements ✅
9. ✅ **Scoreboard** - Public player ranking by wins and points
10. ✅ **Bot AI** - Play against computer with Easy/Medium/Hard difficulty
11. ✅ **Reconnection** - Resume games after disconnection
12. ✅ **Admin Dashboard** - Real-time server statistics (planned)
13. ✅ **Cloud Deployment Ready** - Docker configuration included

### Extra Features 💎
- Game history and replay system
- Beautiful, responsive UI with animations
- Toast notifications for real-time updates
- Win streak tracking
- ELO ranking system
- Session management
- Rate limiting protection
- Comprehensive API documentation

## 🏗️ Architecture

```
┌─────────────┐         WebSocket/REST API          ┌─────────────┐
│   Frontend  │◄──────────────────────────────────►│   Backend   │
│  (HTML/JS)  │         Socket.IO + HTTPS          │ (FastAPI)   │
└─────────────┘                                     └──────┬──────┘
                                                           │
                                                    ┌──────▼──────┐
                                                    │   Database  │
                                                    │  (SQLite)   │
                                                    └─────────────┘
```

### Backend Components
- **FastAPI** - REST API server
- **Socket.IO** - Real-time WebSocket communication
- **SQLAlchemy** - ORM for database operations
- **Game Manager** - Event-bus pattern for managing multiple games
- **Bot AI** - Minimax algorithm with alpha-beta pruning

### Frontend Components
- Vanilla JavaScript (no frameworks)
- Socket.IO Client
- Responsive CSS with animations

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- pip
- Modern web browser

### Installation

1. **Clone the repository**
```bash
cd "d:\GitHub\computer networks 2\Nueva carpeta (2)"
```

2. **Install backend dependencies**
```bash
cd backend
pip install -r requirements.txt
```

3. **Configure environment**
```bash
# Copy example env file
cp .env.example .env

# Edit .env and set your configuration
# At minimum, set a secure SECRET_KEY
```

4. **Run the server**
```bash
python run.py
```

The server will start on `http://localhost:8000`

5. **Open the frontend**
```bash
cd ../frontend
# Open public/index.html in your web browser
# Or use a simple HTTP server:
python -m http.server 8080
```

Then navigate to `http://localhost:8080/public/index.html`

## 📖 Usage

### Register/Login
1. Open the frontend in your browser
2. Register a new account or login with existing credentials
3. You'll be redirected to the lobby

### Play Against Bot
1. In the lobby, click one of the bot difficulty buttons:
   - **Easy** - Random moves
   - **Medium** - Minimax with limited depth
   - **Hard** - Full Minimax (unbeatable)

### Play Against Human
1. Wait for another player to come online
2. Click "Invite" next to their name
3. They will receive the invitation and can accept/reject
4. Once accepted, the game begins!

### During Game
- Click on an empty cell to make your move when it's your turn
- The board updates in real-time for both players
- Click "Forfeit Game" if you want to surrender

## 🧪 Testing

### Manual Testing
1. Open two browser windows/tabs
2. Register/login with different accounts in each
3. Invite each other and play a game
4. Test all features: moves, forfeit, etc.

### Network Monitoring with Wireshark
1. Start Wireshark and capture on loopback interface
2. Filter: `tcp.port == 8000`
3. Play a game and observe:
   - WebSocket handshake
   - Game messages (JSON payloads)
   - Authentication tokens

## 📁 Project Structure

```
capstone-tictactoe/
├── backend/
│   ├── app/
│   │   ├── auth/           # Authentication logic
│   │   ├── game/           # Game logic and bot AI
│   │   ├── utils/          # Utilities (logging, validators)
│   │   ├── websocket/      # Socket.IO events
│   │   ├── config.py       # Configuration
│   │   ├── database.py     # Database setup
│   │   ├── models.py       # SQLAlchemy models
│   │   └── server.py       # Main server
│   ├── requirements.txt
│   └── run.py
├── frontend/
│   ├── public/             # HTML pages
│   ├── css/                # Stylesheets
│   └── js/                 # JavaScript
├── docs/                   # Documentation
├── CLAUDE.md              # AI assistant guidance
└── README.md              # This file
```

## 🔐 Security Features

- **Password Hashing**: bcrypt with cost factor 12
- **JWT Authentication**: Secure token-based auth
- **Session Management**: Secure session handling for reconnection
- **Input Validation**: Server-side validation of all inputs
- **SQL Injection Prevention**: SQLAlchemy ORM
- **Rate Limiting**: Protection against spam/DDoS
- **CORS Configuration**: Proper cross-origin setup

## 🎮 Game Logic

### Tic-Tac-Toe Rules
- 3x3 grid
- Players take turns placing X or O
- First to get 3 in a row (horizontal, vertical, or diagonal) wins
- If all 9 cells are filled with no winner, it's a draw

### Bot AI - Minimax Algorithm
The bot uses the Minimax algorithm:
- **Easy**: Random valid moves
- **Medium**: Minimax with depth limit (some mistakes)
- **Hard**: Full Minimax with alpha-beta pruning (optimal play, unbeatable)

## 📊 Database Schema

### Main Tables
- `users` - User accounts
- `games` - Game sessions
- `moves` - Individual moves (for replay)
- `user_stats` - Player statistics
- `invitations` - Game invitations
- `sessions` - User sessions
- `server_logs` - Event logs

See [models.py](backend/app/models.py) for complete schema.

## 🌐 API Endpoints

### REST API
- `POST /api/register` - Register new user
- `POST /api/login` - Login user
- `GET /api/users/me` - Get current user info
- `GET /api/stats` - Get user statistics
- `GET /api/stats/leaderboard` - Get top players
- `GET /api/games/history` - Get game history

### Socket.IO Events
- `authenticate` - Authenticate with JWT token
- `invite_player` - Send game invitation
- `accept_invitation` - Accept invitation
- `reject_invitation` - Reject invitation
- `play_vs_bot` - Start bot game
- `make_move` - Make a move
- `forfeit_game` - Forfeit current game

See [WEBSOCKET_EVENTS.md](docs/WEBSOCKET_EVENTS.md) for complete documentation.

## 🐳 Docker Deployment

```bash
# Build and run with Docker Compose
docker-compose up -d

# Stop
docker-compose down
```

The application will be available at:
- Backend: http://localhost:8000
- Frontend: http://localhost:8080

## 📝 Logging

Logs are written to:
- **Console**: Real-time log output
- **File**: `logs/server.log`
- **Database**: `server_logs` table

Log levels: INFO, WARNING, ERROR, CRITICAL

## 🔧 Configuration

Edit `.env` file to configure:
- Server host and port
- Database URL
- JWT secret key
- CORS origins
- Log level
- And more...

See `.env.example` for all options.

## 🤝 Contributing

This is a capstone project for academic purposes.

## 📄 License

Educational use only - Jala University Computer Networks 2 Course (2025)

## 👨‍💻 Author

Developed as Capstone Project for Computer Networks 2 (CSNT-245)
Jala University - 2025

## 🙏 Acknowledgments

- Course instructor and practitioners
- Jala University
- Socket.IO and FastAPI communities

## 📞 Support

For issues or questions about the project:
1. Check the documentation in the `docs/` folder
2. Review the code comments
3. Contact your course practitioner

---

**Note**: This project demonstrates understanding of:
- Client-server architecture
- Network protocols (TCP/IP, WebSocket)
- Real-time communication
- Security in networked applications
- Event-driven architecture
- Database design and ORM
- API design (REST and WebSocket)

Built with ❤️ for learning computer networking concepts.
