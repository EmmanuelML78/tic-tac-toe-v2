# 📚 DOCUMENTACIÓN COMPLETA DE ENDPOINTS - TIC-TAC-TOE API

## 🌐 Información General

- **Base URL:** `http://localhost:8000`
- **Versión:** 1.0.0
- **Framework:** FastAPI + Socket.IO
- **Autenticación:** JWT Bearer Token

---

## 🔓 ENDPOINTS PÚBLICOS (Sin Autenticación)

### 1. Health Check

```
GET /health
```

**Descripción:** Verifica el estado del servidor  
**Respuesta:**

```json
{
  "status": "healthy",
  "timestamp": "2025-10-17T02:07:03.056488"
}
```

**Status Code:** 200 ✅

---

### 2. Root Endpoint

```
GET /
```

**Descripción:** Información básica de la API  
**Respuesta:**

```json
{
  "message": "Tic-Tac-Toe Multiplayer API",
  "version": "1.0.0",
  "status": "online"
}
```

**Status Code:** 200 ✅

---

### 3. Registrar Usuario

```
POST /api/register
```

**Descripción:** Crea una nueva cuenta de usuario  
**Body:**

```json
{
  "username": "player1",
  "password": "SecurePass123!",
  "email": "player1@example.com" // Opcional
}
```

**Validaciones:**

- Username: 3-20 caracteres, alfanumérico + guiones bajos
- Password: Mínimo 8 caracteres, debe incluir mayúsculas, minúsculas y números

**Respuesta Exitosa:**

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6...",
  "token_type": "bearer",
  "user_id": 1,
  "username": "player1"
}
```

**Status Code:** 200 ✅

**Errores:**

- 400: Username ya existe
- 400: Validación de username/password falló

---

### 4. Login

```
POST /api/login
```

**Descripción:** Autentica un usuario existente  
**Body:**

```json
{
  "username": "player1",
  "password": "SecurePass123!"
}
```

**Respuesta Exitosa:**

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6...",
  "token_type": "bearer",
  "user_id": 1,
  "username": "player1"
}
```

**Status Code:** 200 ✅

**Errores:**

- 401: Credenciales incorrectas

---

### 5. Leaderboard

```
GET /api/stats/leaderboard?limit=10
```

**Descripción:** Obtiene la tabla de líderes  
**Query Params:**

- `limit` (opcional): Número de jugadores a mostrar (default: 10)

**Respuesta:**

```json
[
  {
    "rank": 1,
    "username": "pro_player",
    "wins": 50,
    "losses": 10,
    "draws": 5,
    "win_rate": 76.9,
    "ranking_points": 1500,
    "best_streak": 10
  },
  ...
]
```

**Status Code:** 200 ✅

---

## 🔐 ENDPOINTS PROTEGIDOS (Requieren Autenticación)

**Header requerido:**

```
Authorization: Bearer {access_token}
```

---

### 6. Obtener Usuario Actual

```
GET /api/users/me
```

**Descripción:** Obtiene información del usuario autenticado  
**Respuesta:**

```json
{
  "id": 1,
  "username": "player1",
  "email": "player1@example.com",
  "is_online": true,
  "created_at": "2025-10-17T02:06:55.206024"
}
```

**Status Code:** 200 ✅

**Errores:**

- 401: Token inválido o expirado
- 403: Sin autorización

---

### 7. Estadísticas del Usuario

```
GET /api/stats
```

**Descripción:** Obtiene estadísticas detalladas del usuario  
**Respuesta:**

```json
{
  "total_games": 65,
  "wins": 50,
  "losses": 10,
  "draws": 5,
  "win_rate": 76.9,
  "ranking_points": 1500,
  "current_streak": 3,
  "best_streak": 10
}
```

**Status Code:** 200 ✅

---

### 8. Historial de Juegos

```
GET /api/games/history?limit=20
```

**Descripción:** Obtiene el historial de partidas del usuario  
**Query Params:**

