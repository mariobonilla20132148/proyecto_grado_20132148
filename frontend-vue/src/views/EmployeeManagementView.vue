<template>
  <div class="management-view">
    <div class="header">
      <h1>Gestión de Empleados</h1>
      <button @click="openModal()" class="add-button">Añadir Empleado</button>
    </div>

    <div class="controls-container">
      <input type="text" v-model="searchQuery" placeholder="Buscar por Nombre, Apellido o DNI..." class="search-input">
      <div class="custom-select-wrapper">
        <select v-model="filterDepartment" @change="filterCargo = null">
          <option :value="null">Todos los Departamentos</option>
          <option v-for="d in formData.departments" :value="d.id" :key="d.id">{{ d.nombre }}</option>
        </select>
        <span class="custom-select-arrow"></span>
      </div>
      <div class="custom-select-wrapper">
        <select v-model="filterCargo" :disabled="!filterDepartment">
          <option :value="null">Todos los Cargos</option>
          <option v-for="c in tableCargosFilter" :value="c.id" :key="c.id">{{ c.nombre }}</option>
        </select>
        <span class="custom-select-arrow"></span>
      </div>
      <div class="custom-select-wrapper">
        <select v-model="sortBy">
          <option value="nombre">Ordenar por Nombre (A-Z)</option>
          <option value="apellido">Ordenar por Apellido (A-Z)</option>
          <option value="id_empleado">Ordenar por DNI</option>
        </select>
        <span class="custom-select-arrow"></span>
      </div>
    </div>

    <div v-if="loading" class="loading-message">Cargando empleados...</div>
    <div v-else-if="error" class="error-message">{{ error }}</div>
    
    <div v-else class="table-container"> 
      <table>
        <thead>
          <tr>
            <th>Estado</th>
            <th>DNI</th>
            <th>Nombre Completo</th>
            <th>Teléfono</th>
            <th>Departamento</th>
            <th>Cargo</th>
            <th class="actions-header">Acciones</th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="processedEmployees.length === 0">
            <td colspan="7" class="no-data-row">No se encontraron empleados.</td>
          </tr>
          <tr v-for="emp in processedEmployees" :key="emp.id_empleado">
            <td>
              <span :class="['status-dot', emp.activo ? 'active' : 'inactive']"></span>
              {{ emp.activo ? 'Activo' : 'Inactivo' }}
            </td>
            <td>{{ emp.id_empleado }}</td>
            <td>{{ emp.nombre }} {{ emp.apellido }}</td>
            <td>{{ emp.telefono || 'N/A' }}</td>
            <td>{{ emp.departamento_nombre || 'N/A' }}</td>
            <td>{{ emp.cargo_nombre || 'N/A' }}</td>
            <td class="actions-cell">
              <button @click="viewRecords(emp.id_empleado)" class="action-btn view-btn" title="Ver Registros">📄</button>
              <button @click="openModal(emp)" class="action-btn edit-btn" title="Editar">✏️</button>
              <button @click="promptDelete(emp)" class="action-btn delete-btn" title="Eliminar">🗑️</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <div v-if="isModalOpen" class="modal-overlay" @click.self="closeModal">
      <div class="modal-content">
        <h3 class="modal-header">{{ isEditing ? 'Editar Empleado' : 'Añadir Nuevo Empleado' }}</h3>
        
        <div class="form-container">
          <form @submit.prevent="handleSubmit" id="employee-form">
            <div class="form-grid">
              
              <h4 class="form-section-header full-width-grid-item">Datos Personales</h4>
              <div class="form-group"><label>DNI</label><input v-model="form.id_empleado" :disabled="isEditing" required class="form-input-field"></div>
              <div class="form-group"><label>Nombre</label><input v-model="form.nombre" required class="form-input-field"></div>
              <div class="form-group"><label>Apellido</label><input v-model="form.apellido" required class="form-input-field"></div>
              <div class="form-group"><label>Email</label><input type="email" v-model="form.correo_electronico" class="form-input-field"></div>
              <div class="form-group"><label>Teléfono</label><input v-model="form.telefono" class="form-input-field"></div>
              <div class="form-group"><label>Fecha de Nacimiento</label><input type="date" v-model="form.fecha_nacimiento" class="form-input-field"></div>
              <div class="form-group full-width-grid-item">
                  <label>Género</label>
                  <div class="custom-select-wrapper form-select-field">
                      <select v-model="form.genero">
                          <option value="">Seleccionar</option>
                          <option value="Masculino">Masculino</option>
                          <option value="Femenino">Femenino</option>
                      </select>
                      <span class="custom-select-arrow"></span>
                  </div>
              </div>

              <h4 class="form-section-header full-width-grid-item">Información Laboral</h4>
              <div class="form-group">
                  <label>Departamento</label>
                  <div class="custom-select-wrapper form-select-field">
                      <select v-model="form.id_departamento" @change="handleDepartmentChange" required>
                          <option :value="null" disabled>Seleccione...</option>
                          <option v-for="d in formData.departments" :value="d.id" :key="d.id">{{d.nombre}}</option>
                      </select>
                      <span class="custom-select-arrow"></span>
                  </div>
              </div>
              <div class="form-group">
                  <label>Cargo</label>
                  <div class="custom-select-wrapper form-select-field">
                      <select v-model="form.id_cargo" required :disabled="!form.id_departamento">
                          <option :value="null" disabled>Seleccione un depto.</option>
                          <option v-for="c in modalCargosFilter" :value="c.id" :key="c.id">{{c.nombre}}</option>
                      </select>
                      <span class="custom-select-arrow"></span>
                  </div>
              </div>
              <div class="form-group"><label>Fecha de Contratación</label><input type="date" v-model="form.fecha_contratacion" required class="form-input-field"></div>
              <div class="form-group">
                  <label>Horario</label>
                  <div class="custom-select-wrapper form-select-field">
                      <select v-model="form.id_horario" required>
                          <option :value="null" disabled>Seleccione...</option>
                          <option v-for="h in formData.horarios" :value="h.id" :key="h.id">{{h.nombre}}</option>
                      </select>
                      <span class="custom-select-arrow"></span>
                  </div>
              </div>

              <h4 class="form-section-header full-width-grid-item">Credenciales y Sistema</h4>
              <div class="form-group">
                  <label>Rol</label>
                  <div class="custom-select-wrapper form-select-field">
                      <select v-model="form.rol" required>
                          <option value="empleado">Empleado</option>
                          <option value="admin">Administrador</option>
                      </select>
                      <span class="custom-select-arrow"></span>
                  </div>
              </div>
              <div class="form-group">
                  <label>Contraseña</label>
                  <input type="password" v-model="form.password" :placeholder="isEditing ? 'Dejar en blanco para no cambiar' : 'Contraseña inicial requerida'" :required="!isEditing" class="form-input-field">
              </div>
              
              <div v-if="isEditing" class="form-group full-width-grid-item status-toggle-group">
                <label>Estado del Empleado</label>
                <div class="status-toggle">
                  <span :class="{ 'active-label': !form.activo }">Inactivo</span>
                  <label class="switch">
                    <input type="checkbox" v-model="form.activo">
                    <span class="slider round"></span>
                  </label>
                  <span :class="{ 'active-label': form.activo }">Activo</span>
                </div>
              </div>
            </div>
          </form>
        </div>

        <div class="modal-actions">
          <button type="button" @click="closeModal" class="cancel-btn">Cancelar</button>
          <button type="submit" form="employee-form" class="submit-btn">
            {{ isEditing ? 'Guardar Cambios' : 'Crear Empleado' }}
          </button>
        </div>
      </div>
    </div>

    <div v-if="showDeleteModal" class="modal-overlay">
        <div class="modal-content delete-confirm-modal">
            <h3>Confirmar Eliminación</h3>
            <p>¿Estás seguro de que quieres eliminar a <strong>{{ itemToDelete.nombre }} {{ itemToDelete.apellido }}</strong>?</p>
            <p class="warning">Esta acción no se puede deshacer.</p>
            <div class="modal-actions centered-actions">
                <button @click="closeDeleteModal" class="cancel-btn">Cancelar</button>
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
      employees: [], loading: true, error: null, isModalOpen: false, isEditing: false, form: {},
      formData: { departments: [], cargos: [], horarios: [] },
      showDeleteModal: false, itemToDelete: null,
      searchQuery: '',
      sortBy: 'nombre',
      filterDepartment: null,
      filterCargo: null,
    };
  },
  computed: {
    processedEmployees() {
      let filtered = [...this.employees];
      if (this.searchQuery) {
        const query = this.searchQuery.toLowerCase();
        filtered = filtered.filter(emp => 
          emp.nombre.toLowerCase().includes(query) ||
          emp.apellido.toLowerCase().includes(query) ||
          emp.id_empleado.toLowerCase().includes(query)
        );
      }
      if (this.filterDepartment) {
        filtered = filtered.filter(emp => emp.id_departamento == this.filterDepartment);
      }
      if (this.filterCargo) {
        filtered = filtered.filter(emp => emp.id_cargo == this.filterCargo);
      }
      return filtered.sort((a, b) => {
        if (a[this.sortBy] < b[this.sortBy]) return -1;
        if (a[this.sortBy] > b[this.sortBy]) return 1;
        return 0;
      });
    },
    modalCargosFilter() {
      if (!this.form.id_departamento) return [];
      return this.formData.cargos.filter(c => c.id_departamento == this.form.id_departamento);
    },
    tableCargosFilter() {
        if (!this.filterDepartment) return [];
        return this.formData.cargos.filter(c => c.id_departamento == this.filterDepartment);
    }
  },
  methods: {
    handleDepartmentChange() {
        this.form.id_cargo = null;
    },
    async fetchEmployees() {
      this.loading = true; this.error = null;
      try {
        const response = await axios.get('/api/empleados');
        this.employees = response.data;
      } catch (error) {
        this.error = "No se pudieron cargar los empleados."; console.error(error);
      } finally { this.loading = false; }
    },
    async fetchFormData() {
      try {
        const response = await axios.get('/api/data_for_forms');
        this.formData = response.data;
      } catch (error) { console.error("Error cargando datos para formularios:", error); }
    },
    openModal(employee = null) {
      if (employee) {
        this.isEditing = true;
        this.form = { 
            ...employee, 
            password: '', 
            fecha_nacimiento: employee.fecha_nacimiento ? new Date(employee.fecha_nacimiento).toISOString().split('T')[0] : null,
            fecha_contratacion: employee.fecha_contratacion ? new Date(employee.fecha_contratacion).toISOString().split('T')[0] : null,
        };
      } else {
        this.isEditing = false;
        this.form = { 
            fecha_contratacion: new Date().toISOString().split('T')[0],
            activo: true, rol: 'empleado', genero: '',
            id_departamento: null, id_cargo: null, id_horario: null,
            password: ''
        };
      }
      this.isModalOpen = true;
    },
    closeModal() { this.isModalOpen = false; this.form = {}; },
    async handleSubmit() {
      if (!this.isEditing && (!this.form.password || this.form.password.length < 6)) {
        alert('Para un nuevo empleado, la contraseña es requerida y debe tener al menos 6 caracteres.');
        return;
      }

      const apiCall = this.isEditing 
        ? axios.put(`/api/empleados/${this.form.id_empleado}`, this.form)
        : axios.post('/api/empleados', this.form);
      try {
        await apiCall;
        this.closeModal(); this.fetchEmployees();
      } catch (error) {
        alert(error.response?.data?.message || 'Ocurrió un error.');
      }
    },
    promptDelete(employee) {
        this.itemToDelete = employee;
        this.showDeleteModal = true;
    },
    closeDeleteModal() {
        this.showDeleteModal = false; this.itemToDelete = null;
    },
    async confirmDelete() {
        if (!this.itemToDelete) return;
        try {
            await axios.delete(`/api/empleados/${this.itemToDelete.id_empleado}`);
            this.closeDeleteModal(); this.fetchEmployees();
        } catch (error) { alert(error.response?.data?.message || 'No se pudo eliminar.'); }
    },
    viewRecords(dni) { 
      this.$router.push({ name: 'admin-employee-records', params: { employeeDni: dni } }); 
    }
  },
  async created() {
    this.fetchFormData(); this.fetchEmployees();
  }
};
</script>

