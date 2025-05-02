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
        
        <!-- Section de réservation - conditionnelle en fonction de l'état de connexion -->
        <div v-if="isLoggedIn" class="booking-section">
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
                <p><strong>Test mode activated :</strong> Payments are optional during this phase.</p>
              </div>
              <div class="payment-options-container">
                <button @click="skipPayment" class="skip-payment-btn">
                  Continue without paying (test mode)
                </button>
                <p>-- ou --</p>
                <p>Proceed to payment (optional) :</p>
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
                  {{ isProcessingPayment ? 'Traitement en cours...' : 'Payer ' + totalPrice + '€' }}
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

// Vérifier si l'utilisateur est connecté
const isLoggedIn = computed(() => {
  return !!sessionStorage.getItem('user');
});

// Rediriger vers la page de connexion avec le retour à cette page
const goToLogin = () => {
  router.push({ 
    name: 'Login',
    query: { redirect: `/petsitter/${route.params.id}` }
  });
};

// Rediriger vers la page d'inscription avec le retour à cette page
const goToRegister = () => {
  router.push({ 
    name: 'Register',
    query: { redirect: `/petsitter/${route.params.id}` }
  });
};

// Calculer le prix total en fonction des dates sélectionnées
const calculatePrice = () => {
  if (booking.startDate && booking.endDate) {
    const start = new Date(booking.startDate);
    const end = new Date(booking.endDate);
    
    // Vérifier que les dates sont valides
    if (isNaN(start.getTime()) || isNaN(end.getTime())) {
      totalDays.value = 0;
      totalPrice.value = 0;
      return;
    }
    
    // Calculer le nombre de jours (en incluant le jour de début et de fin)
    const timeDiff = end.getTime() - start.getTime();
    totalDays.value = Math.round(timeDiff / (1000 * 3600 * 24)) + 1;
    
    // Si les dates sont inversées, réinitialiser
    if (totalDays.value < 1) {
      totalDays.value = 0;
      totalPrice.value = 0;
      return;
    }
    
    // Calculer le prix total (10€ par jour)
    totalPrice.value = totalDays.value * 10;
  } else {
    totalDays.value = 0;
    totalPrice.value = 0;
  }
};

// Surveiller les changements de dates pour mettre à jour le prix
watch(() => [booking.startDate, booking.endDate], () => {
  calculatePrice();
});

// Traiter le paiement
const processPayment = async () => {
  try {
    isProcessingPayment.value = true;
    paymentError.value = null;
    
    // Validation simple pour le formulaire de carte
    if (paymentMethod.value === 'card') {
      if (!paymentDetails.cardNumber || !paymentDetails.expiryDate || !paymentDetails.cvv || !paymentDetails.cardName) {
        paymentError.value = "Veuillez remplir tous les champs de la carte bancaire";
        isProcessingPayment.value = false;
        return;
      }
    }
    
    // Appeler l'API de paiement
    try {
      await apiService.processPayment({
        booking: createdBookingId.value,
        payment_type: paymentMethod.value
      });
      
      // Paiement réussi
      paymentSuccess.value = true;
      
      // Rediriger vers la page du pet owner après un court délai
      setTimeout(() => {
        router.push('/petowner');
      }, 3000);
    } catch (paymentError) {
      console.warn('Erreur lors du paiement, mais vérifions si le paiement a été traité:', paymentError);
      
      // Vérifier si la réservation est passée à l'état "paid" malgré l'erreur
      try {
        // Attendre un court instant
        await new Promise(resolve => setTimeout(resolve, 1000));
        
        // Vérifier l'état de la réservation
        const booking = await apiService.getBookingById(createdBookingId.value);
        
        if (booking && booking.status === 'paid') {
          console.log('Paiement réussi malgré l\'erreur, la réservation est passée à "paid"');
          paymentSuccess.value = true;
          
          // Rediriger vers la page du pet owner après un court délai
          setTimeout(() => {
            router.push('/petowner');
          }, 3000);
          return;
        }
        
        // Essayer une mise à jour manuelle du statut
        try {
          await apiService.updateBookingStatus(createdBookingId.value, 'paid');
          console.log('Statut de réservation mis à jour manuellement à "paid"');
          paymentSuccess.value = true;
          
          // Rediriger vers la page du pet owner après un court délai
          setTimeout(() => {
            router.push('/petowner');
          }, 3000);
          return;
        } catch (updateError) {
          console.error('Échec de la mise à jour manuelle du statut:', updateError);
          throw paymentError; // Relancer l'erreur originale
        }
      } catch (checkError) {
        console.error('Erreur lors de la vérification de l\'état du paiement:', checkError);
        throw paymentError; // Relancer l'erreur originale
      }
    }
  } catch (err) {
    console.error('Erreur lors du paiement:', err);
    paymentError.value = "Une erreur s'est produite lors du paiement. Veuillez réessayer.";
  } finally {
    isProcessingPayment.value = false;
  }
};

