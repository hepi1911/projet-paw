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

        <div v-if="error" class="error-message">
          {{ error }}
        </div>

        <button type="submit" class="submit-button">Login</button>

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
const auth = useAuthStore()

const email = ref('')
const password = ref('')
const error = ref('')

const handleLogin = async () => {
  // Récupérer l'ID de session actuel pour cette fenêtre
  const sessionId = localStorage.getItem('currentSessionId')
  
  if (!sessionId) {
    console.error('Session ID manquant, impossible de se connecter')
    error.value = 'Erreur système: session non initialisée'
    return
  }
  
  const result = await auth.login(email.value, password.value, sessionId)
  if (result.success) {
    // Récupérer le paramètre de redirection de l'URL s'il existe
    const redirectPath = router.currentRoute.value.query.redirect
    
    if (redirectPath) {
      // Si un chemin de redirection est spécifié dans l'URL, l'utiliser
      router.push(redirectPath)
    } else {
      // Sinon, rediriger en fonction du rôle
      const userData = JSON.parse(localStorage.getItem(`user_${sessionId}`) || '{}')
      const userRole = userData.role
      
      switch (userRole) {
        case 'petowner':
          router.push('/petowner')
          break
        case 'petsitter':
          router.push('/petsitter')
          break
        case 'company':
          router.push('/company')
          break
        default:
          // Si le rôle n'est pas reconnu, rediriger vers la page d'accueil
          router.push('/')
          break
      }
    }
  } else {
    error.value = result.error
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

.submit-button:hover {
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