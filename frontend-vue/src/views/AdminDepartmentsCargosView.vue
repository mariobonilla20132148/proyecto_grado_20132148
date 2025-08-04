<template>
  <div class="admin-view">
    <h1>Gestión Administrativa</h1>
    <p class="subtitle">Añade, visualiza y elimina los datos maestros del sistema.</p>

    <div class="admin-section">
      <h2>Departamentos</h2>
      <form @submit.prevent="addDepartment" class="add-form">
        <input v-model="newDepartment.nombre" placeholder="Nombre del nuevo departamento" required>
        <button type="submit" class="add-button">Añadir</button>
      </form>
      <div v-if="loading.departments" class="loading-text">Cargando...</div>
      <div v-else-if="error.departments" class="error-text">{{ error.departments }}</div>
      <table v-else-if="data.departments.length > 0">
        <tbody>
          <tr v-for="dept in data.departments" :key="dept.id">
            <td>{{ dept.nombre }}</td>
            <td class="actions-cell">
              <button @click="promptDelete('departments', dept)" class="delete-btn" title="Borrar">🗑️</button>
            </td>
          </tr>
        </tbody>
      </table>
      <div v-else class="no-data-text">No hay departamentos creados.</div>
    </div>

    <div class="admin-section">
      <h2>Cargos</h2>
      <form @submit.prevent="addCargo" class="add-form">
        <input v-model="newCargo.nombre" placeholder="Nombre del nuevo cargo" required>
        <div class="custom-select-wrapper">
          <select v-model="newCargo.id_departamento" required>
            <option :value="null" disabled>Asignar a Departamento</option>
            <option v-for="dept in data.departments" :key="dept.id" :value="dept.id">{{ dept.nombre }}</option>
          </select>
          <span class="custom-select-arrow"></span>
        </div>
        <button type="submit" class="add-button">Añadir</button>
      </form>
      <div v-if="loading.cargos" class="loading-text">Cargando...</div>
      <div v-else-if="error.cargos" class="error-text">{{ error.cargos }}</div>
      <table v-else-if="data.cargos.length > 0">
        <tbody>
          <tr v-for="cargo in data.cargos" :key="cargo.id">
            <td>
              {{ cargo.nombre }}
              <small>({{ getDepartmentName(cargo.id_departamento) }})</small>
            </td>
            <td class="actions-cell">
              <button @click="promptDelete('cargos', cargo)" class="delete-btn" title="Borrar">🗑️</button>
            </td>
          </tr>
        </tbody>
      </table>
      <div v-else class="no-data-text">No hay cargos creados.</div>
    </div>

    <div class="admin-section">
      <h2>Horarios</h2>
      <form @submit.prevent="addHorario" class="add-form horario-form">
        <input v-model="newHorario.nombre" placeholder="Nombre del horario (ej. Turno Mañana)" required>
        <input type="time" v-model="newHorario.entrada" required title="Hora de Entrada">
        <input type="time" v-model="newHorario.salida" required title="Hora de Salida">
        <button type="submit" class="add-button">Añadir</button>
      </form>
      <div v-if="loading.horarios" class="loading-text">Cargando...</div>
      <div v-else-if="error.horarios" class="error-text">{{ error.horarios }}</div>
      <table v-else-if="data.horarios.length > 0">
        <tbody>
          <tr v-for="horario in data.horarios" :key="horario.id">
            <td>{{ horario.nombre }} ({{ formatTimeDisplay(horario.hora_entrada_esperada) }} - {{ formatTimeDisplay(horario.hora_salida_esperada) }})</td>
            <td class="actions-cell">
              <button @click="promptDelete('horarios', horario)" class="delete-btn" title="Borrar">🗑️</button>
            </td>
          </tr>
        </tbody>
      </table>
      <div v-else class="no-data-text">No hay horarios creados.</div>
    </div>

    <div v-if="showDeleteModal" class="modal-overlay" @click.self="closeDeleteModal">
      <div class="modal-content">
        <h3>Confirmar Eliminación</h3>
        <p>¿Estás seguro de que quieres eliminar <strong>"{{ itemToDelete.name }}"</strong>?</p>
        <p v-if="deleteError" class="error-text modal-error">{{ deleteError }}</p>
        <div class="modal-actions">
          <button @click="closeDeleteModal" class="cancel-button">Cancelar</button>
          <button @click="confirmDelete" class="confirm-delete-btn">Sí, Eliminar</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';
