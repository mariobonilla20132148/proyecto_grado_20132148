<template>
  <div class="records-view">
    <div v-if="loading" class="loading-message">Cargando tus datos...</div>
    <div v-else-if="error" class="error-message">{{ error }}</div>
    <div v-else>
      <div class="employee-header">
        <h1>Mis Registros de Asistencia</h1>
        <p>Hola, {{ employee.nombre }}. Aquí está tu historial.</p>
        <p v-if="employee.horario_nombre">Tu horario asignado: {{ employee.horario_nombre }} ({{ employee.horario_entrada_esperada?.substring(0,5) }} - {{ employee.horario_salida_esperada?.substring(0,5) }})</p>
      </div>

      <hr>

      <div class="summary-section">
        <h2>Resumen de Horas Trabajadas</h2>
        
        <div v-if="isCurrentlyWorking" class="current-status-message">
          <p>✅ ¡Actualmente estás trabajando!</p>
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
  </div>
</template>

<script>
import axios from 'axios';
export default {
  data() {
    return {
      loading: true, error: null, employee: {}, records: [],
      employeeDni: localStorage.getItem('userDni'),

      summaryHours: {
        daily: [],
        monthly: []
      },
      isCurrentlyWorking: false,
      currentSummaryDate: new Date(), 
      sortOrder: 'desc', 
    };
  },
  computed: {
  
    calendarMonths() {
      return [
        'Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
        'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'
      ];
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
      get() {
        return this.currentSummaryDate.getMonth();
      },
      set(value) {
        this.currentSummaryDate = new Date(this.currentSummaryDate.getFullYear(), value, 1);
      }
    },
    currentSummaryYear: {
      get() {
        return this.currentSummaryDate.getFullYear();
      },
      set(value) {
        this.currentSummaryDate = new Date(value, this.currentSummaryDate.getMonth(), 1);
      }
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
        const recordDateLocal = new Date(record.timestamp); 
        const dayKey = this.formatDateToYYYYMMDD(recordDateLocal); 
        
        if (dayKey.startsWith(monthKey)) {
          if (!grouped[dayKey]) {
            grouped[dayKey] = {
              date: dayKey,
              entries: [],
              totalDurationMs: 0,
              totalFormatted: '0h 0m'
            };
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
        if (this.sortOrder === 'asc') {
          return a.date.localeCompare(b.date);
        } else {
          return b.date.localeCompare(a.date);
        }
      });

      return sortedGroups;
    },
    // Removed: sortedRawRecords()
  },
  methods: {
    async fetchData() {
      if (!this.employeeDni) {
        this.error = "No se pudo identificar tu usuario.";
        this.loading = false;
        return;
      }
      try {
        const [employeeRes, recordsRes] = await Promise.all([
          axios.get(`/api/empleados/${this.employeeDni}`),
          axios.get(`/api/registros?empleado_dni=${this.employeeDni}`)
        ]);
        this.employee = employeeRes.data;
        this.records = recordsRes.data;
        this.calculateWorkedHoursSummary(); 
        this.checkCurrentlyWorking(); 
      } catch (err) {
        this.error = "No se pudieron cargar tus datos.";
        console.error("Error fetching data for MyRecordsView:", err);
      } finally {
        this.loading = false;
      }
    },
    formatDate(iso) { return new Date(iso).toLocaleDateString('es-ES'); },
    formatTime(iso) { return new Date(iso).toLocaleTimeString('es-ES', { hour: '2-digit', minute: '2-digit' }); },
    
    getTodayDateString() {
      return this.formatDateToYYYYMMDD(new Date());
    },
    formatDateToYYYYMMDD(date) {
      const year = date.getFullYear();
      const month = String(date.getMonth() + 1).padStart(2, '0');
      const day = String(date.getDate()).padStart(2, '0');
      return `${year}-${month}-${day}`;
    },
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
    calculateWorkedHoursSummary() {
      this.summaryHours = { daily: [], monthly: [] };

      if (!this.records || this.records.length === 0) {
        return;
      }

      const dailyDurations = new Map();
      const sortedRecords = [...this.records].sort((a, b) => new Date(a.timestamp) - new Date(b.timestamp));
      const employeeActiveShift = new Map(); 

      sortedRecords.forEach(record => {
        const recordDateLocal = new Date(record.timestamp); 
        
        if (record.tipo === 'entrada') {
          employeeActiveShift.set(record.id_empleado, { type: 'entrada', timestamp: recordDateLocal });
        } else if (record.tipo === 'salida') {
          const entry = employeeActiveShift.get(record.id_empleado);
          if (entry && entry.type === 'entrada') {
            const entryTimestamp = entry.timestamp;
            const exitTimestamp = recordDateLocal;

            const entryDayKey = this.formatDateToYYYYMMDD(entryTimestamp);
            const exitDayKey = this.formatDateToYYYYMMDD(exitTimestamp);

            if (entryDayKey === exitDayKey) {
              const durationMs = exitTimestamp - entryTimestamp;
              dailyDurations.set(entryDayKey, (dailyDurations.get(entryDayKey) || 0) + durationMs);
            } else {
              const endOfEntryDay = new Date(entryTimestamp.getFullYear(), entryTimestamp.getMonth(), entryTimestamp.getDate(), 23, 59, 59, 999);
              const durationOnEntryDay = endOfEntryDay - entryTimestamp;
              dailyDurations.set(entryDayKey, (dailyDurations.get(entryDayKey) || 0) + durationOnEntryDay);

              const startOfExitDay = new Date(exitTimestamp.getFullYear(), exitTimestamp.getMonth(), exitTimestamp.getDate(), 0, 0, 0, 0);
              const durationOnExitDay = exitTimestamp - startOfExitDay;
              dailyDurations.set(exitDayKey, (dailyDurations.get(exitDayKey) || 0) + durationOnExitDay);
            }
            employeeActiveShift.delete(record.id_empleado); 
          }
        }
      });
      
      this.summaryHours.daily = Array.from(dailyDurations.entries()).map(([date, ms]) => {
        return {
          date: date,
          totalDurationMs: ms, 
          totalHours: Math.floor(ms / 3600000),
          totalMinutes: Math.floor((ms % 3600000) / 60000),
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
          totalHours: Math.floor(ms / 3600000),
          totalMinutes: Math.floor((ms % 3600000) / 60000),
          formatted: this.formatMillisecondsToHoursMinutes(ms)
        };
      }).sort((a, b) => b.month.localeCompare(a.month));
    },
    checkCurrentlyWorking() {
      this.isCurrentlyWorking = false;
      const employeeActiveShift = new Map();
      const sortedRecords = [...this.records].sort((a, b) => new Date(a.timestamp) - new Date(b.timestamp));

      sortedRecords.forEach(record => {
        if (record.tipo === 'entrada') {
          employeeActiveShift.set(record.id_empleado, record);
        } else if (record.tipo === 'salida') {
          employeeActiveShift.delete(record.id_empleado);
        }
      });

      if (employeeActiveShift.has(this.employeeDni)) {
        this.isCurrentlyWorking = true;
      }
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
    }
  },
  created() {
    this.fetchData();
    this.currentSummaryDate = new Date(); 
  }
};
</script>

