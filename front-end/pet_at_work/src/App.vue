<script setup>
import { RouterLink, RouterView, useRouter } from 'vue-router'
import { useAuthStore } from './stores/auth'
import LanguageSelector from './components/LanguageSelector.vue'
import { onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { setLocale } from './i18n'

const auth = useAuthStore()
const router = useRouter()
const i18n = useI18n()

// S'assurer que la langue est correctement chargée depuis localStorage au démarrage
// et définir l'anglais comme langue par défaut si aucune préférence n'est stockée
onMounted(() => {
  const storedLocale = localStorage.getItem('locale')
  if (storedLocale && storedLocale !== i18n.locale.value) {
    setLocale(storedLocale)
  } else if (!storedLocale) {
    // Si aucune langue n'est stockée, définir l'anglais par défaut
    setLocale('en')
  }
})

const handleLogout = () => {
  auth.logout()
  router.push('/login')
}
</script>

<template>
  <div class="app-container">
    <header>
      <nav>
        <div class="nav-left">
          <RouterLink to="/" class="logo-link">PetAtWork</RouterLink>
        </div>

        <div class="nav-right">
          <div class="nav-actions">
            <template v-if="auth.isAuthenticated">
              <RouterLink v-if="auth.user?.role === 'petowner'" to="/petowner" class="nav-button">
                {{ $t('home.petowner') }}
                <span class="arrow-wrapper">
                  <span class="arrow"></span>
                </span>
              </RouterLink>
              <RouterLink v-if="auth.user?.role === 'petsitter'" to="/petsitter" class="nav-button">
                {{ $t('home.petsitter') }}
                <span class="arrow-wrapper">
                  <span class="arrow"></span>
                </span>
              </RouterLink>
              <RouterLink v-if="auth.user?.role === 'company'" to="/company" class="nav-button">
                {{ $t('home.company') }}
                <span class="arrow-wrapper">
                  <span class="arrow"></span>
                </span>
              </RouterLink>
              <a href="#" @click.prevent="handleLogout" class="nav-button logout-btn">
                {{ $t('auth.logout') }}
                <span class="arrow-wrapper">
                  <span class="arrow"></span>
                </span>
              </a>
            </template>
            <template v-else>
              <RouterLink to="/login" class="nav-button">
                {{ $t('auth.login') }}
                <span class="arrow-wrapper">
                  <span class="arrow"></span>
                </span>
              </RouterLink>
            </template>
          </div>
          <LanguageSelector class="language-selector-nav" />
        </div>
      </nav>
    </header>

    <main>
      <RouterView />
    </main>
  </div>
</template>

<style>
/* Layout */
#app {
  width: 100%;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  margin: 0;
  padding: 0;
  overflow-x: hidden;
}

.app-container {
  width: 100%;
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  padding: 0;
  margin: 0;
}

