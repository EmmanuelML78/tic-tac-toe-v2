/**
 * Registration functionality
 */

document.getElementById('register-form').addEventListener('submit', async (e) => {
    e.preventDefault();

    const username = document.getElementById('register-username').value.trim();
    const email = document.getElementById('register-email').value.trim();
    const password = document.getElementById('register-password').value;
    const passwordConfirm = document.getElementById('register-password-confirm').value;

    // Validation
    if (!username || !password || !passwordConfirm) {
        showError('error-message', 'Please fill in all required fields');
        return;
    }

    if (username.length < 3 || username.length > 20) {
        showError('error-message', 'Username must be 3-20 characters');
        return;
    }

    if (!/^[a-zA-Z0-9_]+$/.test(username)) {
        showError('error-message', 'Username can only contain letters, numbers, and underscores');
        return;
    }

    if (password.length < 6) {
        showError('error-message', 'Password must be at least 6 characters');
        return;
    }

    if (password !== passwordConfirm) {
        showError('error-message', 'Passwords do not match');
        return;
    }

    hideError('error-message');
    showLoading();

    try {
        const response = await fetch(`${CONFIG.API_URL}/api/register`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                username,
                password,
                email: email || null
            })
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.detail || 'Registration failed');
        }

        // Store token and user info
        Storage.setToken(data.access_token);
        Storage.setUserInfo(data.user_id, data.username);

        // Redirect to lobby
        window.location.href = 'lobby.html';

    } catch (error) {
        hideLoading();
        showError('error-message', error.message);
    }
});
