import { createI18n } from 'vue-i18n'
import fr from './fr.json'
import en from './en.json'

// Récupérer la langue préférée du navigateur ou utiliser l'anglais par défaut
const getBrowserLocale = () => {
  const storedLocale = localStorage.getItem('locale')
  if (storedLocale) return storedLocale
  
  const navigatorLocale = navigator.language.split('-')[0]
  return navigatorLocale === 'fr' || navigatorLocale === 'en' ? navigatorLocale : 'en'
}

// Créer l'instance i18n
const i18n = createI18n({
  legacy: false, // Utiliser le mode Composition API
  locale: getBrowserLocale(),
  fallbackLocale: 'en',
  messages: {
    fr,
    en
  }
})

// Fonction pour changer la langue
export const setLocale = (locale) => {
  i18n.global.locale.value = locale
  localStorage.setItem('locale', locale)
  document.querySelector('html').setAttribute('lang', locale)
}

export default i18n