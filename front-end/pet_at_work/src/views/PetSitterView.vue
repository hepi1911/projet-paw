<template>
  <div class="view-container">
    <!-- Indicateur de chargement -->
    <div v-if="isLoading" class="loading-overlay">
      <div class="loading-spinner"></div>
      <p>Loading data...</p>
    </div>
    
    <!-- Vue pour utilisateur non connecté -->
    <div v-else-if="!isLoggedIn" class="public-view">
      <h1>Pet Sitter Services</h1>
      
      <div class="login-prompt">
        <p>Please <router-link to="/login">log in</router-link> or <router-link to="/register">register</router-link> to access all pet sitting services.</p>
      </div>

      <!-- Section Companies - visible by all -->
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
                <button class="reservation-btn" @click.stop="promptLogin">
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
    
    <!-- Vue pour utilisateur connecté -->
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
        <h2 class="section-title">Pending bookings</h2>
        <div class="bookings-grid">
          <div v-for="booking in pendingBookings" 
              :key="booking.id" 
              class="booking-card pending">
            <div class="booking-banner">
              <span class="status-badge">{{ getStatusLabel('pending') }}</span>
            </div>
            <div class="booking-content">
              <div class="booking-avatar">
                <div class="avatar-image">🐾</div>
              </div>
              
              <h3 class="booking-title">{{ getAnimalName(booking.animal) }}</h3>
              
              <div class="booking-details">
                <div class="detail">
                  <i class="detail-icon">👤</i>
                  <span>{{ getOwnerName(booking.animal_owner) || 'Propriétaire inconnu' }}</span>
                </div>
                <div class="detail">
                  <i class="detail-icon">🗓️</i>
                  <span>{{ formatDate(booking.start_date) }} - {{ formatDate(booking.end_date) }}</span>
                </div>
                <div class="detail">
                  <i class="detail-icon">⏳</i>
                  <span class="status-text pending">{{ getStatusLabel('pending') }}</span>
                </div>
              </div>
              
              <div class="booking-actions">
                <button class="accept-btn" @click="updateBookingStatus(booking.id, 'accepted')" :disabled="isUpdating">
                  <i class="btn-icon">✅</i>
                  {{ isUpdating === booking.id ? 'En cours...' : 'Accepter' }}
                </button>
                <button class="refuse-btn" @click="updateBookingStatus(booking.id, 'refused')" :disabled="isUpdating">
                  <i class="btn-icon">❌</i>
                  {{ isUpdating === booking.id ? 'En cours...' : 'Refuser' }}
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
      <div v-else-if="!error && bookings.length === 0" class="empty-message">
        <div class="empty-icon">📅</div>
        <h3>No bookings</h3>
        <p>No bookings pending at the moment.</p>
      </div>

      <!-- Section Toutes les Réservations -->
      <div v-if="!error && bookings.length > 0" class="bookings-section">
        <h2 class="section-title">All my bookings</h2>
        <div class="bookings-grid">
          <div v-for="booking in bookings" 
              :key="booking.id" 
              class="booking-card"
              :class="booking.status">
            <div class="booking-banner">
              <span class="status-badge">{{ getStatusLabel(booking.status) }}</span>
            </div>
            <div class="booking-content">
              <div class="booking-avatar">
                <div class="avatar-image">🐾</div>
              </div>
              
              <h3 class="booking-title">{{ getAnimalName(booking.animal) }}</h3>
              
              <div class="booking-details">
                <div class="detail">
                  <i class="detail-icon">👤</i>
                  <span>{{ getOwnerName(booking.animal_owner) || 'Propriétaire inconnu' }}</span>
                </div>
                <div class="detail">
                  <i class="detail-icon">🗓️</i>
                  <span>{{ formatDate(booking.start_date) }} - {{ formatDate(booking.end_date) }}</span>
                </div>
                <div class="detail">
                  <i class="detail-icon" v-if="booking.status === 'pending'">⏳</i>
                  <i class="detail-icon" v-else-if="booking.status === 'accepted'">✅</i>
                  <i class="detail-icon" v-else-if="booking.status === 'refused'">❌</i>
                  <i class="detail-icon" v-else-if="booking.status === 'cancelled'">🚫</i>
                  <span class="status-text" :class="booking.status">{{ getStatusLabel(booking.status) }}</span>
                </div>
              </div>
              
              <div v-if="booking.status === 'accepted'" class="booking-actions">
                <button 
                  class="book-company-btn" 
                  @click="bookCompanyForAnimal(booking)" 
                  :disabled="animalsWithCompanyBookings[booking.animal]"
                  :title="animalsWithCompanyBookings[booking.animal] ? 'Cet animal a déjà une réservation auprès d\'une entreprise' : ''"
                >
                  <i class="btn-icon">🏢</i>
                  {{ animalsWithCompanyBookings[booking.animal] ? 'Déjà réservé' : 'Réserver pour cet animal' }}
                </button>
              </div>
              
              <div v-if="animalsWithCompanyBookings[booking.animal]" class="reservation-info">
                <div class="detail">
                  <i class="detail-icon">🔄</i>
                  <span>Existing booking with {{ getCompanyName(animalsWithCompanyBookings[booking.animal].company) }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Section Réservations complètes (client → pet sitter → compagnie) -->
      <div v-if="!error && linkedBookings.length > 0" class="linked-bookings-section">
        <h2 class="section-title">Bookings client → you → company</h2>
        <div class="bookings-grid">
          <div v-for="(item, idx) in linkedBookings" :key="idx" class="booking-card linked">
            <div class="booking-banner special-banner">
              <span class="status-badge">Linked booking</span>
            </div>
            <div class="booking-content">
              <div class="booking-avatar">
                <div class="avatar-image">🔄</div>
              </div>
              
              <h3 class="booking-title">{{ getAnimalName(item.clientBooking.animal) }}</h3>
              
              <div class="booking-details">
                <div class="detail">
                  <i class="detail-icon">👤</i>
                  <span>{{ getOwnerName(item.clientBooking.animal_owner) }}</span>
                </div>
                <div class="detail">
                  <i class="detail-icon">🗓️</i>
                  <span>{{ formatDate(item.clientBooking.start_date) }} - {{ formatDate(item.clientBooking.end_date) }}</span>
                </div>
                <div class="detail company-detail">
                  <i class="detail-icon">🏢</i>
                  <span>{{ getCompanyName(item.companyBooking.company) }}</span>
                </div>
                <div class="detail">
                  <i class="detail-icon">🗓️</i>
                  <span>{{ formatDate(item.companyBooking.start_date) }} - {{ formatDate(item.companyBooking.end_date) }}</span>
                </div>
                <div class="detail">
                  <i class="detail-icon" v-if="item.companyBooking.status === 'pending'">⏳</i>
                  <i class="detail-icon" v-else-if="item.companyBooking.status === 'accepted'">✅</i>
                  <i class="detail-icon" v-else-if="item.companyBooking.status === 'refused'">❌</i>
                  <i class="detail-icon" v-else-if="item.companyBooking.status === 'cancelled'">🚫</i>
                  <span class="status-text" :class="item.companyBooking.status">{{ getStatusLabel(item.companyBooking.status) }}</span>
                </div>
              </div>
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
const isUpdating = ref(null);
const showReservationModal = ref(false);
const selectedCompanyId = ref(null);
const selectedCompany = ref(null);
const isSubmittingReservation = ref(false);
const currentUser = ref(null);
const showProfileModal = ref(false);
const isUpdatingProfile = ref(false);
const linkedBookings = ref([]);
const companyBookingsMap = ref({});
const isLoading = ref(true);
const error = ref(null);

// Check if the user is logged in
const isLoggedIn = computed(() => {
  return !!sessionStorage.getItem('user');
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

// Fonction pour charger les données - modifiée pour vérifier le statut de connexion
const loadData = async () => {
  isLoading.value = true;
  error.value = null;
  
  try {
    // Charger les compagnies pour tous les utilisateurs (authentifiés ou non)
    companies.value = await apiService.getAvailableCompanies();
    
    // Si l'utilisateur n'est pas connecté, charger uniquement les compagnies
    if (!isLoggedIn.value) {
      isLoading.value = false;
      return;
    }
    
    // Charger des données supplémentaires pour les utilisateurs authentifiés
    const userData = JSON.parse(sessionStorage.getItem('user') || '{}');
    const currentUserId = userData.user_id;
    
    if (!currentUserId) {
      console.error('User ID not found');
      return;
    }
    
    // Récupérer les informations de l'utilisateur actuel
    currentUser.value = await apiService.getUserById(currentUserId);
    console.log('Profil du pet sitter chargé:', currentUser.value);
    
    // Récupérer les réservations du pet sitter
    const allBookings = await apiService.getAllBookings();
    bookings.value = allBookings.filter(booking => booking.sitter === currentUserId);
    console.log('Réservations chargées:', bookings.value);
    
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
    error.value = 'Une erreur est survenue lors du chargement des données. Veuillez réessayer.';
    console.error('Erreur lors du chargement des données:', err);
  } finally {
    isLoading.value = false;
  }
};

// Fonction pour rediriger vers la connexion lorsqu'un utilisateur non authentifié tente de faire une réservation
const promptLogin = () => {
  router.push('/login?redirect=' + router.currentRoute.value.path);
};

// Fonction pour ouvrir la modal de modification de profil
const openProfileModal = () => {
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
    
    const bookingIndex = bookings.value.findIndex(b => b.id === bookingId);
    if (bookingIndex !== -1) {
      bookings.value[bookingIndex].status = newStatus;
    }
    
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
    
    const startDate = new Date(newReservation.value.start_date);
    const endDate = new Date(newReservation.value.end_date);
    
    if (endDate < startDate) {
      alert('La date de fin doit être postérieure à la date de début');
      isSubmittingReservation.value = false;
      return;
    }
    
    await apiService.createPetSitterCompanyBooking({
      company: selectedCompanyId.value,
      service_type: newReservation.value.service_type,
      start_date: newReservation.value.start_date,
      end_date: newReservation.value.end_date,
      details: newReservation.value.details
    });
    
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
  
  companyReservationForm.value = {
    service_type: 'collaboration',
    start_date: booking.start_date,
    end_date: booking.end_date,
    details: `Réservation liée à la garde de l'animal ${getAnimalName(booking.animal)}`
  };
  
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
    
    cancelCompanyReservation();
    alert('Votre réservation a été envoyée à l\'entreprise avec succès !');
    
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
    
    if (profileForm.value.newPassword) {
      if (profileForm.value.newPassword !== profileForm.value.confirmPassword) {
        alert('Les nouveaux mots de passe ne correspondent pas.');
        isUpdatingProfile.value = false;
        return;
      }
      
      if (!profileForm.value.currentPassword) {
        alert('Veuillez entrer votre mot de passe actuel pour confirmer le changement.');
        isUpdatingProfile.value = false;
        return;
      }
    }
    
    const updateData = {
      name: profileForm.value.name,
      email: profileForm.value.email,
      address: profileForm.value.address || '',
      experience: profileForm.value.experience || '',
      capacity: profileForm.value.capacity || null
    };
    
    if (profileForm.value.newPassword && profileForm.value.currentPassword) {
      updateData.current_password = profileForm.value.currentPassword;
      updateData.new_password = profileForm.value.newPassword;
    }
    
    await apiService.updateUserProfile(currentUser.value.id, updateData);
    
    currentUser.value = { 
      ...currentUser.value, 
      name: profileForm.value.name,
      email: profileForm.value.email,
      address: profileForm.value.address,
      experience: profileForm.value.experience,
      capacity: profileForm.value.capacity
    };
    
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

/* Styles for public view */
.public-view {
  width: 100%;
  max-width: var(--max-content-width);
  margin: 0 auto;
  padding: var(--space-xl);
}

.login-prompt {
  background-color: var(--color-background-soft);
  border-radius: var(--border-radius-md);
  padding: var(--space-lg);
  margin-bottom: var(--space-xl);
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

.section-title {
  font-size: 1.75rem;
  margin-bottom: 1.5rem;
  color: var(--color-heading);
  position: relative;
  display: inline-block;
}

.section-title:after {
  content: '';
  position: absolute;
  bottom: -0.5rem;
  left: 0;
  width: 50%;
  height: 4px;
  background-color: var(--color-primary);
  border-radius: 2px;
}

.bookings-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: var(--space-lg);
  margin-top: var(--space-md);
}

.booking-card {
  background-color: var(--color-background);
  border-radius: var(--border-radius-md);
  box-shadow: var(--shadow-md);
  overflow: hidden;
  transition: transform var(--transition-speed), box-shadow var(--transition-speed);
  position: relative;
}

.booking-card:hover {
  transform: translateY(-3px);
  box-shadow: var(--shadow-lg);
}

.booking-banner {
  height: 40px;
  position: relative;
  background-color: var(--color-background-mute);
  display: flex;
  align-items: center;
  justify-content: flex-end;
  padding: 0 var(--space-md);
}

.booking-card.pending .booking-banner {
  background-color: var(--color-warning);
}

.booking-card.accepted .booking-banner {
  background-color: var(--color-success);
}

.booking-card.refused .booking-banner {
  background-color: var(--color-danger);
}

.booking-card.cancelled .booking-banner {
  background-color: var(--color-text-light);
}

.booking-card.linked .booking-banner.special-banner {
  background-color: #6d28d9;  /* Couleur violet pour les réservations liées */
}

.status-badge {
  color: white;
  font-weight: 600;
  font-size: var(--font-size-sm);
  padding: var(--space-xs) var(--space-sm);
  border-radius: var(--border-radius-sm);
}

.booking-content {
  padding: var(--space-md);
}

.booking-avatar {
  display: flex;
  justify-content: center;
  margin: var(--space-sm) 0;
}

.booking-avatar .avatar-image {
  width: 50px;
  height: 50px;
  background-color: var(--color-primary-light, #e0f2fe);
  color: var(--color-primary);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 2rem;
}

.booking-title {
  text-align: center;
  font-size: var(--font-size-lg);
  margin-bottom: var(--space-md);
  color: var(--color-heading);
}

.booking-details {
  display: flex;
  flex-direction: column;
  gap: var(--space-sm);
  margin-bottom: var(--space-md);
}

.detail {
  display: flex;
  align-items: center;
  gap: var(--space-sm);
  font-size: var(--font-size-sm);
}

.detail-icon {
  font-size: 1.2rem;
}

.company-detail {
  margin-top: var(--space-sm);
  padding-top: var(--space-sm);
  border-top: 1px dashed var(--color-border);
}

.reservation-info {
  background-color: var(--color-background-soft);
  padding: var(--space-sm);
  border-radius: var(--border-radius-sm);
  margin-top: var(--space-md);
  font-size: var(--font-size-sm);
}

.booking-actions {
  display: flex;
  gap: var(--space-sm);
  justify-content: center;
  margin-top: var(--space-md);
}

.accept-btn, .refuse-btn {
  display: flex;
  align-items: center;
  gap: var(--space-xs);
  padding: var(--space-xs) var(--space-sm);
  border: none;
  border-radius: var(--border-radius-sm);
  font-weight: 600;
  cursor: pointer;
  transition: background-color var(--transition-speed);
}

.book-company-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: var(--space-xs);
  padding: var(--space-xs) var(--space-sm);
  border: none;
  border-radius: var(--border-radius-sm);
  font-weight: 600;
  cursor: pointer;
  background-color: var(--color-primary);
  color: white;
  transition: background-color var(--transition-speed);
}

.book-company-btn:hover:not(:disabled) {
  background-color: var(--color-primary-hover);
}

.book-company-btn:disabled {
  background-color: var(--color-text-light);
  cursor: not-allowed;
}

.accept-btn {
  background-color: var(--color-success);
  color: white;
}

.accept-btn:hover:not(:disabled) {
  background-color: var(--color-success-dark);
}

.refuse-btn {
  background-color: var(--color-danger);
  color: white;
}

.refuse-btn:hover:not(:disabled) {
  background-color: var(--color-danger-dark);
}

.status-text {
  font-weight: 600;
}

.status-text.pending {
  color: var(--color-warning);
}

.status-text.accepted {
  color: var(--color-success);
}

.status-text.refused, .status-text.cancelled {
  color: var(--color-danger);
}

.empty-icon {
  font-size: 3rem;
  margin-bottom: var(--space-md);
  color: var(--color-primary);
}

.companies-list-vertical {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: var(--space-lg);
  margin-top: var(--space-md);
}

.company-card-vertical {
  background-color: var(--color-background);
  border-radius: var(--border-radius-md);
  box-shadow: var(--shadow-md);
  overflow: hidden;
  cursor: pointer;
  transition: transform var(--transition-speed), box-shadow var(--transition-speed);
  padding: var(--space-md);
}

.company-card-vertical:hover {
  transform: translateY(-3px);
  box-shadow: var(--shadow-lg);
}

.company-info h3 {
  margin-bottom: var(--space-sm);
  color: var(--color-heading);
}

.capacity, .address {
  margin-bottom: var(--space-sm);
  color: var(--color-text-light);
}

.company-card-actions {
  margin-top: var(--space-md);
}

.reservation-btn {
  background-color: var(--color-primary);
  color: white;
  border: none;
  padding: var(--space-sm) var(--space-md);
  border-radius: var(--border-radius-sm);
  font-weight: 600;
  cursor: pointer;
  transition: background-color var(--transition-speed);
}

.reservation-btn:hover {
  background-color: var(--color-primary-hover);
}

.profile-card {
  background-color: var(--color-background);
  border-radius: var(--border-radius-md);
  padding: var(--space-lg);
  box-shadow: var(--shadow-md);
  margin-bottom: var(--space-xl);
}

.profile-actions {
  margin-top: var(--space-md);
}

.edit-profile-btn {
  background-color: var(--color-secondary);
  color: white;
  border: none;
  padding: var(--space-sm) var(--space-md);
  border-radius: var(--border-radius-sm);
  font-weight: 600;
  cursor: pointer;
  transition: background-color var(--transition-speed);
}

.edit-profile-btn:hover {
  background-color: var(--color-secondary-hover);
}

.section-description {
  margin-bottom: var(--space-lg);
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

  .bookings-grid,
  .companies-list-vertical {
    grid-template-columns: 1fr;
  }
}
</style>