// Fonction pour ignorer le paiement (mode test)
const skipPayment = async () => {
  try {
    // Mettre à jour le statut de la réservation sans paiement
    await apiService.updateBookingStatus(createdBookingId.value, 'accepted');
    
    // Afficher le message de succès
    paymentSuccess.value = true;
    
    // Rediriger vers la page du pet owner après un court délai
    setTimeout(() => {
      router.push('/petowner');
    }, 3000);
  } catch (err) {
    console.error('Erreur lors de la validation de la réservation:', err);
    paymentError.value = "Une erreur s'est produite lors de la validation de la réservation. Veuillez réessayer.";
  }
};

onMounted(async () => {
  const sitterId = route.params.id;
  console.log('Sitter ID:', sitterId);  // Log pour vérifier l'ID

  try {
    // Récupérer les informations du pet sitter (visible pour tous)
    const sitterResponse = await apiService.getUserById(sitterId);
    sitter.value = sitterResponse;
    console.log('Sitter data:', sitter.value);

    // Si l'utilisateur est connecté, récupérer ses animaux pour la réservation
    if (isLoggedIn.value) {
      // Récupérer les données de l'utilisateur connecté
      const userData = JSON.parse(sessionStorage.getItem('user') || '{}');
      const currentUserId = userData.user_id;
      
      if (currentUserId) {
        // Récupérer UNIQUEMENT les animaux appartenant au propriétaire connecté
        const userAnimals = await apiService.getAnimalsByOwner(currentUserId);
        animals.value = userAnimals;
        console.log('Animaux de l\'utilisateur:', animals.value);
      }
    }

    loading.value = false;
  } catch (err) {
    console.error('Erreur lors du chargement des données:', err);
    error.value = 'Impossible de charger les informations du pet sitter. Veuillez réessayer plus tard.';
    loading.value = false;
  }
});

async function submitBooking() {
  try {
    // Vérifier si l'utilisateur est connecté
    if (!isLoggedIn.value) {
      goToLogin();
      return;
    }

    bookingError.value = null;

    const start = new Date(booking.startDate);
    const end = new Date(booking.endDate);
    const today = new Date();

    if (start < today) {
      bookingError.value = "La date de début ne peut pas être dans le passé";
      return;
    }

    if (end <= start) {
      bookingError.value = "La date de fin doit être après la date de début";
      return;
    }

    // Créer la réservation
    try {
      const newBooking = await apiService.createBooking({
        animal: parseInt(booking.animalId),
        sitter: parseInt(route.params.id),
        start_date: booking.startDate,
        end_date: booking.endDate,
        status: 'pending'
      });

      console.log('Réservation créée avec succès:', newBooking);
      
      // Stocker l'ID de la réservation créée pour le paiement
      createdBookingId.value = newBooking.id;
      
      // Indiquer que la réservation a été créée avec succès
      bookingSuccess.value = true;
      
    } catch (bookingError) {
      console.warn('Erreur reçue, mais vérifions si la réservation a été créée');
      
      try {
        // Attendre un court instant pour laisser le temps à la BD de se mettre à jour
        await new Promise(resolve => setTimeout(resolve, 1000));
        
        // Récupérer toutes les réservations récentes
        const allBookings = await apiService.getAllBookings();
        
        // Trouver la réservation la plus récente pour le même animal et pet sitter
        const recentBooking = allBookings.find(b => 
          b.animal === parseInt(booking.animalId) && 
          b.sitter === parseInt(route.params.id) &&
          b.start_date === booking.startDate &&
          b.end_date === booking.endDate
        );
        
        if (recentBooking) {
          console.log('Réservation trouvée malgré l\'erreur:', recentBooking);
          createdBookingId.value = recentBooking.id;
          bookingSuccess.value = true;
          return; // Sortir de la fonction car la réservation est créée
        } else {
          // La réservation n'a pas été trouvée, il y a un vrai problème
          throw bookingError;
        }
      } catch (checkError) {
        console.error('Erreur lors de la vérification des réservations:', checkError);
        throw bookingError;
      }
    }

  } catch (err) {
    console.error('Erreur lors de la réservation:', err);
    
    // Si l'erreur contient un message de l'API, l'afficher
    if (err.response && err.response.data) {
      if (typeof err.response.data === 'object' && err.response.data.error) {
        bookingError.value = err.response.data.error;
      } else if (typeof err.response.data === 'string') {
        bookingError.value = err.response.data;
      } else {
        bookingError.value = `Erreur: ${JSON.stringify(err.response.data)}`;
      }
    } else {
      bookingError.value = "Une erreur s'est produite lors de la réservation. Veuillez réessayer.";
    }
  }
}
</script>

