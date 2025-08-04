<template>
  <div class="employee-records">
    <button @click="goBack" class="back-button">← Volver a Empleados</button>
    <h1>Registros de Asistencia</h1>

    <div v-if="loadingEmployeeDetails" class="loading-message">Cargando información del empleado...</div>
    <div v-else-if="employeeDetails.id_empleado" class="employee-details-summary">
      <h2>Información del Empleado</h2>
      <p><strong>DNI:</strong> {{ employeeDetails.id_empleado }}</p>
      <p><strong>Nombre Completo:</strong> {{ employeeDetails.nombre }} {{ employeeDetails.apellido }}</p>
      <p><strong>Teléfono:</strong> {{ employeeDetails.telefono || 'N/A' }}</p>
      <p><strong>Correo Electrónico:</strong> {{ employeeDetails.correo_electronico || 'N/A' }}</p>
      <p><strong>Género:</strong> {{ employeeDetails.genero || 'N/A' }}</p>
      <p><strong>Fecha de Nacimiento:</strong> {{ employeeDetails.fecha_nacimiento || 'N/A' }}</p>
      <p><strong>Departamento:</strong> {{ employeeDetails.departamento_nombre || 'N/A' }}</p>
      <p><strong>Cargo:</strong> {{ employeeDetails.cargo_nombre || 'N/A' }}</p>
      <p><strong>Horario:</strong> {{ employeeDetails.horario_nombre || 'N/A' }}
        <span v-if="employeeDetails.horario_entrada_esperada && employeeDetails.horario_salida_esperada">
          ({{ employeeDetails.horario_entrada_esperada.substring(0,5) }} - {{ employeeDetails.horario_salida_esperada.substring(0,5) }})
        </span>
      </p>
      <p><strong>Fecha de Contratación:</strong> {{ employeeDetails.fecha_contratacion || 'N/A' }}</p>
      <p><strong>Estado:</strong> <span :class="employeeDetails.activo ? 'status-active' : 'status-inactive'">{{ employeeDetails.activo ? 'Activo' : 'Inactivo' }}</span></p>
    </div>
    <hr>

    <div v-if="showAddRecordModal" class="modal-overlay" @click.self="closeAddRecordModal">
      <div class="modal-content add-record-modal-content">
        <h3>Añadir Nuevo Registro para {{ employeeName }}</h3>
        <form @submit.prevent="addRecord">
          <div class="form-group">
            <label for="new_record_tipo">Tipo:</label>
            <select id="new_record_tipo" v-model="newRecord.tipo" required>
              <option value="entrada">Entrada</option>
              <option value="salida">Salida</option>
            </select>
          </div>
          <div class="form-group">
            <label for="new_record_date">Fecha:</label>
            <input type="date" id="new_record_date" v-model="newRecord.timestamp_date" required class="modern-input">
          </div>
          <div class="form-group">
            <label for="new_record_time">Hora:</label>
            <input type="time" id="new_record_time" v-model="newRecord.timestamp_time" required class="modern-input">
          </div>
          <div class="form-group">
            <label for="new_record_observaciones">Observaciones:</label>
            <textarea id="new_record_observaciones" v-model="newRecord.observaciones" placeholder="Observaciones (opcional)"></textarea>
          </div>
          <div class="form-actions">
            <button type="submit" class="save-button">Guardar Registro</button>
            <button type="button" class="cancel-button" @click="closeAddRecordModal">Cancelar</button>
          </div>
        </form>
      </div>
    </div>

    <div v-if="showEditModal" class="modal-overlay" @click.self="closeEditModal">
      <div class="modal-content edit-record-modal">
        <h3>Editar Registro de Asistencia</h3>
        <form @submit.prevent="saveEditedRecord">
          <div class="form-group">
            <label for="edit_date">Fecha:</label>
            <input type="date" id="edit_date" v-model="recordToEdit.timestamp_date" required class="modern-input">
          </div>
          <div class="form-group">
            <label for="edit_time">Hora:</label>
            <input type="time" id="edit_time" v-model="recordToEdit.timestamp_time" required class="modern-input">
          </div>
          <div class="form-group">
            <label for="edit_tipo">Tipo:</label>
            <select id="edit_tipo" v-model="recordToEdit.tipo" required>
              <option value="entrada">Entrada</option>
              <option value="salida">Salida</option>
            </select>
          </div>
          <div class="form-group">
            <label for="edit_observaciones">Observaciones:</label>
            <textarea id="edit_observaciones" v-model="recordToEdit.observaciones"></textarea>
          </div>
          <div class="form-actions">
            <button type="submit" class="save-button">Guardar Cambios</button>
            <button type="button" class="cancel-button" @click="closeEditModal">Cancelar</button>
          </div>
        </form>
        <p v-if="editMessage" :class="{'success-message': editMessage.includes('éxito'), 'error-message': editMessage.includes('Error')}" class="message-status">{{ editMessage }}</p>
      </div>
    </div>

    <div v-if="showDeleteConfirmModal" class="modal-overlay" @click.self="cancelDeleteRecord">
      <div class="modal-content">
        <h3>Confirmar Eliminación</h3>
        <p>¿Estás seguro de que quieres eliminar el registro con ID: {{ recordIdToDeleteConfirm }}?</p>
        <button class="confirm-button" @click="confirmDeleteRecord">Sí, Eliminar</button>
        <button class="cancel-button" @click="cancelDeleteRecord">Cancelar</button>
      </div>
    </div>
    <hr>
    <div class="summary-section">
      <h2>Resumen de Horas Trabajadas</h2>

      <div v-if="isCurrentlyWorking" class="current-status-message">
        <p>✅ ¡Actualmente está trabajando!</p>
      </div>

      <div v-if="summaryHours.daily.length === 0 && summaryHours.monthly.length === 0 && !isCurrentlyWorking" class="no-records-message">
        No hay datos de resumen disponibles.
      </div>
      <div v-else class="summary-content">
        <div class="quick-summary-cards">
          <div class="summary-card quick-summary-card">
            <h4>Horas Trabajadas Hoy</h4>
            <p>{{ todayWorkedHours }}</p>
          </div>
          <div class="summary-card quick-summary-card">
            <h4>Horas Trabajadas Esta Semana</h4>
            <p>{{ thisWeekWorkedHours }}</p>
          </div>
          <div class="summary-card quick-summary-card">
            <h4>Horas Trabajadas Este Mes (Seleccionado)</h4>
            <p>{{ thisMonthWorkedHours }}</p>
          </div>
        </div>

        <div>
          <h3>Detalle Mensual</h3>

          <p v-if="addRecordMessage" :class="{'success-message': addRecordMessage.includes('éxito'), 'error-message': addRecordMessage.includes('Error')}" class="message-status">{{ addRecordMessage }}</p>
          <div class="detail-actions-row">
            <button @click="openAddRecordModal" class="add-new-record-button">➕ Añadir Nuevo Registro</button>
            <button @click="generateReport" class="export-report-button" :disabled="isExporting">
              <span v-if="!isExporting">📊 Exportar Reporte (Mes Actual)</span>
              <span v-else>Generando...</span>
            </button>
          </div>

          <div class="summary-month-selector">
            <button @click="prevSummaryMonth">←</button>
            <div class="summary-selectors-group">
              <select v-model="currentSummaryMonth" @change="setSummaryMonth">
                <option v-for="(month, index) in calendarMonths" :key="index" :value="index">{{ month }}</option>
              </select>
              <select v-model="currentSummaryYear" @change="setSummaryYear">
                <option v-for="year in calendarYears" :key="year" :value="year">{{ year }}</option>
              </select>
            </div>
            <button @click="nextSummaryMonth">→</button>
          </div>
          <div class="sort-controls">
            <button @click="toggleSortOrder" class="sort-button">
              Ordenar: {{ sortOrder === 'desc' ? 'Más Reciente Primero ↓' : 'Más Antiguo Primero ↑' }}
            </button>
          </div>
          <div v-if="filteredMonthlySummaryGrouped.length > 0">
            <div v-for="dayGroup in filteredMonthlySummaryGrouped" :key="dayGroup.date" class="summary-card detail-summary-card time-entry-card">
              <div class="time-entry-header">
                <div class="day-info">
                  <span class="day-name">{{ getDayName(dayGroup.date) }}</span>
                  <span class="date-number">{{ formatDateToDDMM(dayGroup.date) }}</span>
                </div>
                <div class="total-hours">
                  {{ dayGroup.totalFormatted }}
                </div>
              </div>
              <div class="time-entries">
                <div v-for="entry in dayGroup.entries" :key="entry.id_registro" class="time-entry-item">
                  <span class="entry-time">{{ formatTime(entry.timestamp) }}</span>
                  <span :class="{'entry-type': entry.tipo === 'entrada', 'exit-type': entry.tipo === 'salida'}">{{ entry.tipo.charAt(0).toUpperCase() + entry.tipo.slice(1) }}</span>
                  <span class="entry-observation">{{ entry.observaciones || '' }}</span>
                  <button class="action-button edit-button-small" @click="openEditModal(entry)">✏️</button>
                  <button class="action-button delete-button-small" @click="setRecordToDelete(entry.id_registro)">🗑️</button>
                </div>
              </div>
            </div>
          </div>
          <div v-else class="no-records-message">
            No hay registros de horas trabajadas para el mes seleccionado.
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  name: 'EmployeeRecordsView',
  props: ['employeeDni'],
  data() {
    return {
      employeeName: 'Empleado',
      records: [],
      loading: true,
      loadingEmployeeDetails: true,
      error: null,
      showEditModal: false,
      recordToEdit: null,
      editMessage: '',
      showDeleteConfirmModal: false,
      recordIdToDeleteConfirm: null,
      showAddRecordModal: false,
      newRecord: {
        id_empleado: this.employeeDni,
        tipo: 'entrada',
        timestamp_date: '',
        timestamp_time: '',
        observaciones: ''
      },
      addRecordMessage: '',
      employeeDetails: {
        id_empleado: '', nombre: '', apellido: '', telefono: '', correo_electronico: '',
        genero: '', fecha_nacimiento: '', activo: true, fecha_contratacion: '',
        id_departamento: null, departamento_nombre: '', id_cargo: null, cargo_nombre: '',
        id_horario: null, horario_nombre: '', horario_entrada_esperada: '', horario_salida_esperada: '',
        rol: ''
      },
      summaryHours: { daily: [], monthly: [] },
      isCurrentlyWorking: false,
      currentSummaryDate: new Date(),
      sortOrder: 'desc',
      isExporting: false,
    };
  },
  computed: {
    calendarMonths() {
      return ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'];
    },
    calendarYears() {
      const currentYear = new Date().getFullYear();
      const years = [];
      for (let i = currentYear - 10; i <= currentYear + 10; i++) {
        years.push(i);
      }
      return years;
    },
    currentSummaryMonth: {
      get() { return this.currentSummaryDate.getMonth(); },
      set(value) { this.currentSummaryDate = new Date(this.currentSummaryDate.getFullYear(), value, 1); }
    },
    currentSummaryYear: {
      get() { return this.currentSummaryDate.getFullYear(); },
      set(value) { this.currentSummaryDate = new Date(value, this.currentSummaryDate.getMonth(), 1); }
    },
    todayWorkedHours() {
      const today = this.getTodayDateString();
      const summary = this.summaryHours.daily.find(s => s.date === today);
      return summary ? summary.formatted : '0h 0m';
    },
    thisWeekWorkedHours() {
      const today = new Date();
      const thisWeekNum = this.getWeekNumberLocal(today);
      const thisYear = today.getFullYear();
      let totalMsThisWeek = 0;
      this.summaryHours.daily.forEach(daySummary => {
        const parts = daySummary.date.split('-').map(Number);
        const dayDateLocal = new Date(parts[0], parts[1] - 1, parts[2]);
        if (dayDateLocal.getFullYear() === thisYear && this.getWeekNumberLocal(dayDateLocal) === thisWeekNum) {
          totalMsThisWeek += daySummary.totalDurationMs;
        }
      });
      return this.formatMillisecondsToHoursMinutes(totalMsThisWeek);
    },
    thisMonthWorkedHours() {
      const selectedMonthKey = `${this.currentSummaryDate.getFullYear()}-${String(this.currentSummaryDate.getMonth() + 1).padStart(2, '0')}`;
      const summary = this.summaryHours.monthly.find(s => s.month === selectedMonthKey);
      return summary ? summary.formatted : '0h 0m';
    },
    filteredMonthlySummaryGrouped() {
      const selectedYear = this.currentSummaryDate.getFullYear();
      const selectedMonth = String(this.currentSummaryDate.getMonth() + 1).padStart(2, '0');
      const monthKey = `${selectedYear}-${selectedMonth}`;

      const grouped = {};
      this.records.forEach(record => {
        const recordDate = new Date(record.timestamp);
        const dayKey = this.formatDateToYYYYMMDD(recordDate);

        if (dayKey.startsWith(monthKey)) {
          if (!grouped[dayKey]) {
            grouped[dayKey] = { date: dayKey, entries: [], totalDurationMs: 0, totalFormatted: '0h 0m' };
          }
          grouped[dayKey].entries.push(record);
        }
      });

      Object.values(grouped).forEach(dayGroup => {
        dayGroup.entries.sort((a, b) => new Date(a.timestamp) - new Date(b.timestamp));
        const dailySummary = this.summaryHours.daily.find(s => s.date === dayGroup.date);
        dayGroup.totalDurationMs = dailySummary ? dailySummary.totalDurationMs : 0;
        dayGroup.totalFormatted = dailySummary ? dailySummary.formatted : '0h 0m';
      });

      const sortedGroups = Object.values(grouped).sort((a, b) => {
        if (this.sortOrder === 'asc') { return a.date.localeCompare(b.date); }
        else { return b.date.localeCompare(a.date); }
      });
      return sortedGroups;
    },
  },
  methods: {
    goBack() { this.$router.push('/admin/empleados'); },
    async fetchEmployeeDetails() {
      this.loadingEmployeeDetails = true; this.error = null;
      try {
        const response = await axios.get(`/api/empleados/${this.employeeDni}`);
        if (response.data) { this.employeeDetails = response.data; this.employeeName = `${response.data.nombre} ${response.data.apellido}`; }
      } catch (err) { this.employeeName = 'Desconocido'; this.error = 'No se pudo cargar la información del empleado.'; console.error('Error al cargar detalles del empleado:', err); }
      finally { this.loadingEmployeeDetails = false; }
    },
    async fetchRecords() {
      this.loading = true; this.error = null;
      try {
        const response = await axios.get(`/api/registros?empleado_dni=${this.employeeDni}`);
        this.records = response.data;
        this.calculateWorkedHoursSummary();
        this.checkCurrentlyWorking();
      } catch (error) { this.error = 'Error al cargar los registros de asistencia.'; this.records = []; console.error('Error al cargar registros del empleado:', error); }
      finally { this.loading = false; }
    },
    formatTime(isoString) { return new Date(isoString).toLocaleTimeString('es-ES', { hour: '2-digit', minute: '2-digit' }); },
    getDayName(dateString) {
      const parts = dateString.split('-').map(Number);
      const date = new Date(parts[0], parts[1] - 1, parts[2]);
      return date.toLocaleDateString('es-ES', { weekday: 'short' });
    },
    formatDateToDDMM(dateString) {
      const parts = dateString.split('-').map(Number);
      const date = new Date(parts[0], parts[1] - 1, parts[2]);
      const day = String(date.getDate()).padStart(2, '0');
      const month = date.toLocaleDateString('es-ES', { month: 'short' });
      return `${day} ${month}`;
    },
    openEditModal(record) {
      const recordDateLocal = new Date(record.timestamp);
      this.recordToEdit = { ...record, timestamp_date: this.formatDateToYYYYMMDD(recordDateLocal), timestamp_time: this.formatTimeToHHMM(recordDateLocal) };
      this.editMessage = ''; this.showEditModal = true;
    },
    closeEditModal() { this.showEditModal = false; this.recordToEdit = null; this.editMessage = ''; },
    async saveEditedRecord() {
      this.editMessage = '';
      if (!this.recordToEdit.timestamp_date || !this.recordToEdit.timestamp_time || !this.recordToEdit.tipo) { this.editMessage = 'Fecha, hora y tipo son obligatorios.'; return; }
      try {
        const timestampToSend = `${this.recordToEdit.timestamp_date}T${this.recordToEdit.timestamp_time}:00`;
        const dataToSend = { timestamp: timestampToSend, tipo: this.recordToEdit.tipo, observaciones: this.recordToEdit.observaciones };
        await axios.put(`/api/registros/${this.recordToEdit.id_registro}`, dataToSend);
        this.editMessage = 'Registro actualizado con éxito.'; this.fetchRecords();
        setTimeout(() => { this.closeEditModal(); }, 1500);
      } catch (error) { this.editMessage = error.response?.data?.message || 'Error desconocido al actualizar el registro.'; console.error('Error al guardar cambios:', error); }
    },
    setRecordToDelete(recordId) { this.recordIdToDeleteConfirm = recordId; this.showDeleteConfirmModal = true; },
    cancelDeleteRecord() { this.showDeleteConfirmModal = false; this.recordIdToDeleteConfirm = null; },
    async confirmDeleteRecord() {
      if (!this.recordIdToDeleteConfirm) return;
      try {
        await axios.delete(`/api/registros/${this.recordIdToDeleteConfirm}`);
        this.editMessage = 'Registro eliminado con éxito.'; this.fetchRecords();
        setTimeout(() => { this.cancelDeleteRecord(); this.editMessage = ''; }, 1500);
      } catch (error) { this.editMessage = error.response?.data?.message || 'Error desconocido al eliminar el registro.'; console.error('Error al eliminar registro:', error); }
      finally { this.showDeleteConfirmModal = false; this.recordIdToDeleteConfirm = null; }
    },
    openAddRecordModal() {
      this.resetAddRecordForm();
      this.newRecord.timestamp_date = this.formatDateToYYYYMMDD(new Date());
      this.newRecord.timestamp_time = this.formatTimeToHHMM(new Date());
      this.showAddRecordModal = true;
    },
    closeAddRecordModal() { this.showAddRecordModal = false; this.addRecordMessage = ''; },
    async addRecord() {
      this.addRecordMessage = '';
      if (!this.newRecord.id_empleado || !this.newRecord.tipo || !this.newRecord.timestamp_date || !this.newRecord.timestamp_time) { this.addRecordMessage = 'DNI, tipo, fecha y hora son obligatorios para el registro.'; return; }
      try {
        const timestampToSend = `${this.newRecord.timestamp_date}T${this.newRecord.timestamp_time}:00`;
        const recordToSend = { id_empleado: this.employeeDni, tipo: this.newRecord.tipo, timestamp: timestampToSend, observaciones: this.newRecord.observaciones };
        await axios.post('/api/registros', recordToSend);
        this.addRecordMessage = 'Registro añadido con éxito.'; this.resetAddRecordForm(); this.fetchRecords();
        setTimeout(() => { this.closeAddRecordModal(); }, 1500);
      } catch (error) { this.addRecordMessage = error.response?.data?.message || 'Error desconocido al añadir registro.'; console.error('Error al añadir registro:', error); }
    },
    resetAddRecordForm() {
      this.newRecord = { id_empleado: this.employeeDni, tipo: 'entrada', timestamp_date: '', timestamp_time: '', observaciones: '' };
      this.addRecordMessage = '';
    },
    formatDateToYYYYMMDD(date) {
      const year = date.getFullYear();
      const month = String(date.getMonth() + 1).padStart(2, '0');
      const day = String(date.getDate()).padStart(2, '0');
      return `${year}-${month}-${day}`;
    },
    formatTimeToHHMM(date) {
      const hours = String(date.getHours()).padStart(2, '0');
      const minutes = String(date.getMinutes()).padStart(2, '0');
      return `${hours}:${minutes}`;
    },
    getTodayDateString() { return this.formatDateToYYYYMMDD(new Date()); },
    calculateWorkedHoursSummary() {
      this.summaryHours = { daily: [], monthly: [] };
      if (!this.records || this.records.length === 0) { return; }
      const dailyDurations = new Map();
      const sortedRecords = [...this.records].sort((a, b) => new Date(a.timestamp) - new Date(b.timestamp));
      const employeeActiveShift = new Map();

      sortedRecords.forEach(record => {
        const recordDate = new Date(record.timestamp);
        if (record.tipo === 'entrada') {
          employeeActiveShift.set(record.id_empleado, { type: 'entrada', timestamp: recordDate });
        } else if (record.tipo === 'salida') {
          const entry = employeeActiveShift.get(record.id_empleado);
          if (entry && entry.type === 'entrada') {
            const entryTimestamp = entry.timestamp;
            const exitTimestamp = recordDate;
            const entryDayKey = this.formatDateToYYYYMMDD(entryTimestamp);
            const exitDayKey = this.formatDateToYYYYMMDD(exitTimestamp);

            if (entryDayKey === exitDayKey) {
              const durationMs = exitTimestamp - entryTimestamp;
              dailyDurations.set(entryDayKey, (dailyDurations.get(entryDayKey) || 0) + durationMs);
            } else {
              // --- INICIO DE LA CORRECCIÓN PARA EL CÁLCULO DE MEDIANOCHE ---
              const boundaryMidnight = new Date(exitTimestamp.getFullYear(), exitTimestamp.getMonth(), exitTimestamp.getDate(), 0, 0, 0, 0);
              const durationOnEntryDay = boundaryMidnight - entryTimestamp;
              dailyDurations.set(entryDayKey, (dailyDurations.get(entryDayKey) || 0) + durationOnEntryDay);
              const durationOnExitDay = exitTimestamp - boundaryMidnight;
              dailyDurations.set(exitDayKey, (dailyDurations.get(exitDayKey) || 0) + durationOnExitDay);
              // --- FIN DE LA CORRECCIÓN ---
            }
            employeeActiveShift.delete(record.id_empleado);
          }
        }
      });

      this.summaryHours.daily = Array.from(dailyDurations.entries()).map(([date, ms]) => {
        return {
          date: date, totalDurationMs: ms,
          formatted: this.formatMillisecondsToHoursMinutes(ms)
        };
      }).sort((a, b) => b.date.localeCompare(a.date));

      const monthlyDurations = new Map();
      this.summaryHours.daily.forEach(daySummary => {
        const parts = daySummary.date.split('-').map(Number);
        const dateLocal = new Date(parts[0], parts[1] - 1, parts[2]);
        const monthKey = `${dateLocal.getFullYear()}-${String(dateLocal.getMonth() + 1).padStart(2, '0')}`;
        monthlyDurations.set(monthKey, (monthlyDurations.get(monthKey) || 0) + daySummary.totalDurationMs);
      });

      this.summaryHours.monthly = Array.from(monthlyDurations.entries()).map(([month, ms]) => {
        return {
          month: month,
          formatted: this.formatMillisecondsToHoursMinutes(ms)
        };
      }).sort((a, b) => b.month.localeCompare(a.month));
    },
    checkCurrentlyWorking() {
      this.isCurrentlyWorking = false;
      const employeeActiveShift = new Map();
      const sortedRecords = [...this.records].sort((a, b) => new Date(a.timestamp) - new Date(b.timestamp));
      sortedRecords.forEach(record => {
        if (record.tipo === 'entrada') { employeeActiveShift.set(record.id_empleado, record); }
        else if (record.tipo === 'salida') { employeeActiveShift.delete(record.id_empleado); }
      });
      if (employeeActiveShift.has(this.employeeDni)) { this.isCurrentlyWorking = true; }
    },
    formatMillisecondsToHoursMinutes(ms) {
      const totalSeconds = Math.floor(ms / 1000);
      const hours = Math.floor(totalSeconds / 3600);
      const minutes = Math.floor((totalSeconds % 3600) / 60);
      return `${hours}h ${minutes}m`;
    },
    getWeekNumberLocal(d) {
      d = new Date(d.getFullYear(), d.getMonth(), d.getDate());
      d.setDate(d.getDate() + 4 - (d.getDay() || 7));
      var yearStart = new Date(d.getFullYear(), 0, 4);
      var weekNo = Math.ceil((((d - yearStart) / 86400000) + 1) / 7);
      return weekNo;
    },
    prevSummaryMonth() {
      this.currentSummaryDate = new Date(this.currentSummaryDate.getFullYear(), this.currentSummaryDate.getMonth() - 1, 1);
    },
    nextSummaryMonth() {
      this.currentSummaryDate = new Date(this.currentSummaryDate.getFullYear(), this.currentSummaryDate.getMonth() + 1, 1);
    },
    setSummaryMonth(event) {
      const newMonth = parseInt(event.target.value);
      this.currentSummaryDate = new Date(this.currentSummaryDate.getFullYear(), newMonth, 1);
    },
    setSummaryYear(event) {
      const newYear = parseInt(event.target.value);
      this.currentSummaryDate = new Date(newYear, this.currentSummaryDate.getMonth(), 1);
    },
    toggleSortOrder() {
      this.sortOrder = this.sortOrder === 'desc' ? 'asc' : 'desc';
    },
   async generateReport() {
    if (this.isExporting) return;
    this.isExporting = true;
    try {
        const year = this.currentSummaryDate.getFullYear();
        const month = this.currentSummaryDate.getMonth() + 1;

        // Obtenemos el offset de la zona horaria del NAVEGADOR en minutos.
        // getTimezoneOffset() devuelve la diferencia en minutos entre UTC y la hora local.
        const timezoneOffsetMinutes = new Date().getTimezoneOffset();

        const response = await axios.get('/api/reports/attendance_summary', {
            params: {
                employee_dni: this.employeeDni,
                month: month,
                year: year,
                // Enviamos el offset al backend para que el reporte se genere en la hora local correcta
                timezone_offset_minutes: timezoneOffsetMinutes
            },
            responseType: 'blob',
        });

        const url = window.URL.createObjectURL(new Blob([response.data]));
        const link = document.createElement('a');
        link.href = url;

        const contentDisposition = response.headers['content-disposition'];
        let fileName = `Reporte_${this.employeeDni}_${year}-${month}.xlsx`;
        if (contentDisposition) {
            const fileNameMatch = contentDisposition.match(/filename="(.+)"/);
            if (fileNameMatch && fileNameMatch.length === 2) {
                fileName = fileNameMatch[1];
            }
        }
        link.setAttribute('download', fileName);
        document.body.appendChild(link);
        link.click();
        link.remove();
        window.URL.revokeObjectURL(url);

    } catch (error) {
        console.error("Error al generar el reporte:", error);
        alert("No se pudo generar el reporte. Verifique la consola para más detalles.");
    } finally {
        this.isExporting = false;
    }
}
  },
  mounted() {
    if (this.employeeDni) {
      this.fetchEmployeeDetails();
      this.fetchRecords();
      this.currentSummaryDate = new Date();
    } else {
      this.error = 'DNI del empleado no proporcionado en la URL.';
      this.loading = false;
    }
  }
};
</script>

