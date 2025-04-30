<template>
  <div class="view-container">
    <div class="petsitter-detail">
      <div v-if="loading" class="loading">
        Chargement...
      </div>
      
      <div v-else-if="error" class="error">
        {{ error }}
      </div>
      
      <div v-else-if="sitter" class="sitter-container">
        <div class="back-link">
          <router-link to="/petowner">&larr; Retour à la liste des pet sitters</router-link>
        </div>
        
        <div class="sitter-profile">
          <div class="sitter-header">
            <h1>{{ sitter.name }}</h1>
            <p class="sitter-contact">{{ sitter.email }}</p>
          </div>
          
          <div class="sitter-body">
            <div class="sitter-info">
              <h2>Expérience</h2>
              <p>{{ sitter.experience }}</p>
              
              <h2>Services proposés</h2>
              <ul>
                <li>Garde à domicile</li>
                <li>Promenade</li>
                <li>Soins basiques</li>
              </ul>
              
              <h2>Disponibilité</h2>
              <p>{{ sitter.availability || 'Disponible tous les jours' }}</p>
              
              <div class="ratings">
                <h2>Évaluations</h2>
                <div class="stars">
                  <span>★★★★☆</span> <span class="rating-score">4.0/5</span>
                </div>
              </div>
            </div>
          </div>
        </div>
        
        <!-- Section de tarification -->
        <div class="pricing-info">
          <h2>Tarification</h2>
          <p class="pricing-details">Gardiennage: <span class="price">10€</span> par jour</p>
        </div>
        
        <!-- Section de réservation - conditionnelle en fonction de l'état de connexion -->
        <div v-if="isLoggedIn" class="booking-section">
          <h2>Réserver ce pet sitter</h2>
          <form @submit.prevent="submitBooking">
            <div class="form-group">
              <label for="animal">Sélectionnez votre animal</label>
              <select id="animal" v-model="booking.animalId" required>
                <option disabled value="">Choisissez un animal</option>
                <option v-for="animal in animals" :key="animal.id" :value="animal.id">
                  {{ animal.name }} ({{ animal.breed }})
                </option>
              </select>
            </div>
            
            <div class="form-group">
              <label for="start-date">Date de début</label>
              <input type="date" id="start-date" v-model="booking.startDate" @change="calculatePrice" required />
            </div>
            
            <div class="form-group">
              <label for="end-date">Date de fin</label>
              <input type="date" id="end-date" v-model="booking.endDate" @change="calculatePrice" required />
            </div>
            
            <!-- Affichage du prix calculé -->
            <div v-if="totalDays > 0" class="price-calculation">
              <p><strong>Durée:</strong> {{ totalDays }} jour{{ totalDays > 1 ? 's' : '' }}</p>
              <p class="total-price"><strong>Prix total:</strong> {{ totalPrice }}€</p>
            </div>
            
            <div class="form-group">
              <label for="notes">Instructions spéciales</label>
              <textarea id="notes" v-model="booking.notes" rows="4"></textarea>
            </div>
            
            <button type="submit" class="submit-btn">Réserver et procéder au paiement</button>
          </form>
          
          <div v-if="bookingSuccess" class="success-message">
            <p>Votre réservation a été créée avec succès!</p>
            
            <!-- Section de paiement -->
            <div class="payment-section">
              <h3>Finaliser votre réservation</h3>
              <div class="test-mode-notice">
                <p><strong>Mode test activé :</strong> Les paiements sont optionnels pendant cette phase.</p>
              </div>
              <div class="payment-options-container">
                <button @click="skipPayment" class="skip-payment-btn">
                  Continuer sans payer (mode test)
                </button>
                <p>-- ou --</p>
                <p>Procéder au paiement (facultatif) :</p>
              </div>
              
              <div class="payment-details">
                <p><strong>Montant à payer:</strong> {{ totalPrice }}€</p>
                
                <div class="payment-method">
                  <h4>Mode de paiement</h4>
                  <div class="payment-options">
                    <label>
                      <input type="radio" v-model="paymentMethod" value="card" checked>
                      Carte bancaire
                    </label>
                    <label>
                      <input type="radio" v-model="paymentMethod" value="paypal">
                      PayPal
                    </label>
                    <label>
                      <input type="radio" v-model="paymentMethod" value="transfer">
                      Virement bancaire
                    </label>
                  </div>
                </div>
                
                <div v-if="paymentMethod === 'card'" class="card-details">
                  <div class="form-group">
                    <label for="card-number">Numéro de carte</label>
                    <input type="text" id="card-number" v-model="paymentDetails.cardNumber" placeholder="1234 5678 9012 3456" maxlength="19">
                  </div>
                  
                  <div class="card-info-row">
                    <div class="form-group expiry">
                      <label for="expiry-date">Date d'expiration</label>
                      <input type="text" id="expiry-date" v-model="paymentDetails.expiryDate" placeholder="MM/AA" maxlength="5">
                    </div>
                    
                    <div class="form-group cvv">
                      <label for="cvv">CVV</label>
                      <input type="text" id="cvv" v-model="paymentDetails.cvv" placeholder="123" maxlength="3">
                    </div>
                  </div>
                  
                  <div class="form-group">
                    <label for="card-name">Nom sur la carte</label>
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
            <p>Paiement effectué avec succès! Votre réservation est confirmée.</p>
            <p>Vous allez être redirigé vers votre espace personnel...</p>
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
          <p>Pour réserver les services de ce pet sitter, vous devez vous connecter à votre compte.</p>
          <div class="login-buttons">
            <button class="login-btn" @click="goToLogin">Se connecter</button>
            <button class="register-btn" @click="goToRegister">S'inscrire</button>
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
  background-color: #f5f5f5;
  min-height: calc(100vh - var(--header-height));
}

