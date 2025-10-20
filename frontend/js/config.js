const CONFIG = {
    API_URL: 'http://localhost:8000',
    SOCKET_URL: 'http://localhost:8000',
    STORAGE_KEYS: {
        TOKEN: 'tictactoe_token',
        USER_ID: 'tictactoe_user_id',
        USERNAME: 'tictactoe_username'
    },
    GAME: {
        MOVE_TIMEOUT: 30000,
        BOARD_SIZE: 3,
        BOT_DIFFICULTIES: ['easy', 'medium', 'hard']
    }
};

const Storage = {
    setToken(token) {
        localStorage.setItem(CONFIG.STORAGE_KEYS.TOKEN, token);
    },

    getToken() {
        return localStorage.getItem(CONFIG.STORAGE_KEYS.TOKEN);
    },

    setUserInfo(userId, username) {
        localStorage.setItem(CONFIG.STORAGE_KEYS.USER_ID, userId);
        localStorage.setItem(CONFIG.STORAGE_KEYS.USERNAME, username);
    },

    getUserInfo() {
        return {
            userId: localStorage.getItem(CONFIG.STORAGE_KEYS.USER_ID),
            username: localStorage.getItem(CONFIG.STORAGE_KEYS.USERNAME)
        };
    },

    clearAll() {
        localStorage.removeItem(CONFIG.STORAGE_KEYS.TOKEN);
        localStorage.removeItem(CONFIG.STORAGE_KEYS.USER_ID);
        localStorage.removeItem(CONFIG.STORAGE_KEYS.USERNAME);
    },

    isAuthenticated() {
        return !!this.getToken();
    }
};
