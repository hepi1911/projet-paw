<template>
  <div class="view-container">
    <div class="void-pulse">
      <span class="orbit-overlay"></span>
      <svg class="texture-filter">
        <filter id="void-texture">
          <feTurbulence
            result="noise"
            numOctaves="3"
            baseFrequency="0.02"
            type="turbulence"
          ></feTurbulence>
          <feGaussianBlur
            result="blur"
            stdDeviation="1"
            in="noise"
          ></feGaussianBlur>
          <feSpecularLighting
            result="specular"
            lighting-color="#ff8f00"
            specularExponent="20"
            specularConstant="1"
            surfaceScale="3"
            in="blur"
          >
            <feDistantLight elevation="45" azimuth="90"></feDistantLight>
          </feSpecularLighting>
          <feComposite
            result="lit"
            operator="over"
            in2="SourceGraphic"
            in="specular"
          ></feComposite>
          <feBlend mode="screen" in2="lit" in="SourceGraphic"></feBlend>
        </filter>
      </svg>
      <div class="blocks-container" v-if="!showCompanies">
        <div class="card" @click="$router.push('/petowner')">
          <div class="first-content">
            <span class="icon">🐾</span>
            <h2>Pet Owner</h2>
          </div>
          <div class="second-content">
            <p>Find the perfect sitter for your pet</p>
          </div>
        </div>
        
        <div class="card" @click="handlePetSitterClick">
          <div class="first-content">
            <span class="icon">👤</span>
            <h2>Pet Sitter</h2>
          </div>
          <div class="second-content">
            <p>Start your journey as a pet sitter</p>
          </div>
        </div>
        
        <div class="card" @click="$router.push('/company')">
          <div class="first-content">
            <span class="icon">🏢</span>
            <h2>Company</h2>
          </div>
          <div class="second-content">
            <p>Business solutions for pet services</p>
          </div>
        </div>
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
      console.error('Error verifying user data:', error);
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
  width: 100%;
  position: relative;
  overflow: hidden;
}

.void-pulse {
  width: 100%;
  min-height: calc(100vh - var(--header-height));
  margin: 0;
  padding: 0;
  background: radial-gradient(ellipse, orangered, transparent, orange) orange;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
}

.texture-filter {
  position: absolute;
  width: 0;
  height: 0;
}

.orbit-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
}

.blocks-container {
  position: relative;
  z-index: 1;
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: var(--space-xl);
  padding: var(--space-xl);
  max-width: 1200px;
  margin: 0 auto;
}

.card {
  background: #fff3e0;
  backdrop-filter: blur(10px);
  border-radius: var(--border-radius-lg);
  padding: var(--space-xl);
  cursor: pointer;
  transition: all var(--transition-speed);
  border: 2px solid transparent;
  box-shadow: var(--shadow-md);
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
}

.card:hover {
  transform: translateY(-5px);
  box-shadow: var(--shadow-lg);
  border-color: var(--color-primary);
}

.first-content {
  margin-bottom: var(--space-lg);
}

.icon {
  font-size: 3rem;
  display: block;
  margin-bottom: var(--space-md);
}

h2 {
  color: var(--color-heading);
  font-size: 2rem;
  font-weight: 800;
  margin: 0;
  text-transform: uppercase;
  letter-spacing: 1px;
  font-family: 'Inter', 'Helvetica Neue', Arial, sans-serif;
  background: linear-gradient(135deg, var(--color-heading) 0%, var(--color-primary) 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  margin-bottom: 0.5rem;
}

.second-content p {
  color: var(--color-text);
  margin: 0;
  font-size: 1.15rem;
  font-weight: 400;
  line-height: 1.6;
  opacity: 0.9;
  background: linear-gradient(135deg, var(--color-text) 0%, var(--color-text-light) 100%);
  -webkit-background-clip: text;
  background-clip: text;
  -webkit-text-fill-color: transparent;
  max-width: 80%;
  margin: 0 auto;
  padding-top: 0.5rem;
  position: relative;
}

.second-content p::after {
  content: '';
  position: absolute;
  bottom: -0.75rem;
  left: 50%;
  transform: translateX(-50%);
  width: 40px;
  height: 2px;
  background: linear-gradient(90deg, transparent, var(--color-primary), transparent);
}

.card:hover .second-content p {
  opacity: 1;
  transform: translateY(-2px);
  transition: all var(--transition-speed) ease;
}

.companies-list {
  width: 100%;
  max-width: 100%;
  margin: var(--space-xl) auto;
  padding: var(--space-xl);
  background-color: var(--color-background);
  border-radius: var(--border-radius-md);
  box-shadow: var(--shadow-md);
  text-align: center;
}

.companies-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--space-md);
  margin: var(--space-xl) 0;
  width: 100%;
}

.company-item {
  background-color: var(--color-background-mute);
  border-radius: var(--border-radius-md);
  padding: var(--space-lg);
  text-align: left;
  cursor: pointer;
  transition: transform var(--transition-speed), box-shadow var(--transition-speed);
  box-shadow: var(--shadow-sm);
  border-left: 4px solid var(--color-primary);
  width: 100%;
  max-width: 600px;
}

.company-item:hover {
  transform: translateY(-3px);
  box-shadow: var(--shadow-md);
}

.company-item h3 {
  margin-top: 0;
  color: var(--color-heading);
}

.company-info {
  color: var(--color-text);
  margin: var(--space-sm) 0;
}

.loading, .empty-list {
  margin: var(--space-xl) 0;
  color: var(--color-text-light);
}

.back-button {
  background-color: var(--color-primary);
  color: white;
  border: none;
  border-radius: var(--border-radius-sm);
  padding: var(--space-sm) var(--space-lg);
  font-weight: 600;
  cursor: pointer;
  transition: background-color var(--transition-speed);
}

.back-button:hover {
  background-color: var(--color-primary-hover);
}

@media (max-width: 768px) {
  .view-container {
    padding: var(--space-md);
  }

  .blocks-container {
    gap: var(--space-md);
  }

  .card {
    width: 100%;
    max-width: 300px;
    height: 250px;
  }
}
</style>