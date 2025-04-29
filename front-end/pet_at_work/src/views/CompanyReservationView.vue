<template>
  <div class="view-container">
    <div class="company-reservation">
      <div v-if="loading" class="loading">
        Chargement...
      </div>
      
      <div v-else-if="error" class="error">
        {{ error }}
      </div>
      
      <div v-else-if="company" class="reservation-container">
        <div class="back-link">
          <router-link to="/petsitter">&larr; Retour à la liste des entreprises</router-link>
        </div>
        
        <div class="company-profile">
          <div class="company-header">
            <h1>{{ company.name }}</h1>
            <p class="company-contact">{{ company.email }}</p>
          </div>
          
          <div class="company-body">
            <div class="company-info">
              <h2>Adresse</h2>
              <p>{{ company.address }}</p>
              
              <h2>Capacité d'accueil</h2>
              <p>{{ company.capacity }} animaux</p>
            </div>
          </div>
        </div>
        
        <div class="reservation-section">
          <h2>Réserver auprès de cette entreprise</h2>
          <form @submit.prevent="submitReservation" class="reservation-form">
            <div class="form-group">
              <label for="service-type">Type de service souhaité</label>
              <select id="service-type" v-model="reservation.serviceType" required>
                <option disabled value="">Choisissez un type de service</option>
                <option value="formation">Formation spécialisée</option>
                <option value="consultation">Consultation professionnelle</option>
                <option value="collaboration">Collaboration pour garde d'animaux</option>
              </select>
            </div>
            
            <div class="form-group">
              <label for="start-date">Date de début</label>
              <input type="date" id="start-date" v-model="reservation.startDate" required min="today" />
            </div>
            
            <div class="form-group">
              <label for="end-date">Date de fin</label>
              <input type="date" id="end-date" v-model="reservation.endDate" required :min="reservation.startDate" />
            </div>
            
            <div class="form-group">
              <label for="details">Détails de la demande</label>
              <textarea id="details" v-model="reservation.details" rows="4" placeholder="Précisez vos besoins, vos attentes et toute information pertinente pour votre réservation."></textarea>
            </div>
            
            <button type="submit" class="submit-btn" :disabled="isSubmitting">
              {{ isSubmitting ? 'Demande en cours...' : 'Envoyer ma demande' }}
            </button>
          </form>
          
          <div v-if="reservationSuccess" class="success-message">
            Votre demande de réservation a été envoyée avec succès! L'entreprise vous contactera bientôt.
          </div>
          
          <div v-if="reservationError" class="error-message">
            {{ reservationError }}
          </div>
        </div>
      </div>
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
const loading = ref(true);
const error = ref(null);
const reservationSuccess = ref(false);
const reservationError = ref(null);
const isSubmitting = ref(false);

const reservation = ref({
  serviceType: '',
  startDate: '',
  endDate: '',
  details: ''
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
    
    // Vérifier le rôle de l'utilisateur
    if (userData.role !== 'petsitter') {
      console.error('Cette page est réservée aux pet sitters');
      router.push('/');
      return;
    }
    
    // Récupérer les détails de l'entreprise
    const companyId = route.params.id;
    company.value = await apiService.getUserById(companyId);
    
    loading.value = false;
  } catch (err) {
    console.error('Erreur lors du chargement des données:', err);
    error.value = 'Impossible de charger les informations de l\'entreprise. Veuillez réessayer plus tard.';
    loading.value = false;
  }
});

async function submitReservation() {
  try {
    isSubmitting.value = true;
    reservationError.value = null;

    const start = new Date(reservation.startDate);
    const end = new Date(reservation.endDate);
    const today = new Date();

    if (start < today) {
      reservationError.value = "La date de début ne peut pas être dans le passé";
      return;
    }

    if (end <= start) {
      reservationError.value = "La date de fin doit être après la date de début";
      return;
    }

    // Récupérer l'ID de l'utilisateur connecté
    const userData = JSON.parse(localStorage.getItem('user') || '{}');
    const currentUserId = userData.user_id;
    
    if (!currentUserId) {
      reservationError.value = "Vous devez être connecté pour effectuer une réservation";
      router.push('/login');
      return;
    }

    // Créer l'objet de données pour la réservation
    const bookingData = {
      petsitter: currentUserId,
      company: company.value.id,
      service_type: reservation.serviceType,
      start_date: reservation.startDate,
      end_date: reservation.endDate,
      details: reservation.details,
      status: 'pending'
    };
    
    // Appeler l'API pour créer la réservation
    // Note: il faudrait peut-être adapter l'API pour gérer ce type de réservation spécifique
    await apiService.createPetSitterCompanyBooking(bookingData);
    
    reservationSuccess.value = true;
    
    // Réinitialiser le formulaire
    reservation.value = {
      serviceType: '',
      startDate: '',
      endDate: '',
      details: ''
    };
    
    // Rediriger vers la page pet sitter après un court délai
    setTimeout(() => {
      router.push('/petsitter');
    }, 3000);
    
  } catch (err) {
    console.error('Erreur lors de la réservation:', err);
    reservationError.value = "Une erreur s'est produite lors de la réservation. Veuillez réessayer.";
  } finally {
    isSubmitting.value = false;
  }
}
</script>

<style scoped>
.view-container {
  background-color: #f5f5f5;
  min-height: calc(100vh - var(--header-height));
}

.company-reservation {
  width: 100%;
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
}

.loading, .error {
  text-align: center;
  padding: 40px;
  font-size: 18px;
}

.error {
  color: #e74c3c;
}

.back-link {
  margin-bottom: 20px;
}

.back-link a {
  color: #42b983;
  text-decoration: none;
}

.reservation-container {
  display: flex;
  flex-direction: column;
  gap: 30px;
}

.company-profile {
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  padding: 25px;
}

.company-header h1 {
  margin-top: 0;
  margin-bottom: 10px;
  color: #2c3e50;
}

.company-contact {
  color: #7f8c8d;
  font-size: 16px;
  margin-bottom: 20px;
}

.company-body {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.company-info h2 {
  color: #2c3e50;
  font-size: 18px;
  margin-top: 25px;
  margin-bottom: 10px;
}

.reservation-section {
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  padding: 25px;
}

.reservation-section h2 {
  margin-top: 0;
  margin-bottom: 20px;
  color: #2c3e50;
}

.reservation-form {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.form-group {
  margin-bottom: 15px;
}

.form-group label {
  display: block;
  margin-bottom: 5px;
  font-weight: 600;
  color: #2c3e50;
}

.form-group input,
.form-group select,
.form-group textarea {
  width: 100%;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 16px;
}

.submit-btn {
  background-color: #42b983;
  color: white;
  border: none;
  padding: 12px 20px;
  border-radius: 4px;
  font-size: 16px;
  cursor: pointer;
  transition: background-color 0.3s;
  font-weight: 600;
}

.submit-btn:hover {
  background-color: #3aa876;
}

.submit-btn:disabled {
  background-color: #9E9E9E;
  cursor: not-allowed;
}

.success-message {
  background-color: #E8F5E9;
  color: #388E3C;
  padding: 15px;
  border-radius: 4px;
  margin-top: 20px;
  text-align: center;
}

.error-message {
  background-color: #FFEBEE;
  color: #D32F2F;
  padding: 15px;
  border-radius: 4px;
  margin-top: 20px;
  text-align: center;
}

@media (max-width: 768px) {
  .reservation-container {
    flex-direction: column;
  }
  
  .company-profile, .reservation-section {
    width: 100%;
  }
}
</style>