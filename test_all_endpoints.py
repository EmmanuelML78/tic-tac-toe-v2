"""
Script de prueba completo para todos los endpoints del backend
Prueba endpoints REST (FastAPI) y eventos WebSocket (Socket.IO)
"""
import requests
import socketio
import json
import time
from datetime import datetime
from typing import Dict, Optional
import asyncio

# Configuración
BASE_URL = "http://localhost:8000"
SOCKET_URL = "http://localhost:8000"

# Configuración adicional para debug
import warnings
warnings.filterwarnings('ignore')
import logging
logging.basicConfig(level=logging.WARNING)

# Colores para output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    END = '\033[0m'
    BOLD = '\033[1m'

def print_test(name: str):
    """Imprime el nombre del test"""
    print(f"\n{Colors.CYAN}{Colors.BOLD}{'='*60}{Colors.END}")
    print(f"{Colors.CYAN}{Colors.BOLD}TEST: {name}{Colors.END}")
    print(f"{Colors.CYAN}{Colors.BOLD}{'='*60}{Colors.END}")

def print_success(message: str):
    """Imprime mensaje de éxito"""
    print(f"{Colors.GREEN}✓ {message}{Colors.END}")

def print_error(message: str):
    """Imprime mensaje de error"""
    print(f"{Colors.RED}✗ {message}{Colors.END}")

def print_info(message: str):
    """Imprime mensaje informativo"""
    print(f"{Colors.BLUE}ℹ {message}{Colors.END}")

def print_warning(message: str):
    """Imprime mensaje de advertencia"""
    print(f"{Colors.YELLOW}⚠ {message}{Colors.END}")

# Variables globales para almacenar datos de prueba
test_data = {
    'user1': {},
    'user2': {},
    'tokens': {},
    'game_id': None,
    'invitation_id': None
}

# ============================================================================
# PRUEBAS DE ENDPOINTS REST
# ============================================================================

def test_health_check():
    """Prueba el endpoint de health check"""
    print_test("Health Check")
    
    try:
        response = requests.get(f"{BASE_URL}/health")
        assert response.status_code == 200
        data = response.json()
        
        print_info(f"Status: {data.get('status')}")
        print_info(f"Timestamp: {data.get('timestamp')}")
        
        assert data.get('status') == 'healthy'
        print_success("Health check pasado")
        return True
    except Exception as e:
        print_error(f"Health check falló: {str(e)}")
        return False

def test_root_endpoint():
    """Prueba el endpoint raíz"""
    print_test("Root Endpoint")
    
    try:
        response = requests.get(f"{BASE_URL}/")
        assert response.status_code == 200
        data = response.json()
        
        print_info(f"Message: {data.get('message')}")
        print_info(f"Version: {data.get('version')}")
        print_info(f"Status: {data.get('status')}")
        
        assert data.get('status') == 'online'
        print_success("Root endpoint pasado")
        return True
    except Exception as e:
        print_error(f"Root endpoint falló: {str(e)}")
        return False

def test_register_user1():
    """Registra el primer usuario de prueba"""
    print_test("Register User 1")
    
    try:
        username = f"testuser1_{int(time.time())}"
        password = "TestPass123!"
        
        payload = {
            "username": username,
            "password": password,
            "email": f"{username}@test.com"
        }
        
        response = requests.post(f"{BASE_URL}/api/register", json=payload)
        
        print_info(f"Status Code: {response.status_code}")
        print_info(f"Response: {response.text[:200]}")
        
        assert response.status_code == 200
        data = response.json()
        
        assert 'access_token' in data
        assert 'user_id' in data
        assert data['username'] == username
        
        # Guardar datos del usuario
        test_data['user1'] = {
            'username': username,
            'password': password,
            'user_id': data['user_id'],
            'token': data['access_token']
        }
        
        print_success(f"Usuario 1 registrado: {username} (ID: {data['user_id']})")
        print_info(f"Token: {data['access_token'][:50]}...")
        return True
    except Exception as e:
        print_error(f"Registro de usuario 1 falló: {str(e)}")
        return False

