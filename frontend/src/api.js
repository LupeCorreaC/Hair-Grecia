import axios from 'axios';

const api = axios.create({ baseURL: '/api', timeout: 10000 });
api.interceptors.request.use((config) => {
  const token = sessionStorage.getItem('hair_token');
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});
export const messageFromError = (error) =>
  error.response?.data?.error || 'No fue posible conectar con la aplicación. Revisa que el servidor esté encendido.';
export default api;
