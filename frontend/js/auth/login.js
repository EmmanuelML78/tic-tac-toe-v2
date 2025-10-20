document.getElementById('login-form').addEventListener('submit', async (e) => {
    e.preventDefault();

    const username = document.getElementById('login-username').value.trim();
    const password = document.getElementById('login-password').value;

    if (!username || !password) {
        showError('error-message', 'Please fill in all fields');
        return;
    }

    hideError('error-message');
    showLoading();

    try {
        const response = await fetch(`${CONFIG.API_URL}/api/login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ username, password })
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.detail || 'Login failed');
        }

        Storage.setToken(data.access_token);
        Storage.setUserInfo(data.user_id, data.username);
        window.location.href = 'lobby.html';

    } catch (error) {
        hideLoading();
        showError('error-message', error.message);
    }
});
