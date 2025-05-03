import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import LoginView from '../views/LoginView.vue'
import RegisterView from '../views/RegisterView.vue'
import ProfileView from '../views/ProfileView.vue'
import ForgotPasswordView from '../views/ForgotPasswordView.vue'
import PetOwnerView from '../views/PetOwnerView.vue'
import PetSitterView from '../views/PetSitterView.vue'
import CompanyView from '../views/CompanyView.vue'
import { requireAuth, requireRole, redirectLoggedIn, requireRoleForBooking } from './routeGuards'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'Home',
      component: HomeView
      // Pas de garde-route ici - accessible à tous
    },
    {
      path: '/login',
      name: 'Login',
      component: LoginView,
      beforeEnter: redirectLoggedIn
      // Rediriger l'utilisateur déjà connecté vers sa page de rôle
    },
    {
      path: '/register',
      name: 'Register',
      component: RegisterView,
      beforeEnter: redirectLoggedIn
      // Rediriger l'utilisateur déjà connecté vers sa page de rôle
    },
    {
      path: '/forgot-password',
      name: 'ForgotPassword',
      component: ForgotPasswordView,
      beforeEnter: redirectLoggedIn
      // Rediriger l'utilisateur déjà connecté vers sa page de rôle
    },
    {
      path: '/profile',
      name: 'Profile',
      component: ProfileView,
      beforeEnter: requireAuth
      // Nécessite d'être connecté pour voir le profil
    },
    {
      path: '/petowner',
      name: 'PetOwner',
      component: PetOwnerView
      // Navigation libre, vérifications au niveau du composant
    },
    {
      path: '/petsitter',
      name: 'PetSitter',
      component: PetSitterView
      // Navigation libre, vérifications au niveau du composant
    },
    {
      path: '/petsitter/:id',
      name: 'PetSitterDetail',
      component: () => import('../views/PetSitterDetailView.vue')
      // Navigation libre, réservation uniquement pour les utilisateurs connectés en tant que petowner
    },
    {
      path: '/company-reservation/:id',
      name: 'CompanyReservation',
      component: () => import('../views/CompanyReservationView.vue'),
      beforeEnter: requireRole('petsitter')
      // Cette route nécessite toujours un rôle spécifique
    },
    {
      path: '/company/:id',
      name: 'CompanyDetail',
      component: () => import('../views/CompanyDetailView.vue')
      // Navigation libre, mais les réservations nécessitent une connexion
    },
    {
      path: '/company',
      name: 'Company',
      component: CompanyView
      // Navigation libre, vérifications au niveau du composant
    }
  ]
})

// Navigation guard globale pour gérer les préférences de connexion
router.beforeEach((to, from, next) => {
  // Si l'utilisateur est déjà connecté et va vers une page qui n'est pas protégée
  // On le laisse naviguer normalement
  const userDataString = sessionStorage.getItem('user');
  
  // Si l'utilisateur n'est pas connecté ou si la route n'a pas de protection spécifique
  // On permet la navigation
  next();
});

export default router