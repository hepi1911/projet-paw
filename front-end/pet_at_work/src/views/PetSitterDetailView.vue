<template>
  <div class="view-container">
    <div class="petsitter-detail">
      <div v-if="loading" class="loading">
        Loading...
      </div>
      
      <div v-else-if="error" class="error">
        {{ error }}
      </div>
      
      <div v-else-if="sitter" class="sitter-container">
        <div class="back-link">
          <router-link to="/petowner">&larr; Back to the list of pet sitters</router-link>
        </div>
        
        <div class="sitter-profile">
          <div class="sitter-header">
            <h1>{{ sitter.name }}</h1>
            <p class="sitter-contact">{{ sitter.email }}</p>
          </div>
          
          <div class="sitter-body">
            <div class="sitter-info">
              <h2>Experience</h2>
              <p>{{ sitter.experience }}</p>
              
              <h2>Services on offer</h2>
              <ul>
                <li>Petsitting at home</li>
                <li>Walk</li>
                <li>Basic care</li>
              </ul>
              
              <h2>Availability</h2>
              <p>{{ sitter.availability || 'Disponible tous les jours' }}</p>
              
              <div class="ratings">
                <h2>Ratings</h2>
                <div class="stars">
                  <span>★★★★☆</span> <span class="rating-score">4.0/5</span>
                </div>
              </div>
            </div>
          </div>
        </div>
        
        <!-- Section de tarification -->
        <div class="pricing-info">
          <h2>Pricing</h2>
          <p class="pricing-details">Guarding: <span class="price">10£</span> per day</p>
        </div>
        
        <!-- Section de réservation - vérification du rôle utilisateur -->
        <div v-if="isLoggedIn && userHasRole('petowner')" class="booking-section">
          <h2>Book this pet sitter</h2>
          <form @submit.prevent="submitBooking">
            <div class="form-group">
              <label for="animal">Select your pet</label>
              <select id="animal" v-model="booking.animalId" required>
                <option disabled value="">Choose a pet</option>
                <option v-for="animal in animals" :key="animal.id" :value="animal.id">
                  {{ animal.name }} ({{ animal.breed }})
                </option>
              </select>
            </div>
            
            <div class="form-group">
              <label for="start-date">Start date</label>
              <input type="date" id="start-date" v-model="booking.startDate" @change="calculatePrice" required />
            </div>
            
            <div class="form-group">
              <label for="end-date">End date</label>
              <input type="date" id="end-date" v-model="booking.endDate" @change="calculatePrice" required />
            </div>
            
            <!-- Affichage du prix calculé -->
            <div v-if="totalDays > 0" class="price-calculation">
              <p><strong>Duration:</strong> {{ totalDays }} day{{ totalDays > 1 ? 's' : '' }}</p>
              <p class="total-price"><strong>Total price:</strong> {{ totalPrice }}£</p>
            </div>
            
            <div class="form-group">
              <label for="notes">Special instructions</label>
              <textarea id="notes" v-model="booking.notes" rows="4"></textarea>
            </div>
            
            <button type="submit" class="submit-btn">Book and pay</button>
          </form>
          
          <div v-if="bookingSuccess" class="success-message">
            <p>Your booking has been successfully created!</p>
            
            <!-- Section de paiement -->
            <div class="payment-section">
              <h3>Finalise your booking</h3>
              <div class="test-mode-notice">
                <p><strong>Information :</strong> Payment is required to confirm your booking.</p>
              </div>
              
              <div class="payment-details">
                <p><strong>Amount due:</strong> {{ totalPrice }}£</p>
                
                <div class="payment-method">
                  <h4>Method of payment</h4>
                  <div class="payment-options">
                    <label>
                      <input type="radio" v-model="paymentMethod" value="card" checked>
                      Credit card
                    </label>
                    <label>
                      <input type="radio" v-model="paymentMethod" value="paypal">
                      PayPal
                    </label>
                    <label>
                      <input type="radio" v-model="paymentMethod" value="transfer">
                      Bank transfer
                    </label>
                  </div>
                </div>
                
                <div v-if="paymentMethod === 'card'" class="card-details">
                  <div class="form-group">
                    <label for="card-number">Card number</label>
                    <input type="text" id="card-number" v-model="paymentDetails.cardNumber" placeholder="1234 5678 9012 3456" maxlength="19">
                  </div>
                  
                  <div class="card-info-row">
                    <div class="form-group expiry">
                      <label for="expiry-date">Expiry date</label>
                      <input type="text" id="expiry-date" v-model="paymentDetails.expiryDate" placeholder="MM/AA" maxlength="5">
                    </div>
                    
                    <div class="form-group cvv">
                      <label for="cvv">CVV</label>
                      <input type="text" id="cvv" v-model="paymentDetails.cvv" placeholder="123" maxlength="3">
                    </div>
                  </div>
                  
                  <div class="form-group">
                    <label for="card-name">Name on card</label>
                    <input type="text" id="card-name" v-model="paymentDetails.cardName" placeholder="JEAN DUPONT">
                  </div>
                </div>
                
                <button @click="processPayment" class="payment-btn" :disabled="isProcessingPayment">
                  {{ isProcessingPayment ? 'Traitement en cours...' : 'Payer ' + totalPrice + '£' }}
                </button>
              </div>
            </div>
          </div>
          
          <div v-if="paymentSuccess" class="payment-success">
            <p>Payment made successfully! Your booking is confirmed.</p>
            <p>You will be redirected to your personal space...</p>
          </div>
          
          <div v-if="bookingError" class="error-message">
            {{ bookingError }}
          </div>
          
          <div v-if="paymentError" class="error-message">
            {{ paymentError }}
          </div>
        </div>
        
        <!-- Message pour les utilisateurs connectés qui ne sont pas pet owners -->
        <div v-else-if="isLoggedIn && !userHasRole('petowner')" class="role-message">
          <p>You are currently logged in as a <strong>{{ userRole }}</strong>.</p>
          <p>Only pet owners can make reservations with pet sitters.</p>
          <div class="navigation-options">
            <router-link :to="'/' + userRole" class="nav-btn">Go to your {{ userRole }} dashboard</router-link>
          </div>
        </div>
        
        <!-- Message pour encourager la connexion - visible uniquement pour les utilisateurs non connectés -->
        <div v-else class="login-prompt">
          <p>To book the services of this pet sitter, you need to log in to your account.</p>
          <div class="login-buttons">
            <button class="login-btn" @click="goToLogin">Login</button>
            <button class="register-btn" @click="goToRegister">Register</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, reactive, computed, watch } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { apiService } from '../services/api';

