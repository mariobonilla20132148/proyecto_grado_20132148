<template>
  <div class="home-container">
    <div class="fichaje-wrapper">
      <div class="time-display">
        <div class="current-time">{{ currentTime }}</div>
        <div class="current-date">{{ currentDate }}</div>
      </div>

      <div class="scan-badge-card" @click="openScannerModal">
        <div class="barcode-visual"></div>
        <p class="scan-text">Escanear Carnet</p>
      </div>

      <p class="or-separator">O</p>

      <div class="fichaje-card">
        <h2>Identificar Manualmente</h2>
        <div class="input-group">
          <input type="text" v-model="dni" placeholder="Ingrese su DNI" @keyup.enter="fichar" :disabled="loading">
          <button @click="fichar" :disabled="loading">
            <span v-if="!loading">Marcar</span>
            <span v-else>...</span>
          </button>
        </div>
        <p v-if="fichajeMessage" class="message" :class="fichajeStatus">{{ fichajeMessage }}</p>
      </div>

      <div class="admin-login-link">
        <router-link to="/login">Acceso Administrativo</router-link>
      </div>
    </div>

    <div v-if="showFichajeModal" class="modal-overlay">
      <div class="modal-content" :class="fichajeType === 'entrada' ? 'entrada-modal' : 'salida-modal'">
        <h3>{{ modalMessage }}</h3>
        <p>Registro exitoso</p>
      </div>
    </div>

    <div v-if="showScannerModal" class="modal-overlay">
      <div class="modal-content scanner-modal">
        <h3>Apunte la cámara al código de barras</h3>
        <div id="qr-reader"></div>
        <p v-if="scanError" class="message error">{{ scanError }}</p>
        <button @click="closeScannerModal" class="cancel-button">Cancelar</button>
      </div>
    </div>

  </div>
</template>

<script>
import { nextTick } from 'vue';
import axios from 'axios';
import { Html5Qrcode } from 'html5-qrcode';

export default {
  data() {
    return {
      currentTime: '',
      currentDate: '',
      intervalId: null,
      dni: '',
      fichajeMessage: '',
      fichajeStatus: '',
      loading: false,
      showFichajeModal: false,
      modalMessage: '',
      fichajeType: '',
      showScannerModal: false,
      scanError: '',
      html5QrcodeScanner: null,
    };
  },
  methods: {
    updateTime() {
      const now = new Date();
      this.currentTime = now.toLocaleTimeString('es-ES', { hour: '2-digit', minute: '2-digit', second: '2-digit' });
      this.currentDate = now.toLocaleDateString('es-ES', { weekday: 'long', day: 'numeric', month: 'long' });
    },
    async fichar() {
      if (!this.dni || this.loading) return;
      this.loading = true;
      this.fichajeMessage = '';
      this.fichajeStatus = '';

      try {
        const response = await axios.post('/api/fichar', { dni: this.dni });
        if (response.data.success) {
          const { tipo, nombre_empleado, genero } = response.data;
          
          let saludo = "¡Hola,";
          if (tipo === 'entrada') {
              saludo = genero === 'Femenino' ? '¡Bienvenida,' : '¡Bienvenido,';
          } else {
              saludo = '¡Hasta luego,';
          }

          this.modalMessage = `${saludo} ${nombre_empleado}!`;
          this.fichajeType = tipo;
          this.showFichajeModal = true;
          setTimeout(() => { this.showFichajeModal = false; }, 2500);
        }
      } catch (error) {
        this.fichajeMessage = error.response?.data?.message || 'Error de conexión con el servidor.';
        this.fichajeStatus = 'error';
      } finally {
        this.loading = false;
        this.dni = '';
      }
    },
    
    async openScannerModal() {
      this.scanError = '';
      this.showScannerModal = true;
      await nextTick();
      this.html5QrcodeScanner = new Html5Qrcode('qr-reader');
      
      const config = { 
        fps: 10,
        qrbox: { width: 250, height: 250 }
      };

      // Función que se ejecuta al escanear correctamente
      const onScanSuccess = (decodedText) => {
        this.dni = decodedText.trim();
        this.closeScannerModal();
        this.fichar();
      };
      
      // Función que se ejecuta si hay un error
      const onScanFailure = () => {
        // No hace falta hacer nada aquí, pero la función es requerida por la librería
      };

      try {
        await this.html5QrcodeScanner.start(
          { facingMode: "environment" }, 
          config, 
          onScanSuccess, 
          onScanFailure
        );
      } catch (err) {
        this.scanError = 'No se pudo iniciar la cámara. Revisa los permisos.';
        console.error("Error al iniciar la cámara: ", err);
      }
    },

    async closeScannerModal() {
      if (this.html5QrcodeScanner) {
        try {
          await this.html5QrcodeScanner.stop();
          this.html5QrcodeScanner = null;
        } catch (err) {
          // A veces `stop()` puede dar un error si ya está detenido. Lo ignoramos.
        }
      }
      this.showScannerModal = false;
    }
  },
  created() {
    this.updateTime();
    this.intervalId = setInterval(this.updateTime, 1000);
  },
  beforeUnmount() {
    clearInterval(this.intervalId);
    if (this.html5QrcodeScanner) {
      this.closeScannerModal();
    }
  }
};
</script>