header {
  background: linear-gradient(to right, #ff8f00, #ff6d00);
  height: var(--header-height);
  position: fixed;
  width: 100%;
  top: 0;
  left: 0;
  z-index: 100;
  box-shadow: 0 2px 8px rgba(255, 111, 0, 0.3);
  border-bottom: 2px solid #ff6d00;
  display: flex;
  justify-content: center;
}

nav {
  height: 100%;
  width: 100%;
  max-width: var(--max-content-width);
  margin: 0;
  padding: 0 var(--space-md);
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.nav-left {
  display: flex;
  align-items: center;
  gap: var(--space-md);
  padding: 0;
  margin: 0;
}

.nav-right {
  display: flex;
  align-items: center;
  gap: var(--space-md);
  padding: 0;
  margin: 0;
}

.logo-link {
  font-size: 1.5rem;
  font-weight: 700;
  color: white;
  text-decoration: none;
  text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.2);
  padding: 0;
  margin: 0;
}

.nav-actions {
  display: flex;
  gap: var(--space-md);
  margin: 0;
  padding: 0;
  align-items: center;
}

.nav-button {
  --primary-color: white;
  --secondary-color: var(--button-secondary-color);
  --hover-color: #fff3e0;
  --arrow-width: var(--button-arrow-width);
  --arrow-stroke: var(--button-arrow-stroke);
  box-sizing: border-box;
  border: 2px solid white;
  border-radius: var(--button-border-radius);
  color: white;
  padding: 0.8em 1.4em;
  background: transparent;
  display: flex;
  transition: 0.2s all;
  align-items: center;
  gap: 0.6em;
  font-weight: bold;
  text-decoration: none;
}

.nav-button .arrow-wrapper {
  display: flex;
  justify-content: center;
  align-items: center;
}

.nav-button .arrow {
  margin-top: 1px;
  width: var(--arrow-width);
  background: white;
  height: var(--arrow-stroke);
  position: relative;
  transition: 0.2s;
}

.nav-button .arrow::before {
  content: "";
  box-sizing: border-box;
  position: absolute;
  border: solid white;
  border-width: 0 var(--arrow-stroke) var(--arrow-stroke) 0;
  display: inline-block;
  top: -3px;
  right: 3px;
  transition: 0.2s;
  padding: 3px;
  transform: rotate(-45deg);
}

.nav-button:hover {
  background-color: white;
  color: #ff6d00;
}

.nav-button:hover .arrow {
  background: #ff6d00;
}

.nav-button:hover .arrow:before {
  right: 0;
  border-color: #ff6d00;
}

.nav-button.router-link-active {
  background-color: #ffc166;
}

.logout-btn {
  border: 2px solid var(--color-primary);
  color: var(--color-primary);
}

.logout-btn:hover {
  background-color: var(--color-danger);
  border-color: var(--color-danger);
  color: white;
}

.language-selector-nav {
  margin-left: var(--space-xl);
}

.language-selector-nav :deep(.language-button) {
  color: var(--color-text);
  border: 2px solid var(--color-primary);
}

.language-selector-nav :deep(.language-button:hover) {
  background-color: var(--color-primary);
  color: white;
}

/* Responsive styles */
@media (max-width: 768px) {
  nav {
    padding: 0 var(--space-xs);
  }

  .nav-actions {
    gap: var(--space-xs);
  }

  .nav-button {
    padding: var(--space-xs) var(--space-sm);
    font-size: 0.9rem;
  }

  .logo-link {
    font-size: 1.2rem;
  }
}

/* Navigation links */
nav a {
  color: var(--color-primary);
  text-decoration: none;
  padding: var(--space-sm);
  border-radius: var(--border-radius-sm);
  transition: background-color var(--transition-speed);
  font-weight: 500;
}

nav a:hover {
  background-color: transparent;
}

nav a.router-link-active {
  font-weight: 600;
  background-color: transparent;
}

/* User actions */
.user-actions {
  display: flex;
  align-items: center;
  gap: var(--space-md);
  margin-left: auto;
}

.profile-btn, .logout-btn {
  background: transparent;
  border: 1px solid white;
  color: white;
  padding: var(--space-sm) var(--space-md);
  border-radius: var(--border-radius-sm);
  cursor: pointer;
  transition: all var(--transition-speed);
  font-weight: 500;
}

.profile-btn:hover, .logout-btn:hover {
  background: white;
  color: var(--color-primary);
}

/* Main content */
main {
  flex: 1;
  width: 100%;
  margin-top: var(--header-height);
  padding: 0;
}

/* Responsive */
@media (max-width: 768px) {
  nav {
    padding: 0 var(--space-sm);
    gap: var(--space-sm);
  }

  .user-actions {
    gap: var(--space-sm);
  }

  .profile-btn, .logout-btn {
    padding: var(--space-xs) var(--space-sm);
    font-size: 14px;
  }
}

/* Global styles */
:root {
  --header-height: 64px;
  --max-content-width: 1200px;
  --transition-speed: 0.2s;
}

/* Layout */
.view-container {
  min-height: calc(100vh - var(--header-height));
  padding: 0;
  margin: 0;
  width: 100%;
  background: radial-gradient(ellipse, orangered, transparent, orange) orange;
}

/* Cards */
.card {
  background: var(--color-background);
  border-radius: var(--radius-md);
  padding: var(--space-lg);
  box-shadow: var(--shadow-md);
  transition: transform var(--transition-speed);
}

.card:not(.login-container):not(.register-container):hover {
  transform: translateY(-3px);
  box-shadow: var(--shadow-lg);
}

/* Booking cards */
.booking-card {
  border-left: 5px solid var(--color-border);
  margin-bottom: var(--space-md);
}

.booking-card.pending {
  border-left-color: var(--color-warning);
}

.booking-card.pending .status {
  color: var(--color-warning);
}

.booking-card.accepted {
  border-left-color: var(--color-success);
}

.booking-card.accepted .status {
  color: var(--color-success);
}

.booking-card.refused {
  border-left-color: var(--color-danger);
}

.booking-card.refused .status {
  color: var(--color-danger);
}

.booking-card.cancelled {
  border-left-color: var(--color-text-light);
  opacity: 0.8;
}

.booking-card.cancelled .status {
  color: var(--color-text-light);
}

/* Forms */
.form-group {
  margin-bottom: var(--space-md);
}

.form-group label {
  display: block;
  margin-bottom: var(--space-xs);
  color: var(--color-text);
  font-weight: 500;
}

.form-group input,
.form-group textarea,
.form-group select {
  width: 100%;
  padding: var(--space-sm);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);
  font-size: 1rem;
  transition: border-color var(--transition-speed);
}

