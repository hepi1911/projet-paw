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
  background: white;
  border: 1px solid #ddd;
  padding: 6px 12px;
  border-radius: 4px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 5px;
}

.arrow {
  font-size: 10px;
}

.language-dropdown {
  position: absolute;
  top: 100%;
  right: 0;
  background: white;
  border: 1px solid #ddd;
  border-radius: 4px;
  min-width: 120px;
  z-index: 100;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
}

.language-option {
  padding: 8px 12px;
  cursor: pointer;
}

.language-option:hover {
  background: #f5f5f5;
}

.language-option.active {
  background: #e6f7ff;
  font-weight: bold;
}
</style>