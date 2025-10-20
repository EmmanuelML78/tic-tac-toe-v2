# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Capstone Project: Network Multiplayer Game ("March of the Legion")**

This is a Computer Networks 2 (CSNT-245) capstone project from Jala University. The goal is to design, develop, and implement a two-player (2P) multiplayer game application connected over a network, ensuring consistent game state synchronization for both players.

Game options include: tic-tac-toe, Connect 4, hexapawn, or other turn-based games approved by the practitioner.

## Architecture

### High-Level System Design

```
CLIENT (Socket) <---> NETWORK <---> APP SERVER
                                    - EVENT BUS
                                    - BBDD (Database)
```

**Client-Server Architecture:**
- **Clients**: Handle user registration, authentication, game creation/joining, and game UI
- **Server**: Manages user authentication, game session creation, message routing, and event processing
- **Event-Driven Architecture**: Server uses an event-bus pattern to manage action queues and turn-based gameplay
- **Database**: Persists user credentials (securely), game state, and server logs

### Key Components

1. **Client Application**
   - User registration and authentication
   - Display online users
   - Create/accept/reject game invitations
   - Game board rendering and move submission
   - Real-time game state updates

2. **Server Application**
   - User management backend
   - Game session management backend
   - Socket communication over TCP/IP
   - Optional: MQTT communication support
   - Event-bus for processing game actions
   - Server event logging (player connections, game start/end, errors)

3. **Database**
   - Secure storage of user credentials (username/password)
   - Game state persistence
   - Server event logs (desirable)

## Technology Stack

**Preferred Languages/Frameworks:**
- .NET/C# or Java (preferred - well-documented, robust libraries)
- Python or JavaScript (acceptable if well-justified)

**Required Tools:**
- Git for version control
- Wireshark for network traffic monitoring and debugging

**Communication Protocols:**
- TCP-based sockets (primary)
- MQTT (optional)
- Security protocols: TLS, SSL, SHA-64 (desirable)

## Core Requirements

### Base Requirements (Must Implement)

1. **User Registration**: Multiple users with username/password, securely persisted
2. **User Authentication**: Authenticate users without exposing credentials
3. **Online Users Display**: Show currently online users
4. **Game Creation**: Users can create games and invite online users
5. **Invitation Management**: Accept or reject game invitations
6. **Turn-Based Gameplay**: Update board state on player turns, synchronized for both players
7. **Game Results**: Display final results (winner/loser/draw) to both players
8. **Game Abandonment**: Allow players to forfeit, granting victory to opponent
9. **Server Monitoring**: Log player connections, game sessions (start/end), errors; persist to database (desirable)

### Optional Requirements (Nice-to-Have)

1. **Scoreboard**: Public player ranking by wins/draws
2. **Bot Player**: AI opponent managed by server (player vs. computer)
3. **Failure Recovery**: Reconnection to in-progress games after disconnection
4. **Server Dashboard**: Admin interface showing real-time server status (connected users, active games, connection stats, errors)
5. **Cloud Deployment**: Deploy application to cloud and test with remote users

## Development Workflow

### Phase 1: Design
- Define functional and non-functional requirements
- Design client-server architecture
- Plan security policies and message routing

### Phase 2: Implementation
- Develop server: authentication, game creation, message routing
- Implement client: registration, game creation/joining, gameplay
- Integrate security protocols

### Phase 3: Testing
- Design functional test cases
- Test all game outcome scenarios (win/lose/draw/forfeit)
- Use Wireshark to verify message integrity and confidentiality
- Optional: Perform intrusion/DDoS/MITM attack testing

### Phase 4: Documentation & Presentation
- Document network components (client, server, database, protocol, broker)
- Create network sequence diagrams and state diagrams
- Explain IPC (inter-process communication) and message payloads
- Justify library choices for network communication
- Document monitoring and debugging procedures
- Prepare final presentation demonstrating functionality and concepts

## Key Concepts

### Programming Concepts
- Object-oriented programming and design patterns
- Data serialization/deserialization
- TCP-based communication protocols (sockets, MQTT)
- Database persistence
- Exception handling

### Implementation Patterns
- Event-driven architecture
- Service-oriented implementation
- Network communication monitoring

### Security Considerations
- Identify communication vulnerabilities
- Implement encryption protocols (TLS, SSL)
- Secure password storage (hashing with SHA-64 or similar)
- Protect against common attacks (Man-in-the-Middle)

## Game State Management

The server must maintain consistent game state across both clients using:
- Event-bus pattern for action queuing
- Turn-based synchronization
- Real-time state broadcasting to connected players
- Message routing based on active game sessions

## Testing Strategy

**End-to-End Testing Required:**
- Complete game flow from registration to game completion
- All possible game outcomes (win, lose, draw, forfeit)
- Network security verification via Wireshark
- Multiple concurrent game sessions
- User disconnection/reconnection scenarios

## Evaluation Criteria

1. **Complete Functionality**: Registration, game creation, joining/inviting, gameplay
2. **Security Implementation**: Secure communication, protection against common attacks
3. **Code Quality**: Well-documented, structured, following best practices
4. **Final Presentation**: Clear demonstration and explanation of functionality and security concepts

## References

- Tic-tac-toe: https://www.crazygames.com/es/juego/tic-tac-toe
- Connect 4: https://www.crazygames.com/es/juego/4-in-a-row-connected-multiplayer-online
- Hexapawn: https://www.mrozilla.cz/lab/hexapawn/