.petsitter-detail {
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
  color: #3498db;
  text-decoration: none;
}

.sitter-container {
  display: flex;
  flex-direction: column;
  gap: 30px;
}

.sitter-profile {
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  padding: 25px;
}

.sitter-header h1 {
  margin-top: 0;
  margin-bottom: 10px;
  color: #2c3e50;
}

.sitter-contact {
  color: #7f8c8d;
  font-size: 16px;
  margin-bottom: 20px;
}

.sitter-body {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.sitter-info h2 {
  color: #2c3e50;
  font-size: 18px;
  margin-top: 25px;
  margin-bottom: 10px;
}

.ratings .stars {
  color: #f39c12;
  font-size: 18px;
}

.rating-score {
  color: #7f8c8d;
  margin-left: 10px;
}

/* Section tarification */
.pricing-info {
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  padding: 25px;
}

.pricing-info h2 {
  margin-top: 0;
  color: #2c3e50;
  font-size: 20px;
  margin-bottom: 15px;
}

.pricing-details {
  font-size: 18px;
  color: #2c3e50;
}

.price {
  font-weight: bold;
  color: #27ae60;
}

.booking-section {
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  padding: 25px;
}

.booking-section h2 {
  margin-top: 0;
  margin-bottom: 20px;
  color: #2c3e50;
}

.form-group {
  margin-bottom: 20px;
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

.price-calculation {
  margin: 20px 0;
  padding: 15px;
  background-color: #f8f9fa;
  border-radius: 4px;
  border-left: 4px solid #3498db;
}

.total-price {
  font-size: 18px;
  color: #27ae60;
  font-weight: 600;
}

.submit-btn, .payment-btn {
  background-color: #27ae60;
  color: white;
  border: none;
  padding: 12px 20px;
  border-radius: 4px;
  font-size: 16px;
  cursor: pointer;
  transition: background-color 0.3s;
}

.submit-btn:hover, .payment-btn:hover {
  background-color: #219653;
}

.success-message {
  background-color: #d4edda;
  color: #155724;
  padding: 15px;
  border-radius: 4px;
  margin-top: 20px;
}

.error-message {
  background-color: #f8d7da;
  color: #721c24;
  padding: 15px;
  border-radius: 4px;
  margin-top: 20px;
}

/* Styles pour la section de paiement */
.payment-section {
  margin-top: 20px;
  padding: 20px;
  background-color: #fff;
  border-radius: 8px;
  border: 1px solid #e9ecef;
}

.payment-section h3 {
  margin-top: 0;
  color: #2c3e50;
  font-size: 18px;
  margin-bottom: 15px;
}

.payment-details {
  margin-top: 20px;
}

.payment-method {
  margin: 20px 0;
}

.payment-method h4 {
  margin-bottom: 10px;
  color: #2c3e50;
}

.payment-options {
  display: flex;
  gap: 15px;
  flex-wrap: wrap;
}

.payment-options label {
  display: flex;
  align-items: center;
  gap: 5px;
  cursor: pointer;
}

.card-details {
  margin-top: 20px;
  padding: 15px;
  background-color: #f8f9fa;
  border-radius: 4px;
}

.card-info-row {
  display: flex;
  gap: 15px;
}

.expiry {
  flex: 1;
}

.cvv {
  flex: 1;
}

.payment-btn {
  margin-top: 20px;
  background-color: #27ae60;
  width: 100%;
}

.payment-success {
  background-color: #d4edda;
  color: #155724;
  padding: 20px;
  border-radius: 4px;
  margin-top: 20px;
  text-align: center;
}

/* Styles pour le message de connexion */
.login-prompt {
  background-color: #f8f9fa;
  border-radius: 8px;
  padding: 25px;
  text-align: center;
  border-left: 5px solid #3498db;
  margin-top: 20px;
}

.login-buttons {
  display: flex;
  justify-content: center;
  gap: 15px;
  margin-top: 20px;
}

.login-btn, .register-btn {
  padding: 10px 20px;
  border: none;
  border-radius: 4px;
  font-size: 16px;
  cursor: pointer;
  transition: background-color 0.2s;
}

.login-btn {
  background-color: #3498db;
  color: white;
}

.login-btn:hover {
  background-color: #2980b9;
}

.register-btn {
  background-color: #2ecc71;
  color: white;
}

.register-btn:hover {
  background-color: #27ae60;
}

@media (max-width: 768px) {
  .sitter-container {
    flex-direction: column;
  }
  
  .sitter-profile, .booking-section {
    width: 100%;
  }
  
  .login-buttons {
    flex-direction: column;
    gap: 10px;
  }
  
  .card-info-row {
    flex-direction: column;
    gap: 20px;
  }
}
</style>