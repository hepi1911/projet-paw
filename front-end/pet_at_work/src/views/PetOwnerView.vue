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
            <h2>{{ $t('animals.my_animals') }}</h2>
            
            <!-- Formulaire d'ajout d'animal -->
            <div class="add-animal-card">
              <h3>{{ $t('animals.add_animal') }}</h3>
              <form @submit.prevent="addAnimal" class="add-animal-form">
                <div class="form-group">
                  <label for="animal-name">{{ $t('animals.name') }}</label>
                  <input 
                    id="animal-name" 
                    v-model="newAnimal.name" 
                    type="text" 
                    required 
                    :placeholder="$t('petowner.animal_name_placeholder')">
                </div>
                
                <div class="form-group">
                  <label for="animal-breed">{{ $t('animals.breed') }}</label>
                  <input 
                    id="animal-breed" 
                    v-model="newAnimal.breed" 
                    type="text" 
                    required
                    :placeholder="$t('petowner.animal_breed_placeholder')">
                </div>
                
                <div class="form-group">
                  <label for="animal-age">{{ $t('animals.age') }}</label>
                  <input 
                    id="animal-age" 
                    v-model="newAnimal.age" 
                    type="text" 
                    required
                    :placeholder="$t('petowner.animal_age_placeholder')">
                </div>
                
                <div class="form-group">
                  <label for="animal-maladie">{{ $t('petowner.medical_conditions') }}</label>
                  <textarea 
                    id="animal-maladie" 
                    v-model="newAnimal.maladie" 
                    :placeholder="$t('petowner.medical_conditions_placeholder')"></textarea>
                </div>
                
                <button type="submit" class="add-animal-btn" :disabled="isSubmitting">
                  {{ isSubmitting ? $t('petowner.adding_animal') : $t('petowner.add_animal_btn') }}
                </button>
              </form>
            </div>
            
            <!-- Liste des animaux de l'utilisateur -->
            <div class="animals-list" v-if="userAnimals.length > 0">
              <div v-for="animal in userAnimals" :key="animal.id" class="animal-card">
                <div class="animal-info">
                  <h3>{{ animal.name }}</h3>
                  <p><strong>{{ $t('animals.breed') }}:</strong> {{ animal.breed }}</p>
                  <p><strong>{{ $t('animals.age') }}:</strong> {{ animal.age }}</p>
                  <p v-if="animal.maladie"><strong>{{ $t('petowner.medical_conditions') }}:</strong> {{ animal.maladie }}</p>
                  <p v-else><strong>{{ $t('petowner.medical_conditions') }}:</strong> {{ $t('animals.no_disease') }}</p>
                </div>
              </div>
            </div>
            
            <!-- Message si aucun animal -->
            <div v-else class="no-animals-message">
              {{ $t('animals.no_animals') }}
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
            <h2>{{ $t('petowner.available_petsitters') }}</h2>
            <div class="sitters-list">
              <div v-for="sitter in petSitters" 
                   :key="sitter.id" 
                   class="sitter-card"
                   @click="handleSitterClick(sitter.id)">
                <div class="sitter-info">
                  <h3>{{ sitter.name }}</h3>
                  <p class="experience">{{ truncateExperience(sitter.experience) }}</p>
                  <p class="contact">{{ $t('petowner.contact') }}: {{ sitter.email }}</p>
                </div>
                <div class="card-footer">
                  <span class="view-more">{{ $t('petowner.view_more') }} →</span>
                </div>
              </div>
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
</script>

<style scoped>
.petowner-dashboard {
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

.pets-section {
  margin-bottom: var(--space-xl);
}

.pets-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: var(--space-lg);
  margin-top: var(--space-lg);
}

.pet-card {
  background-color: var(--color-background);
  border-radius: var(--border-radius-md);
  padding: var(--space-lg);
  box-shadow: var(--shadow-md);
  transition: transform var(--transition-speed), box-shadow var(--transition-speed);
}

.pet-card:hover {
  transform: translateY(-3px);
  box-shadow: var(--shadow-lg);
}

.pet-info {
  margin-top: var(--space-md);
  color: var(--color-text);
}

.pet-actions {
  margin-top: var(--space-md);
  display: flex;
  gap: var(--space-sm);
}

.edit-pet-btn {
  background-color: var(--color-primary);
  color: white;
  border: none;
  padding: var(--space-sm) var(--space-md);
  border-radius: var(--border-radius-sm);
  cursor: pointer;
  font-weight: 600;
  transition: background-color var(--transition-speed);
}

.edit-pet-btn:hover {
  background-color: var(--color-primary-hover);
}

.delete-pet-btn {
  background-color: var(--color-danger);
  color: white;
  border: none;
  padding: var(--space-sm) var(--space-md);
  border-radius: var(--border-radius-sm);
  cursor: pointer;
  font-weight: 600;
  transition: background-color var(--transition-speed);
}

.delete-pet-btn:hover {
  background-color: var(--color-danger-dark);
}

.add-pet-btn {
  background-color: var(--color-success);
  color: white;
  border: none;
  padding: var(--space-md);
  border-radius: var(--border-radius-sm);
  cursor: pointer;
  font-weight: 600;
  transition: background-color var(--transition-speed);
  width: 100%;
}

.add-pet-btn:hover {
  background-color: var(--color-success-dark);
}

.loading, .empty-message {
  text-align: center;
  padding: var(--space-xl);
  background-color: var(--color-background-mute);
  border-radius: var(--border-radius-md);
  margin: var(--space-xl) 0;
  color: var(--color-text-light);
}

.bookings-section {
  margin-bottom: var(--space-xl);
}

.booking-card {
  background-color: var(--color-background);
  border-radius: var(--border-radius-md);
  padding: var(--space-lg);
  box-shadow: var(--shadow-md);
  border-left: 5px solid var(--color-border);
  margin-bottom: var(--space-md);
  transition: transform var(--transition-speed);
}

.booking-card:hover {
  transform: translateY(-3px);
}

.booking-card.pending {
  border-left-color: var(--color-warning);
}

.booking-card.accepted {
  border-left-color: var(--color-success);
}

.booking-card.refused {
  border-left-color: var(--color-danger);
}

.booking-card.cancelled {
  border-left-color: var(--color-text-light);
  opacity: 0.8;
}

.status {
  font-weight: 600;
}

.status.pending {
  color: var(--color-warning);
}

.status.accepted {
  color: var(--color-success);
}

.status.refused {
  color: var(--color-danger);
}

.status.cancelled {
  color: var(--color-text-light);
}

@media (max-width: 768px) {
  .petowner-dashboard {
    padding: var(--space-md);
  }
  
  .dashboard-header {
    flex-direction: column;
    gap: var(--space-md);
    text-align: center;
  }
  
  .pets-grid {
    grid-template-columns: 1fr;
  }
  
  .pet-actions {
    flex-direction: column;
  }
}
</style>