<style scoped>
/* Estilos generales */
.home-container { display: flex; justify-content: center; align-items: center; min-height: 100vh; background-color: #f0f2f5; }
.fichaje-wrapper { width: 100%; max-width: 450px; text-align: center; }
.time-display { margin-bottom: 2rem; }
.current-time { font-size: 4rem; font-weight: 700; color: #2c3e50; line-height: 1; }
.current-date { font-size: 1.1rem; color: #7f8c8d; }
.scan-badge-card { background: white; padding: 2rem; border-radius: 15px; box-shadow: 0 8px 25px rgba(0,0,0,0.08); cursor: pointer; transition: transform 0.2s, box-shadow 0.2s; }
.scan-badge-card:hover { transform: translateY(-5px); box-shadow: 0 12px 30px rgba(0,0,0,0.12); }
.barcode-visual { width: 100px; height: 60px; margin: 0 auto 1rem; background: repeating-linear-gradient(to right, #333, #333 4px, #fff 4px, #fff 8px); }
.scan-text { font-size: 1.2rem; font-weight: 600; color: #34495e; margin: 0; }
.or-separator { margin: 1.5rem 0; font-weight: bold; color: #95a5a6; }
.fichaje-card { background: white; padding: 2rem; border-radius: 12px; box-shadow: 0 8px 25px rgba(0,0,0,0.08); }
h2 { margin-top: 0; color: #34495e; }
.input-group { display: flex; gap: 0.5rem; }
.input-group input { flex-grow: 1; padding: 0.9rem; border: 1px solid #ccc; border-radius: 6px; font-size: 1rem; }
.input-group button { background: #3498db; color: white; border: none; padding: 0 1.5rem; border-radius: 6px; cursor: pointer; font-weight: bold; }
.admin-login-link { margin-top: 2rem; }
.admin-login-link a { color: #3498db; text-decoration: none; font-weight: 500; }
.message { margin-top: 1rem; padding: 0.7rem; border-radius: 4px; font-weight: 500; }
.error { color: #e74c3c; background: #fdeded; }
.modal-overlay { position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.6); display: flex; justify-content: center; align-items: center; z-index: 1000; }
.modal-content { padding: 3rem 4rem; border-radius: 10px; color: white; text-align: center; }
.modal-content h3 { font-size: 1.8rem; font-weight: bold; margin: 0 0 0.5rem 0; }
.modal-content p { font-size: 1rem; margin: 0; opacity: 0.9; }
.entrada-modal { background: #2ecc71; }
.salida-modal { background: #3498db; }

/* Estilos para el modal del escáner */
.scanner-modal {
  background: white;
  padding: 2rem;
  border-radius: 15px;
  width: 90%;
  max-width: 500px;
  color: #333;
}
.scanner-modal h3 {
  margin-top: 0;
  margin-bottom: 1.5rem;
}
#qr-reader {
  width: 100%;
  border-radius: 8px;
  overflow: hidden;
  border: 2px solid #eee;
  margin-bottom: 1.5rem;
}
.cancel-button {
  width: 100%;
  padding: 0.9rem;
  background: #95a5a6;
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 1.1rem;
  cursor: pointer;
  font-weight: bold;
}
</style>