- `limit` (opcional): Número de juegos a mostrar (default: 20)

**Respuesta:**

```json
[
  {
    "game_id": 123,
    "opponent": "player2",
    "result": "win",
    "is_bot_game": false,
    "finished_at": "2025-10-17T01:30:00.000000"
  },
  {
    "game_id": 122,
    "opponent": "Bot",
    "result": "loss",
    "is_bot_game": true,
    "finished_at": "2025-10-17T01:15:00.000000"
  }
]
```

**Status Code:** 200 ✅

---

## 🔌 WEBSOCKET EVENTS

**Conexión:** `ws://localhost:8000/socket.io/`

### Flujo de Autenticación

1. **Conectar al servidor**

```javascript
const socket = io("http://localhost:8000");
```

2. **Autenticar con JWT**

```javascript
socket.emit("authenticate", {
  token: "eyJhbGciOiJIUzI1NiIsInR5cCI6...",
});
```

3. **Recibir confirmación**

```javascript
socket.on("authenticated", (data) => {
  console.log(data);
  // { user_id: 1, username: 'player1' }
});
```

---

### Eventos del Cliente → Servidor

#### 1. authenticate

```javascript
socket.emit("authenticate", {
  token: "jwt_token_here",
});
```

**Respuesta:** `authenticated` o `error`

---

#### 2. play_vs_bot

```javascript
socket.emit("play_vs_bot", {
  difficulty: "medium", // 'easy', 'medium', 'hard'
});
```

**Respuesta:** `game_started`

---

#### 3. invite_player

```javascript
socket.emit("invite_player", {
  target_user_id: 2,
});
```

**Respuesta:** `invitation_sent`  
**Al destinatario:** `invitation_received`

---

#### 4. accept_invitation

```javascript
socket.emit("accept_invitation", {
  invitation_id: 1,
});
```

**Respuesta:** `game_started` (a ambos jugadores)

---

#### 5. reject_invitation

```javascript
socket.emit("reject_invitation", {
  invitation_id: 1,
});
```

**Al remitente:** `invitation_rejected`

---

#### 6. make_move

```javascript
socket.emit("make_move", {
  game_id: 1,
  position: 4, // 0-8, posición en el tablero
});
```

**Respuesta:** `move_made` (a ambos jugadores)

**Board positions:**

```
0 | 1 | 2
---------
3 | 4 | 5
---------
6 | 7 | 8
```

---

#### 7. forfeit_game

```javascript
socket.emit("forfeit_game", {
  game_id: 1,
});
```

**Respuesta:** `game_forfeited` (a ambos jugadores)

---

### Eventos del Servidor → Cliente

#### authenticated

```json
{
  "user_id": 1,
  "username": "player1"
}
```

---

#### online_users

```json
{
  "users": [
    {
      "id": 1,
      "username": "player1",
      "in_game": false
    },
    {
      "id": 2,
      "username": "player2",
      "in_game": true
    }
  ]
}
```

---

#### invitation_received

```json
{
  "invitation_id": 1,
  "from_user_id": 2,
  "from_username": "player2"
}
```

---

#### invitation_sent

```json
{
  "invitation_id": 1,
  "to_username": "player2"
}
```

---

#### invitation_rejected

```json
{
  "invitation_id": 1
}
```

---

#### game_started

```json
{
  "game_id": 1,
  "player1": {
    "id": 1,
    "username": "player1",
    "symbol": "X"
  },
  "player2": {
    "id": 2,
    "username": "player2",
    "symbol": "O"
  },
  "board": [null, null, null, null, null, null, null, null, null],
  "current_turn": 1,
  "is_bot_game": false,
  "bot_difficulty": null
}
```

---

#### move_made

```json
{
  "game_id": 1,
  "position": 4,
  "player_id": 1,
  "board": [null, null, null, null, "X", null, null, null, null],
  "current_turn": 2,
  "game_over": false
}
```

