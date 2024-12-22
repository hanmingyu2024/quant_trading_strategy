import api from './api';

export const authService = {
    async login(username, password) {
        const response = await api.post('/auth/login', { username, password });
        return response.data;
    },

    async register(userData) {
        const response = await api.post('/auth/register', userData);
        return response.data;
    },

    async getCurrentUser() {
        const response = await api.get('/users/me');
        return response.data;
    },

    async updateProfile(userData) {
        const response = await api.put('/users/me', userData);
        return response.data;
    }
};
