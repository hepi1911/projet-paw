<template>
  <div class="language-selector">
    <button @click="toggleDropdown" class="language-button">
      {{ currentLanguageLabel }}
      <span class="arrow">▼</span>
    </button>
    <div v-if="showDropdown" class="language-dropdown">
      <div 
        v-for="lang in languages" 
        :key="lang.code" 
        @click="changeLanguage(lang.code)"
        class="language-option"
        :class="{ active: currentLang === lang.code }"
      >
        {{ lang.label }}
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { setLocale } from '@/i18n'

const i18n = useI18n()
const showDropdown = ref(false)
const currentLang = computed(() => i18n.locale.value)

const languages = [
  { code: 'fr', label: 'Français' },
  { code: 'en', label: 'English' }
]

const currentLanguageLabel = computed(() => {
  const lang = languages.find(l => l.code === currentLang.value)
  return lang ? lang.label : 'Language'
})

const toggleDropdown = () => {
  showDropdown.value = !showDropdown.value
}

const changeLanguage = (langCode) => {
  setLocale(langCode)
  showDropdown.value = false
}

// Fermer le menu déroulant lorsqu'on clique ailleurs sur la page
const handleClickOutside = (event) => {
  const selector = document.querySelector('.language-selector')
  if (selector && !selector.contains(event.target)) {
    showDropdown.value = false
  }
}

onMounted(() => {
  document.addEventListener('click', handleClickOutside)
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
})
</script>

<style scoped>
.language-selector {
  position: relative;
  display: inline-block;
}

.language-button {
  background: var(--color-background);
  border: 1px solid var(--color-border);
  padding: var(--space-sm) var(--space-md);
  border-radius: var(--border-radius-sm);
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: var(--space-xs);
  transition: border-color var(--transition-speed);
}

.language-button:hover {
  border-color: var(--color-border-hover);
}

.arrow {
  font-size: 0.625rem;
  color: var(--color-text-light);
}

.language-dropdown {
  position: absolute;
  top: 100%;
  right: 0;
  background: var(--color-background);
  border: 1px solid var(--color-border);
  border-radius: var(--border-radius-sm);
  min-width: 120px;
  z-index: 100;
  box-shadow: var(--shadow-sm);
}

.language-option {
  padding: var(--space-sm) var(--space-md);
  cursor: pointer;
  color: var(--color-text);
  transition: background-color var(--transition-speed);
}

.language-option:hover {
  background: var(--color-background-soft);
}

.language-option.active {
  background: var(--color-primary);
  color: white;
  font-weight: 600;
}
</style>