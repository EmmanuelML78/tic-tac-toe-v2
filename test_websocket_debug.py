"""
Test rápido solo para bot game y invitaciones
"""
import requests
import socketio
import time

BASE_URL = "http://localhost:8000"
SOCKET_URL = "http://localhost:8000"

# Wait for server to start
time.sleep(3)

# Register users
print("Registrando usuarios...")
username1 = f"testuser1_{int(time.time())}"
username2 = f"testuser2_{int(time.time())}"

r1 = requests.post(f"{BASE_URL}/api/register", json={
    "username": username1,
    "password": "TestPass123!"
})
user1 = r1.json()
print(f"User 1: {username1} (ID: {user1['user_id']})")

r2 = requests.post(f"{BASE_URL}/api/register", json={
    "username": username2,
    "password": "TestPass123!"
})
user2 = r2.json()
print(f"User 2: {username2} (ID: {user2['user_id']})")

# Test Bot Game
print("\n" + "="*60)
print("TEST: Bot Game")
print("="*60)

sio1 = socketio.Client(logger=False, engineio_logger=False)
events_received = []

@sio1.on('authenticated')
def on_auth(data):
    print(f"✓ Authenticated: {data}")
    events_received.append(('authenticated', data))

@sio1.on('game_started')
def on_game_started(data):
    print(f"✓ Game started: {data}")
    events_received.append(('game_started', data))

@sio1.on('move_made')
def on_move(data):
    print(f"✓ Move made: position={data.get('position')}, game_over={data.get('game_over')}")
    events_received.append(('move_made', data))

@sio1.on('error')
def on_error(data):
    print(f"✗ Error: {data}")
    events_received.append(('error', data))

print("Conectando...")
sio1.connect(SOCKET_URL)
time.sleep(0.5)

print("Autenticando...")
sio1.emit('authenticate', {'token': user1['access_token']})
time.sleep(1.5)

print("Iniciando juego contra bot...")
sio1.emit('play_vs_bot', {'difficulty': 'medium'})
time.sleep(2)

# Check if game started
game_started = [e for e in events_received if e[0] == 'game_started']
if game_started:
    print(f"✓ SUCCESS: Bot game started!")
    game_data = game_started[0][1]
    game_id = game_data['game_id']
    
    # Make a move
    print(f"Haciendo movimiento en posición 4...")
    sio1.emit('make_move', {'game_id': game_id, 'position': 4})
    time.sleep(2)
    
    moves = [e for e in events_received if e[0] == 'move_made']
    print(f"Movimientos recibidos: {len(moves)}")
else:
    print("✗ FAIL: Bot game did not start")
    print(f"Events received: {events_received}")

sio1.disconnect()

# Test Invitations
print("\n" + "="*60)
print("TEST: Player Invitation")
print("="*60)

events1 = []
events2 = []

sio1 = socketio.Client(logger=False, engineio_logger=False)
sio2 = socketio.Client(logger=False, engineio_logger=False)

@sio1.on('authenticated')
def on_auth1(data):
    print(f"✓ User 1 authenticated")
    events1.append(('authenticated', data))

@sio2.on('authenticated')
def on_auth2(data):
    print(f"✓ User 2 authenticated")
    events2.append(('authenticated', data))

@sio1.on('invitation_sent')
def on_inv_sent(data):
    print(f"✓ User 1: Invitation sent - {data}")
    events1.append(('invitation_sent', data))

@sio2.on('invitation_received')
def on_inv_received(data):
    print(f"✓ User 2: Invitation received - {data}")
    events2.append(('invitation_received', data))

@sio1.on('game_started')
def on_game1(data):
    print(f"✓ User 1: Game started")
    events1.append(('game_started', data))

@sio2.on('game_started')
def on_game2(data):
    print(f"✓ User 2: Game started")
    events2.append(('game_started', data))

@sio1.on('error')
def on_error1(data):
    print(f"✗ User 1 error: {data}")
    events1.append(('error', data))

@sio2.on('error')
def on_error2(data):
    print(f"✗ User 2 error: {data}")
    events2.append(('error', data))

print("Conectando ambos usuarios...")
sio1.connect(SOCKET_URL)
time.sleep(0.5)
sio2.connect(SOCKET_URL)
time.sleep(0.5)

print("Autenticando...")
sio1.emit('authenticate', {'token': user1['access_token']})
time.sleep(1)
sio2.emit('authenticate', {'token': user2['access_token']})
time.sleep(2)

print(f"Enviando invitación de User 1 ({user1['user_id']}) a User 2 ({user2['user_id']})...")
sio1.emit('invite_player', {'target_user_id': user2['user_id']})
time.sleep(3)

# Check results
inv_sent = [e for e in events1 if e[0] == 'invitation_sent']
inv_received = [e for e in events2 if e[0] == 'invitation_received']

print(f"\nUser 1 events: {[e[0] for e in events1]}")
print(f"User 2 events: {[e[0] for e in events2]}")

if inv_sent and inv_received:
    print("✓ SUCCESS: Invitation sent and received!")
    
    # Accept invitation
    invitation_id = inv_received[0][1]['invitation_id']
    print(f"User 2 aceptando invitación {invitation_id}...")
    sio2.emit('accept_invitation', {'invitation_id': invitation_id})
    time.sleep(2)
    
    game1 = [e for e in events1 if e[0] == 'game_started']
    game2 = [e for e in events2 if e[0] == 'game_started']
    
    if game1 and game2:
        print("✓ SUCCESS: Game started for both players!")
    else:
        print(f"✗ FAIL: Game started events - User1: {len(game1)}, User2: {len(game2)}")
else:
    print(f"✗ FAIL: Invitation failed")
    print(f"  - Invitation sent: {len(inv_sent)}")
    print(f"  - Invitation received: {len(inv_received)}")

sio1.disconnect()
sio2.disconnect()

print("\n" + "="*60)
print("Tests completados")
print("="*60)