def test_register_user2():
    """Registra el segundo usuario de prueba"""
    print_test("Register User 2")
    
    try:
        username = f"testuser2_{int(time.time())}"
        password = "TestPass456!"
        
        payload = {
            "username": username,
            "password": password,
            "email": f"{username}@test.com"
        }
        
        response = requests.post(f"{BASE_URL}/api/register", json=payload)
        assert response.status_code == 200
        data = response.json()
        
        test_data['user2'] = {
            'username': username,
            'password': password,
            'user_id': data['user_id'],
            'token': data['access_token']
        }
        
        print_success(f"Usuario 2 registrado: {username} (ID: {data['user_id']})")
        return True
    except Exception as e:
        print_error(f"Registro de usuario 2 falló: {str(e)}")
        return False

def test_register_duplicate():
    """Prueba registrar un usuario duplicado (debe fallar)"""
    print_test("Register Duplicate User (Should Fail)")
    
    try:
        payload = {
            "username": test_data['user1']['username'],
            "password": "AnyPassword123!"
        }
        
        response = requests.post(f"{BASE_URL}/api/register", json=payload)
        
        # Debe fallar con 400
        assert response.status_code == 400
        data = response.json()
        
        print_info(f"Error esperado: {data.get('detail')}")
        print_success("Validación de usuario duplicado funciona correctamente")
        return True
    except Exception as e:
        print_error(f"Prueba de usuario duplicado falló: {str(e)}")
        return False

def test_login_user1():
    """Prueba login del usuario 1"""
    print_test("Login User 1")
    
    try:
        payload = {
            "username": test_data['user1']['username'],
            "password": test_data['user1']['password']
        }
        
        response = requests.post(f"{BASE_URL}/api/login", json=payload)
        assert response.status_code == 200
        data = response.json()
        
        assert 'access_token' in data
        assert data['user_id'] == test_data['user1']['user_id']
        
        # Actualizar token
        test_data['user1']['token'] = data['access_token']
        
        print_success(f"Login exitoso: {data['username']}")
        return True
    except Exception as e:
        print_error(f"Login falló: {str(e)}")
        return False

def test_login_invalid():
    """Prueba login con credenciales inválidas (debe fallar)"""
    print_test("Login with Invalid Credentials (Should Fail)")
    
    try:
        payload = {
            "username": test_data['user1']['username'],
            "password": "WrongPassword123!"
        }
        
        response = requests.post(f"{BASE_URL}/api/login", json=payload)
        
        # Debe fallar con 401
        assert response.status_code == 401
        
        print_success("Validación de credenciales incorrectas funciona correctamente")
        return True
    except Exception as e:
        print_error(f"Prueba de login inválido falló: {str(e)}")
        return False

def test_get_current_user():
    """Prueba obtener información del usuario actual"""
    print_test("Get Current User Info")
    
    try:
        headers = {
            "Authorization": f"Bearer {test_data['user1']['token']}"
        }
        
        response = requests.get(f"{BASE_URL}/api/users/me", headers=headers)
        assert response.status_code == 200
        data = response.json()
        
        print_info(f"User ID: {data.get('id')}")
        print_info(f"Username: {data.get('username')}")
        print_info(f"Email: {data.get('email')}")
        print_info(f"Is Online: {data.get('is_online')}")
        
        assert data['id'] == test_data['user1']['user_id']
        assert data['username'] == test_data['user1']['username']
        
        print_success("Información de usuario obtenida correctamente")
        return True
    except Exception as e:
        print_error(f"Get current user falló: {str(e)}")
        return False

def test_get_current_user_unauthorized():
    """Prueba obtener usuario sin token (debe fallar)"""
    print_test("Get Current User Unauthorized (Should Fail)")
    
    try:
        response = requests.get(f"{BASE_URL}/api/users/me")
        
        # Debe fallar con 401 o 403
        assert response.status_code in [401, 403]
        
        print_success("Validación de autorización funciona correctamente")
        return True
    except Exception as e:
        print_error(f"Prueba de usuario no autorizado falló: {str(e)}")
        return False

