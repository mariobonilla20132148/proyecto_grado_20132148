<template>
  <div class="login-page">
    <div class="login-form">
      <h2>Acceso Interno</h2>
      <form @submit.prevent="handleLogin">
        <div class="form-group">
          <label for="dni">DNI / Usuario</label>
          <input type="text" id="dni" v-model="form.dni" required>
        </div>
        <div class="form-group">
          <label for="password">Contraseña</label>
          <input type="password" id="password" v-model="form.password" required>
        </div>
        <p v-if="error" class="error-message">{{ error }}</p>
        <button type="submit" class="submit-button">Entrar</button>
      </form>
    </div>

    <div v-if="showChangePasswordModal" class="modal-overlay">
        <div class="modal-content">
            <h3>Cambiar Contraseña</h3>
            <p>Es tu primer inicio de sesión. Debes establecer una nueva contraseña.</p>
            <div class="form-group">
                <label>Nueva Contraseña</label>
                <input type="password" v-model="newPassword" required>
            </div>
             <p v-if="changePasswordError" class="error-message">{{ changePasswordError }}</p>
            <button @click="handleChangePassword" class="submit-button">Guardar Contraseña</button>
        </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';
export default {
  emits: ['login-success'],
  data() {
    return {
      form: { dni: '', password: '' },
      error: '',
      showChangePasswordModal: false,
      newPassword: '',
      changePasswordError: '',
      userToChangePassword: ''
    };
  },
  methods: {
    async handleLogin() {
      this.error = '';
      try {
        const response = await axios.post('/api/login', this.form);
        if (response.data.success) {
          localStorage.setItem('access_token', response.data.access_token);
          localStorage.setItem('userDni', response.data.user_dni);
          localStorage.setItem('userRole', response.data.user_role);

          if (response.data.is_first_login) {
              this.userToChangePassword = response.data.user_dni;
              this.showChangePasswordModal = true;
          } else {
            this.$emit('login-success');
            this.$router.push('/');
          }
        }
      } catch (err) {
        this.error = err.response?.data?.message || 'No se pudo iniciar sesión.';
      }
    },
    async handleChangePassword() {
        this.changePasswordError = '';
        if (this.newPassword.length < 6) {
            this.changePasswordError = "La contraseña es muy corta.";
            return;
        }
        try {
            const response = await axios.post(`/api/change_password/${this.userToChangePassword}`, { new_password: this.newPassword });
            if (response.data.success) {
                this.showChangePasswordModal = false;
                this.error = "Contraseña cambiada. Por favor, inicia sesión de nuevo.";
                this.form.password = ''; 
                
                localStorage.removeItem('access_token');
                localStorage.removeItem('userDni');
                localStorage.removeItem('userRole');
            }
        } catch (err) {
            this.changePasswordError = err.response?.data?.message || "Error al cambiar la contraseña.";
        }
    }
  }
};
</script>

<style scoped>
.login-page { display: flex; justify-content: center; align-items: center; min-height: 80vh; }
.login-form { padding: 2.5rem; background: white; border-radius: 8px; box-shadow: 0 4px 20px rgba(0,0,0,0.1); width: 100%; max-width: 400px; }
h2 { text-align: center; color: #333; margin-top: 0; margin-bottom: 2rem; }
.form-group { margin-bottom: 1.5rem; }
label { display: block; margin-bottom: 0.5rem; font-weight: bold; color: #555; }
input { width: 100%; padding: 0.8rem; border: 1px solid #ccc; border-radius: 4px; box-sizing: border-box; font-size: 1rem; }
.submit-button { width: 100%; padding: 0.9rem; background: #42b983; color: white; border: none; border-radius: 4px; font-size: 1.1rem; cursor: pointer; font-weight: bold; }
.error-message { color: #e74c3c; text-align: center; margin-top: 1rem; font-weight: 500; }
.modal-overlay { position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.7); display: flex; justify-content: center; align-items: center; }
.modal-content { background: white; padding: 2rem; border-radius: 8px; }
</style>