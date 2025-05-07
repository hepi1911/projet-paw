<template>
  <div class="view-container">
    <div class="profile-container">
      <h1>{{ $t('profile.title') }}</h1>
      <div class="profile">
        <h2>My Profile</h2>
        <form @submit.prevent="updateProfile" class="profile-form">
          <div class="form-group">
            <label for="name">Name</label>
            <input type="text" id="name" v-model="form.name" required>
          </div>

          <div class="form-group">
            <label for="email">Email</label>
            <input type="email" id="email" v-model="form.email" required>
          </div>

          <div class="form-group">
            <label for="address">Address</label>
            <input type="text" id="address" v-model="form.address" 
                   :required="form.role === 'petowner' || form.role === 'company'">
          </div>

          <div class="form-group" v-if="form.role === 'petsitter'">
            <label for="experience">Experience</label>
            <textarea id="experience" v-model="form.experience" required></textarea>
          </div>

          <div class="form-group" v-if="form.role === 'company'">
            <label for="capacity">Capacity</label>
            <input type="number" id="capacity" v-model="form.capacity" required>
          </div>

          <h3>Change password</h3>
          <div class="form-group">
            <label for="currentPassword">Current password</label>
            <input type="password" id="currentPassword" v-model="form.currentPassword">
          </div>

          <div class="form-group">
            <label for="newPassword">New password</label>
            <input type="password" id="newPassword" v-model="form.newPassword"
                   :disabled="!form.currentPassword"
                   pattern="^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$"
                   title="Password must contain at least 8 characters, one uppercase letter, one lowercase letter, one number and one special character">
          </div>

          <div class="form-group">
            <label for="confirmPassword">Confirm new password</label>
            <input type="password" id="confirmPassword" v-model="form.confirmPassword"
                   :disabled="!form.currentPassword">
          </div>

          <button type="submit" class="btn btn-primary">Update</button>
        </form>
      </div>
    </div>
  </div>
</template>

<script>
import { ref } from 'vue'
import { useAuthStore } from '../stores/auth'
import { apiService } from '../services/api'

export default {
  name: 'ProfileView',
  setup() {
    const authStore = useAuthStore()
    const user = authStore.user

    const form = ref({
      name: user.name,
      email: user.email,
      role: user.role,
      address: user.address || '',
      experience: user.experience || '',
      capacity: user.capacity || null,
      currentPassword: '',
      newPassword: '',
      confirmPassword: ''
    })

    const updateProfile = async () => {
      try {
        // Vérifier la concordance des mots de passe uniquement si un nouveau mot de passe est fourni
        if (form.value.newPassword) {
          if (form.value.newPassword !== form.value.confirmPassword) {
            alert('Passwords do not match')
            return
          }
          if (!/^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$/.test(form.value.newPassword)) {
            alert('The password does not meet the security criteria')
            return
          }
          
          // Vérifier que le mot de passe actuel est bien renseigné
          if (!form.value.currentPassword) {
            alert('Please enter your current password to confirm the change.')
            return
          }
        }

        const userData = {
          name: form.value.name,
          email: form.value.email,
          address: form.value.address,
          experience: form.value.experience,
          capacity: form.value.capacity
        }

        // Ajouter les informations de mot de passe uniquement si un nouveau mot de passe est fourni
        if (form.value.newPassword && form.value.currentPassword) {
          userData.current_password = form.value.currentPassword
          userData.new_password = form.value.newPassword
        }

        const response = await apiService.updateProfile(userData)
        authStore.setUser(response)
        alert(' Profile updated successfully')

        // Réinitialiser les champs de mot de passe
        form.value.currentPassword = ''
        form.value.newPassword = ''
        form.value.confirmPassword = ''
      } catch (error) {
        if (error.response?.status === 400) {
          alert(error.response.data.error || 'Error updating profile')
        } else {
          alert('An error has occurred')
        }
      }
    }

    return {
      form,
      updateProfile
    }
  }
}
</script>

<style scoped>
.view-container {
  background-color: var(--color-background-soft);
  min-height: calc(100vh - var(--header-height));
  padding: var(--space-xl);
}

.profile-container {
  width: 100%;
  max-width: 800px;
  margin: 0 auto;
  background: var(--color-background);
  padding: var(--space-xl);
  border-radius: var(--border-radius-md);
  box-shadow: var(--shadow-md);
}

.profile {
  max-width: 600px;
  margin: 0 auto;
  padding: var(--space-lg);
}

.profile-form {
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
  font-weight: 600;
  color: var(--color-text);
}

input, textarea {
  padding: var(--space-sm);
  border: 1px solid var(--color-border);
  border-radius: var(--border-radius-sm);
  font-size: 1rem;
}

input:focus, textarea:focus {
  border-color: var(--color-primary);
  outline: none;
}

textarea {
  min-height: 100px;
  resize: vertical;
}

button {
  padding: var(--space-sm);
  background-color: var(--color-success);
  color: white;
  border: none;
  border-radius: var(--border-radius-sm);
  cursor: pointer;
  font-weight: 600;
  transition: background-color var(--transition-speed);
}

button:hover {
  background-color: var(--color-success-dark);
}

@media (max-width: 768px) {
  .view-container {
    padding: var(--space-md);
  }

  .profile-container {
    padding: var(--space-lg);
  }

  .profile {
    padding: var(--space-md);
  }
}
</style>