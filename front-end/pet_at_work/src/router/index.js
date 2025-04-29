import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import LoginView from '../views/LoginView.vue'
import RegisterView from '../views/RegisterView.vue'
import ProfileView from '../views/ProfileView.vue'
import ForgotPasswordView from '../views/ForgotPasswordView.vue'
import PetOwnerView from '../views/PetOwnerView.vue'
import PetSitterView from '../views/PetSitterView.vue'
import CompanyView from '../views/CompanyView.vue'
import { requireAuth, requireRole, redirectLoggedIn } from './routeGuards'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'Home',
      component: HomeView,
      beforeEnter: redirectLoggedIn
    },
    {
      path: '/login',
      name: 'Login',
      component: LoginView,
      beforeEnter: redirectLoggedIn
    },
    {
      path: '/register',
      name: 'Register',
      component: RegisterView,
      beforeEnter: redirectLoggedIn
    },
    {
      path: '/forgot-password',
      name: 'ForgotPassword',
      component: ForgotPasswordView,
      beforeEnter: redirectLoggedIn
    },
    {
      path: '/profile',
      name: 'Profile',
      component: ProfileView,
      beforeEnter: requireAuth
    },
    {
      path: '/petowner',
      name: 'PetOwner',
      component: PetOwnerView,
      beforeEnter: requireRole('petowner')
    },
    {
      path: '/petsitter',
      name: 'PetSitter',
      component: PetSitterView,
      beforeEnter: requireRole('petsitter')
    },
    {
      path: '/petsitter/:id',
      name: 'PetSitterDetail',
      component: () => import('../views/PetSitterDetailView.vue'),
      // Le détail des pet sitters est accessible sans connexion
    },
    {
      path: '/company-reservation/:id',
      name: 'CompanyReservation',
      component: () => import('../views/CompanyReservationView.vue'),
      beforeEnter: requireRole('petsitter')
    },
    {
      path: '/company/:id',
      name: 'CompanyDetail',
      component: () => import('../views/CompanyDetailView.vue'),
      beforeEnter: requireAuth
    },
    {
      path: '/company',
      name: 'Company',
      component: CompanyView,
      beforeEnter: requireRole('company')
    }
  ]
})

export default router