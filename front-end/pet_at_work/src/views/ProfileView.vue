<template>
  <div class="view-container">
    <div class="profile-container">
      <h1>{{ $t('profile.title') }}</h1>
      <div class="profile">
        <h2>Mon Profil</h2>
        <form @submit.prevent="updateProfile" class="profile-form">
          <div class="form-group">
            <label for="name">Nom</label>
            <input type="text" id="name" v-model="form.name" required>
          </div>

          <div class="form-group">
            <label for="email">Email</label>
            <input type="email" id="email" v-model="form.email" required>
          </div>

          <div class="form-group">
            <label for="address">Adresse</label>
            <input type="text" id="address" v-model="form.address" 
                   :required="form.role === 'petowner' || form.role === 'company'">
          </div>

          <div class="form-group" v-if="form.role === 'petsitter'">
            <label for="experience">Expérience</label>
            <textarea id="experience" v-model="form.experience" required></textarea>
          </div>

          <div class="form-group" v-if="form.role === 'company'">
            <label for="capacity">Capacité</label>
            <input type="number" id="capacity" v-model="form.capacity" required>
          </div>

          <h3>Changer le mot de passe</h3>
          <div class="form-group">
            <label for="currentPassword">Mot de passe actuel</label>
            <input type="password" id="currentPassword" v-model="form.currentPassword">
          </div>

          <div class="form-group">
            <label for="newPassword">Nouveau mot de passe</label>
            <input type="password" id="newPassword" v-model="form.newPassword"
                   :disabled="!form.currentPassword"
                   pattern="^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$"
                   title="Le mot de passe doit contenir au moins 8 caractères, une majuscule, une minuscule, un chiffre et un caractère spécial">
          </div>

          <div class="form-group">
            <label for="confirmPassword">Confirmer le nouveau mot de passe</label>
            <input type="password" id="confirmPassword" v-model="form.confirmPassword"
                   :disabled="!form.currentPassword">
          </div>

          <button type="submit" class="btn btn-primary">Mettre à jour</button>
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
            alert('Les mots de passe ne correspondent pas')
            return
          }
          if (!/^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$/.test(form.value.newPassword)) {
            alert('Le mot de passe ne respecte pas les critères de sécurité')
            return
          }
          
          // Vérifier que le mot de passe actuel est bien renseigné
          if (!form.value.currentPassword) {
            alert('Veuillez entrer votre mot de passe actuel pour confirmer le changement')
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
        alert('Profil mis à jour avec succès')

        // Réinitialiser les champs de mot de passe
        form.value.currentPassword = ''
        form.value.newPassword = ''
        form.value.confirmPassword = ''
      } catch (error) {
        if (error.response?.status === 400) {
          alert(error.response.data.error || 'Erreur lors de la mise à jour du profil')
        } else {
          alert('Une erreur est survenue')
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
  background-color: #f5f5f5;
  min-height: calc(100vh - var(--header-height));
  padding: 2rem 1rem;
}

.profile-container {
  width: 100%;
  max-width: 800px;
  margin: 0 auto;
  background: white;
  padding: 2rem;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.profile {
  max-width: 600px;
  margin: 0 auto;
  padding: 20px;
}

.profile-form {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

label {
  font-weight: bold;
}

input, textarea {
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
}

textarea {
  min-height: 100px;
}

button {
  padding: 10px;
  background-color: #4CAF50;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

button:hover {
  background-color: #45a049;
}
</style>