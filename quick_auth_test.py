import requests
import json
import time

time.sleep(3)  # Wait for server to be ready

# Generate unique username
username = f'testuser_{int(time.time())}'

# Register
print("=" * 60)
print("Testing Registration...")
r = requests.post('http://localhost:8000/api/register', json={
    'username': username,
    'password': 'Test123!'
})
print(f'Register Status: {r.status_code}')
data = r.json()
print(f'User ID: {data.get("user_id")}')
token = data.get('access_token')
print(f'Token: {token[:50] if token else "None"}...')

# Test protected endpoint
print("\n" + "=" * 60)
print("Testing Protected Endpoint...")
r2 = requests.get('http://localhost:8000/api/users/me', headers={
    'Authorization': f'Bearer {token}'
})
print(f'Protected endpoint status: {r2.status_code}')

if r2.status_code == 200:
    print('✅ SUCCESS! User data:')
    print(json.dumps(r2.json(), indent=2))
else:
    print(f'❌ FAILED: {r2.text}')
