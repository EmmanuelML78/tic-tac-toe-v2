# 🔧 Guía de Depuración del Token

## Problema Solucionado ✅

Se ha corregido el manejo del token en el frontend con las siguientes mejoras:

### 1. **Orden de carga de scripts en `lobby.html`**

- ✅ Los scripts ahora se cargan en el orden correcto:
  1.  Socket.IO Client
  2.  `config.js` (configuración y Storage)
  3.  `notifications.js` (funciones de utilidad)
  4.  `lobby.js` (funcionalidad principal)

### 2. **Validación mejorada en `lobby.js`**

- ✅ Verificación exhaustiva de autenticación al cargar la página
- ✅ Validación de datos del usuario (userId y username)
- ✅ Mensajes de error claros y redirección automática al login
- ✅ Logs de depuración en consola

### 3. **Manejo mejorado de Socket.IO**

- ✅ Token enviado en el handshake inicial (`auth` y `query`)
- ✅ Evento `auth_error` para manejar fallos de autenticación
- ✅ Logs detallados de conexión y autenticación

### 4. **Mejoras en llamadas API**

- ✅ Manejo de errores mejorado en `loadLeaderboard()`
- ✅ Manejo de errores mejorado en `loadUserStats()`
- ✅ Validación de respuestas HTTP
- ✅ Mensajes de error amigables al usuario

## Cómo Probar 🧪

### Opción 1: Página de Prueba de Token

1. Abre el archivo `frontend/test_token.html` en tu navegador
2. Usa los botones para:
   - ✅ Verificar el estado del storage
   - ✅ Probar la configuración
   - ✅ Hacer login de prueba
   - ✅ Probar llamadas API con el token
   - ✅ Limpiar el storage

### Opción 2: Flujo Normal

1. **Inicia los servicios:**

   ```powershell
   # Backend
   cd backend
   docker compose up -d

   # O usa el script
   .\start_backend.bat
   ```

2. **Abre el frontend:**

   - Navega a `frontend/public/index.html`
   - Regístrate o inicia sesión
   - Deberías ser redirigido a `lobby.html`

3. **Verifica en la consola del navegador (F12):**
   ```
   🔍 Lobby Debug Info:
   - Token exists: true
   - Token value: eyJ0eXAiOiJKV1QiLCJhbGc...
   - Is authenticated: true
   - User info: {userId: "1", username: "testuser"}
   ✓ Authentication check passed
   🔌 Initializing socket connection...
   - Socket URL: http://localhost:8000
   - Token available: true
   ✓ Connected to server, socket ID: xyz123
   📤 Sending authentication...
   ✓ Authenticated successfully: {...}
   📊 Loading leaderboard...
   ✓ Leaderboard loaded: 5 players
   📈 Loading user stats...
   ✓ User stats loaded: {...}
   ```

## Verificaciones de Depuración 🔍

### 1. Verificar que el token se guarda correctamente

Abre la consola del navegador después de hacer login:

```javascript
// Verificar token
console.log("Token:", localStorage.getItem("tictactoe_token"));

// Verificar userId
console.log("User ID:", localStorage.getItem("tictactoe_user_id"));

// Verificar username
console.log("Username:", localStorage.getItem("tictactoe_username"));

// Usar las funciones del Storage
console.log("Storage.getToken():", Storage.getToken());
console.log("Storage.getUserInfo():", Storage.getUserInfo());
console.log("Storage.isAuthenticated():", Storage.isAuthenticated());
```

### 2. Verificar la conexión del Socket

```javascript
// En lobby.html, abre la consola
console.log("Socket connected:", socket?.connected);
console.log("Socket ID:", socket?.id);
```

### 3. Verificar llamadas API

```javascript
// Probar manualmente una llamada API
const token = Storage.getToken();
fetch("http://localhost:8000/api/stats", {
  headers: {
    Authorization: `Bearer ${token}`,
  },
})
  .then((r) => r.json())
  .then((data) => console.log("Stats:", data))
  .catch((err) => console.error("Error:", err));
```

## Problemas Comunes y Soluciones 🛠️

### Problema: "Session expired or not logged in"

**Causa:** No hay token en localStorage

**Solución:**

1. Asegúrate de hacer login correctamente
2. Verifica que el backend esté corriendo (`docker compose up -d`)
3. Limpia el localStorage: `Storage.clearAll()`
4. Vuelve a hacer login

### Problema: "Invalid session data"

**Causa:** Token existe pero falta userId o username

**Solución:**

1. Limpia el storage: `Storage.clearAll()`
2. Vuelve a hacer login
3. Verifica que `login.js` y `register.js` estén guardando correctamente:
   ```javascript
   Storage.setToken(data.access_token);
   Storage.setUserInfo(data.user_id, data.username);
   ```

### Problema: "Authentication failed" en Socket.IO

**Causa:** Token inválido o expirado

**Solución:**

1. Verifica que el backend acepte el token:
   ```powershell
   docker compose logs backend
   ```
2. Cierra sesión y vuelve a iniciar sesión
3. Verifica que el backend esté configurado correctamente

### Problema: No se carga el leaderboard o stats

**Causa:** Error en la llamada API o token inválido

**Solución:**

1. Abre la consola (F12) y busca errores
2. Verifica la pestaña "Network" para ver las respuestas HTTP
3. Confirma que el header Authorization se está enviando:
   ```
   Authorization: Bearer eyJ0eXAiOiJKV1Qi...
   ```

## Archivos Modificados 📝

1. ✅ `frontend/public/lobby.html` - Orden de scripts corregido
2. ✅ `frontend/js/lobby/lobby.js` - Validación y logs mejorados
3. ✅ `frontend/test_token.html` - Nueva página de prueba (NUEVO)
4. ✅ `DEBUG_TOKEN.md` - Esta guía (NUEVO)

## Próximos Pasos 🚀

Si todavía tienes problemas:

1. Usa `test_token.html` para diagnosticar
2. Revisa los logs del backend: `docker compose logs -f backend`
3. Verifica la consola del navegador (F12)
4. Asegúrate de que el backend esté corriendo en `http://localhost:8000`
5. Prueba con un usuario nuevo para descartar problemas de sesión

---

**Última actualización:** Octubre 16, 2025
