// frontend/src/api.js
import axios from "axios";

const api = axios.create({
    baseURL: "http://127.0.0.1:8000",
});

// 请求拦截器：每次请求前，自动从本地存储获取 Token 并带上
api.interceptors.request.use(
    (config) => {
        const token = localStorage.getItem("token");
        if (token) {
            config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
    },
    (error) => Promise.reject(error),
);

export default api;