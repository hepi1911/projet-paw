<template>
  <div class="view-container">
    <!-- Barre de notification pour les nouvelles demandes -->
    <div v-if="showNotificationBar" class="notification-bar">
      <span>{{ notification }}</span>
      <button class="close-btn" @click="showNotificationBar = false">&times;</button>
    </div>
    
    <div class="company-dashboard">
      <h1>Dashboard Company</h1>
      
      <!-- Navigation -->
      <div class="profile-nav">
        <button class="profile-btn" @click="goToProfile">See my profile</button>
      </div>

      <!-- Information de la compagnie -->
      <div class="company-info-section" v-if="currentCompany">
        <h2>My company</h2>
        <div class="company-info-card">
          <div class="company-details">
            <h3>{{ currentCompany.name }}</h3>
            <p><strong>Address:</strong> {{ currentCompany.address || 'Not specified' }}</p>
            <p class="capacity-info">
              <strong>Capacity:</strong> {{ currentCompany.capacity || 0 }} pets
              <span v-if="currentCapacityUsed > 0" class="capacity-used">
                ({{ currentCapacityUsed }} in progress)
              </span>
            </p>
            <div class="capacity-bar-container">
              <div class="capacity-bar" :class="capacityBarClass" :style="{ width: capacityPercentage + '%' }"></div>
            </div>
          </div>
          <div class="company-actions">
            <button class="edit-profile-btn" @click="openProfileModal">Modify my profile</button>
          </div>
        </div>
      </div>

      <!-- Réservations en attente -->
      <div class="bookings-section" v-if="pendingBookings.length > 0">
        <h2>Pending booking</h2>
        <div class="bookings-list">
          <div v-for="booking in pendingBookings" 
               :key="booking.id" 
               class="booking-card pending">
            <div class="booking-info">
              <h3>Booking of {{ getPetSitterName(booking.petsitter) }}</h3>
              <p><strong>Type of service:</strong> {{ getServiceLabel(booking.service_type) }}</p>
              <p><strong>Dates:</strong> {{ formatDate(booking.start_date) }} - {{ formatDate(booking.end_date) }}</p>
              <p><strong>Details:</strong> {{ booking.details || 'Aucun détail fourni' }}</p>
              <p class="status"><strong>Status:</strong> On hold</p>
              
              <div class="booking-actions">
                <button 
                  class="accept-btn" 
                  @click="updateBookingStatus(booking.id, 'accepted')" 
                  :disabled="isUpdating === booking.id || isCapacityFull"
                  :title="isCapacityFull ? 'Maximum capacity reached' : ''"
                >
                  {{ isUpdating === booking.id ? 'In progress...' : 'Accept' }}
                </button>
                <button 
                  class="refuse-btn" 
                  @click="updateBookingStatus(booking.id, 'refused')" 
                  :disabled="isUpdating === booking.id"
                >
                  {{ isUpdating === booking.id ? 'In progress...' : 'Refuse' }}
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
      <div v-else-if="!loading" class="empty-message">
        <p>No bookings pending</p>
      </div>

      <!-- Toutes les réservations -->
      <div class="bookings-section" v-if="bookings.length > 0">
        <h2>Booking history</h2>
        <div class="bookings-list">
          <div v-for="booking in bookings" 
               :key="booking.id" 
               class="booking-card"
               :class="booking.status">
            <div class="booking-info">
              <h3>Booking of {{ getPetSitterName(booking.petsitter) }}</h3>
              <p><strong>Type of service:</strong> {{ getServiceLabel(booking.service_type) }}</p>
              <p><strong>Dates:</strong> {{ formatDate(booking.start_date) }} - {{ formatDate(booking.end_date) }}</p>
              <p><strong>Details:</strong> {{ booking.details || 'Aucun détail fourni' }}</p>
              <p class="status"><strong>Status:</strong> {{ getStatusLabel(booking.status) }}</p>
              <p class="payment-status" v-if="booking.status === 'accepted'">
                <strong>Payment:</strong> 
                <span :class="booking.company_paid ? 'paid' : 'unpaid'">
                  {{ booking.company_paid ? 'Completed' : 'Payment required' }}
                </span>
              </p>
              
              <div class="booking-actions" v-if="booking.status === 'accepted' && !booking.company_paid">
                <button 
                  class="payment-btn" 
                  @click="initiatePayment(booking.id)"
                  :disabled="isProcessingPayment"
                >
                  <i class="btn-icon">💳</i>
                  {{ isUpdating === booking.id ? 'Processing...' : 'Make a payment' }}
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
      <div v-else-if="!loading && pendingBookings.length === 0" class="empty-message">
        <p>No bookings to display</p>
      </div>

      <!-- Loading indicator -->
      <div v-if="loading" class="loading">
        <p>Loading data...</p>
      </div>
    </div>
    
    <!-- Modal de modification du profil -->
    <div v-if="showProfileModal" class="modal-backdrop" @click="showProfileModal = false">
      <div class="modal-content" @click.stop>
        <h3>Modify my company profile</h3>
        
        <form @submit.prevent="updateCompanyProfile" class="profile-form">
          <div class="form-group">
            <label for="name">Name of the company</label>
            <input type="text" id="name" v-model="profileForm.name" required>
          </div>
          
          <div class="form-group">
            <label for="email">Email</label>
            <input type="email" id="email" v-model="profileForm.email" required>
          </div>
          
          <div class="form-group">
            <label for="address">Address</label>
            <input type="text" id="address" v-model="profileForm.address">
          </div>
          
          <div class="form-group">
            <label for="capacity">Capacity (number of pets)</label>
            <input type="number" id="capacity" v-model="profileForm.capacity" min="1">
          </div>
          
          <h4>Change the password (optional)</h4>
          
          <div class="form-group">
            <label for="current-password">Current password</label>
            <input type="password" id="current-password" v-model="profileForm.currentPassword">
          </div>
          
          <div class="form-group">
            <label for="new-password">New password</label>
            <input type="password" id="new-password" v-model="profileForm.newPassword">
          </div>
          
          <div class="form-group">
            <label for="confirm-password">Confirm the new password</label>
            <input type="password" id="confirm-password" v-model="profileForm.confirmPassword">
          </div>
          
          <div class="form-actions">
            <button type="button" class="cancel-btn" @click="showProfileModal = false">Cancel</button>
            <button type="submit" class="submit-btn" :disabled="isUpdatingProfile">
              {{ isUpdatingProfile ? 'Update in progress...' : 'To update' }}
            </button>
          </div>
        </form>
      </div>
    </div>
    
    <!-- Modal de paiement -->
    <div v-if="showPaymentModal" class="modal-backdrop" @click="showPaymentModal = false">
      <div class="modal-content payment-modal" @click.stop>
        <h3>Payment Confirmation</h3>
        
        <div v-if="currentPaymentBooking" class="payment-details">
          <p class="payment-message">{{ currentPaymentBooking.details }}</p>
          
          <div class="payment-summary">
            <div class="payment-item">
              <span class="label">Service Amount:</span>
              <span class="value">{{ currentPaymentBooking.amount.toFixed(2) }}€</span>
            </div>
            <div class="payment-item">
              <span class="label">Service Fee:</span>
              <span class="value">{{ currentPaymentBooking.serviceFee.toFixed(2) }}€</span>
            </div>
            <div class="payment-item total">
              <span class="label">Total Amount:</span>
              <span class="value">{{ currentPaymentBooking.totalAmount.toFixed(2) }}€</span>
            </div>
          </div>
          
          <div class="payment-method">
            <h4>Payment Method</h4>
            <div class="payment-options">
              <label class="payment-option">
                <input type="radio" v-model="paymentMethod" value="card" checked>
                <span class="payment-option-label">Credit Card</span>
              </label>
              <label class="payment-option">
                <input type="radio" v-model="paymentMethod" value="paypal">
                <span class="payment-option-label">PayPal</span>
              </label>
              <label class="payment-option">
                <input type="radio" v-model="paymentMethod" value="transfer">
                <span class="payment-option-label">Bank Transfer</span>
              </label>
            </div>
          </div>
          
          <div class="form-actions">
            <button type="button" class="cancel-btn" @click="showPaymentModal = false">Cancel</button>
            <button 
              type="button" 
              class="pay-btn" 
              @click="processPayment()"
              :disabled="isProcessingPayment"
            >
              {{ isProcessingPayment ? 'Processing...' : 'Confirm Payment' }}
            </button>
          </div>
        </div>
        
        <div v-else class="payment-error">
          <p>Unable to process payment. Please try again.</p>
          <button type="button" class="cancel-btn" @click="showPaymentModal = false">Close</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { apiService } from '../services/api';

