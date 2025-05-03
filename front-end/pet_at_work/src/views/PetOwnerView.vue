<template>
  <div class="view-container">
    <div class="petowner-dashboard">
      <h1>{{ $t('petowner.dashboard') }}</h1>
      <div class="petowner-container">
        <div class="pet-owner">
          <h1>{{ $t('petowner.space_title') }}</h1>
          
          <!-- Sélection du mode de vue (Pet Owner/Pet Sitter) - Visible seulement si l'utilisateur a plusieurs rôles -->
          <div class="view-mode-selector" v-if="hasMultipleRoles">
            <h3>See bookings for:</h3>
            <div class="view-mode-buttons">
              <button 
                class="mode-btn" 
                :class="{ 'active': viewMode === 'owner' }"
                @click="switchViewMode('owner')"
                :disabled="!userHasRole('petowner')">
                Pet Owner
              </button>
              <button 
                class="mode-btn" 
                :class="{ 'active': viewMode === 'sitter' }"
                @click="switchViewMode('sitter')"
                :disabled="!userHasRole('petsitter')">
                Pet Sitter
              </button>
            </div>
          </div>
          
          <!-- Navigation - Affichage conditionnel selon l'état d'authentification -->
          <div class="profile-nav">
            <div v-if="isLoggedIn">
              <button class="profile-btn" @click="goToProfile">{{ $t('petowner.view_profile') }}</button>
            </div>
            <div v-else>
              <button class="login-btn" @click="goToLogin">{{ $t('auth.login') }}</button>
              <button class="register-btn" @click="goToRegister">{{ $t('auth.register') }}</button>
            </div>
          </div>

          <!-- Section Mes Animaux - Visible uniquement pour les utilisateurs connectés -->
          <div class="animals-section" v-if="isLoggedIn && viewMode === 'owner'">
            <h2 class="section-title">{{ $t('animals.my_animals') }}</h2>
            
            <!-- Panneau avec onglets pour ajouter/voir les animaux -->
            <div class="animal-panel">
              <div class="panel-tabs">
                <button 
                  :class="['tab-btn', { active: activeTab === 'list' }]" 
                  @click="activeTab = 'list'"
                >
                  <i class="tab-icon">🐾</i> Mes animaux
                </button>
                <button 
                  :class="['tab-btn', { active: activeTab === 'add' }]" 
                  @click="activeTab = 'add'"
                >
                  <i class="tab-icon">➕</i> Ajouter un animal
                </button>
              </div>
              
              <div class="panel-content">
                <!-- Onglet d'ajout d'animal -->
                <div v-if="activeTab === 'add'" class="add-animal-content">
                  <h3 class="content-title">
                    <span class="pet-emoji">🐶</span>
                    {{ $t('animals.add_animal') }}
                  </h3>
                  
                  <form @submit.prevent="addAnimal" class="add-animal-form">
                    <div class="form-step active">
                      <div class="form-row">
                        <div class="form-group">
                          <label for="animal-name">{{ $t('animals.name') }}</label>
                          <div class="input-container">
                            <i class="input-icon">🏷️</i>
                            <input 
                              id="animal-name" 
                              v-model="newAnimal.name" 
                              type="text" 
                              required 
                              :placeholder="$t('petowner.animal_name_placeholder')">
                          </div>
                        </div>
                        
                        <div class="form-group">
                          <label for="animal-breed">{{ $t('animals.breed') }}</label>
                          <div class="input-container">
                            <i class="input-icon">🧬</i>
                            <input 
                              id="animal-breed" 
                              v-model="newAnimal.breed" 
                              type="text" 
                              required
                              :placeholder="$t('petowner.animal_breed_placeholder')">
                          </div>
                        </div>
                      </div>
                      
                      <div class="form-row">
                        <div class="form-group">
                          <label for="animal-age">{{ $t('animals.age') }}</label>
                          <div class="input-container">
                            <i class="input-icon">🗓️</i>
                            <input 
                              id="animal-age" 
                              v-model="newAnimal.age" 
                              type="text" 
                              required
                              :placeholder="$t('petowner.animal_age_placeholder')">
                          </div>
                        </div>
                        
                        <div class="form-group animal-type">
                          <label>Type</label>
                          <div class="animal-type-selector">
                            <div 
                              :class="['type-option', { selected: selectedAnimalType === 'dog' }]"
                              @click="selectedAnimalType = 'dog'"
                            >
                              <span class="type-emoji">🐕</span>
                              <span class="type-label">Chien</span>
                            </div>
                            <div 
                              :class="['type-option', { selected: selectedAnimalType === 'cat' }]"
                              @click="selectedAnimalType = 'cat'"
                            >
                              <span class="type-emoji">🐈</span>
                              <span class="type-label">Chat</span>
                            </div>
                            <div 
                              :class="['type-option', { selected: selectedAnimalType === 'other' }]"
                              @click="selectedAnimalType = 'other'"
                            >
                              <span class="type-emoji">🐾</span>
                              <span class="type-label">Autre</span>
                            </div>
                          </div>
                        </div>
                      </div>
                      
                      <div class="form-group wide">
                        <label for="animal-maladie">{{ $t('petowner.medical_conditions') }}</label>
                        <div class="input-container textarea-container">
                          <i class="input-icon">🏥</i>
                          <textarea 
                            id="animal-maladie" 
                            v-model="newAnimal.maladie" 
                            :placeholder="$t('petowner.medical_conditions_placeholder')"></textarea>
                        </div>
                      </div>
                      
                      <div class="form-actions">
                        <button type="submit" class="add-animal-btn" :disabled="isSubmitting">
                          <span v-if="isSubmitting" class="spinner"></span>
                          <span v-else class="btn-text">
                            <i class="btn-icon">🐾</i>
                            {{ isSubmitting ? $t('petowner.adding_animal') : $t('petowner.add_animal_btn') }}
                          </span>
                        </button>
                      </div>
                    </div>
                  </form>
                </div>
                
                <!-- Onglet liste des animaux -->
                <div v-else class="animals-list-content">
                  <div v-if="userAnimals.length > 0" class="animals-grid">
                    <div 
                      v-for="animal in userAnimals" 
                      :key="animal.id" 
                      class="animal-card"
                    >
                      <div class="animal-avatar">
                        <div class="avatar-image">
                          {{ getAnimalEmoji(animal.breed) }}
                        </div>
                      </div>
                      
                      <div class="animal-content">
                        <h3 class="animal-name">{{ animal.name }}</h3>
                        <div class="animal-details">
                          <p class="detail"><i class="detail-icon">🧬</i> {{ animal.breed }}</p>
                          <p class="detail"><i class="detail-icon">🗓️</i> {{ animal.age }} {{ animal.age == 1 ? 'an' : 'ans' }}</p>
                          <div class="detail medical" v-if="animal.maladie">
                            <i class="detail-icon">🏥</i>
                            <div class="detail-content">
                              <strong>{{ $t('petowner.medical_conditions') }}:</strong>
                              <p>{{ animal.maladie }}</p>
                            </div>
                          </div>
                          <div class="detail medical" v-else>
                            <i class="detail-icon">💪</i>
                            <div class="detail-content">
                              <strong>{{ $t('petowner.medical_conditions') }}:</strong>
                              <p>{{ $t('animals.no_disease') }}</p>
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                  
                  <div v-else class="no-animals">
                    <div class="no-animals-illustration">🐾</div>
                    <p class="no-animals-text">{{ $t('animals.no_animals') }}</p>
                    <button @click="activeTab = 'add'" class="add-first-animal-btn">
                      <i class="btn-icon">➕</i> Ajouter votre premier animal
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Section Réservations des Pet Owners -->
          <div class="bookings-section" v-if="isLoggedIn && viewMode === 'owner' && ownerBookings.length > 0">
            <h2>{{ $t('bookings.my_bookings') }} (Owner)</h2>
            <div class="bookings-list">
              <div v-for="booking in ownerBookings" 
                   :key="booking.id" 
                   class="booking-card"
                   :class="booking.status">
                <div class="booking-info">
                  <h3>{{ getAnimalName(booking.animal) }}</h3>
                  <p><strong>{{ $t('bookings.sitter') }}:</strong> {{ getSitterName(booking.sitter) }}</p>
                  <p><strong>{{ $t('petowner.dates') }}:</strong> {{ formatDate(booking.start_date) }} - {{ formatDate(booking.end_date) }}</p>
                  <p class="status"><strong>{{ $t('bookings.status') }}:</strong> {{ getStatusLabel(booking.status) }}</p>
                  
                  <!-- Bouton de suppression pour les réservations en attente ou acceptées -->
                  <div class="booking-actions" v-if="booking.status === 'pending' || booking.status === 'accepted'">
                    <button class="delete-btn" @click.stop="confirmDeleteBooking(booking.id)" :disabled="isDeleting === booking.id">
                      {{ isDeleting === booking.id ? $t('petowner.deleting') : $t('petowner.cancel_booking') }}
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Section Réservations des Pet Sitters -->
          <div class="bookings-section" v-if="isLoggedIn && viewMode === 'sitter' && sitterBookings.length > 0">
            <h2>Bookings (Pet Sitter)</h2>
            <div class="bookings-list">
              <div v-for="booking in sitterBookings" 
                   :key="booking.id" 
                   class="booking-card"
                   :class="booking.status">
                <div class="booking-info">
                  <h3>{{ getAnimalName(booking.animal) }}</h3>
                  <p><strong>Owner:</strong> {{ getOwnerName(booking.animal_owner) || 'Propriétaire inconnu' }}</p>
                  <p><strong>Dates:</strong> {{ formatDate(booking.start_date) }} - {{ formatDate(booking.end_date) }}</p>
                  <p class="status"><strong>Status:</strong> {{ getStatusLabel(booking.status) }}</p>
                  <div v-if="booking.status === 'pending'" class="booking-actions">
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

          <!-- Message si aucune réservation -->
          <div v-if="isLoggedIn && ((viewMode === 'owner' && ownerBookings.length === 0) || (viewMode === 'sitter' && sitterBookings.length === 0))" class="no-bookings-message">
            <p>No bookings to display at the moment.</p>
          </div>

          <!-- Section Pet Sitters - Visible pour tous les utilisateurs -->
          <div class="pet-sitters-section">
            <h2 class="section-title">{{ $t('petowner.available_petsitters') }}</h2>
            
            <!-- Filtres et recherche -->
            <div class="sitter-filters">
              <div class="search-container">
                <div class="search-box">
                  <i class="search-icon">🔍</i>
                  <input 
                    type="text" 
                    v-model="searchQuery" 
                    placeholder="Rechercher un pet sitter..." 
                    class="search-input"
                  />
                </div>
                <div class="filter-tags">
                  <button 
                    v-for="(tag, index) in filterTags" 
                    :key="index" 
                    class="filter-tag"
                    :class="{ active: selectedTags.includes(tag.value) }"
                    @click="toggleFilterTag(tag.value)"
                  >
                    {{ tag.label }}
                  </button>
                </div>
              </div>
            </div>
            
            <!-- Affichage en carte ou liste -->
            <div class="view-toggle">
              <button 
                :class="['view-btn', { active: viewType === 'grid' }]" 
                @click="viewType = 'grid'"
              >
                <span class="grid-icon">▥</span> Grille
              </button>
              <button 
                :class="['view-btn', { active: viewType === 'list' }]" 
                @click="viewType = 'list'"
              >
                <span class="list-icon">☰</span> Liste
              </button>
            </div>
            
            <!-- Message si aucun pet sitter trouvé -->
            <div v-if="filteredPetSitters.length === 0" class="no-results">
              <div class="no-results-icon">🔎</div>
              <h3>Aucun résultat trouvé</h3>
              <p>Aucun pet sitter ne correspond à votre recherche. Essayez d'autres critères.</p>
            </div>
            
            <!-- Affichage en grille -->
            <div v-else-if="viewType === 'grid'" class="sitters-grid">
              <div 
                v-for="sitter in filteredPetSitters" 
                :key="sitter.id" 
                class="sitter-card"
                @click="handleSitterClick(sitter.id)"
              >
                <div class="card-banner" :style="{ backgroundColor: getRandomColor(sitter.id) }"></div>
                <div class="card-content">
                  <div class="sitter-avatar">
                    <div class="avatar-placeholder" :style="{ backgroundColor: getRandomColor(sitter.id) }">
                      {{ getInitials(sitter.name) }}
                    </div>
                  </div>
                  
                  <h3 class="sitter-name">{{ sitter.name }}</h3>
                  
                  <div class="sitter-rating">
                    <div class="stars">
                      <span v-for="n in 5" :key="n" class="star" :class="{ 'filled': n <= (sitter.rating || 4) }">
                        {{ n <= (sitter.rating || 4) ? '★' : '☆' }}
                      </span>
                    </div>
                    <span class="rating-score">{{ sitter.rating || '4.0' }}</span>
                  </div>
                  
                  <div class="sitter-badges">
                    <span class="badge" v-if="sitter.capacity">
                      <span class="badge-icon">🏠</span> {{ sitter.capacity }} animaux
                    </span>
                    <span class="badge verified">
                      <span class="badge-icon">✓</span> Vérifié
                    </span>
                  </div>
                  
                  <p class="experience-preview">{{ truncateExperience(sitter.experience) }}</p>
                  
                  <div class="sitter-tags">
                    <span class="tag" v-for="(tag, index) in getRandomTags(sitter.id)" :key="index">
                      {{ tag }}
                    </span>
                  </div>
                  
                  <div class="sitter-contact">
                    <div class="contact-email">
                      <span class="contact-icon">✉️</span>
                      <span class="contact-value">{{ sitter.email }}</span>
                    </div>
                    <div class="contact-address" v-if="sitter.address">
                      <span class="contact-icon">📍</span>
                      <span class="contact-value">{{ truncateAddress(sitter.address) }}</span>
                    </div>
                  </div>
                </div>
                
                <div class="card-footer">
                  <button class="view-details-btn">
                    {{ $t('petowner.view_more') }}
                    <span class="arrow-icon">→</span>
                  </button>
                </div>
              </div>
            </div>
            
            <!-- Affichage en liste -->
            <div v-else class="sitters-list">
              <div 
                v-for="sitter in filteredPetSitters" 
                :key="sitter.id" 
                class="sitter-list-item"
                @click="handleSitterClick(sitter.id)"
              >
                <div class="sitter-list-avatar">
                  <div class="avatar-placeholder" :style="{ backgroundColor: getRandomColor(sitter.id) }">
                    {{ getInitials(sitter.name) }}
                  </div>
                </div>
                
                <div class="sitter-list-info">
                  <div class="sitter-list-header">
                    <h3 class="sitter-name">{{ sitter.name }}</h3>
                    <div class="sitter-rating">
                      <div class="stars">
                        <span v-for="n in 5" :key="n" class="star" :class="{ 'filled': n <= (sitter.rating || 4) }">
                          {{ n <= (sitter.rating || 4) ? '★' : '☆' }}
                        </span>
                      </div>
                      <span class="rating-score">{{ sitter.rating || '4.0' }}</span>
                    </div>
                  </div>
                  
                  <p class="experience-preview">{{ truncateExperience(sitter.experience) }}</p>
                  
                  <div class="sitter-list-footer">
                    <div class="sitter-tags">
                      <span class="tag" v-for="(tag, index) in getRandomTags(sitter.id)" :key="index">
                        {{ tag }}
                      </span>
                    </div>
                    
                    <button class="view-details-btn">
                      {{ $t('petowner.view_more') }}
                      <span class="arrow-icon">→</span>
                    </button>
                  </div>
                </div>
              </div>
            </div>
            
            <!-- Pagination -->
            <div class="pagination" v-if="totalPages > 1">
              <button 
                class="page-btn prev" 
                :disabled="currentPage === 1"
                @click="currentPage--"
              >
                «
              </button>
              
              <button 
                v-for="page in displayedPages" 
                :key="page"
                :class="['page-btn', { active: currentPage === page }]"
                @click="currentPage = page"
              >
                {{ page }}
              </button>
              
              <button 
                class="page-btn next" 
                :disabled="currentPage === totalPages"
                @click="currentPage++"
              >
                »
              </button>
            </div>
          </div>

          <!-- Message pour encourager la connexion - Visible uniquement pour les utilisateurs non connectés -->
          <div class="login-prompt" v-if="!isLoggedIn">
            <p>{{ $t('petowner.login_prompt') }}</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import { useRouter } from 'vue-router';