const route = useRoute();
const router = useRouter();

const sitter = ref(null);
const animals = ref([]);
const loading = ref(true);
const error = ref(null);
const bookingSuccess = ref(false);
const bookingError = ref(null);
const paymentSuccess = ref(false);
const paymentError = ref(null);
const isProcessingPayment = ref(false);
const createdBookingId = ref(null);
const totalDays = ref(0);
const totalPrice = ref(0);
const paymentMethod = ref('card');
const paymentDetails = reactive({
  cardNumber: '',
  expiryDate: '',
  cvv: '',
  cardName: ''
});

const booking = reactive({
  animalId: '',
  startDate: '',
  endDate: '',
  notes: ''
});

// Check if user is logged in
const isLoggedIn = computed(() => {
  return !!sessionStorage.getItem('user');
});

// Get user role
const userRole = computed(() => {
  if (!isLoggedIn.value) return null;
  const userData = JSON.parse(sessionStorage.getItem('user') || '{}');
  return userData.role;
});

// Check if user has a specific role
const userHasRole = (role) => {
  if (!isLoggedIn.value) return false;
  return userRole.value === role;
};

// Calculate price when dates change
const calculatePrice = () => {
  if (!booking.startDate || !booking.endDate) {
    totalDays.value = 0;
    totalPrice.value = 0;
    return;
  }
  
  const start = new Date(booking.startDate);
  const end = new Date(booking.endDate);
  
  if (end < start) {
    bookingError.value = 'End date must be after start date';
    totalDays.value = 0;
    totalPrice.value = 0;
    return;
  }
  
  bookingError.value = null;
  // Calculate the difference in days
  const diffTime = Math.abs(end - start);
  const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24)) + 1; // Including the end day
  
  totalDays.value = diffDays;
  // Fixed price of 10£ per day
  totalPrice.value = diffDays * 10;
};

