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
    const storedUser = sessionStorage.getItem('user')
    const token = sessionStorage.getItem('token')
    
    if (storedUser && token) {
      try {
        user.value = JSON.parse(storedUser)
        isAuthenticated.value = true
        console.log('Authentication restored from sessionStorage')
      } catch (e) {
        console.error('Erreur lors de la restauration de l\'authentification:', e)
        // En cas d'erreur, on nettoie le sessionStorage
        sessionStorage.removeItem('user')
        sessionStorage.removeItem('token')
        user.value = null
        isAuthenticated.value = false
      }
    } else {
      // Si l'un des deux est manquant, on nettoie tout
      if (storedUser || token) {
        sessionStorage.removeItem('user')
        sessionStorage.removeItem('token')
      }
      user.value = null
      isAuthenticated.value = false
    }
  }

  // Appeler initializeAuth immédiatement
  initializeAuth()

  const login = async (email, password) => {
    try {
      const response = await apiService.login(email, password)

      user.value = response.user || {} 
      isAuthenticated.value = true
  
      sessionStorage.setItem('user', JSON.stringify(user.value))
      
      console.log('Login successful, user role:', user.value.role)
      
      // Nous ne redirigeons plus l'utilisateur ici, cette logique est déplacée dans le composant LoginView
      
      return { 
        success: true, 
        isAdmin: isAdmin.value,
        role: user.value.role
      }
    } catch (error) {
      console.error('Erreur de connexion:', error)
      return { success: false, error: 'Email ou mot de passe incorrect' }
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
    apiService.logout();
    user.value = null;
    isAuthenticated.value = false;
    
    // Rediriger vers la page de connexion
    router.push('/login');
  }

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