<template>
  <div class="view-container">
    <div class="company-reservation">
      <div v-if="loading" class="loading">
        Loading...
      </div>
      
      <div v-else-if="error" class="error">
        {{ error }}
      </div>
      
      <div v-else-if="company" class="reservation-container">
        <div class="back-link">
          <router-link to="/petsitter">&larr; Back to the list of companies</router-link>
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
              
              <h2>Capacity</h2>
              <p>{{ company.capacity }} pets</p>
            </div>
          </div>
        </div>
        
        <div class="reservation-section">
          <h2>Book with this company</h2>
          <form @submit.prevent="submitReservation" class="reservation-form">
            <div class="form-group">
              <label for="service-type">Type of service desired</label>
              <select id="service-type" v-model="reservation.serviceType" required>
                <option disabled value="">Choose a type of service</option>
                <option value="formation">Specialist training</option>
                <option value="consultation">Professional consultation</option>
                <option value="collaboration">Collaboration for pet sitting</option>
              </select>
            </div>
            
            <div class="form-group">
              <label for="start-date">Start date</label>
              <input type="date" id="start-date" v-model="reservation.startDate" required min="today" />
            </div>
            
            <div class="form-group">
              <label for="end-date">End date</label>
              <input type="date" id="end-date" v-model="reservation.endDate" required :min="reservation.startDate" />
            </div>
            
            <div class="form-group">
              <label for="details">Request details</label>
              <textarea id="details" v-model="reservation.details" rows="4" placeholder="Précisez vos besoins, vos attentes et toute information pertinente pour votre réservation."></textarea>
            </div>
            
            <button type="submit" class="submit-btn" :disabled="isSubmitting">
              {{ isSubmitting ? 'Demande en cours...' : 'Envoyer ma demande' }}
            </button>
          </form>
          
          <div v-if="reservationSuccess" class="success-message">
            Your booking request has been sent successfully! The company will contact you shortly.
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
  min-height: calc(100vh - var(--header-height));
  padding: var(--space-xl);
}

.back-link a {
  color: var(--color-primary);
  text-decoration: none;
}

.reservation-container {
  display: flex;
  flex-direction: column;
  gap: var(--space-xl);
}

.company-profile {
  background-color: var(--color-background);
  border-radius: var(--border-radius-md);
  box-shadow: var(--shadow-md);
  padding: var(--space-lg);
}

.company-header h1 {
  margin-top: 0;
  margin-bottom: var(--space-sm);
  color: var(--color-heading);
}

.company-contact {
  color: var(--color-text-light);
  margin-bottom: var(--space-lg);
}

.company-body {
  display: flex;
  flex-direction: column;
  gap: var(--space-md);
}

.company-info h2 {
  color: var(--color-heading);
  font-size: 18px;
  margin: var(--space-lg) 0 var(--space-sm);
}

.reservation-section {
  background-color: var(--color-background);
  border-radius: var(--border-radius-md);
  box-shadow: var(--shadow-md);
  padding: var(--space-lg);
}

.reservation-section h2 {
  margin-bottom: var(--space-lg);
}

.form-group {
  margin-bottom: var(--space-md);
}

.form-group label {
  display: block;
  margin-bottom: var(--space-xs);
  font-weight: 600;
  color: var(--color-text);
}

.form-group input,
.form-group select,
.form-group textarea {
  width: 100%;
  padding: var(--space-sm);
  border: 1px solid var(--color-border);
  border-radius: var(--border-radius-sm);
  font-size: 16px;
}

.submit-btn {
  background-color: var(--color-secondary);
  color: white;
  border: none;
  padding: var(--space-sm) var(--space-md);
  border-radius: var(--border-radius-sm);
  font-size: 16px;
  cursor: pointer;
  transition: background-color var(--transition-speed);
  font-weight: 600;
}

.submit-btn:hover:not(:disabled) {
  background-color: var(--color-secondary-hover);
}

.submit-btn:disabled {
  background-color: var(--color-text-light);
  cursor: not-allowed;
}

.success-message {
  background-color: var(--color-success-light);
  color: var(--color-success-dark);
  padding: var(--space-md);
  border-radius: var(--border-radius-sm);
  margin-top: var(--space-md);
  text-align: center;
}

.error-message {
  background-color: var(--color-danger-light);
  color: var(--color-danger-dark);
  padding: var(--space-md);
  border-radius: var(--border-radius-sm);
  margin-top: var(--space-md);
  text-align: center;
}

@media (max-width: 768px) {
  .view-container {
    padding: var(--space-md);
  }
}
</style>