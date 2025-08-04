<template>
  <div class="dashboard-view">
    <h1>Dashboard Administrativo</h1>

    <div v-if="loading" class="loading-message">Cargando datos del dashboard...</div>
    <div v-else-if="error" class="error-message">{{ error }}</div>

    <div v-else class="dashboard-grid">
      <div class="stats-cards">
        <div class="stat-card">
          <h3>Total de Empleados</h3>
          <p class="stat-number">{{ summary.total_employees }}</p>
        </div>
        <div class="stat-card">
          <h3>Empleados Activos</h3>
          <p class="stat-number">{{ summary.active_employees }}</p>
        </div>
        <div class="stat-card">
          <h3>Trabajando Ahora</h3>
          <p class="stat-number">{{ summary.clocked_in_count }}</p>
        </div>
      </div>

      <div class="recent-activity-card">
        <h2>Actividad Reciente</h2>
        <ul v-if="summary.recent_records.length > 0">
          <li v-for="record in summary.recent_records" :key="record.id_registro">
            <span :class="['chip', record.tipo]">{{ record.tipo }}</span>
            <span class="activity-name">{{ record.nombre_completo }}</span>
            <span class="activity-time">{{ formatRelativeTime(record.timestamp) }}</span>
          </li>
        </ul>
        <p v-else>No hay registros recientes.</p>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  name: 'DashboardView',
  data() {
    return {
      loading: true,
      error: null,
      summary: {
        total_employees: 0,
        active_employees: 0,
        clocked_in_count: 0,
        recent_records: [],
      },
    };
  },
  methods: {
    async fetchSummary() {
      this.loading = true;
      this.error = null;
      try {
        const response = await axios.get('/api/dashboard_summary');
        this.summary = response.data;
      } catch (err) {
        this.error = 'No se pudieron cargar los datos del dashboard.';
        console.error(err);
      } finally {
        this.loading = false;
      }
    },
    formatRelativeTime(isoString) {
      const date = new Date(isoString);
      const now = new Date();
      const diffSeconds = Math.round((now - date) / 1000);

      if (diffSeconds < 60) return `hace ${diffSeconds} seg`;
      const diffMinutes = Math.round(diffSeconds / 60);
      if (diffMinutes < 60) return `hace ${diffMinutes} min`;
      const diffHours = Math.round(diffMinutes / 60);
      if (diffHours < 24) return `hace ${diffHours} h`;
      
      return date.toLocaleDateString('es-ES');
    },
  },
  mounted() {
    this.fetchSummary();
  },
};
</script>

<style scoped>
.dashboard-view {
  max-width: 1200px;
  margin: auto;
}

h1 {
  text-align: center;
  margin-bottom: 2rem;
  color: #2c3e50;
}

.stats-cards {
  display: flex;
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.stat-card {
  flex: 1;
  background: white;
  padding: 1.5rem;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.08);
  text-align: center;
}

.stat-card h3 {
  margin: 0 0 0.5rem 0;
  font-size: 1rem;
  color: #7f8c8d;
  text-transform: uppercase;
}

.stat-number {
  margin: 0;
  font-size: 2.5rem;
  font-weight: bold;
  color: #34495e;
}

.recent-activity-card {
  background: white;
  padding: 1.5rem;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.08);
}

.recent-activity-card h2 {
  margin-top: 0;
  border-bottom: 1px solid #ecf0f1;
  padding-bottom: 1rem;
}

.recent-activity-card ul {
  list-style: none;
  padding: 0;
  margin: 0;
}

.recent-activity-card li {
  display: flex;
  align-items: center;
  padding: 0.75rem 0;
  border-bottom: 1px solid #f9f9f9;
}

.recent-activity-card li:last-child {
  border-bottom: none;
}

.chip {
  padding: 0.25rem 0.6rem;
  border-radius: 12px;
  font-size: 0.8rem;
  font-weight: bold;
  color: white;
  width: 60px;
  text-align: center;
  margin-right: 1rem;
}

.chip.entrada {
  background-color: #27ae60;
}
.chip.salida {
  background-color: #3498db;
}

.activity-name {
  font-weight: bold;
  color: #2c3e50;
}

.activity-time {
  margin-left: auto;
  font-size: 0.9rem;
  color: #95a5a6;
}
</style>