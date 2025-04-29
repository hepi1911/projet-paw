<template>
  <div class="view-container">
    <div class="company-detail" v-if="company">
      <div class="detail-card">
        <h1>{{ company.name }}</h1>
        <div class="info-section">
          <p><strong>Adresse:</strong> {{ company.address }}</p>
          <p><strong>Capacité d'accueil:</strong> {{ company.capacity }} animaux</p>
          <p><strong>Contact:</strong> {{ company.email }}</p>
        </div>
        
        <!-- Reservation Section -->
        <div class="reservation-section">
          <h2>Réserver une place pour votre animal</h2>
          
          <div v-if="userAnimals.length === 0" class="no-animals">
            <p>Vous n'avez pas encore enregistré d'animaux.</p>
            <router-link to="/profile/animals" class="btn-add-animal">Ajouter un animal</router-link>
          </div>
          
          <form v-else @submit.prevent="submitReservation" class="reservation-form">
            <div class="form-group">
              <label for="animal">Sélectionnez votre animal:</label>
              <select id="animal" v-model="reservation.animalId" required>
                <option value="" disabled>Choisir un animal</option>
                <option v-for="animal in userAnimals" :key="animal.id" :value="animal.id">
                  {{ animal.name }} ({{ animal.species }})
                </option>
              </select>
            </div>
            
            <div class="form-group">
              <label for="start-date">Date de début:</label>
              <input type="date" id="start-date" v-model="reservation.startDate" required :min="today">
            </div>
            
            <div class="form-group">
              <label for="end-date">Date de fin:</label>
              <input type="date" id="end-date" v-model="reservation.endDate" required :min="reservation.startDate">
            </div>
            
            <div class="form-group">
              <label for="notes">Notes spéciales (allergies, médicaments, etc.):</label>
              <textarea id="notes" v-model="reservation.notes" rows="3"></textarea>
            </div>
            
            <button type="submit" class="btn-reserve" :disabled="isSubmitting">
              {{ isSubmitting ? 'Réservation en cours...' : 'Réserver' }}
            </button>
            
            <div v-if="reservationMessage" :class="['message', reservationStatus]">
              {{ reservationMessage }}
            </div>
          </form>
        </div>
      </div>
    </div>
    <div v-else class="loading">
      Chargement...
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { apiService } from '../services/api';

const route = useRoute();
const router = useRouter();
const company = ref(null);
const userAnimals = ref([]);
const isSubmitting = ref(false);
const reservationMessage = ref('');
const reservationStatus = ref('');

const reservation = ref({
  animalId: '',
  startDate: '',
  endDate: '',
  notes: ''
});

const today = computed(() => {
  const date = new Date();
  return date.toISOString().split('T')[0];
});

onMounted(async () => {
  try {
    // Récupérer l'ID de l'utilisateur connecté depuis le localStorage
    const userData = JSON.parse(localStorage.getItem('user') || '{}');
    const currentUserId = userData.user_id;
    
    if (!currentUserId) {
      console.error('Utilisateur non connecté ou ID non disponible');
      router.push('/login');
      return;
    }
    
    // Récupérer les détails de l'entreprise
    company.value = await apiService.getUserById(route.params.id);
    
    // Récupérer UNIQUEMENT les animaux appartenant au propriétaire connecté
    userAnimals.value = await apiService.getAnimalsByOwner(currentUserId);
    console.log('Animaux de l\'utilisateur:', userAnimals.value);
    
    if (userAnimals.value.length === 0) {
      console.log('L\'utilisateur n\'a pas encore d\'animaux enregistrés');
    }
  } catch (error) {
    console.error('Erreur lors du chargement des données:', error);
  }
});

const submitReservation = async () => {
  isSubmitting.value = true;
  reservationMessage.value = '';
  
  try {
    // Vérifier que l'utilisateur est bien connecté
    const userData = JSON.parse(localStorage.getItem('user') || '{}');
    if (!userData.user_id) {
      reservationMessage.value = 'Vous devez être connecté pour effectuer une réservation.';
      reservationStatus.value = 'error';
      router.push('/login');
      return;
    }
    
    // Créer l'objet de données pour la réservation
    const bookingData = {
      company: company.value.id,
      animal: reservation.value.animalId,
      start_date: reservation.value.startDate,
      end_date: reservation.value.endDate
    };
    
    // Utiliser apiService au lieu d'appeler directement l'API
    await apiService.createBooking(bookingData);
    
    reservationMessage.value = 'Réservation effectuée avec succès! Vous recevrez une confirmation par email.';
    reservationStatus.value = 'success';
    
    // Réinitialiser le formulaire
    reservation.value = {
      animalId: '',
      startDate: '',
      endDate: '',
      notes: ''
    };
    
    // Rediriger vers la page du pet owner après un court délai
    setTimeout(() => {
      router.push('/petowner');
    }, 2000);
    
  } catch (error) {
    console.error('Erreur lors de la réservation:', error);
    reservationMessage.value = 'Erreur lors de la réservation. Veuillez réessayer plus tard.';
    reservationStatus.value = 'error';
  } finally {
    isSubmitting.value = false;
  }
};
</script>

<style scoped>
.view-container {
  background-color: #f5f5f5;
  min-height: calc(100vh - var(--header-height));
  display: flex;
  justify-content: center;
  align-items: start;
  padding-top: 2rem;
}

.company-detail {
  width: 100%;
  max-width: 800px;
  margin: 0 auto;
  padding: 0 2rem;
}

.detail-card {
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  padding: 2rem;
}

.info-section {
  margin-bottom: 2rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid #eee;
}

.reservation-section {
  margin-top: 2rem;
}

.reservation-section h2 {
  margin-bottom: 1.5rem;
  font-size: 1.5rem;
  color: #333;
}

.reservation-form {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

label {
  font-weight: 600;
  color: #555;
}

input, select, textarea {
  padding: 0.75rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 1rem;
}

.btn-reserve {
  background-color: #4CAF50;
  color: white;
  border: none;
  padding: 1rem;
  border-radius: 4px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: background-color 0.3s;
  margin-top: 1rem;
}

.btn-reserve:hover {
  background-color: #388E3C;
}

.btn-reserve:disabled {
  background-color: #9E9E9E;
  cursor: not-allowed;
}

.message {
  margin-top: 1rem;
  padding: 1rem;
  border-radius: 4px;
  text-align: center;
}

.success {
  background-color: #E8F5E9;
  color: #388E3C;
  border: 1px solid #C8E6C9;
}

.error {
  background-color: #FFEBEE;
  color: #D32F2F;
  border: 1px solid #FFCDD2;
}

.no-animals {
  text-align: center;
  padding: 1.5rem;
  background-color: #f9f9f9;
  border-radius: 4px;
}

.btn-add-animal {
  display: inline-block;
  margin-top: 1rem;
  padding: 0.75rem 1.5rem;
  background-color: #2196F3;
  color: white;
  text-decoration: none;
  border-radius: 4px;
  font-weight: 600;
  transition: background-color 0.3s;
}

.btn-add-animal:hover {
  background-color: #1976D2;
}

.loading {
  text-align: center;
  padding: 2rem;
  font-size: 1.2rem;
  color: #757575;
}
</style>