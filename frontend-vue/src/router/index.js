import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import LoginView from '../views/LoginView.vue'
import EmployeeManagementView from '../views/EmployeeManagementView.vue'
import AdminDepartmentsCargosView from '../views/AdminDepartmentsCargosView.vue'
import MyRecordsView from '../views/MyRecordsView.vue'
import EmployeeRecordsView from '../views/EmployeeRecordsView.vue'
import DashboardView from '../views/DashboardView.vue' // 1. Importar el nuevo Dashboard

const routes = [
  { 
    path: '/', 
    name: 'home', 
    component: HomeView 
  },
  { 
    path: '/login', 
    name: 'login', 
    component: LoginView 
  },
  { // 2. Añadir la nueva ruta para el Dashboard
    path: '/dashboard',
    name: 'dashboard',
    component: DashboardView,
    meta: { requiresAuth: true, requiresAdmin: true }
  },
  {
    path: '/mis-registros',
    name: 'my-records',
    component: MyRecordsView,
    meta: { requiresAuth: true }
  },
  {
    path: '/admin/empleados',
    name: 'admin-empleados',
    component: EmployeeManagementView,
    meta: { requiresAuth: true, requiresAdmin: true }
  },
  {
    path: '/admin/gestion',
    name: 'admin-gestion',
    component: AdminDepartmentsCargosView,
    meta: { requiresAuth: true, requiresAdmin: true }
  },
  {
    path: '/admin/registros/:employeeDni',
    name: 'admin-employee-records',
    component: EmployeeRecordsView,
    props: true,
    meta: { requiresAuth: true, requiresAdmin: true }
  }
]

const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes
})

// 3. Mejorar la lógica de redirección para administradores
router.beforeEach((to, from, next) => {
  const isAuthenticated = !!localStorage.getItem('userDni');
  const userRole = localStorage.getItem('userRole');

  // Si un admin logueado intenta ir a la página de fichaje, lo redirigimos a su dashboard
  if (to.name === 'home' && isAuthenticated && userRole === 'admin') {
    next({ name: 'dashboard' });
  } else if (to.meta.requiresAuth && !isAuthenticated) {
    next({ name: 'login' });
  } else if (to.meta.requiresAdmin && userRole !== 'admin') {
    // Si un no-admin intenta acceder a una ruta de admin, lo enviamos a la página de fichaje
    next({ name: 'home' });
  } else {
    next();
  }
});

export default router