.form-group input:focus,
.form-group textarea:focus,
.form-group select:focus {
  border-color: var(--color-primary);
  outline: none;
}

/* Buttons */
.btn {
  padding: var(--space-sm) var(--space-md);
  border: none;
  border-radius: var(--radius-sm);
  font-weight: 600;
  cursor: pointer;
  transition: background-color var(--transition-speed);
}

.btn:disabled {
  background-color: var(--color-text-light);
  cursor: not-allowed;
}

.btn-primary {
  background-color: var(--color-primary);
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background-color: var(--color-primary-dark);
}

.btn-success {
  background-color: var(--color-success);
  color: white;
}

.btn-success:hover:not(:disabled) {
  background-color: var(--color-success-light);
}

.btn-danger {
  background-color: var(--color-danger);
  color: white;
}

.cancelled {
  border-left-color: #95a5a6;
  opacity: 0.8;
}

.cancelled .status {
  color: #95a5a6;
}

/* Global button styles */
.action-btn {
  border: none;
  border-radius: 4px;
  padding: 0.5rem 1rem;
  cursor: pointer;
  font-weight: 600;
  transition: background-color 0.2s;
}

.accept-btn {
  border: none;
  border-radius: 4px;
  padding: 0.5rem 1rem;
  cursor: pointer;
  font-weight: 600;
  transition: background-color 0.2s;
  background-color: #2ecc71;
  color: white;
}

.accept-btn:hover:not(:disabled) {
  background-color: #27ae60;
}

.refuse-btn {
  border: none;
  border-radius: 4px;
  padding: 0.5rem 1rem;
  cursor: pointer;
  font-weight: 600;
  transition: background-color 0.2s;
  background-color: #e74c3c;
  color: white;
}

.refuse-btn:hover:not(:disabled) {
  background-color: #c0392b;
}

.delete-btn {
  border: none;
  border-radius: 4px;
  padding: 0.5rem 1rem;
  cursor: pointer;
  font-weight: 600;
  transition: background-color 0.2s;
  background-color: #e74c3c;
  color: white;
}

.delete-btn:hover:not(:disabled) {
  background-color: #c0392b;
}

button:disabled {
  background-color: #95a5a6;
  cursor: not-allowed;
}

/* Form styles */
.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  margin-bottom: 1rem;
}

.form-group label {
  color: #2c3e50;
  font-weight: 500;
}

.form-group input,
.form-group select,
.form-group textarea {
  padding: 0.8rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 1rem;
}

.form-group textarea {
  min-height: 100px;
  resize: vertical;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
  margin-top: 1.5rem;
}

/* Global modal styles */
.modal-backdrop {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal-content {
  background-color: white;
  border-radius: 8px;
  padding: 2rem;
  width: 90%;
  max-width: 500px;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
}

/* Global notification styles */
.notification-bar {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  background-color: #3498db;
  color: white;
  padding: 1rem;
  text-align: center;
  z-index: 1001;
  animation: slideDown 0.3s ease-out;
}

.notification-bar.success {
  background-color: #2ecc71;
}

.notification-bar.error {
  background-color: #e74c3c;
}

.notification-bar .close-btn {
  position: absolute;
  right: 1rem;
  top: 50%;
  transform: translateY(-50%);
  background: none;
  border: none;
  color: white;
  font-size: 1.5rem;
  cursor: pointer;
  padding: 0;
  line-height: 1;
}

/* Global messages styles */
.error-message {
  background-color: #ffebee;
  color: #c62828;
  padding: 1rem;
  border-radius: 4px;
  margin: 1rem 0;
  text-align: center;
}

.success-message {
  background-color: #e8f5e9;
  color: #2e7d32;
  padding: 1rem;
  border-radius: 4px;
  margin: 1rem 0;
  text-align: center;
}

.info-message {
  background-color: #e3f2fd;
  color: #1565c0;
  padding: 1rem;
  border-radius: 4px;
  margin: 1rem 0;
  text-align: center;
}

/* Loading states */
.loading-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(255, 255, 255, 0.8);
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.loading-spinner {
  width: 50px;
  height: 50px;
  border: 4px solid #f3f3f3;
  border-top: 4px solid #3498db;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

@keyframes slideDown {
  from {
    transform: translateY(-100%);
  }
  to {
    transform: translateY(0);
  }
}
</style>
