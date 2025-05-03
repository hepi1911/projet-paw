<template>
  <div class="view-container">
    <div class="company-detail" v-if="company">
      <div class="detail-card">
        <h1>{{ company.name }}</h1>
        <div class="info-section">
          <p><strong>Address:</strong> {{ company.address }}</p>
          <p><strong>Capacity:</strong> {{ company.capacity }} pets</p>
          <p><strong>Contact:</strong> {{ company.email }}</p>
        </div>
        
        <!-- Reservation Section - Only show login prompt for non-authenticated users -->
        <div v-if="!isLoggedIn" class="login-prompt-section">
          <h2>Book a place for your pet</h2>
          <div class="login-prompt">
            <p>Please <router-link to="/login?redirect=/company/{{company.id}}">log in</router-link> or <router-link to="/register">register</router-link> to book services with this company.</p>
          </div>
        </div>
        
        <!-- Reservation Section - For authenticated users -->
        <div v-else class="reservation-section">
          <h2>Book a place for your pet</h2>
          
          <div v-if="userAnimals.length === 0" class="no-animals">
            <p>You have not yet registered any animals.</p>
            <router-link to="/profile/animals" class="btn-add-animal">Add a pet</router-link>
          </div>
          
          <form v-else @submit.prevent="submitReservation" class="reservation-form">
            <div class="form-group">
              <label for="animal">Select your pet:</label>
              <select id="animal" v-model="reservation.animalId" required>
                <option value="" disabled>Choose a pet</option>
                <option v-for="animal in userAnimals" :key="animal.id" :value="animal.id">
                  {{ animal.name }} ({{ animal.species || animal.breed }})
                </option>
              </select>
            </div>
            
            <div class="form-group">
              <label for="start-date">Start date:</label>
              <input type="date" id="start-date" v-model="reservation.startDate" required :min="today">
            </div>
            
            <div class="form-group">
              <label for="end-date">End date:</label>
              <input type="date" id="end-date" v-model="reservation.endDate" required :min="reservation.startDate">
            </div>
            
            <div class="form-group">
              <label for="notes">Specifications (allergies, medication, etc.):</label>
              <textarea id="notes" v-model="reservation.notes" rows="3"></textarea>
            </div>
            
            <button type="submit" class="btn-reserve" :disabled="isSubmitting">
              {{ isSubmitting ? 'Booking in progress...' : 'Book' }}
            </button>
            
            <div v-if="reservationMessage" :class="['message', reservationStatus]">
              {{ reservationMessage }}
            </div>
          </form>
        </div>
      </div>
    </div>
    <div v-else class="loading">
      Loading...
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

// Check if the user is logged in
const isLoggedIn = computed(() => {
  return !!sessionStorage.getItem('user');
});

const today = computed(() => {
  const date = new Date();
  return date.toISOString().split('T')[0];
});

onMounted(async () => {
  try {
    // Load company details for all users
    company.value = await apiService.getUserById(route.params.id);
    
    // If user is logged in, load their animals
    if (isLoggedIn.value) {
      const userData = JSON.parse(sessionStorage.getItem('user') || '{}');
      const currentUserId = userData.user_id;
      
      if (currentUserId) {
        // Get animals belonging to the logged-in pet owner
        userAnimals.value = await apiService.getAnimalsByOwner(currentUserId);
        console.log('User animals loaded:', userAnimals.value);
      }
    }
  } catch (error) {
    console.error('Error during data loading:', error);
  }
});

const submitReservation = async () => {
  // Verify the user is logged in before submission
  if (!isLoggedIn.value) {
    router.push('/login?redirect=' + router.currentRoute.value.path);
    return;
  }
  
  isSubmitting.value = true;
  reservationMessage.value = '';
  
  try {
    // Verify user is logged in
    const userData = JSON.parse(sessionStorage.getItem('user') || '{}');
    if (!userData.user_id) {
      reservationMessage.value = 'You must be logged in to make a booking.';
      reservationStatus.value = 'error';
      router.push('/login?redirect=' + router.currentRoute.value.path);
      return;
    }
    
    // Create reservation data object
    const bookingData = {
      company: company.value.id,
      animal: reservation.value.animalId,
      start_date: reservation.value.startDate,
      end_date: reservation.value.endDate,
      notes: reservation.value.notes
    };
    
    // Use apiService to create the booking
    await apiService.createBooking(bookingData);
    
    reservationMessage.value = 'Successful booking! You will receive confirmation by email.';
    reservationStatus.value = 'success';
    
    // Reset the form
    reservation.value = {
      animalId: '',
      startDate: '',
      endDate: '',
      notes: ''
    };
    
    // Redirect to the pet owner page after a short delay
    setTimeout(() => {
      router.push('/petowner');
    }, 2000);
    
  } catch (error) {
    console.error('Booking error:', error);
    reservationMessage.value = 'Booking error. Please try again later.';
    reservationStatus.value = 'error';
  } finally {
    isSubmitting.value = false;
  }
};
</script>

