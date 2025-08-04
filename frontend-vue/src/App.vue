<template>
  <div id="app">
    <nav class="main-nav">
      <div class="main-nav-left">
        <router-link to="/" class="navbar-brand">
          <span>SisAsistencia</span>
        </router-link>
        
        <div v-if="isAuthenticated" class="nav-links">
          <!-- Enlace 'Inicio' redirige a Dashboard para Admins, o a Fichaje para otros -->
          <router-link :to="isAdmin ? '/dashboard' : '/'">Inicio</router-link>
          
          <!-- Enlaces específicos de rol -->
          <router-link v-if="!isAdmin" to="/mis-registros">Mis Registros</router-link>
          <router-link v-if="isAdmin" to="/admin/empleados">Empleados</router-link>
          <router-link v-if="isAdmin" to="/admin/gestion">Gestión</router-link>
        </div>
      </div>
      
      <button v-if="isAuthenticated" @click="logout" class="logout-button">Cerrar Sesión</button>
      
      <router-link v-else to="/login" class="login-button">Iniciar Sesión</router-link>
    </nav>
    <main>
      <router-view @login-success="updateAuthStatus" />
    </main>
  </div>
</template>

<script>
export default {
  name: 'App',
  data() {
    return {
      isAuthenticated: false,
      isAdmin: false
    };
  },
  methods: {
    updateAuthStatus() {
      this.isAuthenticated = !!localStorage.getItem('userDni');
      this.isAdmin = localStorage.getItem('userRole') === 'admin';
    },
    logout() {
      localStorage.removeItem('userDni');
      localStorage.removeItem('userRole');
      localStorage.removeItem('access_token');
      this.updateAuthStatus();
      this.$router.push('/'); // Redirigir a la página de fichaje/home
    }
  },
  watch: {
    '$route'() {
      this.updateAuthStatus();
    }
  },
  created() {
    this.updateAuthStatus();
  }
};
</script>

<style>
/* Estilos globales */
body { 
  margin: 0; 
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif; 
  background: #f4f6f9; 
  color: #333; 
}
#app { 
  display: flex; 
  flex-direction: column; 
  min-height: 100vh; 
}

/* Estilos de la barra de navegación */
.main-nav { 
  display: flex; 
  justify-content: space-between; 
  align-items: center; 
  background: #2c3e50;
  padding: 0.8rem 2rem;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1); 
  min-height: 60px;
}
.main-nav-left { 
  display: flex; 
  align-items: center; 
  gap: 1.5rem; 
}
.navbar-brand { 
  display: flex; 
  align-items: center; 
  text-decoration: none; 
  color: white; 
  font-weight: bold; 
  font-size: 1.5rem; 
}
.nav-links { 
  display: flex; 
  align-items: center; 
}
.nav-links a { 
  color: #ecf0f1; 
  text-decoration: none; 
  margin-right: 1.5rem; 
  font-weight: bold; 
  padding: 0.5rem; 
  border-radius: 4px; 
  transition: background-color 0.2s, color 0.2s; 
}
.nav-links a:last-child { 
  margin-right: 0; 
}
.nav-links a.router-link-exact-active { 
  color: white; 
  background-color: #42b983; 
}

/* Estilos de botones */
button, .logout-button, .login-button {
  padding: 0.8rem 1.5rem;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 1em;
  font-weight: bold;
  color: white;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
  text-decoration: none;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}
button:hover:not(:disabled), .logout-button:hover:not(:disabled), .login-button:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 6px 12px rgba(0, 0, 0, 0.15);
}
button:active:not(:disabled), .logout-button:active:not(:disabled), .login-button:active:not(:disabled) {
  transform: translateY(0);
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}
button:disabled, .logout-button:disabled, .login-button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: translateY(0);
  box-shadow: none;
}
.logout-button { 
  background: #e74c3c; 
}
.logout-button:hover:not(:disabled) { 
  background: #c0392b; 
}
.login-button { 
  background: #007bff; 
}
.login-button:hover:not(:disabled) { 
  background: #0056b3; 
}

main { 
  flex-grow: 1; 
  padding: 2rem; 
}

/* Estilos responsivos */
@media (max-width: 768px) {
  .main-nav {
    flex-direction: column;
    align-items: flex-start;
    padding: 0.5rem 1rem;
  }
  .main-nav-left {
    width: 100%;
    flex-direction: column; 
    align-items: flex-start;
    gap: 0.5rem;
    margin-bottom: 0.5rem;
  }
  .navbar-brand {
      width: 100%;
      margin-bottom: 0.5rem;
  }
  .nav-links {
    flex-wrap: wrap;
    margin-top: 0.5rem;
    width: 100%;
  }
  .nav-links a {
    margin-right: 1rem;
    margin-bottom: 0.5rem;
  }
  .nav-links a:last-child {
    margin-right: 1rem;
  }
  .logout-button, .login-button {
    width: 100%;
    margin-top: 0.5rem;
  }
}
@media (max-width: 480px) {
  .navbar-brand {
    font-size: 1.3rem;
  }
  .nav-links a {
    font-size: 0.9em;
    padding: 0.4rem;
  }
}
</style>
