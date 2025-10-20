"""
Script simplificado para probar endpoints sin caracteres especiales
"""
import requests
import socketio
import json
import time
from datetime import datetime

BASE_URL = "http://localhost:8000"
SOCKET_URL = "http://localhost:8000"

test_data = {
    'user1': {},
    'user2': {},
}

def print_result(test_name, passed):
    status = "[PASS]" if passed else "[FAIL]"
    print(f"{status} {test_name}")
    return passed

results = []

# Test 1: Health Check
try:
    r = requests.get(f"{BASE_URL}/health")
    results.append(print_result("Health Check", r.status_code == 200))
except:
    results.append(print_result("Health Check", False))

# Test 2: Root Endpoint
try:
    r = requests.get(f"{BASE_URL}/")
    results.append(print_result("Root Endpoint", r.status_code == 200))
except:
    results.append(print_result("Root Endpoint", False))

# Test 3: Register User 1
try:
    username1 = f"testuser1_{int(time.time())}"
    r = requests.post(f"{BASE_URL}/api/register", json={
        "username": username1,
        "password": "TestPass123!",
        "email": f"{username1}@test.com"
    })
    data = r.json()
    test_data['user1'] = {
        'username': username1,
        'password': "TestPass123!",
        'user_id': data.get('user_id'),
        'token': data.get('access_token')
    }
    results.append(print_result("Register User 1", r.status_code == 200 and 'access_token' in data))
except Exception as e:
    print(f"Error: {e}")
    results.append(print_result("Register User 1", False))

# Test 4: Register User 2
try:
    username2 = f"testuser2_{int(time.time())}"
    r = requests.post(f"{BASE_URL}/api/register", json={
        "username": username2,
        "password": "TestPass456!",
        "email": f"{username2}@test.com"
    })
    data = r.json()
    test_data['user2'] = {
        'username': username2,
        'password': "TestPass456!",
        'user_id': data.get('user_id'),
        'token': data.get('access_token')
    }
    results.append(print_result("Register User 2", r.status_code == 200 and 'access_token' in data))
except:
    results.append(print_result("Register User 2", False))

# Test 5: Register Duplicate (Should Fail)
try:
    r = requests.post(f"{BASE_URL}/api/register", json={
        "username": test_data['user1']['username'],
        "password": "AnyPassword123!"
    })
    results.append(print_result("Register Duplicate (Should Fail)", r.status_code == 400))
except:
    results.append(print_result("Register Duplicate (Should Fail)", False))

# Test 6: Login User 1
try:
    r = requests.post(f"{BASE_URL}/api/login", json={
        "username": test_data['user1']['username'],
        "password": test_data['user1']['password']
    })
    data = r.json()
    test_data['user1']['token'] = data.get('access_token')
    results.append(print_result("Login User 1", r.status_code == 200 and 'access_token' in data))
except:
    results.append(print_result("Login User 1", False))

# Test 7: Login Invalid (Should Fail)
try:
    r = requests.post(f"{BASE_URL}/api/login", json={
        "username": test_data['user1']['username'],
        "password": "WrongPassword123!"
    })
    results.append(print_result("Login Invalid (Should Fail)", r.status_code == 401))
except:
    results.append(print_result("Login Invalid (Should Fail)", False))

# Test 8: Get Current User
try:
    headers = {"Authorization": f"Bearer {test_data['user1']['token']}"}
    r = requests.get(f"{BASE_URL}/api/users/me", headers=headers)
    data = r.json()
    results.append(print_result("Get Current User", r.status_code == 200 and data['id'] == test_data['user1']['user_id']))
except:
    results.append(print_result("Get Current User", False))

# Test 9: Get Current User Unauthorized (Should Fail)
try:
    r = requests.get(f"{BASE_URL}/api/users/me")
    results.append(print_result("Get Current User Unauthorized (Should Fail)", r.status_code in [401, 403]))
except:
    results.append(print_result("Get Current User Unauthorized (Should Fail)", False))

# Test 10: Get Stats
try:
    headers = {"Authorization": f"Bearer {test_data['user1']['token']}"}
    r = requests.get(f"{BASE_URL}/api/stats", headers=headers)
    data = r.json()
    results.append(print_result("Get User Stats", r.status_code == 200 and 'total_games' in data))
except:
    results.append(print_result("Get User Stats", False))

# Test 11: Get Leaderboard
try:
    r = requests.get(f"{BASE_URL}/api/stats/leaderboard?limit=10")
    results.append(print_result("Get Leaderboard", r.status_code == 200))
except:
    results.append(print_result("Get Leaderboard", False))

# Test 12: Get Game History
try:
    headers = {"Authorization": f"Bearer {test_data['user1']['token']}"}
    r = requests.get(f"{BASE_URL}/api/games/history?limit=20", headers=headers)
    results.append(print_result("Get Game History", r.status_code == 200))
except:
    results.append(print_result("Get Game History", False))

