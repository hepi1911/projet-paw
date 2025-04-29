<template>
  <div class="view-container">
    <div class="forgot-password-container">
      <h1>Récupération du mot de passe</h1>

      <!-- Étape 1: Demande d'email -->
      <form v-if="step === 'email'" @submit.prevent="handleEmailSubmit" class="forgot-form">
        <div class="form-group">
          <label for="email">Email:</label>
          <input 
            type="email" 
            id="email" 
            v-model="email" 
            required
            placeholder="votre@email.com">
        </div>

        <div v-if="error" class="error-message">
          {{ error }}
        </div>

        <button type="submit" class="submit-button" :disabled="loading">
          {{ loading ? 'Envoi...' : 'Envoyer le code' }}
        </button>

        <p class="login-link">
          Vous vous souvenez de votre mot de passe? 
          <router-link to="/login">Se connecter</router-link>
        </p>
      </form>

      <!-- Étape 2: Vérification du code -->
      <form v-if="step === 'verify'" @submit.prevent="handleCodeSubmit" class="forgot-form">
        <p class="info-message">
          Un code de vérification a été envoyé à {{ email }}
        </p>

        <div class="form-group">
          <label for="code">Code de vérification:</label>
          <input 
            type="text" 
            id="code" 
            v-model="verificationCode" 
            required
            placeholder="Entrez le code reçu"
            pattern="[0-9]{6}"
            maxlength="6">
        </div>

        <div v-if="error" class="error-message">
          {{ error }}
        </div>

        <button type="submit" class="submit-button" :disabled="loading">
          {{ loading ? 'Vérification...' : 'Vérifier le code' }}
        </button>

        <button type="button" class="resend-button" @click="handleResendCode" :disabled="loading">
          Renvoyer le code
        </button>
      </form>

      <!-- Étape 3: Nouveau mot de passe -->
      <form v-if="step === 'reset'" @submit.prevent="handlePasswordReset" class="forgot-form">
        <div class="form-group">
          <label for="newPassword">Nouveau mot de passe:</label>
          <input 
            type="password" 
            id="newPassword" 
            v-model="newPassword"
            required
            @input="validatePassword"
            placeholder="Nouveau mot de passe">
          <ul class="password-requirements" :class="{ valid: passwordValid }">
            <li :class="{ met: passwordLength }">Au moins 8 caractères</li>
            <li :class="{ met: hasUpperCase }">Au moins une majuscule</li>
            <li :class="{ met: hasLowerCase }">Au moins une minuscule</li>
            <li :class="{ met: hasNumber }">Au moins un chiffre</li>
          </ul>
        </div>

        <div class="form-group">
          <label for="confirmPassword">Confirmer le mot de passe:</label>
          <input 
            type="password" 
            id="confirmPassword" 
            v-model="confirmPassword"
            required
            @input="validatePasswordMatch"
            placeholder="Confirmez le nouveau mot de passe">
          <p class="password-match" :class="{ error: !passwordsMatch && confirmPassword }">
            {{ passwordMatchMessage }}
          </p>
        </div>

        <div v-if="error" class="error-message">
          {{ error }}
        </div>

        <button type="submit" class="submit-button" :disabled="loading">
          {{ loading ? 'Réinitialisation...' : 'Réinitialiser le mot de passe' }}
        </button>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { apiService } from '../services/api'

const router = useRouter()
const step = ref('email')
const loading = ref(false)
const error = ref('')

// Données du formulaire
const email = ref('')
const verificationCode = ref('')
const newPassword = ref('')
const confirmPassword = ref('')

// Validation du mot de passe
const passwordLength = computed(() => newPassword.value.length >= 8)
const hasUpperCase = computed(() => /[A-Z]/.test(newPassword.value))
const hasLowerCase = computed(() => /[a-z]/.test(newPassword.value))
const hasNumber = computed(() => /[0-9]/.test(newPassword.value))
const passwordValid = computed(() => 
  passwordLength.value && 
  hasUpperCase.value && 
  hasLowerCase.value && 
  hasNumber.value
)

const passwordsMatch = computed(() => 
  newPassword.value === confirmPassword.value
)

const passwordMatchMessage = computed(() => {
  if (!confirmPassword.value) return ''
  return passwordsMatch.value ? 'Les mots de passe correspondent' : 'Les mots de passe ne correspondent pas'
})

const handleEmailSubmit = async () => {
  loading.value = true
  error.value = ''

  try {
    await apiService.requestPasswordReset(email.value)
    step.value = 'verify'
  } catch (err) {
    error.value = 'Impossible d\'envoyer le code de vérification. Vérifiez votre email.'
  } finally {
    loading.value = false
  }
}

const handleCodeSubmit = async () => {
  loading.value = true
  error.value = ''

  try {
    await apiService.verifyResetCode(email.value, verificationCode.value)
    step.value = 'reset'
  } catch (err) {
    error.value = 'Code de vérification invalide'
  } finally {
    loading.value = false
  }
}

const handleResendCode = async () => {
  loading.value = true
  error.value = ''

  try {
    await apiService.requestPasswordReset(email.value)
    error.value = 'Un nouveau code a été envoyé'
  } catch (err) {
    error.value = 'Impossible d\'envoyer le code de vérification'
  } finally {
    loading.value = false
  }
}

const handlePasswordReset = async () => {
  if (!passwordValid.value) {
    error.value = 'Le mot de passe ne respecte pas les critères de sécurité'
    return
  }

  if (!passwordsMatch.value) {
    error.value = 'Les mots de passe ne correspondent pas'
    return
  }

  loading.value = true
  error.value = ''

  try {
    await apiService.resetPassword(email.value, verificationCode.value, newPassword.value)
    alert('Votre mot de passe a été réinitialisé avec succès')
    router.push('/login')
  } catch (err) {
    error.value = 'Erreur lors de la réinitialisation du mot de passe'
  } finally {
    loading.value = false
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
}

.forgot-password-container {
  width: 100%;
  max-width: 400px;
  padding: 2rem;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.forgot-form {
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

.submit-button:hover:not(:disabled) {
  background-color: #3aa876;
}

.submit-button:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.resend-button {
  background-color: transparent;
  color: #42b983;
  border: none;
  padding: 0.5rem;
  font-size: 0.9rem;
  cursor: pointer;
  text-decoration: underline;
}

.resend-button:hover:not(:disabled) {
  color: #3aa876;
}

.resend-button:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.error-message {
  color: #dc3545;
  text-align: center;
  font-size: 0.9rem;
}

.info-message {
  color: #2c3e50;
  text-align: center;
  font-size: 0.9rem;
  margin: 0;
}

.login-link {
  text-align: center;
  color: #666;
  font-size: 0.9rem;
  margin: 0;
}

.login-link a {
  color: #42b983;
  text-decoration: none;
}

.login-link a:hover {
  text-decoration: underline;
}

.password-requirements {
  list-style: none;
  padding: 0;
  margin: 0.5rem 0;
  font-size: 0.8rem;
  color: #666;
}

.password-requirements li {
  margin: 0.2rem 0;
  position: relative;
  padding-left: 1.5rem;
}

.password-requirements li:before {
  content: '✗';
  position: absolute;
  left: 0;
  color: #dc3545;
}

.password-requirements li.met:before {
  content: '✓';
  color: #28a745;
}

.password-match {
  font-size: 0.8rem;
  margin: 0.2rem 0;
  color: #28a745;
}

.password-match.error {
  color: #dc3545;
}
</style>