// Submit the booking
const submitBooking = async () => {
  if (!isLoggedIn.value) {
    goToLogin();
    return;
  }
  
  try {
    if (!booking.animalId || !booking.startDate || !booking.endDate) {
      bookingError.value = 'Please fill in all required fields';
      return;
    }
    
    const bookingData = {
      sitter: sitter.value.id,
      animal: booking.animalId,
      start_date: booking.startDate,
      end_date: booking.endDate,
      notes: booking.notes,
      status: 'pending',
      price: totalPrice.value
    };
    
    const response = await apiService.createBooking(bookingData);
    
    bookingSuccess.value = true;
    createdBookingId.value = response.id;
    bookingError.value = null;
  } catch (error) {
    console.error('Error creating booking:', error);
    bookingError.value = 'Failed to create booking. Please try again.';
  }
};

// Process the payment
const processPayment = async () => {
  if (!createdBookingId.value) {
    paymentError.value = 'No booking to pay for';
    return;
  }
  
  isProcessingPayment.value = true;
  
  try {
    const paymentData = {
      booking: createdBookingId.value,
      payment_type: paymentMethod.value,
      card_details: paymentMethod.value === 'card' ? {
        card_number: paymentDetails.cardNumber,
        expiry_date: paymentDetails.expiryDate,
        cvv: paymentDetails.cvv,
        card_name: paymentDetails.cardName
      } : null
    };
    
    await apiService.processPayment(paymentData);
    
    paymentSuccess.value = true;
    paymentError.value = null;
    
    // Redirect to pet owner dashboard after successful payment
    setTimeout(() => {
      router.push('/petowner');
    }, 2000);
  } catch (error) {
    console.error('Payment error:', error);
    paymentError.value = 'Payment processing failed. Please try again.';
  } finally {
    isProcessingPayment.value = false;
  }
};

// Navigation functions
const goToLogin = () => {
  router.push({ 
    name: 'Login',
    query: { redirect: route.fullPath }
  });
};

const goToRegister = () => {
  router.push({ 
    name: 'Register',
    query: { redirect: route.fullPath }
  });
};

onMounted(async () => {
  try {
    // Get sitter details from API using the ID from the route
    const sitterId = route.params.id;
    sitter.value = await apiService.getUserById(sitterId);
    
    // Get user's animals if logged in as pet owner
    if (isLoggedIn.value && userHasRole('petowner')) {
      const userData = JSON.parse(sessionStorage.getItem('user'));
      animals.value = await apiService.getAnimalsByOwner(userData.user_id);
    }
    
    loading.value = false;
  } catch (err) {
    console.error('Error loading data:', err);
    error.value = 'Failed to load pet sitter details';
    loading.value = false;
  }
});

// Watch for date changes to update the price
watch(() => [booking.startDate, booking.endDate], calculatePrice);
</script>

<style scoped>
.view-container {
  width: 100%;
  max-width: var(--max-content-width, 1200px);
  margin: 0 auto;
  padding: var(--space-xl, 2rem);
}

.petsitter-detail {
  background-color: var(--color-background, #fff);
  border-radius: var(--border-radius-lg, 0.5rem);
  box-shadow: var(--shadow-md, 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06));
  overflow: hidden;
}

