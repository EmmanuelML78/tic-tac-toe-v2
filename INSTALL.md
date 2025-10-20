# Installation Guide

## Quick Start (Development)

### Option 1: Manual Installation

#### Step 1: Install Python Dependencies
```bash
cd backend
pip install -r requirements.txt
```

#### Step 2: Configure Environment
```bash
# The .env file is already created with default values
# You can edit it if needed, but it works out of the box
```

#### Step 3: Run the Backend Server
```bash
python run.py
```

The server will start on http://localhost:8000

#### Step 4: Open the Frontend
Open a new terminal:
```bash
cd frontend
python -m http.server 8080
```

Or simply open `frontend/public/index.html` in your browser.

Frontend will be available at: http://localhost:8080/public/index.html

### Option 2: Docker (Recommended for Production)

#### Prerequisites
- Docker
- Docker Compose

#### Steps
```bash
# From project root directory
docker-compose up -d

# Check logs
docker-compose logs -f

# Stop
docker-compose down
```

Access the application:
- Backend API: http://localhost:8000
- Frontend: http://localhost:8080/public/index.html
- API Docs: http://localhost:8000/docs

## Testing the Installation

### 1. Test Backend
Open your browser and navigate to:
- http://localhost:8000 - Should show API info
- http://localhost:8000/health - Should return {"status": "healthy"}
- http://localhost:8000/docs - Interactive API documentation

### 2. Test Frontend
1. Open http://localhost:8080/public/index.html
2. Register a new account
3. You should be redirected to the lobby

### 3. Test Complete Flow
1. Open two browser windows (or use private/incognito mode)
2. Register two different accounts
3. Invite each other to a game
4. Play a complete game
5. Check the leaderboard

## Common Issues

### Backend won't start
**Error**: `ModuleNotFoundError: No module named 'fastapi'`
**Solution**: Make sure you installed dependencies: `pip install -r requirements.txt`

### Frontend can't connect to backend
**Error**: Connection refused or CORS error
**Solution**:
1. Make sure backend is running on port 8000
2. Check CORS_ORIGINS in .env includes your frontend URL
3. Clear browser cache

### Database errors
**Error**: Database file locked or permission error
**Solution**:
1. Make sure no other instance of the server is running
2. Delete `tictactoe.db` file and restart (will reset all data)
3. Check file permissions

### Port already in use
**Error**: `Address already in use`
**Solution**:
1. Change the PORT in .env file
2. Or kill the process using the port:
   - Windows: `netstat -ano | findstr :8000` then `taskkill /PID <pid> /F`
   - Linux/Mac: `lsof -ti:8000 | xargs kill -9`

## Development Setup

### Install Dev Dependencies
```bash
cd backend
pip install -r requirements-dev.txt
```

### Run Tests
```bash
cd backend
pytest
```

### Code Quality
```bash
# Format code
black app/

# Lint
flake8 app/

# Type check
mypy app/
```

## Network Monitoring with Wireshark

1. **Start Wireshark** and select your network interface (usually "Loopback" for local testing)

2. **Apply filter**: `tcp.port == 8000`

3. **Start the application** and play a game

4. **Observe**:
   - HTTP handshake for WebSocket upgrade
   - WebSocket frames with game messages
   - JSON payloads in the data

5. **Verify Security**:
   - Check that passwords are not sent in plain text
   - Verify JWT tokens are being used
   - Inspect message encryption (if SSL/TLS enabled)

## Production Deployment

### Security Checklist
- [ ] Change SECRET_KEY in .env to a secure random string
- [ ] Set DEBUG=False
- [ ] Configure proper CORS_ORIGINS
- [ ] Enable SSL/TLS
- [ ] Use PostgreSQL instead of SQLite for better performance
- [ ] Set up proper logging and monitoring
- [ ] Configure firewall rules
- [ ] Regular backups

### Cloud Deployment Options

#### Heroku
```bash
# Install Heroku CLI
heroku create tictactoe-multiplayer
heroku config:set SECRET_KEY=your-secret-key
git push heroku main
```

#### AWS EC2
1. Launch an EC2 instance (Ubuntu)
2. Install Docker and Docker Compose
3. Clone repository
4. Run `docker-compose up -d`
5. Configure security groups for ports 8000, 8080

#### Digital Ocean
1. Create a Droplet
2. Install Docker
3. Clone and run with docker-compose

## Next Steps

1. Read the [README.md](README.md) for full documentation
2. Review the [API Documentation](http://localhost:8000/docs) when server is running
3. Check [CLAUDE.md](CLAUDE.md) for architecture details
4. Try playing against the bot at different difficulty levels
5. Explore the code in `backend/app/` and `frontend/js/`

## Support

If you encounter issues:
1. Check this installation guide
2. Review error logs in `backend/logs/server.log`
3. Check browser console for frontend errors
4. Consult your course practitioner

---

Happy gaming! 🎮
