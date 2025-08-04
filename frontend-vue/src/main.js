import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import axios from 'axios'

// Configuración global de Axios
axios.defaults.baseURL = 'http://localhost:5000';

// Interceptor de Axios para añadir el token a las cabeceras
axios.interceptors.request.use(config => {
  const token = localStorage.getItem('access_token');
  if (token) {
    // Si tenemos un token, lo añadimos a la cabecera 'Authorization'
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
}, error => {
  return Promise.reject(error);
});

const app = createApp(App)
app.use(router)
app.mount('#app')