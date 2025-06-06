<template>
  <div class="view-container">
    <div class="register-container">
      <h1>{{ $t('auth.register') }}</h1>
      <form v-if="!registrationComplete" @submit.prevent="handleRegister" class="register-form">
        <div class="form-group">
          <label for="name">Name:</label>
          <input 
            type="text" 
            id="name" 
            v-model="formData.name" 
            required
            placeholder="Votre nom">
        </div>

        <div class="form-group">
          <label for="email">Email:</label>
          <input 
            type="email" 
            id="email" 
            v-model="formData.email" 
            required
            placeholder="votre@email.com">
        </div>

        <div class="form-group">
          <label for="password">Password:</label>
          <input 
            type="password" 
            id="password" 
            v-model="formData.password" 
            required
            @input="validatePassword"
            placeholder="Votre mot de passe">
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
            placeholder="Confirmez votre mot de passe">
          <p class="password-match" :class="{ error: !passwordsMatch && confirmPassword }">
            {{ passwordMatchMessage }}
          </p>
        </div>

        <div class="form-group">
          <label for="role">Type of account:</label>
          <select id="role" v-model="formData.role" required>
            <option value="">Select a type</option>
            <option value="petowner">Pet Owner</option>
            <option value="petsitter">Pet Sitter</option>
            <option value="company">Company</option>
          </select>
        </div>

        <!-- Champs conditionnels selon le rôle -->
        <div v-if="formData.role === 'petowner' || formData.role === 'company'" class="form-group">
          <label for="address">Address:</label>
          <input 
            type="text" 
            id="address" 
            v-model="formData.address" 
            required
            placeholder="Votre adresse">
        </div>

        <div v-if="formData.role === 'petsitter'" class="form-group">
          <label for="experience">Experience:</label>
          <textarea 
            id="experience" 
            v-model="formData.experience" 
            required
            placeholder="Describe your experience with animals"></textarea>
        </div>

        <div v-if="formData.role === 'company'" class="form-group">
          <label for="capacity">Capacity:</label>
          <input 
            type="number" 
            id="capacity" 
            v-model="formData.capacity" 
            required
            min="1"
            placeholder="Number of animals">
        </div>

        <div v-if="error" class="error-message">
          {{ error }}
        </div>

        <button type="submit" class="btn btn-primary" :disabled="isLoading">
          <span v-if="isLoading">Registration in progress...</span>
          <span v-else>{{ $t('auth.register') }}</span>
          <div class="arrow-wrapper">
            <div class="arrow"></div>
          </div>
        </button>

        <p class="login-link">
          Already an account? 
          <router-link to="/login">Login</router-link>
        </p>
      </form>

      <div v-else class="confirmation-step">
        <h2>Successful registration!</h2>
        <p>Your account has been created successfully.</p>
        <p>Click ‘Continue’ to go to the login page and log in with your new details.</p>
        <button @click="handleContinue" class="submit-button">Continuer</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const router = useRouter()
const auth = useAuthStore()

const formData = ref({
  name: '',
  email: '',
  password: '',
  role: '',
  address: '',
  experience: '',
  capacity: null
})

const confirmPassword = ref('')
const error = ref('')
const isLoading = ref(false)
const registrationComplete = ref(false) // To track if registration is complete

// Password validation
const passwordLength = computed(() => formData.value.password.length >= 8)
const hasUpperCase = computed(() => /[A-Z]/.test(formData.value.password))
const hasLowerCase = computed(() => /[a-z]/.test(formData.value.password))
const hasNumber = computed(() => /\d/.test(formData.value.password))
const passwordValid = computed(() => 
  passwordLength.value && 
  hasUpperCase.value && 
  hasLowerCase.value && 
  hasNumber.value
)

const passwordsMatch = computed(() => 
  formData.value.password === confirmPassword.value
)

const passwordMatchMessage = computed(() => 
  !confirmPassword.value 
    ? '' 
    : passwordsMatch.value 
      ? 'The passwords match' 
      : 'Passwords do not match'
)

const validatePassword = () => {
  // Validation déjà gérée par les computed properties
}

const validatePasswordMatch = () => {
  // Validation déjà gérée par les computed properties
}

const handleRegister = async () => {
  // Prevent multiple submissions
  if (isLoading.value) return
  
  error.value = ''
  
  // Validate password requirements
  if (!passwordValid.value) {
    error.value = 'Your password does not meet the requirements'
    return
  }
  
  // Validate password matching
  if (!passwordsMatch.value) {
    error.value = 'Passwords do not match'
    return
  }
  
  try {
    isLoading.value = true
    
    // Préparer les données en fonction du rôle
    // Cela évite d'envoyer des champs non pertinents pour certains rôles
    const dataToSend = {
      name: formData.value.name,
      email: formData.value.email,
      password: formData.value.password,
      role: formData.value.role
    };
    
    // Ajouter les champs spécifiques en fonction du rôle
    if (formData.value.role === 'petowner' || formData.value.role === 'company') {
      dataToSend.address = formData.value.address;
    }
    
    if (formData.value.role === 'petsitter') {
      dataToSend.experience = formData.value.experience;
    }
    
    if (formData.value.role === 'company') {
      dataToSend.capacity = formData.value.capacity;
    }
    
    console.log('Prepared registration data:', dataToSend);
    await auth.register(dataToSend)
    registrationComplete.value = true // Mark registration as complete
  } catch (err) {
    console.error('Error caught in component:', err);
    error.value = err.message || 'An error occurred during registration'
  } finally {
    isLoading.value = false
  }
}