def test_get_stats():
    """Prueba obtener estadísticas del usuario"""
    print_test("Get User Stats")
    
    try:
        headers = {
            "Authorization": f"Bearer {test_data['user1']['token']}"
        }
        
        response = requests.get(f"{BASE_URL}/api/stats", headers=headers)
        assert response.status_code == 200
        data = response.json()
        
        print_info(f"Total Games: {data.get('total_games')}")
        print_info(f"Wins: {data.get('wins')}")
        print_info(f"Losses: {data.get('losses')}")
        print_info(f"Draws: {data.get('draws')}")
        print_info(f"Win Rate: {data.get('win_rate')}%")
        print_info(f"Ranking Points: {data.get('ranking_points')}")
        
        assert 'total_games' in data
        assert 'ranking_points' in data
        
        print_success("Estadísticas obtenidas correctamente")
        return True
    except Exception as e:
        print_error(f"Get stats falló: {str(e)}")
        return False

def test_get_leaderboard():
    """Prueba obtener el leaderboard"""
    print_test("Get Leaderboard")
    
    try:
        response = requests.get(f"{BASE_URL}/api/stats/leaderboard?limit=10")
        assert response.status_code == 200
        data = response.json()
        
        print_info(f"Número de jugadores en leaderboard: {len(data)}")
        
        if len(data) > 0:
            for i, player in enumerate(data[:3], 1):
                print_info(f"{i}. {player['username']} - Points: {player['ranking_points']}, Wins: {player['wins']}")
        
        print_success("Leaderboard obtenido correctamente")
        return True
    except Exception as e:
        print_error(f"Get leaderboard falló: {str(e)}")
        return False

def test_get_game_history():
    """Prueba obtener historial de juegos"""
    print_test("Get Game History")
    
    try:
        headers = {
            "Authorization": f"Bearer {test_data['user1']['token']}"
        }
        
        response = requests.get(f"{BASE_URL}/api/games/history?limit=20", headers=headers)
        assert response.status_code == 200
        data = response.json()
        
        print_info(f"Número de juegos en historial: {len(data)}")
        
        if len(data) > 0:
            for game in data[:3]:
                print_info(f"Game vs {game['opponent']}: {game['result']}")
        
        print_success("Historial de juegos obtenido correctamente")
        return True
    except Exception as e:
        print_error(f"Get game history falló: {str(e)}")
        return False

# ============================================================================
# PRUEBAS DE WEBSOCKET
# ============================================================================

class SocketIOTester:
    """Clase para manejar pruebas de Socket.IO"""
    
    def __init__(self, user_data: dict):
        self.user_data = user_data
        self.sio = socketio.Client()
        self.connected = False
        self.authenticated = False
        self.events_received = []
        self.setup_handlers()
    
    def setup_handlers(self):
        """Configura los event handlers"""
        
        @self.sio.on('connect')
        def on_connect():
            print_info(f"[{self.user_data['username']}] Connected to server")
            self.connected = True
        
        @self.sio.on('disconnect')
        def on_disconnect():
            print_info(f"[{self.user_data['username']}] Disconnected from server")
            self.connected = False
        
        @self.sio.on('authenticated')
        def on_authenticated(data):
            print_success(f"[{self.user_data['username']}] Authenticated: {data}")
            self.authenticated = True
            self.events_received.append(('authenticated', data))
        
        @self.sio.on('error')
        def on_error(data):
            print_error(f"[{self.user_data['username']}] Error: {data}")
            self.events_received.append(('error', data))
        
        @self.sio.on('online_users')
        def on_online_users(data):
            print_info(f"[{self.user_data['username']}] Online users: {len(data.get('users', []))} users")
            self.events_received.append(('online_users', data))
        
        @self.sio.on('invitation_received')
        def on_invitation_received(data):
            print_info(f"[{self.user_data['username']}] Invitation received: {data}")
            self.events_received.append(('invitation_received', data))
        
        @self.sio.on('invitation_sent')
        def on_invitation_sent(data):
            print_info(f"[{self.user_data['username']}] Invitation sent: {data}")
            self.events_received.append(('invitation_sent', data))
        
        @self.sio.on('invitation_rejected')
        def on_invitation_rejected(data):
            print_info(f"[{self.user_data['username']}] Invitation rejected: {data}")
            self.events_received.append(('invitation_rejected', data))
        
        @self.sio.on('game_started')
        def on_game_started(data):
            print_success(f"[{self.user_data['username']}] Game started: {data.get('game_id')}")
            self.events_received.append(('game_started', data))
        
        @self.sio.on('move_made')
        def on_move_made(data):
            print_info(f"[{self.user_data['username']}] Move made at position {data.get('position')}")
            self.events_received.append(('move_made', data))
        
        @self.sio.on('game_forfeited')
        def on_game_forfeited(data):
            print_info(f"[{self.user_data['username']}] Game forfeited: {data}")
            self.events_received.append(('game_forfeited', data))
    
    def connect(self):
        """Conecta al servidor"""
        try:
            self.sio.connect(SOCKET_URL)
            time.sleep(0.5)
            return True
        except Exception as e:
            print_error(f"Failed to connect: {str(e)}")
            return False
    
    def authenticate(self):
        """Se autentica con el servidor"""
        try:
            self.sio.emit('authenticate', {'token': self.user_data['token']})
            time.sleep(1)
            return self.authenticated
        except Exception as e:
            print_error(f"Failed to authenticate: {str(e)}")
            return False
    
    def disconnect(self):
        """Desconecta del servidor"""
        if self.connected:
            self.sio.disconnect()
            time.sleep(0.5)
    
    def wait_for_event(self, event_name: str, timeout: float = 5.0) -> Optional[dict]:
        """Espera por un evento específico"""
        start_time = time.time()
        while time.time() - start_time < timeout:
            for event, data in self.events_received:
                if event == event_name:
                    return data
            time.sleep(0.1)
        return None