export default {
  data() {
    return {
      data: { departments: [], cargos: [], horarios: [] },
      loading: { departments: true, cargos: true, horarios: true },
      error: { departments: null, cargos: null, horarios: null },
      newDepartment: { nombre: '' },
      newCargo: { nombre: '', id_departamento: null },
      newHorario: { nombre: '', entrada: '09:00', salida: '17:00' },
      showDeleteModal: false,
      itemToDelete: { id: null, type: '', name: '' },
      deleteError: null
    };
  },
  methods: {
    async fetchData(type) {
      this.loading[type] = true; this.error[type] = null;
      try {
        const response = await axios.get(`/api/${type}`);
        this.data[type] = response.data;
      } catch (error) {
        this.error[type] = `Error al cargar ${type}.`;
        console.error(`Error fetching ${type}:`, error);
      } finally {
        this.loading[type] = false;
      }
    },
    getDepartmentName(deptId) {
        const dept = this.data.departments.find(d => d.id === deptId);
        return dept ? dept.nombre : 'N/A';
    },
    formatTimeDisplay(timeString) {
        // timeString will be "HH:MM:SS" from the backend
        // We want to display "HH:MM"
        if (!timeString) return 'N/A';
        return timeString.substring(0, 5); // Takes "HH:MM"
    },
    async addDepartment() {
      try {
        await axios.post('/api/departments', { nombre_departamento: this.newDepartment.nombre });
        this.newDepartment.nombre = '';
        this.fetchData('departments');
      } catch (error) { alert(error.response?.data?.message || 'Error al añadir.'); }
    },
    async addCargo() {
      if (!this.newCargo.id_departamento) return alert("Por favor, selecciona un departamento.");
      try {
        await axios.post('/api/cargos', { nombre_cargo: this.newCargo.nombre, id_departamento: this.newCargo.id_departamento });
        this.newCargo = { nombre: '', id_departamento: null };
        this.fetchData('cargos');
      } catch (error) { alert(error.response?.data?.message || 'Error al añadir.'); }
    },
    async addHorario() {
      try {
        await axios.post('/api/horarios', { nombre_horario: this.newHorario.nombre, hora_entrada_esperada: this.newHorario.entrada, hora_salida_esperada: this.newHorario.salida });
        this.newHorario = { nombre: '', entrada: '09:00', salida: '17:00' };
        this.fetchData('horarios');
      } catch (error) { alert(error.response?.data?.message || 'Error al añadir.'); }
    },
    promptDelete(type, item) {
      this.itemToDelete = { id: item.id, type: type, name: item.nombre };
      this.deleteError = null;
      this.showDeleteModal = true;
    },
    closeDeleteModal() {
      this.showDeleteModal = false;
    },
    async confirmDelete() {
      const { type, id } = this.itemToDelete;
      try {
        await axios.delete(`/api/${type}/${id}`);
        this.closeDeleteModal();
        this.fetchData(type);
        if (type === 'departments') {
          this.fetchData('cargos');
        }
      } catch (error) {
        this.deleteError = error.response?.data?.message || 'Error al borrar.';
      }
    }
  },
  created() {
    this.fetchData('departments');
    this.fetchData('cargos');
    this.fetchData('horarios');
  }
};
</script>

