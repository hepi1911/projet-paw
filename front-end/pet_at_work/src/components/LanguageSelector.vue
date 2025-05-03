<template>
  <div class="language-selector">
    <label class="hamburger">
      <input type="checkbox" v-model="showDropdown">
      <svg viewBox="0 0 32 32">
        <path class="line line-top-bottom" d="M27 10 13 10C10.8 10 9 8.2 9 6 9 3.5 10.8 2 13 2 15.2 2 17 3.8 17 6L17 26C17 28.2 18.8 30 21 30 23.2 30 25 28.2 25 26 25 23.8 23.2 22 21 22L7 22"></path>
        <path class="line" d="M7 16 27 16"></path>
      </svg>
      <span class="current-lang">{{ currentLanguageLabel }}</span>
    </label>
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

.hamburger {
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: var(--space-sm);
}

.hamburger input {
  display: none;
}

.hamburger svg {
  height: 2em;
  transition: transform 600ms cubic-bezier(0.4, 0, 0.2, 1);
}

.line {
  fill: none;
  stroke: black;
  stroke-linecap: round;
  stroke-linejoin: round;
  stroke-width: 3;
  transition: stroke-dasharray 600ms cubic-bezier(0.4, 0, 0.2, 1),
              stroke-dashoffset 600ms cubic-bezier(0.4, 0, 0.2, 1);
}

.line-top-bottom {
  stroke-dasharray: 12 63;
}

.hamburger input:checked + svg {
  transform: rotate(-45deg);
}

.hamburger input:checked + svg .line-top-bottom {
  stroke-dasharray: 20 300;
  stroke-dashoffset: -32.42;
}

.current-lang {
  color: black;
  font-weight: 600;
  font-size: 0.9rem;
}

.language-dropdown {
  position: absolute;
  top: 100%;
  right: 0;
  background: var(--color-background);
  border: 2px solid var(--color-primary);
  border-radius: var(--border-radius-md);
  min-width: 150px;
  z-index: 100;
  box-shadow: var(--shadow-md);
  margin-top: var(--space-xs);
  overflow: hidden;
}

.language-option {
  padding: var(--space-md);
  cursor: pointer;
  color: var(--color-text);
  transition: all var(--transition-speed);
  font-weight: 500;
}

.language-option:hover {
  background: var(--color-primary);
  color: white;
}

.language-option.active {
  background: var(--color-primary);
  color: white;
  font-weight: 600;
}

/* Animation pour le dropdown */
.language-dropdown {
  animation: slideIn 0.3s ease-out;
}

@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>