def test_websocket_connect_and_auth():
    """Prueba conexión y autenticación WebSocket"""
    print_test("WebSocket Connect and Authenticate")
    
    try:
        client = SocketIOTester(test_data['user1'])
        
        # Conectar
        assert client.connect(), "Failed to connect"
        print_success("Connected to WebSocket server")
        
        # Autenticar
        assert client.authenticate(), "Failed to authenticate"
        print_success("Authenticated via WebSocket")
        
        # Verificar evento de usuarios online
        time.sleep(1)
        online_event = client.wait_for_event('online_users')
        if online_event:
            print_success(f"Received online users event: {len(online_event.get('users', []))} users")
        
        # Desconectar
        client.disconnect()
        print_success("Disconnected successfully")
        
        return True
    except Exception as e:
        print_error(f"WebSocket test failed: {str(e)}")
        return False

def test_websocket_bot_game():
    """Prueba juego contra bot via WebSocket"""
    print_test("WebSocket Bot Game")
    
    try:
        client = SocketIOTester(test_data['user1'])
        
        # Conectar y autenticar
        assert client.connect(), "Failed to connect"
        assert client.authenticate(), "Failed to authenticate"
        
        # Iniciar juego contra bot
        print_info("Starting bot game (medium difficulty)...")
        client.sio.emit('play_vs_bot', {'difficulty': 'medium'})
        
        # Esperar a que inicie el juego
        game_data = client.wait_for_event('game_started', timeout=3.0)
        assert game_data is not None, "Game did not start"
        
        game_id = game_data['game_id']
        print_success(f"Bot game started: Game ID {game_id}")
        print_info(f"Player: {game_data['player1']['username']}")
        print_info(f"Bot: {game_data['player2']['username']}")
        
        # Hacer algunos movimientos
        test_moves = [0, 4, 8]  # Esquina superior izquierda, centro, esquina inferior derecha
        
        for position in test_moves:
            print_info(f"Making move at position {position}...")
            client.sio.emit('make_move', {
                'game_id': game_id,
                'position': position
            })
            time.sleep(1.5)  # Esperar por respuesta y movimiento del bot
            
            # Verificar que se recibió el movimiento
            move_event = client.wait_for_event('move_made', timeout=2.0)
            if move_event:
                print_success(f"Move confirmed at position {move_event.get('position')}")
                
                if move_event.get('game_over'):
                    print_info(f"Game ended: {move_event.get('result')}")
                    break
        
        print_success("Bot game test completed")
        
        # Desconectar
        client.disconnect()
        
        return True
    except Exception as e:
        print_error(f"Bot game test failed: {str(e)}")
        return False