const router = useRouter();
const bookings = ref([]);
const petSitterCache = ref({});
const currentCompany = ref(null);
const loading = ref(true);
const isUpdating = ref(null);
const showProfileModal = ref(false);
const isUpdatingProfile = ref(false);
const notification = ref('');
const showNotificationBar = ref(false);
const profileForm = ref({
  name: '',
  email: '',
  address: '',
  capacity: null,
  currentPassword: '',
  newPassword: '',
  confirmPassword: ''
});
const currentPaymentBooking = ref(null);
const showPaymentModal = ref(false);
const paymentMethod = ref('card');
const isProcessingPayment = ref(false);

// Filtrer les réservations en attente
const pendingBookings = computed(() => {
  return bookings.value.filter(booking => booking.status === 'pending');
});

// Calcul de la capacité utilisée actuellement
const currentCapacityUsed = computed(() => {
  return bookings.value.filter(booking => booking.status === 'accepted').length;
});

// Vérifier si la capacité est pleine
const isCapacityFull = computed(() => {
  if (!currentCompany.value || !currentCompany.value.capacity) return false;
  return currentCapacityUsed.value >= currentCompany.value.capacity;
});

// Calcul du pourcentage de capacité utilisé
const capacityPercentage = computed(() => {
  if (!currentCompany.value || !currentCompany.value.capacity || currentCompany.value.capacity === 0) {
    return 0;
  }
  return Math.min(100, (currentCapacityUsed.value / currentCompany.value.capacity) * 100);
});