import { apiService } from '../services/api';
import { useI18n } from 'vue-i18n';

const router = useRouter();
const { t } = useI18n();
const petSitters = ref([]);
const ownerBookings = ref([]);
const sitterBookings = ref([]);
const animalCache = ref({});
const sitterCache = ref({});
const ownerCache = ref({});
const userAnimals = ref([]);
const isSubmitting = ref(false);
const isUpdating = ref(null);
const viewMode = ref('owner'); // 'owner' ou 'sitter'
const newAnimal = ref({
  name: '',
  breed: '',
  age: '',
  maladie: ''
});
const isDeleting = ref(null);
const searchQuery = ref('');
const activeTab = ref('list');
const selectedAnimalType = ref(null);
const viewType = ref('grid'); // 'grid' ou 'list'
const filterTags = ref([
  { label: 'Chiens', value: 'dogs' },
  { label: 'Chats', value: 'cats' },
  { label: 'À domicile', value: 'home' }
]);
const selectedTags = ref([]);
const currentPage = ref(1);
const totalPages = ref(1);
const displayedPages = computed(() => {
  const pages = [];
  for (let i = 1; i <= totalPages.value; i++) {
    pages.push(i);
  }
  return pages;
});

// Calculer si l'utilisateur est connecté
const isLoggedIn = computed(() => {
  return !!sessionStorage.getItem('user');
});