// Function to handle the "Continue" action after registration
const handleContinue = () => {
  router.push('/login')
}
</script>

<style scoped>
.view-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: calc(100vh - var(--header-height));
  background: radial-gradient(ellipse, orangered, transparent, orange) orange;
  width: 100%;
  margin: 0;
  padding: 0;
}

.register-container {
  width: 100%;
  max-width: 400px;
  padding: var(--space-xl);
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(10px);
  border-radius: var(--border-radius-lg);
  box-shadow: var(--shadow-md);
  margin: 0 auto;
  border: 2px solid var(--color-primary);
}

.register-container:hover {
  transform: translateY(-5px);
  box-shadow: var(--shadow-lg);
  border-color: var(--color-primary);
}

h1, h2 {
  color: var(--color-heading);
  text-align: center;
  margin-bottom: var(--space-lg);
  background: linear-gradient(135deg, var(--color-heading) 0%, var(--color-primary) 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.register-form {
  display: flex;
  flex-direction: column;
  gap: var(--space-lg);
}

.role-buttons {
  display: flex;
  justify-content: center;
  gap: var(--space-md);
  margin-bottom: var(--space-lg);
}

.role-btn {
  padding: var(--space-sm) var(--space-md);
  border: 2px solid var(--color-primary);
  border-radius: var(--border-radius-sm);
  background: none;
  color: var(--color-primary);
  cursor: pointer;
  transition: all var(--transition-speed);
  font-weight: 500;
}

.role-btn.active {
  background-color: var(--color-primary);
  color: white;
}

.role-btn:hover:not(.active) {
  background-color: rgba(52, 152, 219, 0.1);
}

.register-steps {
  margin-top: var(--space-xl);
}

.step-indicator {
  display: flex;
  justify-content: center;
  margin-bottom: var(--space-xl);
}

.step {
  width: 30px;
  height: 30px;
  border-radius: 50%;
  background-color: var(--color-background-mute);
  color: var(--color-text-light);
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 var(--space-sm);
}

.step.active {
  background-color: var(--color-primary);
  color: white;
}

.step.completed {
  background-color: var(--color-success);
  color: white;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: var(--space-xs);
}

.form-group label {
  color: var(--color-text);
  font-weight: 500;
}

.form-group input,
.form-group textarea {
  padding: var(--space-sm);
  border: 1px solid var(--color-border);
  border-radius: var(--border-radius-sm);
  font-size: 1rem;
}

.form-group input:focus,
.form-group textarea:focus {
  border-color: var(--color-primary);
  outline: none;
}

.button-group {
  display: flex;
  justify-content: space-between;
  gap: var(--space-md);
  margin-top: var(--space-lg);
}

.prev-btn,
.next-btn,
.submit-btn {
  padding: var(--space-sm) var(--space-lg);
  border: none;
  border-radius: var(--border-radius-sm);
  font-weight: 600;
  cursor: pointer;
  transition: background-color var(--transition-speed);
  flex: 1;
}

.prev-btn {
  background-color: var(--color-background-mute);
  color: var(--color-text);
}

.prev-btn:hover {
  background-color: var(--color-border);
}

.next-btn,
.submit-btn {
  background-color: var(--color-primary);
  color: white;
}

.next-btn:hover,
.submit-btn:hover {
  background-color: var(--color-primary-hover);
}

.submit-button {
  width: 100%;
  padding: var(--space-md);
  background-color: var(--color-primary);
  color: white;
  border: none;
  border-radius: var(--border-radius-sm);
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: background-color var(--transition-speed);
}

.submit-button:hover:not(:disabled) {
  background-color: var(--color-primary-dark);
}

.submit-button:disabled {
  background-color: var(--color-text-light);
  cursor: not-allowed;
}

.error-message {
  color: var(--color-danger);
  text-align: center;
  font-size: 0.9rem;
  margin-top: var(--space-sm);
}

.login-link {
  text-align: center;
  margin-top: var(--space-lg);
}

.login-link a {
  color: var(--color-primary);
  text-decoration: none;
}

.login-link a:hover {
  text-decoration: underline;
}

@media (max-width: 768px) {
  .register-container {
    padding: var(--space-lg);
    margin: var(--space-md);
  }

  .role-buttons {
    flex-direction: column;
  }

  .role-btn {
    width: 100%;
  }

  .button-group {
    flex-direction: column;
  }
}
</style>