// Classe de la barre de capacité en fonction du remplissage
const capacityBarClass = computed(() => {
  const percentage = capacityPercentage.value;
  if (percentage < 50) return 'low';
  if (percentage < 75) return 'medium';
  return 'high';
});

// Chargement des données
const loadData = async () => {
  try {
    loading.value = true;
    
    // Récupérer l'ID de l'utilisateur connecté depuis le sessionStorage (au lieu de localStorage)
    const userData = JSON.parse(sessionStorage.getItem('user') || '{}');
    const currentUserId = userData.user_id;
    
    if (!currentUserId) {
      console.error('User not logged in');
      router.push('/login');
      return;
    }
    
    // Récupérer les informations de la compagnie actuelle
    currentCompany.value = await apiService.getUserById(currentUserId);
    
    // Récupérer toutes les réservations de la compagnie
    bookings.value = await apiService.getPetSitterCompanyBookings(null, currentUserId);
    
    // Récupérer les informations des pet sitters pour l'affichage
    for (const booking of bookings.value) {
      if (booking.petsitter && !petSitterCache.value[booking.petsitter]) {
        try {
          const petSitter = await apiService.getUserById(booking.petsitter);
          petSitterCache.value[booking.petsitter] = petSitter;
        } catch (error) {
          console.error('Error retrieving pet sitter information:', error);
        }
      }
    }
    
    // Vérifier s'il y a de nouvelles demandes et afficher une notification
    const pendingCount = pendingBookings.value.length;
    if (pendingCount > 0) {
      showNotification(`You have ${pendingCount} new reservation request(s) pending.`);
    }
  } catch (error) {
    console.error('Error loading data:', error);
  } finally {
    loading.value = false;
  }
};

