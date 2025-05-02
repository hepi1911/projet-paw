<template>
  <div class="view-container">
    <div class="login-container">
      <h1>{{ $t('auth.login') }}</h1>
      <form @submit.prevent="handleLogin" class="login-form">
        <div class="form-group">
          <label for="email">Email:</label>
          <input 
            type="email" 
            id="email" 
            v-model="email" 
            required
            placeholder="votre@email.com">
        </div>

        <div class="form-group">
          <label for="password">Password:</label>
          <input 
            type="password" 
            id="password" 
            v-model="password" 
            required
            placeholder="Votre mot de passe">
        </div>

        <div v-if="errorMessage" class="error-message">
          {{ errorMessage }}
        </div>

        <button type="submit" class="submit-button" :disabled="loading">
          <span v-if="loading">Loading...</span>
          <span v-else>Login</span>
        </button>

        <p class="register-link">
          No account yet? 
          <router-link to="/register">Create an account</router-link>
        </p>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const email = ref('')
const password = ref('')
const errorMessage = ref('')
const loading = ref(false)

const handleLogin = async () => {
  errorMessage.value = ''
  loading.value = true
  
  try {
    const result = await authStore.login(email.value, password.value)
    
    if (result.success) {
      // Réinitialiser le store d'authentification
      authStore.initializeAuth()
      
      console.log('Login success, role:', result.role)
      
      // Rediriger vers la page appropriée selon le rôle
      const redirectPath = router.currentRoute.value.query.redirect || getDefaultRedirect(result.role)
      router.push(redirectPath)
    } else {
      errorMessage.value = result.error || 'Une erreur est survenue lors de la connexion'
    }
  } catch (error) {
    console.error('Erreur de connexion:', error)
    errorMessage.value = error.message || 'Une erreur est survenue lors de la connexion'
  } finally {
    loading.value = false
  }
}

// Fonction pour déterminer la redirection par défaut selon le rôle
const getDefaultRedirect = (role) => {
  switch (role) {
    case 'petowner':
      return '/petowner'
    case 'petsitter':
      return '/petsitter'
    case 'company':
      return '/company'
    default:
      return '/'
  }
}
</script>

<style scoped>
.view-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: calc(100vh - var(--header-height));
  background-color: #f5f5f5;
  width: 100%;
  margin: 0 auto;
  padding: 0 1rem;
}

.login-container {
  width: 100%;
  max-width: 400px;
  padding: 2rem;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  margin: 0 auto;
}

h1 {
  text-align: center;
  color: #2c3e50;
  margin-bottom: 2rem;
}

.login-form {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

label {
  color: #2c3e50;
  font-weight: 500;
}

input {
  padding: 0.8rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 1rem;
}

.submit-button {
  background-color: #42b983;
  color: white;
  border: none;
  padding: 1rem;
  border-radius: 4px;
  font-size: 1rem;
  cursor: pointer;
  transition: background-color 0.2s;
}

.submit-button:disabled {
  background-color: #a5d6a7;
  cursor: not-allowed;
}

.submit-button:hover:not(:disabled) {
  background-color: #3aa876;
}

.error-message {
  color: #dc3545;
  text-align: center;
  font-size: 0.9rem;
}

.register-link {
  text-align: center;
  margin-top: 1rem;
  color: #666;
}

.register-link a {
  color: #42b983;
  text-decoration: none;
}

.register-link a:hover {
  text-decoration: underline;
}
</style>