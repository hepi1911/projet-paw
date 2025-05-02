import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { apiService } from '../services/api'
import { useRouter } from 'vue-router'

export const useAuthStore = defineStore('auth', () => {
  const router = useRouter()
  const user = ref(null)
  const isAuthenticated = ref(false)

  // Computed property to check if user is admin
  const isAdmin = computed(() => {
    if (!user.value) return false
    return user.value.is_admin || 
           (user.value.admin_status && 
            (user.value.admin_status.is_staff || user.value.admin_status.is_superuser))
  })

  // Charger l'utilisateur depuis le sessionStorage au démarrage
  const initializeAuth = () => {
    try {
      const storedUser = sessionStorage.getItem('user')
      const token = sessionStorage.getItem('token')
      
      if (storedUser && token) {
        user.value = JSON.parse(storedUser)
        isAuthenticated.value = true
        console.log('Authentication restored from sessionStorage:', user.value)
      } else {
        user.value = null
        isAuthenticated.value = false
        // Nettoyer la session si l'un des éléments est manquant
        sessionStorage.removeItem('user')
        sessionStorage.removeItem('token')
      }
    } catch (e) {
      console.error('Erreur lors de la restauration de l\'authentification:', e)
      user.value = null
      isAuthenticated.value = false
      sessionStorage.removeItem('user')
      sessionStorage.removeItem('token')
    }
  }

  const login = async (email, password) => {
    try {
      const response = await apiService.login(email, password)

      // S'assurer que response.user existe et contient les données nécessaires
      if (!response.user) {
        throw new Error('Les données utilisateur sont manquantes dans la réponse')
      }

      // Mettre à jour l'état
      user.value = response.user
      isAuthenticated.value = true

      // Sauvegarder dans la session
      sessionStorage.setItem('user', JSON.stringify(response.user))
      sessionStorage.setItem('token', response.token)
      
      console.log('Login successful:', user.value)
      
      return { 
        success: true, 
        isAdmin: isAdmin.value,
        role: user.value.role
      }
    } catch (error) {
      console.error('Erreur de connexion:', error)
      // Nettoyer l'état en cas d'erreur
      user.value = null
      isAuthenticated.value = false
      sessionStorage.removeItem('user')
      sessionStorage.removeItem('token')
      
      return { success: false, error: error.message || 'Email ou mot de passe incorrect' }
    }
  }
  

  const register = async (userData) => {
    try {
      console.log('Début du processus d\'inscription', userData);
      const response = await apiService.register(userData);
      console.log('Inscription réussie:', response);
      // Nous ne connectons pas automatiquement l'utilisateur, 
      // il devra se connecter manuellement après l'inscription
      return { success: true, data: response };
    } catch (error) {
      console.error('Erreur d\'inscription:', error);
      // Extraction du message d'erreur à partir de la réponse d'erreur axios
      let errorMessage = 'Erreur lors de l\'inscription';
      
      if (error.response) {
        // Le serveur a répondu avec un statut d'erreur
        console.error('Erreur du serveur:', error.response.data);
        if (error.response.data.error) {
          errorMessage = error.response.data.error;
        } else if (typeof error.response.data === 'string') {
          errorMessage = error.response.data;
        } else if (error.response.data) {
          // Si l'erreur contient des champs spécifiques (validation)
          const errorsFields = Object.keys(error.response.data);
          if (errorsFields.length > 0) {
            const firstField = errorsFields[0];
            errorMessage = `${firstField}: ${error.response.data[firstField].join(', ')}`;
          }
        }
      }
      
      // On lance une erreur qui sera capturée par le composant
      throw new Error(errorMessage);
    }
  }

  const logout = () => {
    apiService.logout()
    user.value = null
    isAuthenticated.value = false
    sessionStorage.removeItem('user')
    sessionStorage.removeItem('token')
    router.push('/login')
  }

  // Appeler initializeAuth immédiatement
  initializeAuth()

  return {
    user,
    isAuthenticated,
    isAdmin,
    login,
    register,
    logout,
    initializeAuth
  }
})