// Mise à jour du statut d'une réservation
const updateBookingStatus = async (bookingId, newStatus) => {
  try {
    isUpdating.value = bookingId;
    
    // Si la compagnie est à capacité maximale et qu'on tente d'accepter, empêcher l'action
    if (newStatus === 'accepted' && isCapacityFull.value) {
      alert('Unable to accept this reservation: maximum capacity reached.');
      return;
    }
    
    // Mettre à jour le statut
    const response = await apiService.updatePetSitterCompanyBookingStatus(bookingId, newStatus);
    
    // Si la réponse indique qu'un paiement est nécessaire
    if (response && response.requires_payment) {
      // Stocker les informations de paiement et ouvrir le modal de paiement
      currentPaymentBooking.value = {
        id: bookingId,
        amount: response.amount,
        serviceFee: response.service_fee || 2.80,
        totalAmount: response.total_amount || (response.amount + 2.80),
        details: response.message || 'Payment required to confirm this reservation'
      };
      showPaymentModal.value = true;
    } else {
      // Mettre à jour la réservation localement
      const bookingIndex = bookings.value.findIndex(b => b.id === bookingId);
      if (bookingIndex !== -1) {
        bookings.value[bookingIndex].status = newStatus;
      }
      
      // Afficher un message de confirmation
      alert(`The reservation was ${getStatusLabel(newStatus).toLowerCase()} successfully!`);
    }
  } catch (error) {
    console.error('Error updating reservation status:', error);
    alert('An error occurred while updating the status. Please try again.');
  } finally {
    isUpdating.value = null;
  }
};

// Fonction pour ouvrir la modal de modification du profil
const openProfileModal = () => {
  // Initialiser le formulaire avec les données de l'entreprise actuelle
  profileForm.value = {
    name: currentCompany.value.name || '',
    email: currentCompany.value.email || '',
    address: currentCompany.value.address || '',
    capacity: currentCompany.value.capacity || null,
    currentPassword: '',
    newPassword: '',
    confirmPassword: ''
  };
  
  showProfileModal.value = true;
};

// Mettre à jour le profil de l'entreprise
const updateCompanyProfile = async () => {
  try {
    isUpdatingProfile.value = true;
    
    // Valider les mots de passe uniquement si un nouveau mot de passe est fourni
    if (profileForm.value.newPassword) {
      if (profileForm.value.newPassword !== profileForm.value.confirmPassword) {
        alert('The new passwords do not match.');
        isUpdatingProfile.value = false;
        return;
      }
      
      // Vérifier que le mot de passe actuel est bien renseigné
      if (!profileForm.value.currentPassword) {
        alert('Please enter your current password to confirm the change.');
        isUpdatingProfile.value = false;
        return;
      }
    }
    
    // Préparer les données à mettre à jour
    const updateData = {
      name: profileForm.value.name,
      email: profileForm.value.email,
      address: profileForm.value.address || '',
      capacity: profileForm.value.capacity || null
    };
    
    // Ajouter les informations de mot de passe uniquement si un nouveau mot de passe est fourni
    if (profileForm.value.newPassword && profileForm.value.currentPassword) {
      updateData.current_password = profileForm.value.currentPassword;
      updateData.new_password = profileForm.value.newPassword;
    }
    
    // Mettre à jour le profil
    await apiService.updateUserProfile(currentCompany.value.id, updateData);
    
    // Mettre à jour les informations locales
    currentCompany.value = { 
      ...currentCompany.value, 
      name: profileForm.value.name,
      email: profileForm.value.email,
      address: profileForm.value.address,
      capacity: profileForm.value.capacity
    };
    
    // Fermer la modal et afficher un message de confirmation
    showProfileModal.value = false;
    alert('Your business profile has been successfully updated!');
  } catch (error) {
    console.error('Error updating profile:', error);
    alert('An error occurred while updating your profile. Please try again.');
  } finally {
    isUpdatingProfile.value = false;
  }
};

// Formater une date pour l'affichage
const formatDate = (dateString) => {
  return new Date(dateString).toLocaleDateString();
};

// Obtenir le nom d'un pet sitter à partir de son ID
const getPetSitterName = (petsitterId) => {
  const petSitter = petSitterCache.value[petsitterId];
  return petSitter ? petSitter.name : 'Pet sitter inconnu';
};

// Obtenir le libellé d'un statut
const getStatusLabel = (status) => {
  const statusLabels = {
    'pending': 'En attente',
    'accepted': 'Acceptée',
    'refused': 'Refusée',
    'cancelled': 'Annulée'
  };
  return statusLabels[status] || status;
};

// Obtenir le libellé d'un type de service
const getServiceLabel = (serviceType) => {
  const serviceLabels = {
    'formation': 'Formation spécialisée',
    'consultation': 'Consultation professionnelle',
    'collaboration': 'Collaboration pour garde d\'animaux'
  };
  return serviceLabels[serviceType] || serviceType;
};