.back-link {
  margin-bottom: var(--space-md, 1rem);
  padding: var(--space-md, 1rem);
}

.back-link a {
  color: var(--color-primary, #ff8c00);
  text-decoration: none;
  font-weight: 500;
  display: inline-flex;
  align-items: center;
  transition: color 0.2s ease;
}

.back-link a:hover {
  color: var(--color-primary-hover, #e67e00);
}

.sitter-profile {
  padding: var(--space-md, 1rem);
  border-bottom: 1px solid var(--color-border, #eaeaea);
}

.sitter-header {
  margin-bottom: var(--space-lg, 1.5rem);
}

.sitter-header h1 {
  margin-bottom: var(--space-xs, 0.5rem);
  font-size: 1.8rem;
  color: var(--color-heading, #333);
}

.sitter-contact {
  color: var(--color-text-light, #666);
  font-size: 0.95rem;
}

.sitter-body {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-lg, 1.5rem);
}

.sitter-info {
  flex: 1;
  min-width: 280px;
}

.sitter-info h2 {
  color: var(--color-heading, #333);
  font-size: 1.2rem;
  margin-top: var(--space-md, 1rem);
  margin-bottom: var(--space-sm, 0.75rem);
}

.sitter-info ul {
  padding-left: var(--space-lg, 1.5rem);
  margin: var(--space-sm, 0.75rem) 0;
}

.ratings {
  margin-top: var(--space-lg, 1.5rem);
}

.stars {
  color: var(--color-primary, #ff8c00);
  font-size: 1.25rem;
}

.rating-score {
  color: var(--color-text, #333);
  margin-left: var(--space-sm, 0.75rem);
  font-size: 0.95rem;
}

.pricing-info {
  background-color: var(--color-background-soft, #f9f9f9);
  padding: var(--space-lg, 1.5rem);
  border-bottom: 1px solid var(--color-border, #eaeaea);
}

.pricing-info h2 {
  color: var(--color-heading, #333);
  margin-bottom: var(--space-sm, 0.75rem);
}

.pricing-details {
  font-size: 1.1rem;
}

.price {
  color: var(--color-primary, #ff8c00);
  font-weight: 700;
}

.booking-section {
  padding: var(--space-lg, 1.5rem);
  background-color: var(--color-background, #fff);
}

.booking-section h2 {
  color: var(--color-heading, #333);
  margin-bottom: var(--space-lg, 1.5rem);
  font-size: 1.5rem;
}

form {
  display: flex;
  flex-direction: column;
  gap: var(--space-md, 1rem);
}

.form-group {
  display: flex;
  flex-direction: column;
}

label {
  margin-bottom: var(--space-xs, 0.5rem);
  font-weight: 500;
  color: var(--color-text, #333);
}

select, input, textarea {
  padding: var(--space-sm, 0.75rem);
  border: 1px solid var(--color-border, #eaeaea);
  border-radius: var(--border-radius-sm, 0.25rem);
  font-size: 1rem;
}

select:focus, input:focus, textarea:focus {
  outline: none;
  border-color: var(--color-primary, #ff8c00);
}

.price-calculation {
  background-color: var(--color-background-soft, #f9f9f9);
  padding: var(--space-md, 1rem);
  border-radius: var(--border-radius-sm, 0.25rem);
  margin: var(--space-sm, 0.75rem) 0;
}

.total-price {
  color: var(--color-primary, #ff8c00);
  font-size: 1.2rem;
  margin-top: var(--space-xs, 0.5rem);
}

.submit-btn, .login-btn, .register-btn {
  background-color: var(--color-primary, #ff8c00);
  color: white;
  border: none;
  padding: var(--space-md, 1rem);
  border-radius: var(--border-radius-sm, 0.25rem);
  font-weight: 600;
  cursor: pointer;
  transition: background-color 0.2s ease;
}

.submit-btn:hover, .login-btn:hover {
  background-color: var(--color-primary-hover, #e67e00);
}

.register-btn {
  background-color: var(--color-secondary, #2c3e50);
}

.register-btn:hover {
  background-color: var(--color-secondary-hover, #1a2530);
}

.success-message, .payment-success {
  background-color: var(--color-success-light, #d4edda);
  color: var(--color-success, #155724);
  padding: var(--space-md, 1rem);
  border-radius: var(--border-radius-sm, 0.25rem);
  margin: var(--space-md, 1rem) 0;
}

.error-message {
  background-color: var(--color-danger-light, #f8d7da);
  color: var(--color-danger, #721c24);
  padding: var(--space-md, 1rem);
  border-radius: var(--border-radius-sm, 0.25rem);
  margin: var(--space-md, 1rem) 0;
}

.payment-section {
  margin-top: var(--space-lg, 1.5rem);
  border-top: 1px dashed var(--color-border, #eaeaea);
  padding-top: var(--space-md, 1rem);
}

.test-mode-notice {
  background-color: var(--color-info-light, #d1ecf1);
  color: var(--color-info, #0c5460);
  padding: var(--space-sm, 0.75rem);
  border-radius: var(--border-radius-sm, 0.25rem);
  margin-bottom: var(--space-md, 1rem);
}

.payment-options-container {
  text-align: center;
  margin: var(--space-md, 1rem) 0;
}

.payment-details {
  margin-top: var(--space-lg, 1.5rem);
}

.payment-method {
  margin: var(--space-md, 1rem) 0;
}

.payment-options {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-md, 1rem);
  margin-top: var(--space-sm, 0.75rem);
}

.card-details {
  margin-top: var(--space-md, 1rem);
}

.card-info-row {
  display: flex;
  gap: var(--space-md, 1rem);
}

.card-info-row .form-group {
  flex: 1;
}

.payment-btn {
  background-color: var(--color-success, #28a745);
  color: white;
  border: none;
  padding: var(--space-md, 1rem);
  border-radius: var(--border-radius-sm, 0.25rem);
  font-weight: 600;
  cursor: pointer;
  transition: background-color 0.2s ease;
  margin-top: var(--space-md, 1rem);
  width: 100%;
}

.payment-btn:hover:not(:disabled) {
  background-color: var(--color-success-hover, #218838);
}

.payment-btn:disabled {
  background-color: var(--color-text-light, #6c757d);
  cursor: not-allowed;
}

.login-prompt {
  text-align: center;
  padding: var(--space-lg, 1.5rem);
  background-color: var(--color-background-soft, #f9f9f9);
}

.login-buttons {
  display: flex;
  gap: var(--space-md, 1rem);
  justify-content: center;
  margin-top: var(--space-md, 1rem);
}

.role-message {
  text-align: center;
  padding: var(--space-lg, 1.5rem);
  background-color: var(--color-info-light, #d1ecf1);
  color: var(--color-info, #0c5460);
}

.nav-btn {
  display: inline-block;
  background-color: var(--color-primary, #ff8c00);
  color: white;
  padding: var(--space-sm, 0.75rem) var(--space-md, 1rem);
  text-decoration: none;
  border-radius: var(--border-radius-sm, 0.25rem);
  margin-top: var(--space-md, 1rem);
}

.nav-btn:hover {
  background-color: var(--color-primary-hover, #e67e00);
}

@media (max-width: 768px) {
  .view-container {
    padding: var(--space-md, 1rem);
  }

  .sitter-body {
    flex-direction: column;
  }

  .card-info-row {
    flex-direction: column;
    gap: var(--space-sm, 0.75rem);
  }

  .login-buttons {
    flex-direction: column;
  }
}

.loading, .error {
  padding: var(--space-lg, 1.5rem);
  text-align: center;
  margin: var(--space-lg, 1.5rem) 0;
}

.error {
  color: var(--color-danger, #721c24);
}
</style>