<style scoped>
.admin-view { max-width: 800px; margin: auto; padding: 2rem; }
h1 { text-align: center; color: #2c3e50; }
.subtitle { text-align: center; color: #7f8c8d; margin-top: 0; margin-bottom: 3rem; }
.admin-section { background: white; padding: 1.5rem 2rem; border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.08); margin-bottom: 2rem; }
h2 { margin-top: 0; border-bottom: 2px solid #ecf0f1; padding-bottom: 0.75rem; margin-bottom: 1.5rem; color: #34495e; }
.add-form { display: flex; gap: 0.75rem; margin-bottom: 1.5rem; }

/* Input and Select styling (from EmployeeManagementView) */
input, select {
  flex-grow: 1;
  padding: 0.75rem;
  border: 1px solid #bdc3c7;
  border-radius: 5px; /* Softer corners */
  font-size: 1rem;
  box-sizing: border-box; /* Include padding in width/height */
}
input:focus, select:focus {
  border-color: #007bff;
  box-shadow: 0 0 0 3px rgba(0, 123, 255, 0.25);
  outline: none;
}

/* Custom Select Wrapper (from EmployeeManagementView) */
.custom-select-wrapper {
  position: relative;
  display: inline-block;
  flex-grow: 1; /* Allow it to grow in flex containers */
}

.custom-select-wrapper select {
  -webkit-appearance: none;
  -moz-appearance: none;
  appearance: none;
  background-color: #fefefe;
  border: 1px solid #ccc;
  border-radius: 8px;
  padding: 0.75rem 30px 0.75rem 10px;
  font-size: 1em;
  width: 100%;
  cursor: pointer;
  outline: none;
}

.custom-select-wrapper select:hover {
  border-color: #a0a0a0;
}

.custom-select-wrapper select:focus {
  border-color: #007bff;
  box-shadow: 0 0 0 3px rgba(0, 123, 255, 0.25);
}

.custom-select-arrow {
  position: absolute;
  right: 10px;
  top: 50%;
  transform: translateY(-50%);
  width: 0;
  height: 0;
  pointer-events: none;
  border-left: 6px solid transparent;
  border-right: 6px solid transparent;
  border-top: 6px solid #666;
}


/* --- Button Base Styles for this component --- */
/* These styles are specifically for buttons within this component's scope. */
.add-button, .delete-btn, .cancel-button, .confirm-delete-btn {
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

/* Hover effect */
.add-button:hover:not(:disabled), .delete-btn:hover:not(:disabled), .cancel-button:hover:not(:disabled), .confirm-delete-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 6px 12px rgba(0, 0, 0, 0.15);
}

/* Active (click) effect */
.add-button:active:not(:disabled), .delete-btn:active:not(:disabled), .cancel-button:active:not(:disabled), .confirm-delete-btn:active:not(:disabled) {
  transform: translateY(0);
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

/* Disabled state */
.add-button:disabled, .delete-btn:disabled, .cancel-button:disabled, .confirm-delete-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: translateY(0);
  box-shadow: none;
}


/* Specific button colors */
.add-button { background-color: #27ae60; } /* Green for add */
.add-button:hover:not(:disabled) { background-color: #229a53; }

.delete-btn { 
  background: none; /* No background for icon buttons */
  border: none;
  padding: 0.2em; /* Smaller padding for icons */
  font-size: 1.2rem; /* Larger icon size */
  color: #c0392b; /* Red icon color */
  box-shadow: none; /* No shadow */
  transition: color 0.2s ease, transform 0.1s ease;
}
.delete-btn:hover:not(:disabled) {
  color: #e74c3c; /* Darker red on hover */
  transform: scale(1.1); /* Slight zoom on hover */
}


.cancel-button { background: #bdc3c7; } /* Light grey for cancel */
.cancel-button:hover:not(:disabled) { background: #aeb6bf; }

.confirm-delete-btn { background: #e74c3c; } /* Red for confirm delete */
.confirm-delete-btn:hover:not(:disabled) { background: #c0392b; }


.horario-form input[type="time"] { flex-grow: 0; min-width: 120px; }
table { width: 100%; }
td { padding: 0.8rem 0.2rem; border-bottom: 1px solid #ecf0f1; }
tr:last-child td { border-bottom: none; }
small { color: #7f8c8d; }
.actions-cell { text-align: right; width: 1%; }

.loading-text, .error-text, .no-data-text { text-align: center; padding: 2rem; color: #95a5a6; font-style: italic; }
.error-text { color: #c0392b; font-weight: bold; }

/* Modal Styles */
.modal-overlay { position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.6); display: flex; justify-content: center; align-items: center; z-index: 1000; }
.modal-content { background: white; padding: 2rem; border-radius: 8px; text-align: center; width: 90%; max-width: 400px; box-shadow: 0 5px 15px rgba(0,0,0,0.3); }
.modal-content h3 { margin-top: 0; }
.modal-actions { display: flex; justify-content: center; gap: 1rem; margin-top: 1.5rem; }


.modal-error { margin-top: 1rem; color: #e74c3c; background-color: #fdd; padding: 0.5rem; border-radius: 4px; }

/* Responsive adjustments */
@media (max-width: 600px) {
  .admin-view {
    padding: 10px;
  }
  h1 {
    font-size: 1.8em;
  }
  .subtitle {
    font-size: 0.9em;
  }
  .admin-section {
    padding: 1rem;
  }
  h2 {
    font-size: 1.5em;
    margin-bottom: 1rem;
  }
  .add-form {
    flex-direction: column;
    gap: 0.5rem;
    margin-bottom: 1rem;
  }
  .add-form input, .add-form .custom-select-wrapper, .add-form button { /* Apply to custom-select-wrapper */
    width: 100%;
    flex-grow: 1;
  }
  .horario-form input[type="time"] {
    min-width: unset;
    width: 100%;
  }
  table {
    display: block;
    width: 100%;
    overflow-x: auto;
    -webkit-overflow-scrolling: touch;
  }
  td.actions-cell {
    min-width: 80px;
  }
  .modal-content {
    padding: 15px;
  }
}
</style>