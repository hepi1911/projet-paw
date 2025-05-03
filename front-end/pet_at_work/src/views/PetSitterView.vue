<template>
  <div class="view-container">
    <!-- Indicateur de chargement -->
    <div v-if="isLoading" class="loading-overlay">
      <div class="loading-spinner"></div>
      <p>Loading data...</p>
    </div>
    
    <div v-else class="pet-sitter-dashboard">
      <h1>Pet Sitter space</h1>
      
      <!-- Navigation -->
      <div class="profile-nav">
        <button class="profile-btn" @click="goToProfile">See my profile</button>
      </div>

      <!-- Section Mon Profil -->
      <div class="profile-section">
        <h2>My Profile</h2>
        <div class="profile-card">
          <div class="profile-info" v-if="currentUser">
            <h3>{{ currentUser.name }}</h3>
            <p><strong>Email:</strong> {{ currentUser.email }}</p>
            <p v-if="currentUser.address"><strong>Address:</strong> {{ currentUser.address }}</p>
            <p v-if="currentUser.experience"><strong>Experience:</strong> {{ currentUser.experience }}</p>
            <p v-if="currentUser.capacity !== null"><strong>Capacity:</strong> {{ currentUser.capacity }} pets</p>
          </div>
          <div class="profile-actions">
            <button class="edit-profile-btn" @click="openProfileModal">Modify my profile</button>
          </div>
        </div>
      </div>
      
      <!-- Message d'erreur -->
      <div v-if="error" class="error-message">
        <p>{{ error }}</p>
        <button @click="loadData" class="retry-btn">Try again</button>
      </div>

      <!-- Section Réservations en attente -->
      <div v-if="!error && pendingBookings.length > 0" class="pending-bookings-section">
        <h2>Pending bookings</h2>
        <div class="bookings-list">
          <div v-for="booking in pendingBookings" 
              :key="booking.id" 
              class="booking-card pending">
            <div class="booking-info">
              <h3>{{ getAnimalName(booking.animal) }}</h3>
              <p><strong>Owner:</strong> {{ getOwnerName(booking.animal_owner) || 'Propriétaire inconnu' }}</p>
              <p><strong>Dates:</strong> {{ formatDate(booking.start_date) }} - {{ formatDate(booking.end_date) }}</p>
              <p class="status"><strong>Status:</strong> On hold</p>
              
              <div class="booking-actions">
                <button class="accept-btn" @click="updateBookingStatus(booking.id, 'accepted')" :disabled="isUpdating">
                  {{ isUpdating === booking.id ? 'En cours...' : 'Accepter' }}
                </button>
                <button class="refuse-btn" @click="updateBookingStatus(booking.id, 'refused')" :disabled="isUpdating">
                  {{ isUpdating === booking.id ? 'En cours...' : 'Refuser' }}
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
      <div v-else-if="!error && bookings.length === 0" class="empty-message">
        <p>No bookings pending at the moment.</p>
      </div>

      <!-- Section Toutes les Réservations -->
      <div v-if="!error && bookings.length > 0" class="bookings-section">
        <h2>All my bookings</h2>
        <div class="bookings-list">
          <div v-for="booking in bookings" 
              :key="booking.id" 
              class="booking-card"
              :class="booking.status">
            <div class="booking-info">
              <h3>{{ getAnimalName(booking.animal) }}</h3>
              <p><strong>Owner:</strong> {{ getOwnerName(booking.animal_owner) || 'Propriétaire inconnu' }}</p>
              <p><strong>Dates:</strong> {{ formatDate(booking.start_date) }} - {{ formatDate(booking.end_date) }}</p>
              <p class="status"><strong>Status:</strong> {{ getStatusLabel(booking.status) }}</p>
              <div v-if="booking.status === 'accepted'" class="booking-actions">
                <button class="book-company-btn" 
                        @click="bookCompanyForAnimal(booking)" 
                        :disabled="animalsWithCompanyBookings[booking.animal]"
                        :title="animalsWithCompanyBookings[booking.animal] ? 'Cet animal a déjà une réservation auprès d\'une entreprise' : ''">
                  {{ animalsWithCompanyBookings[booking.animal] ? 'Déjà réservé' : 'Réserver pour cet animal' }}
                </button>
                <div v-if="animalsWithCompanyBookings[booking.animal]" class="reservation-info">
                  <p>Existing booking with {{ getCompanyName(animalsWithCompanyBookings[booking.animal].company) }}</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Section Réservations complètes (client → pet sitter → compagnie) -->
      <div v-if="!error && linkedBookings.length > 0" class="linked-bookings-section">
        <h2>Bookings client → you → company</h2>
        <div class="bookings-list">
          <div v-for="(item, idx) in linkedBookings" :key="idx" class="booking-card accepted">
            <div>
              <h3>Pet : {{ getAnimalName(item.clientBooking.animal) }}</h3>
              <p><strong>Owner:</strong> {{ getOwnerName(item.clientBooking.animal_owner) }}</p>
              <p><strong>Dates:</strong> {{ formatDate(item.clientBooking.start_date) }} - {{ formatDate(item.clientBooking.end_date) }}</p>
              <p><strong>Company booking:</strong> {{ getCompanyName(item.companyBooking.company) }} ({{ formatDate(item.companyBooking.start_date) }} - {{ formatDate(item.companyBooking.end_date) }})</p>
              <p><strong>Company status:</strong> {{ getStatusLabel(item.companyBooking.status) }}</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Section Companies - Déplacée après les réservations -->
      <div v-if="!error" class="companies-section">
        <h2>Partner companies</h2>
        <p class="section-description">Consult our partner companies for specialist services and training.</p>
        
        <div v-if="companies.length > 0" class="companies-list-vertical">
          <div v-for="company in companies" 
              :key="company.id" 
              class="company-card-vertical"
              @click="goToCompanyDetail(company.id)">
            <div class="company-info">
              <h3>{{ company.name }}</h3>
              <p class="capacity">Capacity: {{ company.capacity }} pets</p>
              <p class="address">{{ company.address }}</p>
              <div class="company-card-actions">
                <button class="reservation-btn" @click.stop="startNewReservation(company.id)">
                  Book a service
                </button>
              </div>
            </div>
          </div>
        </div>
        <div v-else class="empty-message">
          <p>No partner company available at the moment.</p>
        </div>
      </div>
    </div>
    
    <!-- Les modales restent inchangées -->
    <!-- Modal de création de réservation avec une compagnie -->
    <div v-if="showReservationModal" class="modal-backdrop" @click="closeModal">
      <div class="modal-content" @click.stop>
        <h3>Book a service with {{ selectedCompany ? selectedCompany.name : '' }}</h3>
        <form @submit.prevent="createCompanyReservation" class="reservation-form">
          <div class="form-group">
            <label for="service-type">Type of service</label>
            <select id="service-type" v-model="newReservation.service_type" required>
              <option value="">Select a service</option>
              <option value="formation">Specialist training</option>
              <option value="consultation">Professional consultation</option>
              <option value="collaboration">Collaboration for pet sitting</option>
            </select>
          </div>
          
          <div class="form-group">
            <label for="start-date">Start date</label>
            <input type="date" id="start-date" v-model="newReservation.start_date" required>
          </div>
          
          <div class="form-group">
            <label for="end-date">End date</label>
            <input type="date" id="end-date" v-model="newReservation.end_date" required>
          </div>
          
          <div class="form-group">
            <label for="details">Further details</label>
            <textarea id="details" v-model="newReservation.details" 
                      placeholder="Précisez vos besoins et attentes pour ce service"></textarea>
          </div>
          
          <div class="form-actions">
            <button type="button" class="cancel-btn" @click="closeModal">Cancel</button>
            <button type="submit" class="submit-btn" :disabled="isSubmittingReservation">
              {{ isSubmittingReservation ? 'Création en cours...' : 'Créer la réservation' }}
            </button>
          </div>
        </form>
      </div>
    </div>
    
    <!-- Modal de modification du profil -->
    <div v-if="showProfileModal" class="modal-backdrop" @click="showProfileModal = false">
      <div class="modal-content" @click.stop>
        <h3>Modify my profile</h3>
        
        <form @submit.prevent="updateUserProfile" class="profile-form">
          <div class="form-group">
            <label for="name">Name</label>
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
            <label for="experience">Experience</label>
            <textarea id="experience" v-model="profileForm.experience" rows="4" required></textarea>
          </div>
          
          <div class="form-group">
            <label for="capacity">Capacity (number of pets)</label>
            <input type="number" id="capacity" v-model="profileForm.capacity" min="1">
          </div>
          
          <h4>Change password (optional)</h4>
          
          <div class="form-group">
            <label for="current-password">Current password</label>
            <input type="password" id="current-password" v-model="profileForm.currentPassword">
          </div>
          
          <div class="form-group">
            <label for="new-password">New password</label>
            <input type="password" id="new-password" v-model="profileForm.newPassword">
          </div>
          
          <div class="form-group">
            <label for="confirm-password">Confirm new password</label>
            <input type="password" id="confirm-password" v-model="profileForm.confirmPassword">
          </div>
          
          <div class="form-actions">
            <button type="button" class="cancel-btn" @click="showProfileModal = false">Cancel</button>
            <button type="submit" class="submit-btn" :disabled="isUpdatingProfile">
              {{ isUpdatingProfile ? 'Mise à jour en cours...' : 'Mettre à jour' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>

  <!-- Modal pour réserver une entreprise pour un animal spécifique -->
  <div v-if="showCompanyReservationModal" class="modal-backdrop" @click="cancelCompanyReservation">
    <div class="modal-content" @click.stop>
      <h3>Book a company for {{ getAnimalName(selectedBooking?.animal) }}</h3>
      
      <div class="company-selection">
        <p>Choose a company :</p>
        <div class="companies-list-modal">
          <div 
            v-for="company in companies" 
            :key="company.id" 
            class="company-item-modal" 
            :class="{ 'selected': selectedCompanyId === company.id }"
            @click="selectedCompanyId = company.id"
          >
            <h4>{{ company.name }}</h4>
            <p>{{ company.address || 'Adresse non disponible' }}</p>
            <p>Capacity: {{ company.capacity || 'N/A' }}</p>
          </div>
        </div>
      </div>
      
      <form @submit.prevent="submitCompanyReservation" class="reservation-form">
        <div class="form-group">
          <label for="service-type-animal">Type of service</label>
          <select id="service-type-animal" v-model="companyReservationForm.service_type" required>
            <option value="">Select a service</option>
            <option value="formation">Specialist training</option>
            <option value="consultation">Professional consultation</option>
            <option value="collaboration">Collaboration for pet sitting</option>
          </select>
        </div>
        
        <div class="form-group">
          <label for="start-date-animal">Start date</label>
          <input 
            type="date" 
            id="start-date-animal" 
            v-model="companyReservationForm.start_date"
            :min="selectedBooking?.start_date"
            required
          >
        </div>
        
        <div class="form-group">
          <label for="end-date-animal">End date</label>
          <input 
            type="date" 
            id="end-date-animal" 
            v-model="companyReservationForm.end_date"
            :max="selectedBooking?.end_date"
            required
          >
        </div>
        
        <div class="form-group">
          <label for="details-animal">Further details</label>
          <textarea 
            id="details-animal" 
            v-model="companyReservationForm.details" 
            placeholder="Précisez vos besoins..."
          ></textarea>
        </div>
        
        <div class="form-actions">
          <button type="button" class="cancel-btn" @click="cancelCompanyReservation">Cancel</button>
          <button type="submit" class="submit-btn" :disabled="isReserving">
            {{ isReserving ? 'Création en cours...' : 'Créer la réservation' }}
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import { useRouter } from 'vue-router';
import { apiService } from '../services/api';

const router = useRouter();
const bookings = ref([]);
const companies = ref([]);
const animalCache = ref({});
const ownerCache = ref({});
const isUpdating = ref(null); // Pour stocker l'ID de la réservation en cours de mise à jour
const showReservationModal = ref(false);
const selectedCompanyId = ref(null);
const selectedCompany = ref(null);
const isSubmittingReservation = ref(false);
const currentUser = ref(null); // Utilisateur actuel
const showProfileModal = ref(false);
const isUpdatingProfile = ref(false);
const linkedBookings = ref([]);
const companyBookingsMap = ref({});
const isLoading = ref(true); // État de chargement
const error = ref(null); // État d'erreur

const profileForm = ref({
  name: '',
  email: '',
  address: '',
  experience: '',
  capacity: null,
  currentPassword: '',
  newPassword: '',
  confirmPassword: ''
});

const newReservation = ref({
  service_type: '',
  start_date: '',
  end_date: '',
  details: ''
});


// État pour la réservation d'entreprise pour un animal spécifique
const selectedBooking = ref(null);
const showCompanyReservationModal = ref(false);
const isReserving = ref(false);
const companyReservationForm = ref({
  service_type: '',
  start_date: '',
  end_date: '',
  details: ''
});

// Map pour suivre les animaux déjà réservés chez des entreprises
const animalsWithCompanyBookings = ref({});

// Calcul des réservations en attente
const pendingBookings = computed(() => {
  return bookings.value.filter(booking => booking.status === 'pending');
});


// Fonction pour charger les données
const loadData = async () => {
  isLoading.value = true;
  error.value = null; // Réinitialiser l'erreur
  try {
    // Récupérer l'ID de l'utilisateur connecté depuis le sessionStorage (et non localStorage)
    const userData = JSON.parse(sessionStorage.getItem('user') || '{}');
    const currentUserId = userData.user_id;
    
    if (!currentUserId) {
      console.error('Utilisateur non connecté');
      router.push('/login');
      return;
    }
    
    // Récupérer les informations de l'utilisateur actuel
    currentUser.value = await apiService.getUserById(currentUserId);
    console.log('Profil du pet sitter chargé:', currentUser.value);
    
    // Récupérer les réservations du pet sitter
    const allBookings = await apiService.getAllBookings();
    bookings.value = allBookings.filter(booking => booking.sitter === currentUserId);
    console.log('Réservations chargées:', bookings.value);
    
    // Récupérer UNIQUEMENT les compagnies disponibles (non complètes)
    companies.value = await apiService.getAvailableCompanies();
    
    // Récupérer les informations des animaux pour l'affichage
    const animalIds = [...new Set(bookings.value.map(booking => booking.animal))];
    
    for (const animalId of animalIds) {
      try {
        const animal = await apiService.getAnimalById(animalId);
        animalCache.value[animalId] = animal.name;
        
        // Récupérer les informations du propriétaire de l'animal
        if (animal.owner && !ownerCache.value[animal.owner]) {
          const owner = await apiService.getUserById(animal.owner);
          ownerCache.value[animal.owner] = owner.name;
          
          // Ajouter l'ID du propriétaire à chaque réservation pour faciliter l'affichage
          bookings.value.forEach(booking => {
            if (booking.animal === animalId) {
              booking.animal_owner = animal.owner;
            }
          });
        }
      } catch (error) {
        console.error('Erreur lors de la récupération des informations de l\'animal ou du propriétaire:', error);
      }
    }
    
    // Lier les réservations client → pet sitter → compagnie
    try {
      // Récupérer les réservations faites par le pet sitter vers les companies
      const userCompanyBookings = await apiService.getPetSitterCompanyBookings(currentUserId);
      companyBookingsMap.value = {};
      
      // Créer une carte des animaux déjà réservés pour des entreprises
      animalsWithCompanyBookings.value = {};
      
      userCompanyBookings.forEach(booking => {
        companyBookingsMap.value[booking.id] = booking;
        
        // Si la réservation est active (en attente ou acceptée), marquer l'animal comme réservé
        if (booking.animal && (booking.status === 'pending' || booking.status === 'accepted')) {
          animalsWithCompanyBookings.value[booking.animal] = booking;
        }
      });

      // Lier les réservations client → pet sitter → compagnie
      linkedBookings.value = bookings.value
        .filter(booking => booking.status === 'accepted')
        .map(booking => {
          const companyBooking = Object.values(companyBookingsMap.value)
            .find(cb =>
              new Date(cb.start_date) >= new Date(booking.start_date) &&
              new Date(cb.end_date) <= new Date(booking.end_date)
            );
          if (companyBooking) {
            return { clientBooking: booking, companyBooking };
          }
          return null;
        })
        .filter(item => item !== null);
    } catch (error) {
      console.error('Erreur lors du chargement des réservations compagnies:', error);
    }
  } catch (err) {
    error.value = 'Une erreur est survenue lors du chargement des données. Veuillez réessayer.'; // Gérer l'erreur
    console.error('Erreur lors du chargement des données:', err);
  } finally {
    isLoading.value = false;
  }
};

// Fonction pour ouvrir la modal de modification de profil
const openProfileModal = () => {
  // Initialiser le formulaire avec les données de l'utilisateur actuel
  profileForm.value = {
    name: currentUser.value.name || '',
    email: currentUser.value.email || '',
    address: currentUser.value.address || '',
    experience: currentUser.value.experience || '',
    capacity: currentUser.value.capacity || null,
    currentPassword: '',
    newPassword: '',
    confirmPassword: ''
  };
  
  showProfileModal.value = true;
};

// Fonction pour mettre à jour le statut d'une réservation
const updateBookingStatus = async (bookingId, newStatus) => {
  try {
    isUpdating.value = bookingId;
    await apiService.updateBookingStatus(bookingId, newStatus);
    
    // Mettre à jour le statut dans la liste locale
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

// Fonction pour commencer une nouvelle réservation avec une compagnie
const startNewReservation = (companyId) => {
  selectedCompanyId.value = companyId;
  selectedCompany.value = companies.value.find(c => c.id === companyId);
  
  // Initialiser les dates par défaut (aujourd'hui et demain)
  const today = new Date();
  const tomorrow = new Date();
  tomorrow.setDate(today.getDate() + 1);
  
  newReservation.value = {
    service_type: '',
    start_date: today.toISOString().split('T')[0],
    end_date: tomorrow.toISOString().split('T')[0],
    details: ''
  };
  
  showReservationModal.value = true;
};

// Fonction pour créer une réservation avec une compagnie
const createCompanyReservation = async () => {
  try {
    isSubmittingReservation.value = true;
    
    // Valider les dates
    const startDate = new Date(newReservation.value.start_date);
    const endDate = new Date(newReservation.value.end_date);
    
    if (endDate < startDate) {
      alert('La date de fin doit être postérieure à la date de début');
      isSubmittingReservation.value = false;
      return;
    }
    
    // Créer la réservation
    await apiService.createPetSitterCompanyBooking({
      company: selectedCompanyId.value,
      service_type: newReservation.value.service_type,
      start_date: newReservation.value.start_date,
      end_date: newReservation.value.end_date,
      details: newReservation.value.details
    });
    
    // Fermer la modal et afficher un message de confirmation
    closeModal();
    alert('Votre réservation a été envoyée avec succès !');
  } catch (error) {
    console.error('Erreur lors de la création de la réservation:', error);
    alert('Une erreur est survenue lors de la création de la réservation. Veuillez réessayer.');
  } finally {
    isSubmittingReservation.value = false;
  }
};

// Fonction pour démarrer la réservation d'une entreprise pour un animal spécifique
const bookCompanyForAnimal = (booking) => {
  selectedBooking.value = booking;
  
  // Préremplir le formulaire avec les dates de la réservation existante
  companyReservationForm.value = {
    service_type: 'collaboration', // Par défaut
    start_date: booking.start_date,
    end_date: booking.end_date,
    details: `Réservation liée à la garde de l'animal ${getAnimalName(booking.animal)}`
  };
  
  // Afficher la modal
  showCompanyReservationModal.value = true;
};

// Fonction pour soumettre la réservation d'entreprise pour un animal spécifique
const submitCompanyReservation = async () => {
  try {
    if (!selectedBooking.value || !selectedCompanyId.value) {
      alert('Veuillez sélectionner une entreprise.');
      return;
    }
    
    isReserving.value = true;
    
    // Créer la réservation
    await apiService.createPetSitterCompanyBooking({
      company: selectedCompanyId.value,
      pet_sitter: currentUser.value.id,
      animal: selectedBooking.value.animal,
      start_date: companyReservationForm.value.start_date,
      end_date: companyReservationForm.value.end_date,
      service_type: companyReservationForm.value.service_type,
      details: companyReservationForm.value.details,
      linked_booking: selectedBooking.value.id
    });
    
    // Fermer la modal et afficher un message de confirmation
    cancelCompanyReservation();
    alert('Votre réservation a été envoyée à l\'entreprise avec succès !');
    
    // Recharger les données
    await loadData();
  } catch (error) {
    console.error('Erreur lors de la création de la réservation:', error);
    alert('Une erreur est survenue lors de la création de la réservation.');
  } finally {
    isReserving.value = false;
  }
};

// Fonction pour annuler la réservation d'entreprise
const cancelCompanyReservation = () => {
  showCompanyReservationModal.value = false;
  selectedBooking.value = null;
};

// Fermer la modal
const closeModal = () => {
  showReservationModal.value = false;
  selectedCompanyId.value = null;
  selectedCompany.value = null;
};

// Fonction pour mettre à jour le profil de l'utilisateur
const updateUserProfile = async () => {
  try {
    isUpdatingProfile.value = true;
    
    // Valider les mots de passe
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
      experience: profileForm.value.experience || '',
      capacity: profileForm.value.capacity || null
    };
    
    // Ajouter les informations de mot de passe uniquement si un nouveau mot de passe est fourni
    if (profileForm.value.newPassword && profileForm.value.currentPassword) {
      updateData.current_password = profileForm.value.currentPassword;
      updateData.new_password = profileForm.value.newPassword;
    }
    
    // Mettre à jour le profil
    await apiService.updateUserProfile(currentUser.value.id, updateData);
    
    // Mettre à jour les informations locales sans écraser le mot de passe
    currentUser.value = { 
      ...currentUser.value, 
      name: profileForm.value.name,
      email: profileForm.value.email,
      address: profileForm.value.address,
      experience: profileForm.value.experience,
      capacity: profileForm.value.capacity
    };
    
    // Fermer la modal et afficher un message de confirmation
    showProfileModal.value = false;
    alert('Votre profil a été mis à jour avec succès !');
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

// Obtenir le nom d'un animal à partir de son ID
const getAnimalName = (animalId) => {
  return animalCache.value[animalId] || 'Animal inconnu';
};

// Obtenir le nom d'un propriétaire à partir de son ID
const getOwnerName = (ownerId) => {
  return ownerCache.value[ownerId] || 'Propriétaire inconnu';
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

// Rediriger vers la page de détails d'une compagnie
const goToCompanyDetail = (id) => {
  router.push(`/company/${id}`);
};

const getCompanyName = (companyId) => {
  const company = companies.value.find(c => c.id === companyId);
  return company ? company.name : 'Compagnie inconnue';
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
.petsitter-dashboard {
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

.profile-header {
  background-color: var(--color-background);
  border-radius: var(--border-radius-md);
  padding: var(--space-lg);
  box-shadow: var(--shadow-md);
  margin-bottom: var(--space-xl);
}

.experience-section {
  margin-top: var(--space-lg);
  white-space: pre-line;
  color: var(--color-text);
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: var(--space-lg);
  margin: var(--space-lg) 0;
}

.stat-card {
  background-color: var(--color-background);
  padding: var(--space-lg);
  border-radius: var(--border-radius-md);
  box-shadow: var(--shadow-md);
  text-align: center;
}

.stat-value {
  font-size: 1.5rem;
  font-weight: bold;
  color: var(--color-primary);
}

.stat-label {
  color: var(--color-text-light);
  margin-top: var(--space-sm);
}

.companies-section {
  margin-top: var(--space-xl);
}

.company-card {
  background-color: var(--color-background);
  border-radius: var(--border-radius-md);
  padding: var(--space-lg);
  box-shadow: var(--shadow-md);
  margin-bottom: var(--space-md);
  cursor: pointer;
  transition: transform var(--transition-speed), box-shadow var(--transition-speed);
}

.company-card:hover {
  transform: translateY(-3px);
  box-shadow: var(--shadow-lg);
}

.loading, .empty-message {
  text-align: center;
  padding: var(--space-xl);
  background-color: var(--color-background-mute);
  border-radius: var(--border-radius-md);
  margin: var(--space-xl) 0;
  color: var(--color-text-light);
}

@media (max-width: 768px) {
  .petsitter-dashboard {
    padding: var(--space-md);
  }
  
  .dashboard-header {
    flex-direction: column;
    gap: var(--space-md);
    text-align: center;
  }
  
  .stats-grid {
    grid-template-columns: 1fr;
    gap: var(--space-md);
  }
}
</style>