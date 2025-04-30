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
            placeholder="Décrivez votre expérience avec les animaux"></textarea>
        </div>

        <div v-if="formData.role === 'company'" class="form-group">
          <label for="capacity">Capacity:</label>
          <input 
            type="number" 
            id="capacity" 
            v-model="formData.capacity" 
            required
            min="1"
            placeholder="Nombre d'animaux">
        </div>

        <div v-if="error" class="error-message">
          {{ error }}
        </div>

        <button type="submit" class="submit-button" :disabled="isLoading">
          {{ isLoading ? 'Chargement...' : "S'inscrire" }}
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
      ? 'Les mots de passe correspondent' 
      : 'Les mots de passe ne correspondent pas'
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
    error.value = 'Votre mot de passe ne répond pas aux exigences'
    return
  }
  
  // Validate password matching
  if (!passwordsMatch.value) {
    error.value = 'Les mots de passe ne correspondent pas'
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
    
    console.log('Données d\'inscription préparées:', dataToSend);
    await auth.register(dataToSend)
    registrationComplete.value = true // Mark registration as complete
  } catch (err) {
    console.error('Erreur capturée dans le composant:', err);
    error.value = err.message || 'Une erreur est survenue lors de l\'inscription'
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
  background-color: #f5f5f5;
  padding: 2rem 1rem;
}

.register-container {
  width: 100%;
  max-width: 500px;
  padding: 2rem;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.register-form {
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

input, select, textarea {
  padding: 0.8rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 1rem;
}

textarea {
  min-height: 100px;
  resize: vertical;
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

.submit-button:disabled {
  background-color: #ddd;
  cursor: not-allowed;
}

.error-message {
  color: #dc3545;
  text-align: center;
  font-size: 0.9rem;
}

.login-link {
  text-align: center;
  margin-top: 1rem;
  color: #666;
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

.confirmation-step {
  text-align: center;
}

.confirmation-step h2 {
  color: #28a745;
  margin-bottom: 1rem;
}

.confirmation-step p {
  color: #666;
  margin-bottom: 2rem;
}
</style>