// Rediriger vers la page de profil
const goToProfile = () => {
  router.push('/profile');
};

// Afficher une notification
const showNotification = (message) => {
  notification.value = message;
  showNotificationBar.value = true;
  
  // Masquer la notification après 5 secondes
  setTimeout(() => {
    showNotificationBar.value = false;
  }, 5000);
};

// Traiter le paiement
const processPayment = async () => {
  try {
    if (!currentPaymentBooking.value) {
      alert('Error: Missing reservation information');
      return;
    }

    isProcessingPayment.value = true;
    
    // Appeler l'API pour traiter le paiement en utilisant le service modifié
    const response = await apiService.processCompanyPayment(
      currentPaymentBooking.value.id,
      paymentMethod.value
    );
    
    // Mettre à jour la réservation localement
    const bookingIndex = bookings.value.findIndex(b => b.id === currentPaymentBooking.value.id);
    if (bookingIndex !== -1) {
      bookings.value[bookingIndex].status = 'accepted';
      bookings.value[bookingIndex].company_paid = true;
    }
    
    // Fermer le modal et afficher un message de confirmation
    showPaymentModal.value = false;
    currentPaymentBooking.value = null;
    
    alert('Payment processed successfully! The reservation is now confirmed.');
    
    // Rafraîchir les données
    await loadData();
  } catch (error) {
    console.error('Error processing payment:', error);
    alert('An error occurred while processing your payment. Please try again.');
  } finally {
    isProcessingPayment.value = false;
  }
};

// Initialiser le paiement
const initiatePayment = async (bookingId) => {
  try {
    isUpdating.value = bookingId;
    const booking = bookings.value.find(b => b.id === bookingId);
    
    if (!booking) {
      alert('Error: Reservation not found');
      return;
    }
    
    // Calculer le montant standard si non disponible
    const amount = booking.service_cost || 50.0;
    const serviceFee = 2.80;
    const totalAmount = amount + serviceFee;
    
    // Préparer les informations pour le modal de paiement
    currentPaymentBooking.value = {
      id: bookingId,
      amount: amount,
      serviceFee: serviceFee,
      totalAmount: totalAmount,
      details: `Confirmation of payment for the reservation with${getPetSitterName(booking.petsitter)}`
    };
    
    // Ouvrir le modal de paiement
    showPaymentModal.value = true;
    
  } catch (error) {
    console.error('Error initializing payment:', error);
    alert('An error occurred while initializing the payment. Please try again.');
  } finally {
    isUpdating.value = null;
  }
};

// Charger les données au montage du composant
onMounted(async () => {
  await loadData();
});
</script>

<style scoped>
.company-dashboard {
  width: 100%;
  max-width: var(--max-content-width);
  margin: 0 auto;
  padding: var(--space-xl);
}

.dashboard-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--space-xl);
}

/* Section Profil */
.profile-section {
  margin-bottom: var(--space-xl);
}

.profile-card {
  background-color: var(--color-background);
  border-radius: var(--border-radius-md);
  padding: var(--space-lg);
  box-shadow: var(--shadow-md);
  border-left: 5px solid var(--color-primary);
}

.profile-info {
  margin-bottom: var(--space-lg);
}

.profile-actions {
  display: flex;
  gap: var(--space-md);
}

.edit-profile-btn {
  background-color: var(--color-primary);
  color: white;
  border: none;
  padding: var(--space-sm) var(--space-md);
  border-radius: var(--border-radius-sm);
  cursor: pointer;
  font-weight: 600;
  transition: background-color var(--transition-speed);
}

.edit-profile-btn:hover {
  background-color: var(--color-primary-hover);
}

/* Information de la compagnie */
.company-info-section {
  margin-bottom: var(--space-xl);
}

.company-info-card {
  background-color: var(--color-background);
  border-radius: var(--border-radius-md);
  padding: var(--space-lg);
  box-shadow: var(--shadow-md);
  border-left: 5px solid var(--color-primary);
}

.capacity-info {
  margin: var(--space-md) 0;
}

.capacity-used {
  font-style: italic;
  margin-left: var(--space-sm);
}

