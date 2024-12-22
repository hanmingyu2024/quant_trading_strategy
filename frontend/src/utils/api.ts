import axios from 'axios';
import { handleError } from './error';

const api = axios.create({
    baseURL: process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1',
    headers: {
        'Content-Type': 'application/json',
    },
    withCredentials: true
});

// 请求拦截器
api.interceptors.request.use(
    (config) => {
        const token = localStorage.getItem('token');
        if (token) {
            config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
    },
    (error) => Promise.reject(handleError(error))
);

// 响应拦截器
api.interceptors.response.use(
    (response) => response,
    (error) => Promise.reject(handleError(error))
);

export default api; 