// Vérifier si l'utilisateur a plusieurs rôles
const hasMultipleRoles = computed(() => {
  const userData = JSON.parse(sessionStorage.getItem('user') || '{}');
  // Vérifier si l'utilisateur a un rôle de pet owner ET de pet sitter
  return userHasRole('petowner') && userHasRole('petsitter');
});

// Fonction pour changer le mode de vue
const switchViewMode = (mode) => {
  viewMode.value = mode;
};

// Fonction pour gérer le clic sur une carte de pet sitter
const handleSitterClick = (sitterId) => {
  // Naviguer vers la page de détails du pet sitter, pas besoin de vérifier si connecté
  goToSitterDetail(sitterId);
};

// Rediriger vers la page de connexion
const goToLogin = () => {
  router.push({ 
    name: 'Login',
    query: { redirect: '/petowner' }
  });
};

// Rediriger vers la page d'inscription
const goToRegister = () => {
  router.push({ 
    name: 'Register',
    query: { redirect: '/petowner' }
  });
};

// Fonction pour ajouter un nouvel animal
const addAnimal = async () => {
  try {
    isSubmitting.value = true;
    
    // Vérifier si tous les champs requis sont remplis
    if (!newAnimal.value.name || !newAnimal.value.breed || !newAnimal.value.age) {
      alert(t('petowner.fill_all_fields'));
      isSubmitting.value = false;
      return;
    }
    
    // Envoyer les données au backend avec le nom correct du champ
    const createdAnimal = await apiService.createAnimal({
      name: newAnimal.value.name,
      breed: newAnimal.value.breed,
      age: newAnimal.value.age,
      maladie: newAnimal.value.maladie || ''
    });
    
    // Ajouter l'animal créé à la liste des animaux de l'utilisateur
    userAnimals.value.push(createdAnimal);
    
    // Mettre à jour le cache des noms d'animaux
    animalCache.value[createdAnimal.id] = createdAnimal.name;
    
    // Réinitialiser le formulaire
    newAnimal.value = {
      name: '',
      breed: '',
      age: '',
      maladie: ''
    };
    
    // Afficher un message de succès
    alert(t('petowner.animal_added_success'));
  } catch (error) {
    console.error('Erreur lors de l\'ajout de l\'animal:', error);
    alert(t('petowner.animal_add_error'));
  } finally {
    isSubmitting.value = false;
  }
};