.capacity-bar-container {
  height: 8px;
  background-color: var(--color-background-mute);
  border-radius: var(--border-radius-sm);
  margin: var(--space-md) 0;
  width: 100%;
  overflow: hidden;
}

.capacity-bar {
  height: 100%;
  transition: width var(--transition-speed), background-color var(--transition-speed);
}

.capacity-bar.low {
  background-color: var(--color-success);
}

.capacity-bar.medium {
  background-color: var(--color-warning);
}

.capacity-bar.high {
  background-color: var(--color-danger);
}

/* Section Réservations */
.bookings-section {
  margin-bottom: var(--space-xl);
  background-color: var(--color-background-soft);
  border-radius: var(--border-radius-md);
  padding: var(--space-lg);
}

.bookings-list {
  display: flex;
  flex-direction: column;
  gap: var(--space-md);
}

.booking-card {
  background-color: var(--color-background);
  border-radius: var(--border-radius-md);
  padding: var(--space-lg);
  box-shadow: var(--shadow-md);
  border-left: 5px solid var(--color-border);
  transition: transform var(--transition-speed), box-shadow var(--transition-speed);
}

.booking-card:hover {
  transform: translateY(-3px);
  box-shadow: var(--shadow-lg);
}

/* Status-specific styles */
.booking-card.pending {
  border-left-color: var(--color-warning);
}

.booking-card.pending .status {
  color: var(--color-warning);
}

.booking-card.accepted {
  border-left-color: var(--color-success);
}

.booking-card.accepted .status {
  color: var(--color-success);
}

.booking-card.refused {
  border-left-color: var(--color-danger);
}

.booking-card.refused .status {
  color: var(--color-danger);
}

.booking-card.cancelled {
  border-left-color: var(--color-text-light);
  opacity: 0.8;
}

.booking-card.cancelled .status {
  color: var(--color-text-light);
}

/* Actions buttons */
.booking-actions {
  display: flex;
  gap: var(--space-md);
  margin-top: var(--space-md);
}

.accept-btn, .submit-btn {
  background-color: var(--color-success);
  color: white;
  border: none;
  border-radius: var(--border-radius-sm);
  padding: var(--space-sm) var(--space-md);
  cursor: pointer;
  font-weight: 600;
  transition: background-color var(--transition-speed);
}

.accept-btn:hover, .submit-btn:hover {
  background-color: var(--color-success-dark);
}

.refuse-btn, .delete-btn {
  background-color: var(--color-danger);
  color: white;
  border: none;
  border-radius: var(--border-radius-sm);
  padding: var(--space-sm) var(--space-md);
  cursor: pointer;
  font-weight: 600;
  transition: background-color var(--transition-speed);
}

.refuse-btn:hover, .delete-btn:hover {
  background-color: var(--color-danger-dark);
}

.payment-btn {
  background-color: var(--color-primary);
  color: white;
  border: none;
  border-radius: var(--border-radius-sm);
  padding: var(--space-sm) var(--space-md);
  cursor: pointer;
  font-weight: 600;
  transition: background-color var(--transition-speed);
}

.payment-btn:hover {
  background-color: var(--color-primary-hover);
}

button:disabled {
  background-color: var(--color-text-light);
  cursor: not-allowed;
}

/* Loading and empty message */
.loading, .empty-message {
  text-align: center;
  padding: var(--space-xl);
  background-color: var(--color-background-mute);
  border-radius: var(--border-radius-md);
  margin: var(--space-xl) 0;
  color: var(--color-text-light);
}

/* Notification bar */
.notification-bar {
  background-color: var(--color-primary);
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  color: white;
  padding: var(--space-md);
  text-align: center;
  z-index: var(--z-notification, 1000);
}

.notification-bar .close-btn {
  background: none;
  border: none;
  color: white;
  font-size: 1.5rem;
  cursor: pointer;
  position: absolute;
  right: var(--space-md);
  top: var(--space-md);
}

/* Responsive */
@media (max-width: 768px) {
  .company-dashboard {
    padding: var(--space-md);
  }
  
  .booking-actions {
    flex-direction: column;
    gap: var(--space-sm);
  }
  
  .booking-actions button {
    width: 100%;
  }
}
</style>