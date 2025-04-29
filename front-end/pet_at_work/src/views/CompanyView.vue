<template>
  <div class="view-container">
    <div class="company-dashboard">
      <h1>Tableau de bord Company</h1>
      
      <!-- Navigation -->
      <div class="profile-nav">
        <button class="profile-btn" @click="goToProfile">Voir mon profil</button>
      </div>

      <!-- Information de la compagnie -->
      <div class="company-info-section" v-if="currentCompany">
        <h2>Mon entreprise</h2>
        <div class="company-info-card">
          <div class="company-details">
            <h3>{{ currentCompany.name }}</h3>
            <p><strong>Adresse:</strong> {{ currentCompany.address || 'Non spécifiée' }}</p>
            <p class="capacity-info">
              <strong>Capacité:</strong> {{ currentCompany.capacity || 0 }} animaux
              <span v-if="currentCapacityUsed > 0" class="capacity-used">
                ({{ currentCapacityUsed }} en cours)
              </span>
            </p>
            <div class="capacity-bar-container">
              <div class="capacity-bar" :style="{ width: capacityPercentage + '%', backgroundColor: capacityBarColor }"></div>
            </div>
          </div>
          <div class="company-actions">
            <button class="edit-profile-btn" @click="openProfileModal">Modifier mon profil</button>
          </div>
        </div>
      </div>

      <!-- Réservations en attente -->
      <div class="bookings-section" v-if="pendingBookings.length > 0">
        <h2>Réservations en attente</h2>
        <div class="bookings-list">
          <div v-for="booking in pendingBookings" 
               :key="booking.id" 
               class="booking-card pending">
            <div class="booking-info">
              <h3>Réservation de {{ getPetSitterName(booking.petsitter) }}</h3>
              <p><strong>Type de service:</strong> {{ getServiceLabel(booking.service_type) }}</p>
              <p><strong>Dates:</strong> {{ formatDate(booking.start_date) }} - {{ formatDate(booking.end_date) }}</p>
              <p><strong>Détails:</strong> {{ booking.details || 'Aucun détail fourni' }}</p>
              <p class="status"><strong>Statut:</strong> En attente</p>
              
              <div class="booking-actions">
                <button 
                  class="accept-btn" 
                  @click="updateBookingStatus(booking.id, 'accepted')" 
                  :disabled="isUpdating === booking.id || isCapacityFull"
                  :title="isCapacityFull ? 'Capacité maximale atteinte' : ''"
                >
                  {{ isUpdating === booking.id ? 'En cours...' : 'Accepter' }}
                </button>
                <button 
                  class="refuse-btn" 
                  @click="updateBookingStatus(booking.id, 'refused')" 
                  :disabled="isUpdating === booking.id"
                >
                  {{ isUpdating === booking.id ? 'En cours...' : 'Refuser' }}
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
      <div v-else-if="!loading" class="empty-message">
        <p>Aucune réservation en attente.</p>
      </div>

      <!-- Toutes les réservations -->
      <div class="bookings-section" v-if="bookings.length > 0">
        <h2>Historique des réservations</h2>
        <div class="bookings-list">
          <div v-for="booking in bookings" 
               :key="booking.id" 
               class="booking-card"
               :class="booking.status">
            <div class="booking-info">
              <h3>Réservation de {{ getPetSitterName(booking.petsitter) }}</h3>
              <p><strong>Type de service:</strong> {{ getServiceLabel(booking.service_type) }}</p>
              <p><strong>Dates:</strong> {{ formatDate(booking.start_date) }} - {{ formatDate(booking.end_date) }}</p>
              <p><strong>Détails:</strong> {{ booking.details || 'Aucun détail fourni' }}</p>
              <p class="status"><strong>Statut:</strong> {{ getStatusLabel(booking.status) }}</p>
              
              <div class="booking-actions" v-if="booking.status === 'accepted'">
                <!-- Le bouton "Marquer comme terminée" a été supprimé selon la demande -->
              </div>
            </div>
          </div>
        </div>
      </div>
      <div v-else-if="!loading && pendingBookings.length === 0" class="empty-message">
        <p>Aucune réservation à afficher.</p>
      </div>

      <!-- Loading indicator -->
      <div v-if="loading" class="loading">
        <p>Chargement des données...</p>
      </div>
    </div>
    
    <!-- Modal de modification du profil -->
    <div v-if="showProfileModal" class="modal-backdrop" @click="showProfileModal = false">
      <div class="modal-content" @click.stop>
        <h3>Modifier mon profil d'entreprise</h3>
        
        <form @submit.prevent="updateCompanyProfile" class="profile-form">
          <div class="form-group">
            <label for="name">Nom de l'entreprise</label>
            <input type="text" id="name" v-model="profileForm.name" required>
          </div>
          
          <div class="form-group">
            <label for="email">Email</label>
            <input type="email" id="email" v-model="profileForm.email" required>
          </div>
          
          <div class="form-group">
            <label for="address">Adresse</label>
            <input type="text" id="address" v-model="profileForm.address">
          </div>
          
          <div class="form-group">
            <label for="capacity">Capacité (nombre d'animaux)</label>
            <input type="number" id="capacity" v-model="profileForm.capacity" min="1">
          </div>
          
          <h4>Changer le mot de passe (optionnel)</h4>
          
          <div class="form-group">
            <label for="current-password">Mot de passe actuel</label>
            <input type="password" id="current-password" v-model="profileForm.currentPassword">
          </div>
          
          <div class="form-group">
            <label for="new-password">Nouveau mot de passe</label>
            <input type="password" id="new-password" v-model="profileForm.newPassword">
          </div>
          
          <div class="form-group">
            <label for="confirm-password">Confirmer le nouveau mot de passe</label>
            <input type="password" id="confirm-password" v-model="profileForm.confirmPassword">
          </div>
          
          <div class="form-actions">
            <button type="button" class="cancel-btn" @click="showProfileModal = false">Annuler</button>
            <button type="submit" class="submit-btn" :disabled="isUpdatingProfile">
              {{ isUpdatingProfile ? 'Mise à jour en cours...' : 'Mettre à jour' }}
            </button>
          </div>
        </form>
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
const profileForm = ref({
  name: '',
  email: '',
  address: '',
  capacity: null,
  currentPassword: '',
  newPassword: '',
  confirmPassword: ''
});

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

// Couleur de la barre de capacité en fonction du remplissage
const capacityBarColor = computed(() => {
  const percentage = capacityPercentage.value;
  if (percentage < 50) return '#2ecc71'; // Vert
  if (percentage < 75) return '#f39c12'; // Orange
  return '#e74c3c'; // Rouge
});

// Chargement des données
const loadData = async () => {
  try {
    loading.value = true;
    
    // Récupérer l'ID de l'utilisateur connecté depuis le localStorage
    const userData = JSON.parse(localStorage.getItem('user') || '{}');
    const currentUserId = userData.user_id;
    
    if (!currentUserId) {
      console.error('Utilisateur non connecté');
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
          console.error('Erreur lors de la récupération des informations du pet sitter:', error);
        }
      }
    }
  } catch (error) {
    console.error('Erreur lors du chargement des données:', error);
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
      alert('Impossible d\'accepter cette réservation : capacité maximale atteinte.');
      return;
    }
    
    // Mettre à jour le statut
    await apiService.updatePetSitterCompanyBookingStatus(bookingId, newStatus);
    
    // Mettre à jour la réservation localement
    const bookingIndex = bookings.value.findIndex(b => b.id === bookingId);
    if (bookingIndex !== -1) {
      bookings.value[bookingIndex].status = newStatus;
    }
    
    // Afficher un message de confirmation
    alert(`La réservation a été ${getStatusLabel(newStatus).toLowerCase()} avec succès !`);
  } catch (error) {
    console.error('Erreur lors de la mise à jour du statut de la réservation:', error);
    alert('Une erreur est survenue lors de la mise à jour du statut. Veuillez réessayer.');
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
        alert('Les nouveaux mots de passe ne correspondent pas.');
        isUpdatingProfile.value = false;
        return;
      }
      
      // Vérifier que le mot de passe actuel est bien renseigné
      if (!profileForm.value.currentPassword) {
        alert('Veuillez entrer votre mot de passe actuel pour confirmer le changement.');
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
    alert('Votre profil d\'entreprise a été mis à jour avec succès !');
  } catch (error) {
    console.error('Erreur lors de la mise à jour du profil:', error);
    alert('Une erreur est survenue lors de la mise à jour du profil. Veuillez réessayer.');
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

// Charger les données au montage du composant
onMounted(async () => {
  await loadData();
});
</script>

<style scoped>
.view-container {
  background-color: #f5f5f5;
  min-height: calc(100vh - var(--header-height));
}

.company-dashboard {
  width: 100%;
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
}

h1, h2 {
  color: #2c3e50;
  text-align: center;
  margin-bottom: 1.5rem;
}

/* Navigation */
.profile-nav {
  text-align: right;
  margin-bottom: 2rem;
}

.profile-btn {
  padding: 0.5rem 1rem;
  background-color: #3498db;
  color: white;
  border: none;
  border-radius: 4px;
  font-size: 1rem;
  cursor: pointer;
  transition: background-color 0.2s;
}

.profile-btn:hover {
  background-color: #2980b9;
}

/* Information de la compagnie */
.company-info-section {
  margin-bottom: 3rem;
}

.company-info-card {
  background-color: white;
  border-radius: 8px;
  padding: 1.5rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  border-left: 5px solid #3498db;
}

.capacity-info {
  margin: 1rem 0;
}

.capacity-used {
  font-style: italic;
  margin-left: 0.5rem;
}

.capacity-bar-container {
  height: 8px;
  background-color: #ecf0f1;
  border-radius: 4px;
  margin: 1rem 0;
  width: 100%;
  overflow: hidden;
}

.capacity-bar {
  height: 100%;
  transition: width 0.5s ease, background-color 0.5s ease;
}

/* Section Réservations */
.bookings-section {
  margin-bottom: 3rem;
  background-color: #f8f9fa;
  border-radius: 10px;
  padding: 1.5rem;
}

.bookings-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.booking-card {
  background-color: white;
  border-radius: 8px;
  padding: 1.5rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  border-left: 5px solid #ccc;
  transition: transform 0.2s, box-shadow 0.2s;
}

.booking-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

/* Status-specific styles */
.booking-card.pending {
  border-left-color: #f39c12;
}

.booking-card.accepted {
  border-left-color: #2ecc71;
}

.booking-card.refused {
  border-left-color: #e74c3c;
}

.booking-card.cancelled {
  border-left-color: #95a5a6;
  opacity: 0.8;
}

.status {
  font-weight: bold;
}

.booking-card.pending .status {
  color: #f39c12;
}

.booking-card.accepted .status {
  color: #2ecc71;
}

.booking-card.refused .status {
  color: #e74c3c;
}

.booking-card.cancelled .status {
  color: #95a5a6;
}

/* Booking actions */
.booking-actions {
  display: flex;
  gap: 1rem;
  margin-top: 1rem;
}

/* Buttons */
.accept-btn {
  background-color: #2ecc71;
  color: white;
  border: none;
  border-radius: 4px;
  padding: 0.5rem 1rem;
  cursor: pointer;
  font-weight: 600;
  transition: background-color 0.2s;
}

.accept-btn:hover {
  background-color: #27ae60;
}

.refuse-btn {
  background-color: #e74c3c;
  color: white;
  border: none;
  border-radius: 4px;
  padding: 0.5rem 1rem;
  cursor: pointer;
  font-weight: 600;
  transition: background-color 0.2s;
}

.refuse-btn:hover {
  background-color: #c0392b;
}

button:disabled {
  background-color: #95a5a6;
  cursor: not-allowed;
}

/* Loading and empty message */
.loading, .empty-message {
  text-align: center;
  padding: 2rem;
  background-color: #f8f9fa;
  border-radius: 8px;
  margin: 2rem 0;
  color: #6c757d;
}

/* Responsive adjustments */
@media (max-width: 768px) {
  .company-dashboard {
    padding: 1rem;
  }
  
  .booking-actions {
    flex-direction: column;
    gap: 0.5rem;
  }
  
  .booking-actions button {
    width: 100%;
  }
}
</style>