// Fonction pour confirmer la suppression d'une réservation
const confirmDeleteBooking = (bookingId) => {
  if (confirm(t('petowner.confirm_cancel_booking'))) {
    deleteBooking(bookingId);
  }
};

// Fonction pour supprimer une réservation
const deleteBooking = async (bookingId) => {
  try {
    isDeleting.value = bookingId;
    // Utiliser l'API de mise à jour de statut au lieu de delete
    await apiService.updateBookingStatus(bookingId, 'cancelled');
    ownerBookings.value = ownerBookings.value.filter(booking => booking.id !== bookingId);
    alert(t('petowner.booking_cancelled_success'));
  } catch (error) {
    console.error('Erreur lors de la suppression de la réservation:', error);
    alert(t('petowner.booking_cancel_error'));
  } finally {
    isDeleting.value = null;
  }
};

// Fonction pour mettre à jour le statut d'une réservation
const updateBookingStatus = async (bookingId, newStatus) => {
  try {
    isUpdating.value = bookingId;
    await apiService.updateBookingStatus(bookingId, newStatus);
    
    // Mettre à jour le statut dans la liste locale
    const bookingIndex = sitterBookings.value.findIndex(b => b.id === bookingId);
    if (bookingIndex !== -1) {
      sitterBookings.value[bookingIndex].status = newStatus;
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

// Fonction pour récupérer les informations des propriétaires d'animaux
const getOwnerInfo = async (animalId) => {
  try {
    const animal = await apiService.getAnimalById(animalId);
    if (animal && animal.owner) {
      // Récupérer les informations du propriétaire et les mettre en cache
      if (!ownerCache.value[animal.owner]) {
        const owner = await apiService.getUserById(animal.owner);
        ownerCache.value[animal.owner] = owner.name;
      }
      return animal.owner;
    }
    return null;
  } catch (error) {
    console.error('Erreur lors de la récupération des informations du propriétaire:', error);
    return null;
  }
};

onMounted(async () => {
  try {
    // Récupérer la liste des pet sitters (pour tous les utilisateurs)
    petSitters.value = await apiService.getUsersByRole('petsitter');
    
    // Si l'utilisateur est connecté, charger ses données personnelles
    if (isLoggedIn.value) {
      // Récupérer l'ID de l'utilisateur connecté depuis le sessionStorage
      const userData = JSON.parse(sessionStorage.getItem('user') || '{}');
      const currentUserId = userData.user_id;
      const userRole = userData.role;
      
      if (currentUserId) {
        // Définir le mode de vue par défaut en fonction du rôle de l'utilisateur
        // et s'assurer que l'utilisateur ne peut pas accéder à une vue pour laquelle il n'a pas le rôle
        if (userRole === 'petsitter') {
          viewMode.value = 'sitter';
        } else if (userRole === 'petowner') {
          viewMode.value = 'owner';
        } else if (userRole === 'company') {
          // Rediriger vers la vue entreprise si l'utilisateur est une entreprise
          router.push('/company');
          return;
        }
        
        // Récupérer toutes les réservations
        const allBookings = await apiService.getAllBookings();
        
        // Charger les données selon le rôle de l'utilisateur
        if (userRole === 'petowner') {
          // Récupérer uniquement les animaux appartenant à l'utilisateur connecté
          userAnimals.value = await apiService.getAnimalsByOwner(currentUserId);
          
          // Stocker les IDs des animaux de l'utilisateur
          const userAnimalIds = userAnimals.value.map(animal => animal.id);
          
          // Filtrer les réservations pour ne garder que celles concernant les animaux de l'utilisateur
          ownerBookings.value = allBookings.filter(booking => 
            userAnimalIds.includes(booking.animal)
          );
          
          // Mettre en cache les noms des animaux pour un affichage rapide
          for (const animal of userAnimals.value) {
            animalCache.value[animal.id] = animal.name;
          }
        } else if (userRole === 'petsitter') {
          // Filtrer les réservations pour ne garder que celles du pet sitter
          sitterBookings.value = allBookings.filter(booking => 
            booking.sitter === currentUserId
          );
          
          // Pour chaque réservation, récupérer les informations de l'animal et du propriétaire
          for (const booking of sitterBookings.value) {
            try {
              // Récupérer les informations de l'animal s'il n'est pas déjà en cache
              if (!animalCache.value[booking.animal]) {
                const animal = await apiService.getAnimalById(booking.animal);
                animalCache.value[booking.animal] = animal.name;
                
                // Récupérer les informations du propriétaire
                booking.animal_owner = await getOwnerInfo(booking.animal);
              }
            } catch (error) {
              console.error('Erreur lors de la récupération des informations:', error);
            }
          }
        }

        // Mettre en cache les noms des pet sitters pour un affichage rapide (commun aux deux rôles)
        for (const sitter of petSitters.value) {
          sitterCache.value[sitter.id] = sitter.name;
        }
      }
    }
  } catch (error) {
    console.error('Erreur lors du chargement des données:', error);
  }
});

const truncateExperience = (experience) => {
  if (!experience) return '';
  return experience.length > 150 ? experience.substring(0, 150) + '...' : experience;
};

const goToSitterDetail = (id) => {
  router.push(`/petsitter/${id}`);
};

const formatDate = (dateString) => {
  return new Date(dateString).toLocaleDateString();
};

const getAnimalName = (animalId) => {
  return animalCache.value[animalId] || 'Animal inconnu';
};

const getSitterName = (sitterId) => {
  return sitterCache.value[sitterId] || 'Pet sitter inconnu';
};

const getOwnerName = (ownerId) => {
  return ownerCache.value[ownerId] || 'Propriétaire inconnu';
};

const getStatusLabel = (status) => {
  const statusLabels = {
    'pending': 'En attente',
    'accepted': 'Acceptée',
    'refused': 'Refusée',
    'cancelled': 'Annulée'
  };
  return statusLabels[status] || status;
};

const goToProfile = () => {
  router.push('/profile');
};

// Vérifier si l'utilisateur a un rôle spécifique
const userHasRole = (role) => {
  const userData = JSON.parse(sessionStorage.getItem('user') || '{}');
  return userData.role === role;
};

const filteredPetSitters = computed(() => {
  let sitters = petSitters.value;
  if (searchQuery.value) {
    sitters = sitters.filter(sitter => 
      sitter.name.toLowerCase().includes(searchQuery.value.toLowerCase())
    );
  }
  if (selectedTags.value.length > 0) {
    sitters = sitters.filter(sitter => 
      selectedTags.value.some(tag => sitter.tags.includes(tag))
    );
  }
  return sitters;
});

const getInitials = (name) => {
  if (!name) return '';
  const parts = name.split(' ');
  return parts.map(part => part[0]).join('').toUpperCase();
};

const getAnimalEmoji = (breed) => {
  if (!breed) return '🐾';
  const breedLower = breed.toLowerCase();
  if (breedLower.includes('dog') || breedLower.includes('chien')) return '🐕';
  if (breedLower.includes('cat') || breedLower.includes('chat')) return '🐈';
  return '🐾';
};

const getRandomColor = (id) => {
  const colors = ['#f9c74f', '#90be6d', '#f8961e', '#577590', '#43aa8b'];
  return colors[id % colors.length];
};

const getRandomTags = (id) => {
  const tags = ['Chiens', 'Chats', 'À domicile', 'Promenade', 'Garde de nuit'];
  return tags.slice(0, (id % tags.length) + 1);
};

const truncateAddress = (address) => {
  if (!address) return '';
  return address.length > 30 ? address.substring(0, 30) + '...' : address;
};

const toggleFilterTag = (tag) => {
  if (selectedTags.value.includes(tag)) {
    selectedTags.value = selectedTags.value.filter(t => t !== tag);
  } else {
    selectedTags.value.push(tag);
  }
};
</script>

<style scoped>
.petowner-dashboard {
  width: 100%;
  max-width: var(--max-content-width);
  margin: 0 auto;
  padding: var(--space-xl);
}

/* Additional styles for the new pet sitters section */
.pet-sitters-section {
  margin-bottom: var(--space-xl);
}

.sitter-filters {
  margin-bottom: var(--space-lg);
}

.search-container {
  display: flex;
  flex-direction: column;
  gap: var(--space-md);
}

.search-box {
  display: flex;
  align-items: center;
  background-color: var(--color-background);
  border-radius: var(--border-radius-md);
  padding: var(--space-sm) var(--space-md);
  box-shadow: var(--shadow-md);
}

.search-icon {
  margin-right: var(--space-sm);
  color: var(--color-text-light);
}

.search-input {
  border: none;
  outline: none;
  width: 100%;
  font-size: var(--font-size-md);
  color: var(--color-text);
}

.filter-tags {
  display: flex;
  gap: var(--space-sm);
}

.filter-tag {
  background-color: var(--color-background-mute);
  color: var(--color-text-light);
  border: none;
  padding: var(--space-xs) var(--space-sm);
  border-radius: var(--border-radius-sm);
  cursor: pointer;
  font-size: var(--font-size-sm);
}

.filter-tag.active {
  background-color: var(--color-primary);
  color: white;
}

.view-toggle {
  display: flex;
  gap: var(--space-sm);
  margin-bottom: var(--space-lg);
}

.view-btn {
  background-color: var(--color-background-mute);
  color: var(--color-text-light);
  border: none;
  padding: var(--space-xs) var(--space-sm);
  border-radius: var(--border-radius-sm);
  cursor: pointer;
  font-size: var(--font-size-sm);
}

.view-btn.active {
  background-color: var(--color-primary);
  color: white;
}

.sitters-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: var(--space-lg);
}

.sitter-card {
  background-color: var(--color-background);
  border-radius: var(--border-radius-md);
  box-shadow: var(--shadow-md);
  overflow: hidden;
  cursor: pointer;
  transition: transform var(--transition-speed), box-shadow var(--transition-speed);
}

.sitter-card:hover {
  transform: translateY(-3px);
  box-shadow: var(--shadow-lg);
}

.card-banner {
  height: 50px;
}

.card-content {
  padding: var(--space-md);
}

.sitter-avatar {
  display: flex;
  justify-content: center;
  align-items: center;
  margin-bottom: var(--space-md);
}

.avatar-placeholder {
  width: 50px;
  height: 50px;
  background-color: var(--color-primary);
  color: white;
  border-radius: 50%;
  display: flex;
  justify-content: center;
  align-items: center;
  font-weight: bold;
  font-size: var(--font-size-lg);
}

.sitter-name {
  font-size: var(--font-size-lg);
  font-weight: bold;
  margin-bottom: var(--space-sm);
  text-align: center;
}

.sitter-rating {
  display: flex;
  justify-content: center;
  align-items: center;
  margin-bottom: var(--space-sm);
}

.stars {
  display: flex;
}

.star {
  font-size: var(--font-size-md);
  color: var(--color-warning);
}

.star.filled {
  color: var(--color-warning);
}

.rating-score {
  margin-left: var(--space-sm);
  font-weight: bold;
}

.sitter-badges {
  display: flex;
  justify-content: center;
  gap: var(--space-sm);
  margin-bottom: var(--space-sm);
}

.badge {
  background-color: var(--color-background-mute);
  color: var(--color-text-light);
  padding: var(--space-xs) var(--space-sm);
  border-radius: var(--border-radius-sm);
  font-size: var(--font-size-sm);
}

.badge.verified {
  background-color: var(--color-success);
  color: white;
}

.experience-preview {
  margin-bottom: var(--space-sm);
  color: var(--color-text-light);
  text-align: center;
}

.sitter-tags {
  display: flex;
  justify-content: center;
  gap: var(--space-sm);
  margin-bottom: var(--space-sm);
}

.tag {
  background-color: var(--color-background-mute);
  color: var(--color-text-light);
  padding: var(--space-xs) var(--space-sm);
  border-radius: var(--border-radius-sm);
  font-size: var(--font-size-sm);
}

.sitter-contact {
  margin-bottom: var(--space-md);
}

.contact-icon {
  margin-right: var(--space-xs);
}

.contact-value {
  color: var(--color-primary);
}

.card-footer {
  text-align: center;
}

.view-details-btn {
  background-color: var(--color-primary);
  color: white;
  border: none;
  padding: var(--space-sm) var(--space-md);
  border-radius: var(--border-radius-sm);
  cursor: pointer;
  font-weight: 600;
  transition: background-color var(--transition-speed);
}

.view-details-btn:hover {
  background-color: var(--color-primary-hover);
}

.no-results {
  text-align: center;
  padding: var(--space-lg);
  background-color: var(--color-background-mute);
  border-radius: var(--border-radius-md);
  margin: var(--space-lg) 0;
  color: var(--color-text-light);
}

.no-results-icon {
  font-size: var(--font-size-xl);
  margin-bottom: var(--space-md);
}

.pagination {
  display: flex;
  justify-content: center;
  gap: var(--space-sm);
  margin-top: var(--space-lg);
}

.page-btn {
  background-color: var(--color-background-mute);
  color: var(--color-text-light);
  border: none;
  padding: var(--space-xs) var(--space-sm);
  border-radius: var(--border-radius-sm);
  cursor: pointer;
  font-size: var(--font-size-sm);
}

.page-btn.active {
  background-color: var(--color-primary);
  color: white;
}

.page-btn.prev, .page-btn.next {
  font-weight: bold;
}

/* Styles for the new animal form sections */
.animal-type-selector {
  display: flex;
  gap: var(--space-sm);
  margin-top: 0.5rem;
}

.type-option {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 0.75rem;
  border-radius: var(--border-radius-sm);
  background-color: var(--color-background-mute);
  cursor: pointer;
  transition: all 0.3s ease;
}

.type-option.selected {
  background-color: var(--color-primary-light, #e0f2fe);
  border: 2px solid var(--color-primary, #3490dc);
  transform: translateY(-2px);
}

.type-emoji {
  font-size: 1.5rem;
  margin-bottom: 0.25rem;
}

.type-label {
  font-size: 0.875rem;
  color: var(--color-text);
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 500;
  color: var(--color-text);
}

.form-group input, .form-group textarea {
  width: 100%;
  border: none;
  background: transparent;
  padding: 0.5rem;
  outline: none;
  color: var(--color-text);
}

.form-group textarea {
  min-height: 100px;
  resize: vertical;
}

.form-group.wide {
  grid-column: span 2;
}

.form-actions {
  margin-top: 1rem;
  display: flex;
  justify-content: flex-end;
}

.spinner {
  display: inline-block;
  width: 20px;
  height: 20px;
  border: 3px solid rgba(255, 255, 255, 0.3);
  border-radius: 50%;
  border-top-color: white;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.btn-text {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
}

.btn-icon {
  font-size: 1.2rem;
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

.content-title {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 1.5rem;
}

.pet-emoji {
  font-size: 1.5rem;
}

.animal-details {
  margin-top: 0.75rem;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.detail.medical {
  margin-top: 0.5rem;
  display: flex;
  align-items: flex-start;
}

.detail-content {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.detail-content p {
  color: var(--color-text-light);
  font-size: 0.875rem;
}

/* Styles for the pet sitters in list view */
.sitters-list {
  display: flex;
  flex-direction: column;
  gap: var(--space-md);
}

.sitter-list-item {
  display: flex;
  background-color: var(--color-background);
  border-radius: var(--border-radius-md);
  box-shadow: var(--shadow-md);
  overflow: hidden;
  cursor: pointer;
  transition: transform var(--transition-speed), box-shadow var(--transition-speed);
}

.sitter-list-item:hover {
  transform: translateY(-3px);
  box-shadow: var(--shadow-lg);
}

.sitter-list-avatar {
  padding: var(--space-md);
  display: flex;
  align-items: center;
  justify-content: center;
}

.sitter-list-info {
  flex: 1;
  padding: var(--space-md);
  display: flex;
  flex-direction: column;
}

.sitter-list-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--space-sm);
}

.sitter-list-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: auto;
}

.contact-email, .contact-address {
  display: flex;
  align-items: center;
  margin-bottom: var(--space-xs);
}

/* Responsive design for pet sitters section */
@media (max-width: 768px) {
  .petowner-dashboard {
    padding: var(--space-md);
  }
  
  .dashboard-header {
    flex-direction: column;
    gap: var(--space-md);
    text-align: center;
  }
  
  .sitters-grid {
    grid-template-columns: 1fr;
  }
  
  .sitter-filters {
    flex-direction: column;
  }
  
  .search-container {
    width: 100%;
  }
  
  .filter-tags {
    flex-wrap: wrap;
  }
  
  .sitter-list-item {
    flex-direction: column;
  }
  
  .sitter-list-avatar {
    align-self: center;
    margin-top: var(--space-md);
  }
  
  .sitter-list-header {
    flex-direction: column;
    align-items: flex-start;
    gap: var(--space-xs);
  }
  
  .sitter-list-footer {
    flex-direction: column;
    align-items: flex-start;
    gap: var(--space-md);
  }
}

/* Styles for the animal form and list */
.animal-panel {
  background-color: var(--color-background);
  border-radius: var(--border-radius-md);
  box-shadow: var(--shadow-md);
  overflow: hidden;
  margin-bottom: var(--space-lg);
}

.panel-tabs {
  display: flex;
  border-bottom: 1px solid var(--color-border);
}

.tab-btn {
  flex: 1;
  padding: var(--space-md);
  background-color: transparent;
  border: none;
  cursor: pointer;
  font-size: var(--font-size-md);
  transition: all 0.3s ease;
}

.tab-btn.active {
  color: var(--color-primary);
  border-bottom: 3px solid var(--color-primary);
  font-weight: 600;
}

.tab-icon {
  margin-right: var(--space-xs);
}

.panel-content {
  padding: var(--space-lg);
}

.add-animal-content, .animals-list-content {
  min-height: 200px;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--space-md);
  margin-bottom: var(--space-md);
}

.input-container {
  display: flex;
  align-items: center;
  background-color: var(--color-background-mute);
  border-radius: var(--border-radius-sm);
  padding: var(--space-xs) var(--space-sm);
}

.input-icon {
  margin-right: var(--space-sm);
}

.animals-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: var(--space-md);
}

.animal-card {
  background-color: var(--color-background-mute);
  border-radius: var(--border-radius-md);
  padding: var(--space-md);
  box-shadow: var(--shadow-sm);
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.animal-card:hover {
  transform: translateY(-3px);
  box-shadow: var(--shadow-md);
}

.animal-avatar {
  display: flex;
  justify-content: center;
  margin-bottom: var(--space-sm);
}

.avatar-image {
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

.animal-content {
  text-align: center;
}

.animal-name {
  margin-bottom: var(--space-sm);
  font-size: var(--font-size-lg);
}

.detail {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: var(--space-xs);
  font-size: var(--font-size-sm);
}

.detail-icon {
  font-size: 1.2rem;
}

.no-animals {
  text-align: center;
  padding: var(--space-lg) 0;
}

.no-animals-illustration {
  font-size: 3rem;
  margin-bottom: var(--space-md);
  color: var(--color-text-light);
}

.no-animals-text {
  margin-bottom: var(--space-md);
  color: var(--color-text-light);
}

.add-first-animal-btn {
  background-color: var(--color-primary);
  color: white;
  border: none;
  padding: var(--space-sm) var(--space-md);
  border-radius: var(--border-radius-sm);
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: var(--space-xs);
  margin: 0 auto;
  font-weight: 600;
}

.add-animal-btn {
  background-color: var(--color-primary);
  color: white;
  border: none;
  padding: var(--space-sm) var(--space-md);
  border-radius: var(--border-radius-sm);
  cursor: pointer;
  font-weight: 600;
  transition: background-color var(--transition-speed);
}

.add-animal-btn:hover, .add-first-animal-btn:hover {
  background-color: var(--color-primary-hover);
}
</style>