<style scoped>

.employee-records {
  padding: 20px;
  font-family: 'Arial', sans-serif;
  max-width: 900px;
  margin: 0 auto;
  background-color: #f9f9f9;
  border-radius: 10px;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
  color: #333;
}
.back-button {
  background-color: #6c757d;
  margin-bottom: 20px;
  padding: 10px 15px;
  font-size: 0.9em;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  color: white;
}
.back-button:hover { background-color: #5a6268; }
h1 { color: #2c3e50; margin-bottom: 30px; text-align: center; }
h2 { color: #34495e; margin-top: 30px; margin-bottom: 15px; border-bottom: 2px solid #eee; padding-bottom: 10px; }
.loading-message, .error-message, .no-records-message { padding: 20px; margin-top: 20px; border-radius: 8px; font-size: 1.1em; text-align: center; }
.loading-message { background-color: #e0f7fa; color: #007bff; }
.error-message { background-color: #ffe0b2; color: #ff9800; }
.no-records-message { background-color: #fff3cd; color: #856404; }
.modal-overlay {
  position: fixed; top: 0; left: 0; width: 100%; height: 100%;
  background-color: rgba(0, 0, 0, 0.6);
  display: flex; justify-content: center; align-items: center; z-index: 9999;
}
.modal-content {
  background-color: white; padding: 30px; border-radius: 10px;
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.3); text-align: center;
  max-width: 450px; width: 90%; position: relative;
}
.modal-content h3 { color: #333; margin-bottom: 20px; }
.modal-content .confirm-button { background-color: #dc3545; color: white; margin-right: 10px; }
.modal-content .cancel-button { background-color: #6c757d; color: white; }
.add-record-modal-content, .edit-record-modal {
  text-align: left;
}
.form-group {
  margin-bottom: 1rem;
}
.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: bold;
  color: #555;
}
.form-group input, .form-group select, .form-group textarea {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #ccc;
  border-radius: 6px;
  font-size: 1rem;
  box-sizing: border-box;
  transition: border-color 0.2s, box-shadow 0.2s;
}
.form-group input:focus, .form-group select:focus, .form-group textarea:focus {
  border-color: #007bff;
  box-shadow: 0 0 0 3px rgba(0, 123, 255, 0.25);
  outline: none;
}
.form-group textarea {
  min-height: 80px;
  resize: vertical;
}
.form-actions {
  margin-top: 1.5rem;
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}
.save-button { background-color: #28a745; color: white; }
.message-status { margin-top: 10px; font-weight: bold; text-align: center; }
.success-message { color: #28a745; }
.employee-details-summary {
  background-color: #e6f7ff; border: 1px solid #91d5ff; border-radius: 8px;
  padding: 20px; margin-top: 20px; text-align: left; box-shadow: 0 2px 5px rgba(0,0,0,0.05);
}
.employee-details-summary h2 { color: #1890ff; margin-top: 0; }
.status-active { color: #52c41a; font-weight: bold; }
.status-inactive { color: #f5222d; font-weight: bold; }
.summary-section {
  margin-top: 40px; padding: 20px; background-color: #f0f8ff;
  border-radius: 10px; box-shadow: 0 4px 8px rgba(0, 0, 0, 0.05);
}
.summary-section h2 { color: #1890ff; border-bottom-color: #bce0ff; text-align: center; }
.current-status-message {
  background-color: #d4edda; color: #155724; padding: 15px; border-radius: 8px;
  margin-bottom: 20px; font-weight: bold; font-size: 1.1em; border: 1px solid #c3e6cb; text-align: center;
}
.summary-content h3 { color: #34495e; text-align: center; }
.detail-actions-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 1.5rem;
    flex-wrap: wrap;
    gap: 1rem;
}
.add-new-record-button { background-color: #28a745; }
.add-new-record-button:hover { background-color: #218838; }
.export-report-button {
    background-color: #007bff;
    color: white;
}
.export-report-button:hover:not(:disabled) {
    background-color: #0056b3;
}
.quick-summary-cards { display: flex; justify-content: space-around; flex-wrap: wrap; gap: 20px; margin-bottom: 30px; }
.quick-summary-card { flex: 1; min-width: 250px; max-width: 30%; background-color: #f8f9fa; border: 1px solid #e0e0e0; box-shadow: 0 2px 8px rgba(0,0,0,0.05); padding: 20px; border-radius: 10px; text-align: center; }
.quick-summary-card h4 { color: #007bff; margin-top: 0; margin-bottom: 10px; }
.quick-summary-card p { font-size: 1.8em; font-weight: bold; color: #333; }
.summary-month-selector { display: flex; justify-content: center; align-items: center; margin-bottom: 20px; gap: 10px; background-color: #f0f0f0; padding: 10px; border-radius: 8px; }
.summary-month-selector button { background-color: #007bff; color: white; border: none; border-radius: 5px; padding: 8px 12px; cursor: pointer; }
.summary-month-selector select { padding: 8px; border-radius: 5px; border: 1px solid #ccc; }
.sort-controls { margin-bottom: 20px; text-align: right; }
.sort-button { background-color: #f0f0f0; color: #555; border: 1px solid #ccc; padding: 8px 15px; border-radius: 8px; cursor: pointer; }
.time-entry-card { background-color: #ffffff; border: 1px solid #e0e0e0; border-radius: 10px; padding: 15px 20px; margin-bottom: 15px; box-shadow: 0 2px 5px rgba(0,0,0,0.05); }
.time-entry-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px; padding-bottom: 10px; border-bottom: 1px solid #f0f0f0; }
.day-info { display: flex; flex-direction: column; align-items: flex-start; }
.day-name { font-size: 1.2em; font-weight: bold; color: #34495e; text-transform: uppercase; }
.date-number { font-size: 0.9em; color: #777; }
.total-hours { font-size: 1.5em; font-weight: bold; color: #42b983; }
.time-entries { margin-top: 10px; }
.time-entry-item { display: flex; align-items: center; gap: 10px; padding: 8px 0; border-bottom: 1px dotted #eee; }
.time-entry-item:last-child { border-bottom: none; }
.entry-time { font-weight: bold; color: #555; width: 70px; }
.entry-type { font-weight: bold; color: #28a745; }
.exit-type { color: #007bff; }
.entry-observation { color: #666; flex-grow: 1; }
.action-button { background: none; border: none; cursor: pointer; font-size: 1em; }
.edit-button-small { color: #f39c12; }
.delete-button-small { color: #e74c3c; }
</style>