# WebSocket Tests
class SimpleSocketTester:
    def __init__(self, user_data):
        self.user_data = user_data
        self.sio = socketio.Client()
        self.connected = False
        self.authenticated = False
        self.events = []
        self.setup_handlers()
    
    def setup_handlers(self):
        @self.sio.on('connect')
        def on_connect():
            self.connected = True
        
        @self.sio.on('authenticated')
        def on_authenticated(data):
            self.authenticated = True
            self.events.append(('authenticated', data))
        
        @self.sio.on('invitation_received')
        def on_invitation_received(data):
            self.events.append(('invitation_received', data))
        
        @self.sio.on('invitation_sent')
        def on_invitation_sent(data):
            self.events.append(('invitation_sent', data))
        
        @self.sio.on('game_started')
        def on_game_started(data):
            self.events.append(('game_started', data))
        
        @self.sio.on('move_made')
        def on_move_made(data):
            self.events.append(('move_made', data))
    
    def connect(self):
        try:
            self.sio.connect(SOCKET_URL)
            time.sleep(0.5)
            return True
        except:
            return False
    
    def authenticate(self):
        try:
            self.sio.emit('authenticate', {'token': self.user_data['token']})
            time.sleep(1)
            return self.authenticated
        except:
            return False
    
    def disconnect(self):
        if self.connected:
            self.sio.disconnect()
    
    def wait_for_event(self, event_name, timeout=5.0):
        start = time.time()
        while time.time() - start < timeout:
            for evt, data in self.events:
                if evt == event_name:
                    return data
            time.sleep(0.1)
        return None

# Test 13: WebSocket Connect & Auth
try:
    client = SimpleSocketTester(test_data['user1'])
    success = client.connect() and client.authenticate()
    client.disconnect()
    results.append(print_result("WebSocket Connect & Auth", success))
except:
    results.append(print_result("WebSocket Connect & Auth", False))

# Test 14: WebSocket Bot Game
try:
    client = SimpleSocketTester(test_data['user1'])
    client.connect()
    client.authenticate()
    time.sleep(1)
    
    client.sio.emit('play_vs_bot', {'difficulty': 'medium'})
    game_data = client.wait_for_event('game_started', timeout=3.0)
    
    success = game_data is not None
    if success:
        game_id = game_data['game_id']
        client.sio.emit('make_move', {'game_id': game_id, 'position': 0})
        time.sleep(1)
    
    client.disconnect()
    results.append(print_result("WebSocket Bot Game", success))
except Exception as e:
    print(f"Error: {e}")
    results.append(print_result("WebSocket Bot Game", False))

# Test 15: WebSocket Invitation
try:
    client1 = SimpleSocketTester(test_data['user1'])
    client2 = SimpleSocketTester(test_data['user2'])
    
    client1.connect()
    client1.authenticate()
    time.sleep(0.5)
    
    client2.connect()
    client2.authenticate()
    time.sleep(1.5)
    
    client1.events.clear()
    client2.events.clear()
    
    client1.sio.emit('invite_player', {'target_user_id': test_data['user2']['user_id']})
    time.sleep(2)
    
    invitation_data = client2.wait_for_event('invitation_received', timeout=5.0)
    
    success = invitation_data is not None
    if success:
        invitation_id = invitation_data['invitation_id']
        client2.sio.emit('accept_invitation', {'invitation_id': invitation_id})
        time.sleep(1)
    
    client1.disconnect()
    client2.disconnect()
    results.append(print_result("WebSocket Player Invitation", success))
except Exception as e:
    print(f"Error: {e}")
    results.append(print_result("WebSocket Player Invitation", False))

# Test 16: WebSocket Reject Invitation
try:
    client1 = SimpleSocketTester(test_data['user1'])
    client2 = SimpleSocketTester(test_data['user2'])
    
    client1.connect()
    client1.authenticate()
    time.sleep(0.5)
    
    client2.connect()
    client2.authenticate()
    time.sleep(1.5)
    
    client1.events.clear()
    client2.events.clear()
    
    client1.sio.emit('invite_player', {'target_user_id': test_data['user2']['user_id']})
    time.sleep(2)
    
    invitation_data = client2.wait_for_event('invitation_received', timeout=5.0)
    
    success = False
    if invitation_data:
        invitation_id = invitation_data['invitation_id']
        client2.sio.emit('reject_invitation', {'invitation_id': invitation_id})
        time.sleep(1)
        success = True
    
    client1.disconnect()
    client2.disconnect()
    results.append(print_result("WebSocket Reject Invitation", success))
except:
    results.append(print_result("WebSocket Reject Invitation", False))

# Summary
print("\n" + "="*60)
print("RESUMEN DE PRUEBAS")
print("="*60)
passed = sum(results)
total = len(results)
percentage = (passed / total * 100) if total > 0 else 0

print(f"\nTotal: {total} pruebas")
print(f"Pasadas: {passed}")
print(f"Fallidas: {total - passed}")
print(f"Porcentaje de exito: {percentage:.1f}%\n")

if percentage == 100:
    print("TODAS LAS PRUEBAS PASARON!")
elif percentage >= 80:
    print("Mayoria de pruebas pasaron")
else:
    print("Varias pruebas fallaron")
