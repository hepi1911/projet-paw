<template>
  <div class="filter-container">
    <h3>Filter results</h3>
    <div class="filter-group">
      <label for="search">Search by name :</label>
      <input 
        type="text" 
        id="search" 
        v-model="filters.search" 
        placeholder="Nom du pet sitter"
        @input="updateFilters"
      />
    </div>

    <div class="filter-group">
      <label for="experience">Minimum experience (years) :</label>
      <select id="experience" v-model="filters.experience" @change="updateFilters">
        <option value="">Tous</option>
        <option value="1">1+ years</option>
        <option value="2">2+ years</option>
        <option value="5">5+ years</option>
      </select>
    </div>

    <div class="filter-group">
      <label for="location">Location :</label>
      <input 
        type="text" 
        id="location" 
        v-model="filters.location" 
        placeholder="Ville ou code postal"
        @input="updateFilters"
      />
    </div>

    <div class="filter-group">
      <label for="service">Service :</label>
      <select id="service" v-model="filters.service" @change="updateFilters">
        <option value="">All services</option>
        <option value="garde">Home care</option>
        <option value="promenade">Ride</option>
        <option value="visite">Home visit</option>
      </select>
    </div>

    <div class="filter-group">
      <label for="rating">Minimum notice :</label>
      <select id="rating" v-model="filters.rating" @change="updateFilters">
        <option value="">Tous</option>
        <option value="3">3+ stars</option>
        <option value="4">4+ stars</option>
        <option value="5">5 stars</option>
      </select>
    </div>

    <button class="reset-button" @click="resetFilters">
      Reset filters
    </button>
  </div>
</template>

<script setup>
import { ref, reactive, watch, onMounted } from 'vue';

const props = defineProps({
  initialFilters: {
    type: Object,
    default: () => ({})
  }
});

const emit = defineEmits(['filter-change']);

const filters = reactive({
  search: '',
  experience: '',
  location: '',
  service: '',
  rating: '',
  ...props.initialFilters
});

const updateFilters = () => {
  // Émettre l'événement avec les filtres actuels
  emit('filter-change', { ...filters });
};

const resetFilters = () => {
  // Réinitialiser tous les filtres
  filters.search = '';
  filters.experience = '';
  filters.location = '';
  filters.service = '';
  filters.rating = '';
  updateFilters();
};

// Mise à jour des filtres si les props changent
watch(() => props.initialFilters, (newFilters) => {
  Object.assign(filters, newFilters);
}, { deep: true });

onMounted(() => {
  // Émettre l'événement au montage si des filtres initiaux sont présents
  if (Object.values(props.initialFilters).some(val => val !== '')) {
    updateFilters();
  }
});
</script>

<style scoped>
.filter-section {
  margin-bottom: var(--space-lg);
}

h3 {
  color: var(--color-heading);
  margin-bottom: var(--space-md);
}

.filter-container {
  display: flex;
  flex-direction: column;
  gap: var(--space-md);
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: var(--space-xs);
}

label {
  color: var(--color-text);
  font-weight: 500;
}

input, select {
  padding: var(--space-sm);
  border: 1px solid var(--color-border);
  border-radius: var(--border-radius-sm);
  font-size: 1rem;
}

input:focus, select:focus {
  border-color: var(--color-primary);
  outline: none;
}

.reset-button {
  background-color: var(--color-background-mute);
  border: 1px solid var(--color-border);
  border-radius: var(--border-radius-sm);
  padding: var(--space-sm) var(--space-md);
  cursor: pointer;
  margin-top: var(--space-md);
  font-size: 0.9rem;
  transition: background-color var(--transition-speed);
}

.reset-button:hover {
  background-color: var(--color-border);
}

@media (min-width: 768px) {
  .filter-container {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: var(--space-md);
  }
  
  h3, .reset-button {
    grid-column: span 2;
  }
}
</style>