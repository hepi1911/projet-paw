<template>
  <div class="view-container">
    <div class="forgot-password-container">
      <h1>Password recovery</h1>

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
          Remember your password? 
          <router-link to="/login">Login</router-link>
        </p>
      </form>

      <!-- Étape 2: Vérification du code -->
      <form v-if="step === 'verify'" @submit.prevent="handleCodeSubmit" class="forgot-form">
        <p class="info-message">
          A verification code has been sent to {{ email }}
        </p>

        <div class="form-group">
          <label for="code">Verification code:</label>
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
          Resend code
        </button>
      </form>

      <!-- Étape 3: Nouveau mot de passe -->
      <form v-if="step === 'reset'" @submit.prevent="handlePasswordReset" class="forgot-form">
        <div class="form-group">
          <label for="newPassword">New password:</label>
          <input 
            type="password" 
            id="newPassword" 
            v-model="newPassword"
            required
            @input="validatePassword"
            placeholder="Nouveau mot de passe">
          <ul class="password-requirements" :class="{ valid: passwordValid }">
            <li :class="{ met: passwordLength }">At least 8 characters</li>
            <li :class="{ met: hasUpperCase }">At least one upper case letter</li>
            <li :class="{ met: hasLowerCase }">At least one lower case letter</li>
            <li :class="{ met: hasNumber }">At least one digit</li>
          </ul>
        </div>

        <div class="form-group">
          <label for="confirmPassword">Confirm password:</label>
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
  min-height: calc(100vh - var(--header-height));
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: var(--color-background-soft);
  padding: var(--space-lg);
}

.forgot-container {
  width: 100%;
  max-width: 400px;
  background: var(--color-background);
  padding: var(--space-xl);
  border-radius: var(--border-radius-md);
  box-shadow: var(--shadow-md);
}

.forgot-form {
  display: flex;
  flex-direction: column;
  gap: var(--space-lg);
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: var(--space-xs);
}

label {
  color: var(--color-text);
  font-weight: 500;
}

input {
  padding: var(--space-sm);
  border: 1px solid var(--color-border);
  border-radius: var(--border-radius-sm);
  font-size: 1rem;
}

input:focus {
  border-color: var(--color-primary);
  outline: none;
}

.submit-button {
  background-color: var(--color-primary);
  color: white;
  border: none;
  padding: var(--space-md);
  border-radius: var(--border-radius-sm);
  font-size: 1rem;
  cursor: pointer;
  transition: background-color var(--transition-speed);
}

.submit-button:hover:not(:disabled) {
  background-color: var(--color-primary-hover);
}

.submit-button:disabled {
  background-color: var(--color-text-light);
  cursor: not-allowed;
}

.resend-button {
  background-color: transparent;
  color: var(--color-primary);
  border: none;
  padding: var(--space-sm);
  font-size: 0.9rem;
  cursor: pointer;
  text-decoration: underline;
}

.resend-button:hover:not(:disabled) {
  color: var(--color-primary-hover);
}

.resend-button:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.error-message {
  color: var(--color-danger);
  text-align: center;
  font-size: 0.9rem;
}

.info-message {
  color: var(--color-text);
  text-align: center;
  font-size: 0.9rem;
  margin: 0;
}

.login-link {
  text-align: center;
  color: var(--color-text-light);
  font-size: 0.9rem;
  margin: 0;
}

.login-link a {
  color: var(--color-primary);
  text-decoration: none;
}

.login-link a:hover {
  text-decoration: underline;
}

.password-requirements {
  list-style: none;
  padding: 0;
  margin: var(--space-xs) 0;
  font-size: 0.8rem;
  color: var(--color-text-light);
}

.password-requirements li {
  margin: var(--space-xs) 0;
  position: relative;
  padding-left: var(--space-lg);
}

.password-requirements li:before {
  content: '✗';
  position: absolute;
  left: 0;
  color: var(--color-danger);
}

.password-requirements li.met:before {
  content: '✓';
  color: var(--color-success);
}

.password-match {
  font-size: 0.8rem;
  margin: var(--space-xs) 0;
  color: var(--color-success);
}

.password-match.error {
  color: var(--color-danger);
}

@media (max-width: 768px) {
  .view-container {
    padding: var(--space-md);
  }

  .forgot-container {
    padding: var(--space-lg);
  }
}
</style>