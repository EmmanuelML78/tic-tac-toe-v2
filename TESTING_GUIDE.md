# 🧪 Guía de Pruebas Frontend-Backend

## Estado del Sistema

### Contenedores Docker

- ✅ **Backend**: Running en http://localhost:8000
- ✅ **Frontend**: Running en http://localhost:8080

## Páginas de Prueba

### 1. Página de Pruebas Automatizadas

**URL**: http://localhost:8080/test_frontend_backend.html

Esta página incluye pruebas automatizadas para:

- ✅ Health Check del Backend
- ✅ Registro de Usuario
- ✅ Login de Usuario
- ✅ Obtener Perfil de Usuario
- ✅ Conexión WebSocket
- ✅ Crear Juego
- ✅ Listar Juegos Activos
- ✅ Ejecutar Todas las Pruebas

**Instrucciones**:

1. Abre http://localhost:8080/test_frontend_backend.html
2. Haz clic en "Run All Tests" para ejecutar todas las pruebas automáticamente
3. O ejecuta pruebas individuales haciendo clic en cada botón

### 2. Página Principal (Login/Register)

**URL**: http://localhost:8080/public/index.html

**Funcionalidades a probar**:

- ✅ Registro de nuevo usuario
  - Ingresa un username (3-20 caracteres)
  - Ingresa un password (mínimo 6 caracteres)
  - Confirma el password
  - Haz clic en "Register"
- ✅ Login de usuario existente
  - Ingresa username y password
  - Haz clic en "Login"
  - Deberías ser redirigido a lobby.html

### 3. Lobby (Lista de Juegos)

**URL**: http://localhost:8080/public/lobby.html

**Funcionalidades a probar**:

- ✅ Ver lista de juegos activos
- ✅ Crear nuevo juego (PvP o vs Bot)
- ✅ Unirse a un juego existente
- ✅ Ver estadísticas del usuario
- ✅ Logout

### 4. Juego (Tablero de Tic-Tac-Toe)

**URL**: http://localhost:8080/public/game.html

**Funcionalidades a probar**:

- ✅ Tablero de juego funcional
- ✅ Hacer movimientos
- ✅ WebSocket en tiempo real para juegos PvP
- ✅ IA del bot para juegos vs Bot
- ✅ Detección de victoria/empate
- ✅ Abandonar juego

## Pruebas Manuales por Componente

### 1. Autenticación

```bash
# Verificar que el backend esté corriendo
curl http://localhost:8000/health

# Registrar un usuario
curl -X POST http://localhost:8000/api/register \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","password":"password123"}'

# Login
curl -X POST http://localhost:8000/api/login \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","password":"password123"}'
```

### 2. API de Juegos

```bash
# Listar juegos (reemplaza TOKEN con el token obtenido del login)
curl http://localhost:8000/api/games/list \
  -H "Authorization: Bearer TOKEN"

# Crear juego
curl -X POST http://localhost:8000/api/games/create \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"game_type":"pvp","is_private":false}'
```

### 3. Perfil de Usuario

```bash
# Obtener perfil
curl http://localhost:8000/api/profile \
  -H "Authorization: Bearer TOKEN"
```

## Verificar Logs

### Ver logs del Backend

```bash
docker compose logs backend -f
```

### Ver logs del Frontend

```bash
docker compose logs frontend -f
```

### Ver logs de ambos

```bash
docker compose logs -f
```

## Escenarios de Prueba Completos

### Escenario 1: Juego PvP Completo

1. Abre dos ventanas del navegador
2. En ambas ventanas, ve a http://localhost:8080/public/index.html
3. Registra dos usuarios diferentes (user1 y user2)
4. Con user1, crea un juego PvP público
5. Con user2, únete al juego
6. Juega alternando turnos en ambas ventanas
7. Verifica que los movimientos se sincronicen en tiempo real
8. Completa el juego hasta victoria o empate

### Escenario 2: Juego vs Bot

1. Inicia sesión en http://localhost:8080/public/index.html
2. Ve al lobby
3. Crea un juego vs Bot (selecciona dificultad)
4. Haz un movimiento
5. Verifica que el bot responda automáticamente
6. Completa el juego

### Escenario 3: Prueba de Persistencia

1. Crea un usuario y un juego
2. Cierra el navegador
3. Vuelve a abrir y hacer login
4. Verifica que tu juego siga activo (si no ha expirado)

## Verificar Conectividad Frontend-Backend

### Usando DevTools del Navegador

1. **Abre las DevTools** (F12)
2. **Ve a la pestaña Network**
3. **Recarga la página**
4. **Verifica**:

   - ✅ Llamadas a http://localhost:8000/health (200 OK)
   - ✅ Llamadas a http://localhost:8000/api/\* (200 OK)
   - ✅ No hay errores CORS
   - ✅ WebSocket connection (ws://localhost:8000/socket.io/)

5. **Ve a la pestaña Console**
6. **Verifica**:
   - ✅ No hay errores de JavaScript
   - ✅ No hay errores de conexión
   - ✅ Mensajes de WebSocket (si aplica)

## Problemas Comunes y Soluciones

### Error: CORS

**Síntoma**: Error en la consola sobre CORS policy
**Solución**: El backend ya está configurado con CORS. Verifica que uses http://localhost:8080

### Error: Connection Refused

**Síntoma**: No se puede conectar al backend
**Solución**:

```bash
docker compose ps  # Verificar que el backend esté running
docker compose logs backend  # Ver logs de errores
```

### Error: 401 Unauthorized

**Síntoma**: Respuestas 401 en llamadas API
**Solución**: Verifica que el token esté almacenado correctamente en localStorage

### WebSocket no conecta

**Síntoma**: No hay sincronización en tiempo real
**Solución**:

1. Verifica que Socket.IO esté cargado
2. Verifica el token de autenticación
3. Revisa la consola del navegador para errores

## Estado de las Pruebas

### ✅ Completadas

- [x] Backend Health Check
- [x] Configuración CORS
- [x] Contenedores Docker funcionando
- [x] Página de pruebas automatizadas creada

### 🔄 Para Probar

- [ ] Registro de usuario desde UI
- [ ] Login desde UI
- [ ] Creación de juego PvP
- [ ] Juego completo PvP
- [ ] Juego vs Bot
- [ ] WebSocket en tiempo real
- [ ] Persistencia de datos

## Comandos Útiles

```bash
# Ver estado de contenedores
docker compose ps

# Reiniciar todo
docker compose restart

# Ver logs en tiempo real
docker compose logs -f

# Reconstruir y reiniciar
docker compose down
docker compose up -d --build

# Entrar al contenedor del backend
docker exec -it tictactoe-backend /bin/bash

# Entrar al contenedor del frontend
docker exec -it tictactoe-frontend /bin/sh
```

## Siguiente Paso

**Recomendación**: Abre http://localhost:8080/test_frontend_backend.html y haz clic en "Run All Tests" para verificar toda la conectividad automáticamente.