def test_websocket_invitation():
    """Prueba sistema de invitaciones via WebSocket"""
    print_test("WebSocket Player Invitation")
    
    try:
        # Conectar ambos usuarios
        client1 = SocketIOTester(test_data['user1'])
        client2 = SocketIOTester(test_data['user2'])
        
        assert client1.connect(), "User 1 failed to connect"
        assert client1.authenticate(), "User 1 failed to authenticate"
        time.sleep(0.5)
        
        assert client2.connect(), "User 2 failed to connect"
        assert client2.authenticate(), "User 2 failed to authenticate"
        time.sleep(1)
        
        print_success("Both users connected and authenticated")
        
        # Clear events
        client1.events_received.clear()
        client2.events_received.clear()
        
        # Usuario 1 invita a Usuario 2
        print_info(f"User 1 inviting User 2 (ID: {test_data['user2']['user_id']})...")
        client1.sio.emit('invite_player', {
            'target_user_id': test_data['user2']['user_id']
        })
        
        time.sleep(2)  # Increased from 1 to 2 seconds
        
        # Verificar que Usuario 2 recibió la invitación
        invitation_data = client2.wait_for_event('invitation_received', timeout=5.0)  # Increased timeout
        assert invitation_data is not None, "User 2 did not receive invitation"
        
        invitation_id = invitation_data['invitation_id']
        print_success(f"User 2 received invitation (ID: {invitation_id})")
        
        # Usuario 2 acepta la invitación
        print_info("User 2 accepting invitation...")
        client2.sio.emit('accept_invitation', {
            'invitation_id': invitation_id
        })
        
        time.sleep(1)
        
        # Verificar que ambos recibieron el evento de inicio de juego
        game_data1 = client1.wait_for_event('game_started', timeout=3.0)
        game_data2 = client2.wait_for_event('game_started', timeout=3.0)
        
        assert game_data1 is not None, "User 1 did not receive game start"
        assert game_data2 is not None, "User 2 did not receive game start"
        
        game_id = game_data1['game_id']
        print_success(f"PvP game started: Game ID {game_id}")
        print_info(f"Player 1: {game_data1['player1']['username']} (X)")
        print_info(f"Player 2: {game_data2['player2']['username']} (O)")
        
        # Hacer un par de movimientos alternados
        print_info("User 1 making move at position 0...")
        client1.sio.emit('make_move', {
            'game_id': game_id,
            'position': 0
        })
        time.sleep(1)
        
        print_info("User 2 making move at position 4...")
        client2.sio.emit('make_move', {
            'game_id': game_id,
            'position': 4
        })
        time.sleep(1)
        
        print_success("PvP moves executed successfully")
        
        # Desconectar ambos usuarios
        client1.disconnect()
        client2.disconnect()
        
        print_success("Invitation test completed")
        
        return True
    except Exception as e:
        print_error(f"Invitation test failed: {str(e)}")
        return False

def test_websocket_reject_invitation():
    """Prueba rechazo de invitaciones"""
    print_test("WebSocket Reject Invitation")
    
    try:
        # Conectar ambos usuarios
        client1 = SocketIOTester(test_data['user1'])
        client2 = SocketIOTester(test_data['user2'])
        
        assert client1.connect(), "User 1 failed to connect"
        assert client1.authenticate(), "User 1 failed to authenticate"
        time.sleep(0.5)
        
        assert client2.connect(), "User 2 failed to connect"
        assert client2.authenticate(), "User 2 failed to authenticate"
        time.sleep(1)
        
        # Clear events
        client1.events_received.clear()
        client2.events_received.clear()
        
        # Usuario 1 invita a Usuario 2
        print_info(f"User 1 inviting User 2...")
        client1.sio.emit('invite_player', {
            'target_user_id': test_data['user2']['user_id']
        })
        
        time.sleep(2)  # Increased from 1 to 2 seconds
        
        # Usuario 2 recibe la invitación
        invitation_data = client2.wait_for_event('invitation_received', timeout=5.0)  # Increased timeout
        assert invitation_data is not None, "User 2 did not receive invitation"
        
        invitation_id = invitation_data['invitation_id']
        print_success(f"User 2 received invitation (ID: {invitation_id})")
        
        # Usuario 2 RECHAZA la invitación
        print_info("User 2 rejecting invitation...")
        client2.sio.emit('reject_invitation', {
            'invitation_id': invitation_id
        })
        
        time.sleep(1)
        
        # Verificar que Usuario 1 recibió el rechazo
        rejection_data = client1.wait_for_event('invitation_rejected', timeout=3.0)
        assert rejection_data is not None, "User 1 did not receive rejection"
        
        print_success("Invitation rejected successfully")
        
        # Desconectar
        client1.disconnect()
        client2.disconnect()
        
        return True
    except Exception as e:
        print_error(f"Reject invitation test failed: {str(e)}")
        return False