<style scoped>
/* Estilos generales */
.management-view { max-width: 1200px; margin: auto; padding: 2rem; }
.header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 2rem; }
h1 { color: #2c3e50; }
.controls-container { display: flex; flex-wrap: wrap; gap: 1rem; margin-bottom: 2rem; padding: 1rem; background: #f8f9fa; border-radius: 8px; }
.search-input { flex: 2 1 300px; padding: 0.75rem; border: 1px solid #ccc; border-radius: 5px; }
.custom-select-wrapper { position: relative; display: inline-block; flex: 1 1 180px; }
.custom-select-wrapper select { -webkit-appearance: none; -moz-appearance: none; appearance: none; background-color: #fefefe; border: 1px solid #ccc; border-radius: 8px; padding: 0.75rem 30px 0.75rem 10px; font-size: 1em; width: 100%; cursor: pointer; outline: none; box-sizing: border-box; }
.custom-select-arrow { position: absolute; right: 10px; top: 50%; transform: translateY(-50%); width: 0; height: 0; pointer-events: none; border-left: 6px solid transparent; border-right: 6px solid transparent; border-top: 6px solid #666; }
.table-container { width: 100%; overflow-x: auto; margin-bottom: 2rem; }
table { width: 100%; min-width: 768px; border-collapse: collapse; background: white; box-shadow: 0 2px 10px rgba(0,0,0,0.05); }
th, td { border-bottom: 1px solid #ddd; padding: 1rem; text-align: left; }
th { background-color: #f8f9fa; }
.actions-header { text-align: right; }
.actions-cell { text-align: right; white-space: nowrap; }

.status-dot { height: 10px; width: 10px; border-radius: 50%; display: inline-block; margin-right: 8px; }
.status-dot.active { background-color: #27ae60; }
.status-dot.inactive { background-color: #e74c3c; }

.add-button, .cancel-btn, .submit-btn, .confirm-delete-btn {
  padding: 0.8rem 1.5rem;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 1em;
  font-weight: bold;
  color: white;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
  min-width: 160px;
  text-align: center;
}

.add-button { background-color: #3498db; }
.cancel-btn { background: #95a5a6; }
.submit-btn { background: #27ae60; }
.confirm-delete-btn { background: #e74c3c; }
.action-btn { background: none; border: none; padding: 0.4rem; font-size: 1.1em; color: #555; box-shadow: none; transition: color 0.2s ease, transform 0.1s ease; }
.view-btn { color: #1abc9c; }
.edit-btn { color: #f39c12; }
.delete-btn { color: #e74c3c; }
.no-data-row { text-align: center; color: #7f8c8d; padding: 2rem; }
.modal-overlay { position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.6); display: flex; justify-content: center; align-items: center; z-index: 1000; }
.modal-content { background: white; padding: 0; border-radius: 8px; width: 800px; max-width: 90%; display: flex; flex-direction: column; max-height: 90vh; }
.modal-header { padding: 1.5rem 2rem; margin: 0; border-bottom: 1px solid #eee; }
.form-container { overflow-y: auto; padding: 1.5rem 2rem; }
.delete-confirm-modal { width: 400px; text-align: center; padding: 2rem; max-height: none; }
.warning { font-size: 0.9rem; color: #e67e22; }


.form-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1rem 1.5rem; 
}
.form-input-field {
  width: 100%;
  padding: 0.75rem;
  box-sizing: border-box;
  border: 1px solid #ccc;
  border-radius: 4px;
  font-size: 1em;
}
.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
  padding: 1rem 2rem;
  border-top: 1px solid #f9f9f9;
  background: #f9f9f9;
}
.modal-actions.centered-actions {
  justify-content: center;
}


.form-group {
}
.form-group label {
  display: block; 
  margin-bottom: 0.4rem; 
  font-weight: 600;
  font-size: 0.9em;
  color: #34495e;
}
.status-toggle > label.switch {
  margin-bottom: 0; 
}


.full-width-grid-item {
  grid-column: 1 / -1;
}

.form-section-header {
  grid-column: 1 / -1;
  color: #3498db;
  border-bottom: 2px solid #eaedf1;
  padding-bottom: 0.75rem;
  margin-top: 1rem;
  margin-bottom: 0; 
  font-size: 1.1em;
}
.form-section-header:first-of-type {
    margin-top: 0;
}


.status-toggle-group {
  padding-bottom: 5px;
}
.status-toggle {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}
.status-toggle span {
  font-weight: bold;
  color: #bdc3c7;
  transition: color 0.2s ease;
}
.status-toggle .active-label {
  color: #2c3e50;
}
.switch {
  position: relative;
  display: inline-block;
  width: 60px;
  height: 34px;
}
.switch input { 
  opacity: 0;
  width: 0;
  height: 0;
}
.slider {
  position: absolute;
  cursor: pointer;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: #e74c3c;
  transition: .4s;
}
.slider:before {
  position: absolute;
  content: "";
  height: 26px;
  width: 26px;
  left: 4px;
  bottom: 4px;
  background-color: white;
  transition: .4s;
}
input:checked + .slider {
  background-color: #27ae60;
}
input:checked + .slider:before {
  transform: translateX(26px);
}
.slider.round {
  border-radius: 34px;
}
.slider.round:before {
  border-radius: 50%;
}
</style>