# Frontend Structure Update

## Changes Made:

### 1. **New Index Page (index.html)**
- Created a welcome page with "Computer Networks II Capstone" title
- Added project description and features
- Included developers section: Oscar Barajas Cabrera & Emmanuel Medina
- Added tools & technologies section showing Frontend and Backend tools
- Clean, modern design with navigation buttons to Login and Register

### 2. **Separate Login Page (login.html)**
- Moved login functionality to dedicated page
- Clean form with username and password fields
- Navigation links to register and back to home
- Maintains all original login functionality

### 3. **Separate Register Page (register.html)**  
- Moved registration functionality to dedicated page
- Complete registration form with validation
- Navigation links to login and back to home
- Maintains all original registration functionality

### 4. **Updated Styling (auth.css)**
- Enhanced form styling with better focus states
- Improved navigation links styling
- Better responsive design
- Consistent visual hierarchy

## Technologies Listed:

### Frontend:
- HTML5 & CSS3
- JavaScript (ES6+)
- WebSocket Client
- Docker
- Nginx

### Backend:
- Python 3.11
- Flask Framework
- WebSocket Server
- SQLite Database
- Docker

## Navigation Flow:
1. **index.html** → Main landing page with project info
2. **login.html** → User authentication  
3. **register.html** → New user registration
4. **lobby.html** → Game lobby (after successful auth)
5. **game.html** → Game interface

All original functionality is preserved with improved user experience and navigation.