# ============================================================================
# RUNNER PRINCIPAL
# ============================================================================

def run_all_tests():
    """Ejecuta todas las pruebas"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}")
    print("╔════════════════════════════════════════════════════════════╗")
    print("║     PRUEBAS COMPLETAS DE ENDPOINTS - TIC-TAC-TOE API      ║")
    print("╚════════════════════════════════════════════════════════════╝")
    print(f"{Colors.END}\n")
    
    print_info(f"Base URL: {BASE_URL}")
    print_info(f"Socket URL: {SOCKET_URL}")
    print_info(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    results = []
    
    # REST API Tests
    print(f"\n{Colors.BOLD}{Colors.YELLOW}{'='*60}")
    print("PRUEBAS DE REST API")
    print(f"{'='*60}{Colors.END}\n")
    
    rest_tests = [
        ("Health Check", test_health_check),
        ("Root Endpoint", test_root_endpoint),
        ("Register User 1", test_register_user1),
        ("Register User 2", test_register_user2),
        ("Register Duplicate (Should Fail)", test_register_duplicate),
        ("Login User 1", test_login_user1),
        ("Login Invalid (Should Fail)", test_login_invalid),
        ("Get Current User", test_get_current_user),
        ("Get Current User Unauthorized (Should Fail)", test_get_current_user_unauthorized),
        ("Get User Stats", test_get_stats),
        ("Get Leaderboard", test_get_leaderboard),
        ("Get Game History", test_get_game_history),
    ]
    
    for name, test_func in rest_tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print_error(f"Test '{name}' crashed: {str(e)}")
            results.append((name, False))
        time.sleep(0.5)
    
    # WebSocket Tests
    print(f"\n{Colors.BOLD}{Colors.YELLOW}{'='*60}")
    print("PRUEBAS DE WEBSOCKET")
    print(f"{'='*60}{Colors.END}\n")
    
    websocket_tests = [
        ("WebSocket Connect & Auth", test_websocket_connect_and_auth),
        ("WebSocket Bot Game", test_websocket_bot_game),
        ("WebSocket Player Invitation", test_websocket_invitation),
        ("WebSocket Reject Invitation", test_websocket_reject_invitation),
    ]
    
    for name, test_func in websocket_tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print_error(f"Test '{name}' crashed: {str(e)}")
            results.append((name, False))
        time.sleep(1)
    
    # Resumen final
    print(f"\n{Colors.BOLD}{Colors.BLUE}")
    print("╔════════════════════════════════════════════════════════════╗")
    print("║                    RESUMEN DE PRUEBAS                      ║")
    print("╚════════════════════════════════════════════════════════════╝")
    print(f"{Colors.END}\n")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    percentage = (passed / total * 100) if total > 0 else 0
    
    for name, result in results:
        status = f"{Colors.GREEN}✓ PASS{Colors.END}" if result else f"{Colors.RED}✗ FAIL{Colors.END}"
        print(f"{status} - {name}")
    
    print(f"\n{Colors.BOLD}Resultado Final:{Colors.END}")
    print(f"Total: {total} pruebas")
    print(f"{Colors.GREEN}Pasadas: {passed}{Colors.END}")
    print(f"{Colors.RED}Fallidas: {total - passed}{Colors.END}")
    print(f"Porcentaje de éxito: {Colors.BOLD}{percentage:.1f}%{Colors.END}\n")
    
    if percentage == 100:
        print(f"{Colors.GREEN}{Colors.BOLD}🎉 ¡TODAS LAS PRUEBAS PASARON! 🎉{Colors.END}\n")
    elif percentage >= 80:
        print(f"{Colors.YELLOW}{Colors.BOLD}⚠️  Mayoría de pruebas pasaron ⚠️{Colors.END}\n")
    else:
        print(f"{Colors.RED}{Colors.BOLD}❌ Varias pruebas fallaron ❌{Colors.END}\n")

if __name__ == "__main__":
    try:
        run_all_tests()
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Pruebas interrumpidas por el usuario{Colors.END}")
    except Exception as e:
        print(f"\n{Colors.RED}Error fatal: {str(e)}{Colors.END}")