<style scoped>
.records-view { max-width: 900px; margin: auto; padding: 2rem; background-color: #f9f9f9; border-radius: 10px; box-shadow: 0 4px 8px rgba(0,0,0,0.1); color: #333; }
.employee-header { border-bottom: 2px solid #eee; padding-bottom: 1rem; margin-bottom: 2rem; text-align: center; }
h1 { margin: 0; color: #2c3e50; font-size: 2.2em; }
p { font-size: 1.1em; color: #34495e; margin-top: 0.5em; }

hr {
  border: 0;
  height: 1px;
  background-color: #ddd;
  margin: 30px 0;
  width: 100%;
}

.loading-message, .error-message, .no-records-message {
  padding: 20px;
  margin-top: 20px;
  border-radius: 8px;
  font-size: 1.1em;
  text-align: center;
}

.loading-message { background-color: #e0f7fa; color: #007bff; }
.error-message { background-color: #ffe0b2; color: #ff9800; }
.no-records-message { background-color: #fff3cd; color: #856404; }


.summary-section {
  margin-top: 20px; 
  padding: 20px;
  background-color: #e6f7ff; 
  border-radius: 10px;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}

.summary-section h2 {
  color: #1890ff;
  margin-bottom: 25px;
  border-bottom: 2px solid #91d5ff;
  padding-bottom: 10px;
  text-align: center; 
}

.current-status-message {
  background-color: #d4edda; 
  color: #155724; 
  padding: 15px;
  border-radius: 8px;
  margin-bottom: 20px;
  font-weight: bold;
  font-size: 1.1em;
  border: 1px solid #c3e6cb;
  text-align: center;
}

.quick-summary-cards {
  display: flex;
  justify-content: space-around;
  flex-wrap: wrap;
  gap: 20px;
  margin-bottom: 30px;
}

.quick-summary-card {
  flex: 1;
  min-width: 250px;
  max-width: 30%; 
  background-color: #f8f9fa;
  border: 1px solid #e0e0e0;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  padding: 20px;
  border-radius: 10px;
  text-align: center;
}

.quick-summary-card h4 {
  color: #007bff;
  margin-top: 0;
  margin-bottom: 10px;
  font-size: 1.3em;
}

.quick-summary-card p {
  font-size: 1.8em;
  font-weight: bold;
  color: #333;
}

.summary-content h3 {
  color: #34495e;
  margin-top: 30px;
  margin-bottom: 20px;
  font-size: 1.6em;
  border-bottom: 1px solid #eee;
  padding-bottom: 10px;
  text-align: center;
}

.summary-month-selector {
  display: flex;
  justify-content: center;
  align-items: center;
  margin-bottom: 20px;
  gap: 10px;
  background-color: #f0f0f0;
  padding: 10px;
  border-radius: 8px;
  box-shadow: inset 0 1px 3px rgba(0,0,0,0.05);
}

.summary-month-selector button {
  background-color: #007bff;
  color: white;
  border: none;
  border-radius: 5px;
  padding: 8px 12px;
  cursor: pointer;
  font-size: 1em;
  transition: background-color 0.2s ease;
  box-shadow: none;
  margin: 0;
  flex-shrink: 0;
}

.summary-month-selector button:hover {
  background-color: #0056b3;
}

.summary-selectors-group {
  display: flex;
  gap: 5px;
  flex-grow: 1;
  justify-content: center;
}

.summary-month-selector select {
  box-sizing: border-box;
  padding: 8px;
  border: 1px solid #ccc;
  border-radius: 5px;
  font-size: 1em;
  background-color: #fefefe;
  flex-shrink: 1;
  flex-basis: 48%;
  min-width: 95px;
}

.sort-controls {
  margin-bottom: 20px;
  text-align: right;
}

.sort-button {
  background-color: #f0f0f0;
  color: #555;
  border: 1px solid #ccc;
  padding: 8px 15px;
  border-radius: 8px;
  cursor: pointer;
  font-size: 0.9em;
  transition: background-color 0.2s ease, transform 0.2s ease;
}

.sort-button:hover {
  background-color: #e0e0e0;
  transform: translateY(-1px);
}

.detail-summary-card {
  background-color: white;
  border: 1px solid #e0e0e0;
  border-radius: 10px;
  padding: 15px 20px;
  margin-bottom: 15px;
  box-shadow: 0 2px 5px rgba(0,0,0,0.05);
  text-align: left; 
}

.time-entry-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
  padding-bottom: 10px;
  border-bottom: 1px solid #f0f0f0;
}

.day-info {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
}

.day-name {
  font-size: 1.2em;
  font-weight: bold;
  color: #34495e;
  text-transform: uppercase;
}

.date-number {
  font-size: 0.9em;
  color: #777;
}

.total-hours {
  font-size: 1.5em;
  font-weight: bold;
  color: #42b983;
}

.time-entries {
  margin-top: 10px;
}

.time-entry-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px 0;
  border-bottom: 1px dotted #eee;
}

.time-entry-item:last-child {
  border-bottom: none;
}

.entry-time {
  font-weight: bold;
  color: #555;
  flex-shrink: 0;
  width: 70px;
}

.entry-type {
  font-weight: bold;
  flex-shrink: 0;
  width: 60px;
}
.entry-type.entrada { color: #28a745; }
.entry-type.salida { color: #007bff; }

.entry-observation {
  color: #666;
  flex-grow: 1;
  text-align: left;
}

@media (max-width: 768px) {
  .records-view {
    padding: 1rem;
  }
  h1 {
    font-size: 1.8em;
  }
  p {
    font-size: 1em;
  }
  .quick-summary-cards {
    flex-direction: column;
    align-items: center;
  }
  .quick-summary-card {
    max-width: 90%;
    width: 100%;
  }
  .summary-month-selector {
    flex-direction: column;
  }
  .summary-selectors-group {
    width: 100%;
    flex-direction: row;
  }
  .summary-month-selector select {
    width: 100%;
  }
  .time-entry-item {
    flex-wrap: wrap;
    justify-content: space-between;
  }
  .entry-time, .entry-type {
    width: auto;
    flex-basis: 45%;
  }
  .entry-observation {
    flex-basis: 100%;
    margin-top: 5px;
  }
}
</style>