<template>
  <div class="view-container">
    <div class="blocks-container" v-if="!showCompanies">
      <div class="block" @click="$router.push('/petowner')">
        <h2>Pet Owner</h2>
        <p>Find the perfect sitter for your pet</p>
      </div>
      
      <div class="block" @click="handlePetSitterClick">
        <h2>Pet Sitter</h2>
        <p>Start your journey as a pet sitter</p>
      </div>
      
      <div class="block" @click="$router.push('/company')">
        <h2>Company</h2>
        <p>Business solutions for pet services</p>
      </div>
    </div>

    <!-- Liste des compagnies pour les pet sitters -->
    <div v-if="showCompanies" class="companies-list">
      <h2>Available Companies</h2>
      <p>Connect with these companies for pet services</p>
      
      <div v-if="isLoadingCompanies" class="loading">
        Loading companies...
      </div>
      
      <div v-else-if="companies.length === 0" class="empty-list">
        No companies available at the moment.
      </div>
      
      <div v-else class="companies-container">
        <div 
          v-for="company in companies" 
          :key="company.id" 
          class="company-item" 
          @click="goToCompanyDetail(company.id)"
        >
          <h3>{{ company.name }}</h3>
          <p class="company-info">{{ company.address || 'No address provided' }}</p>
          <p class="company-info">Capacity: {{ company.capacity || 'N/A' }}</p>
        </div>
      </div>
      
      <button class="back-button" @click="showCompanies = false">Back</button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { apiService } from '../services/api';

const router = useRouter();
const showCompanies = ref(false);
const companies = ref([]);
const isLoadingCompanies = ref(false);

// Fonction pour vérifier si l'utilisateur est connecté et le rediriger
const checkUserAndRedirect = () => {
  const userDataString = sessionStorage.getItem('user');
  
  if (userDataString) {
    try {
      // Récupérer les données de l'utilisateur
      const userData = JSON.parse(userDataString);
      const userRole = userData.role;
      
      // Rediriger vers la page d'accueil correspondant au rôle
      switch (userRole) {
        case 'petowner':
          router.push('/petowner');
          break;
        case 'petsitter':
          router.push('/petsitter');
          break;
        case 'company':
          router.push('/company');
          break;
        default:
          // Ne rien faire si le rôle n'est pas reconnu
          break;
      }
    } catch (error) {
      console.error('Erreur lors de la vérification des données utilisateur:', error);
    }
  }
};

// Vérifier l'utilisateur au chargement du composant
onMounted(() => {
  checkUserAndRedirect();
});

// Fonction pour gérer le clic sur Pet Sitter
const handlePetSitterClick = async () => {
  router.push('/petsitter');
};

// Redirection vers la page détaillée d'une compagnie
const goToCompanyDetail = (id) => {
  router.push(`/company/${id}`);
};
</script>

<style scoped>
.view-container {
  min-height: calc(100vh - var(--header-height));
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 2rem;
  width: 100%;
  max-width: 1200px;
  margin: 0 auto;
  box-sizing: border-box;
  position: absolute;
  left: 50%;
  transform: translateX(-50%);
}

.blocks-container {
  display: flex;
  gap: 2rem;
  justify-content: center;
  align-items: center; /* Assure un alignement vertical centré */
  flex-wrap: wrap;
  width: 100%;
  padding: 0 1rem;
  box-sizing: border-box;
  max-width: 1200px; /* Correspond à la largeur max du parent */
  margin: 0 auto; /* Centre le conteneur des blocs */
}

.block {
  background-color: #ffffff;
  border-radius: 8px;
  padding: 2rem;
  width: 300px;
  text-align: center;
  cursor: pointer;
  transition: transform 0.3s ease, box-shadow 0.3s ease;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  flex: 1;
  min-width: 280px;
  max-width: calc(33.33% - 2rem);
  height: 100%;
  margin: 1rem 0;
}

h2 {
  margin-bottom: 1rem;
  color: #2c3e50;
}

p {
  color: #666;
}

/* Style pour la liste des compagnies */
.companies-list {
  width: 100%;
  max-width: 100%;
  margin: 2rem auto;
  padding: 2rem;
  box-sizing: border-box;
  background-color: #ffffff;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  text-align: center;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.companies-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
  margin-top: 2rem;
  margin-bottom: 2rem;
  width: 100%;
}

.company-item {
  background-color: #f8f9fa;
  border-radius: 8px;
  padding: 1.5rem;
  text-align: left;
  cursor: pointer;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  border-left: 4px solid #3498db;
}

.company-item:hover {
  transform: translateY(-3px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
}

.company-item h3 {
  margin-top: 0;
  color: #2c3e50;
}

.company-info {
  color: #333333; /* Changé de #7f8c8d (gris clair) à noir plus foncé */
  margin: 0.5rem 0;
}

.loading, .empty-list {
  margin: 2rem 0;
  color: #7f8c8d;
}

.back-button {
  background-color: #3498db;
  color: white;
  border: none;
  border-radius: 4px;
  padding: 0.7rem 1.5rem;
  font-weight: bold;
  cursor: pointer;
  transition: background-color 0.3s ease;
}

.back-button:hover {
  background-color: #2980b9;
}
</style>