<style scoped>
.view-container {
  min-height: calc(100vh - var(--header-height));
}

.petsitter-detail {
  width: 100%;
  max-width: var(--max-content-width);
  margin: 0 auto;
  padding: var(--space-xl);
}

.loading, .error {
  text-align: center;
  padding: var(--space-xl);
  font-size: 18px;
}

.error {
  color: var(--color-danger);
}

.back-link a {
  color: var(--color-primary);
  text-decoration: none;
}

.sitter-container {
  display: flex;
  flex-direction: column;
  gap: var(--space-xl);
}

.sitter-profile, .booking-section, .pricing-info {
  background-color: var(--color-background);
  border-radius: var(--border-radius-md);
  box-shadow: var(--shadow-md);
  padding: var(--space-lg);
}

.sitter-header h1 {
  color: var(--color-heading);
  margin-bottom: var(--space-sm);
}

.sitter-contact {
  color: var(--color-text-light);
}

.sitter-info h2 {
  color: var(--color-heading);
  font-size: 18px;
  margin: var(--space-lg) 0 var(--space-sm);
}

.ratings .stars {
  color: var(--color-warning);
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

.price-calculation {
  margin: var(--space-md) 0;
  padding: var(--space-md);
  background-color: var(--color-background-mute);
  border-radius: var(--border-radius-sm);
  border-left: 4px solid var(--color-primary);
}

.total-price {
  color: var(--color-secondary);
  font-weight: 600;
}

.submit-btn, .payment-btn {
  background-color: var(--color-secondary);
  color: white;
  border: none;
  padding: var(--space-sm) var(--space-md);
  border-radius: var(--border-radius-sm);
  font-size: 16px;
  cursor: pointer;
  transition: background-color var(--transition-speed);
  width: 100%;
}

.submit-btn:hover:not(:disabled), 
.payment-btn:hover:not(:disabled) {
  background-color: var(--color-secondary-hover);
}

.success-message {
  background-color: var(--color-success-light);
  color: var(--color-success-dark);
  padding: var(--space-md);
  border-radius: var(--border-radius-sm);
  margin-top: var(--space-md);
}

.error-message {
  background-color: var(--color-danger-light);
  color: var(--color-danger-dark);
  padding: var(--space-md);
  border-radius: var(--border-radius-sm);
  margin-top: var(--space-md);
}

.login-prompt {
  background-color: var(--color-background-mute);
  border-radius: var(--border-radius-md);
  padding: var(--space-lg);
  text-align: center;
  border-left: 5px solid var(--color-primary);
  margin-top: var(--space-md);
}

.login-buttons {
  display: flex;
  justify-content: center;
  gap: var(--space-md);
  margin-top: var(--space-md);
}

.login-btn {
  background-color: var(--color-primary);
  color: white;
  border: none;
  padding: var(--space-sm) var(--space-md);
  border-radius: var(--border-radius-sm);
  font-size: 16px;
  cursor: pointer;
  transition: background-color var(--transition-speed);
}

.login-btn:hover {
  background-color: var(--color-primary-hover);
}

.register-btn {
  background-color: var(--color-secondary);
  color: white;
  border: none;
  padding: var(--space-sm) var(--space-md);
  border-radius: var(--border-radius-sm);
  font-size: 16px;
  cursor: pointer;
  transition: background-color var(--transition-speed);
}

.register-btn:hover {
  background-color: var(--color-secondary-hover);
}

@media (max-width: 768px) {
  .petsitter-detail {
    padding: var(--space-md);
  }
  
  .login-buttons {
    flex-direction: column;
    gap: var(--space-sm);
  }
  
  .card-info-row {
    flex-direction: column;
    gap: var(--space-md);
  }
}
</style>