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
        <RouterLink to="/">{{ $t('navigation.home') }}</RouterLink>

        <template v-if="auth.isAuthenticated">
          <RouterLink v-if="auth.user?.role === 'petowner'" to="/petowner">{{ $t('home.petowner') }}</RouterLink>
          <RouterLink v-if="auth.user?.role === 'petsitter'" to="/petsitter">{{ $t('home.petsitter') }}</RouterLink>
          <RouterLink v-if="auth.user?.role === 'company'" to="/company">{{ $t('home.company') }}</RouterLink>
          <a href="#" @click.prevent="handleLogout" class="logout-btn">{{ $t('auth.logout') }}</a>
        </template>
        <template v-else>
          <RouterLink to="/login">{{ $t('auth.login') }}</RouterLink>
          <RouterLink to="/register">{{ $t('auth.register') }}</RouterLink>
        </template>
        
        <div class="spacer"></div>
        <LanguageSelector />
      </nav>
    </header>

    <main>
      <RouterView />
    </main>
  </div>
</template>

<style>
#app {
  width: 100%;
  margin: 0;
  padding: 0;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  align-items: center;
}

* {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

:root {
  --header-height: 64px;
  --max-content-width: 1200px; /* Largeur maximale du contenu */
}

body {
  font-family: Arial, sans-serif;
  min-height: 100vh;
  background-color: #f5f5f5;
  margin: 0;
}

.app-container {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  width: 100%;
}

header {
  background-color: #42b983;
  padding: 1rem;
  width: 100%;
  position: sticky;
  top: 0;
  z-index: 100;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

header nav {
  max-width: var(--max-content-width);
  margin: 0 auto;
  padding: 0 1rem;
  display: flex;
  justify-content: center;
  align-items: center;
}

nav a:first-child {
  margin-right: auto;
}

main {
  flex: 1;
  display: flex;
  flex-direction: column;
  width: 100%;
  max-width: var(--max-content-width);
  margin: 0 auto;
  padding: 2rem 1rem;
  align-items: center;
}

nav {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 2rem;
  width: 100%;
}

/* Ajout d'un style global pour les conteneurs de vues */
.view-container {
  width: 100%;
  max-width: var(--max-content-width);
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  align-items: center;
}

nav a {
  color: white;
  text-decoration: none;
  font-weight: 500;
  transition: opacity 0.2s;
}

nav a:hover {
  opacity: 0.8;
}

nav a.router-link-active {
  font-weight: 700;
  text-decoration: underline;
}

.logout-btn {
  cursor: pointer;
}

.spacer {
  flex: 1;
}
</style>