<style scoped>
.view-container {
  min-height: calc(100vh - var(--header-height));
  padding: var(--space-xl);
}

.company-detail {
  width: 100%;
  max-width: var(--max-content-width);
  margin: 0 auto;
}

.detail-card {
  background-color: var(--color-background);
  border-radius: var(--border-radius-md);
  box-shadow: var(--shadow-md);
  padding: var(--space-xl);
}

.info-section {
  margin-bottom: var(--space-xl);
  padding-bottom: var(--space-md);
  border-bottom: 1px solid var(--color-border);
}

.reservation-section {
  margin-top: var(--space-xl);
}

.reservation-section h2 {
  margin-bottom: var(--space-lg);
  font-size: 1.5rem;
  color: var(--color-heading);
}

.reservation-form {
  display: flex;
  flex-direction: column;
  gap: var(--space-md);
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

input, select, textarea {
  padding: var(--space-sm);
  border: 1px solid var(--color-border);
  border-radius: var(--border-radius-sm);
  font-size: 1rem;
}

input:focus, select:focus, textarea:focus {
  border-color: var(--color-primary);
  outline: none;
}

.btn-reserve {
  background-color: var(--color-success);
  color: white;
  border: none;
  padding: var(--space-md);
  border-radius: var(--border-radius-sm);
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: background-color var(--transition-speed);
  margin-top: var(--space-md);
}

.btn-reserve:hover:not(:disabled) {
  background-color: var(--color-success-dark);
}

.btn-reserve:disabled {
  background-color: var(--color-text-light);
  cursor: not-allowed;
}

.message {
  margin-top: var(--space-md);
  padding: var(--space-md);
  border-radius: var(--border-radius-sm);
  text-align: center;
}

.success {
  background-color: var(--color-success-light);
  color: var(--color-success-dark);
  border: 1px solid var(--color-success);
}

.error {
  background-color: var(--color-danger-light);
  color: var(--color-danger-dark);
  border: 1px solid var(--color-danger);
}

.no-animals {
  text-align: center;
  padding: var(--space-lg);
  background-color: var(--color-background-mute);
  border-radius: var(--border-radius-sm);
}

.btn-add-animal {
  display: inline-block;
  margin-top: var(--space-md);
  padding: var(--space-sm) var(--space-lg);
  background-color: var(--color-primary);
  color: white;
  text-decoration: none;
  border-radius: var(--border-radius-sm);
  font-weight: 600;
  transition: background-color var(--transition-speed);
}

.btn-add-animal:hover {
  background-color: var(--color-primary-hover);
}

.loading {
  text-align: center;
  padding: var(--space-xl);
  font-size: 1.2rem;
  color: var(--color-text-light);
}

.login-prompt-section {
  margin-top: var(--space-xl);
}

.login-prompt-section h2 {
  margin-bottom: var(--space-lg);
  font-size: 1.5rem;
  color: var(--color-heading);
}

.login-prompt {
  background-color: var(--color-background-soft);
  border-radius: var(--border-radius-md);
  padding: var(--space-lg);
  text-align: center;
}

.login-prompt a {
  color: var(--color-primary);
  font-weight: bold;
  text-decoration: none;
  transition: color var(--transition-speed);
}

.login-prompt a:hover {
  color: var(--color-primary-hover);
  text-decoration: underline;
}

@media (max-width: 768px) {
  .view-container {
    padding: var(--space-md);
  }

  .detail-card {
    padding: var(--space-lg);
  }
}
</style>