**Cuando termina el juego:**

```json
{
  "game_id": 1,
  "position": 6,
  "player_id": 1,
  "board": ["X", "O", "X", "O", "X", null, "X", null, null],
  "current_turn": null,
  "game_over": true,
  "result": "win",
  "winner_id": 1,
  "winning_line": [0, 4, 8]
}
```

---

#### game_forfeited

```json
{
  "game_id": 1,
  "forfeited_by": 2,
  "winner_id": 1,
  "result": "abandoned"
}
```

---

#### error

```json
{
  "message": "Error description"
}
```

---

## 🎮 EJEMPLOS DE USO

### Ejemplo 1: Registro y Login

```javascript
// Registro
const response = await fetch("http://localhost:8000/api/register", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({
    username: "newplayer",
    password: "SecurePass123!",
    email: "newplayer@example.com",
  }),
});

const data = await response.json();
const token = data.access_token;

// Usar el token para endpoints protegidos
const userInfo = await fetch("http://localhost:8000/api/users/me", {
  headers: { Authorization: `Bearer ${token}` },
});
```

---

### Ejemplo 2: Juego contra Bot

```javascript
const socket = io("http://localhost:8000");

// Autenticar
socket.emit("authenticate", { token: yourJWTToken });

socket.on("authenticated", () => {
  // Iniciar juego contra bot
  socket.emit("play_vs_bot", { difficulty: "hard" });
});

socket.on("game_started", (data) => {
  console.log("Game started:", data.game_id);
  // Hacer primer movimiento
  socket.emit("make_move", {
    game_id: data.game_id,
    position: 4, // Centro del tablero
  });
});

socket.on("move_made", (data) => {
  console.log("Move made at position:", data.position);
  console.log("Board state:", data.board);

  if (data.game_over) {
    console.log("Game over! Result:", data.result);
  }
});
```

---

### Ejemplo 3: Juego PvP

```javascript
// Usuario 1: Enviar invitación
socket.emit("invite_player", { target_user_id: 2 });

socket.on("invitation_sent", (data) => {
  console.log("Invitation sent to:", data.to_username);
});

// Usuario 2: Recibir y aceptar invitación
socket.on("invitation_received", (data) => {
  console.log("Invitation from:", data.from_username);
  socket.emit("accept_invitation", { invitation_id: data.invitation_id });
});

// Ambos usuarios reciben game_started
socket.on("game_started", (data) => {
  console.log("PvP game started!");
  console.log("You are:", data.player1.id === yourUserId ? "X" : "O");
});
```

---

## 🔧 CONFIGURACIÓN

### Variables de Entorno

```env
HOST=0.0.0.0
PORT=8000
DEBUG=False
DATABASE_URL=sqlite+aiosqlite:///./tictactoe.db
SECRET_KEY=your-secret-key-here
CORS_ORIGINS=http://localhost:8080,http://localhost:3000
ACCESS_TOKEN_EXPIRE_MINUTES=60
```

---

## 📊 CÓDIGOS DE ESTADO HTTP

| Código | Significado           |
| ------ | --------------------- |
| 200    | ✅ Éxito              |
| 400    | ❌ Solicitud inválida |
| 401    | ❌ No autenticado     |
| 403    | ❌ Sin permisos       |
| 404    | ❌ No encontrado      |
| 500    | ❌ Error del servidor |

---

## 🎯 VALIDACIONES

### Username

- Longitud: 3-20 caracteres
- Caracteres permitidos: letras, números, guiones bajos
- No puede estar vacío
- Debe ser único

### Password

- Longitud mínima: 8 caracteres
- Debe contener: mayúsculas, minúsculas, números
- Se recomienda incluir caracteres especiales

### Movimientos en el Tablero

- Posición: 0-8 (entero)
- La posición debe estar vacía
- Debe ser el turno del jugador
- El juego no debe haber terminado

---

_Documentación generada automáticamente - Última actualización: 2025-10-17_
