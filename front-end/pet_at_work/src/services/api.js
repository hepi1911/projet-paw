import axios from 'axios'

const API_URL = 'http://localhost:8000/api'

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json'
  }
})

// Intercepteur pour ajouter le token d'authentification
api.interceptors.request.use(config => {
  const token = sessionStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// Intercepteur pour gérer les erreurs d'authentification
api.interceptors.response.use(
  response => response,
  async error => {
    const originalRequest = error.config;
    
    // Si l'erreur est 401 (non autorisé) et que nous n'avons pas déjà tenté de rafraîchir le token
    if (error.response && error.response.status === 401 && !originalRequest._retry) {
      console.error('401 Authentication Error:', error.response.data);
      
      // Marquer la requête comme ayant été retentée
      originalRequest._retry = true;
      
      // Vérifier si le token est stocké
      const token = sessionStorage.getItem('token');
      if (token) {
        console.log('A token exists, but has been rejected. Attempting to reconnect...');
        
        // Ici, nous pourrions implémenter une logique pour rafraîchir le token
        // Pour l'instant, nous allons juste vider les informations d'authentification
        sessionStorage.removeItem('token');
        sessionStorage.removeItem('user');
        
        // Rediriger vers la page de connexion
        window.location.href = '/login';
      }
    }
    
    return Promise.reject(error);
  }
)

export const apiService = {
  // Authentification
  async login(email, password) {
    try {
      const response = await api.post('/login/', {
        email: email,
        password
      })
      
      // Vérifier que la réponse contient les données nécessaires
      if (!response.data || !response.data.access || !response.data.user_id) {
        throw new Error('Invalid response from the server')
      }
      
      // Stocker le token dans sessionStorage
      sessionStorage.setItem('token', response.data.access)
      
      // Construire l'objet utilisateur
      const userData = {
        user_id: response.data.user_id,
        email: response.data.email,
        name: response.data.name,
        role: response.data.role,
        // Ajouter d'autres champs si nécessaire
      }
      
      // Stocker les informations utilisateur
      sessionStorage.setItem('user', JSON.stringify(userData))
      
      console.log('Login successful:', userData)
      
      // Retourner les données nécessaires
      return {
        token: response.data.access,
        user: userData
      }
    } catch (error) {
      console.error('Connection error in api.js:', error)
      if (error.response && error.response.status === 401) {
        throw new Error('Incorrect email or password')
      }
      throw error
    }
  },
  
  async register(userData) {
    console.log('Sending registration data:', userData)
    const response = await api.post('/register/', userData)
    console.log('Server response:', response.data)
    return response.data
  },

  async logout() {
    sessionStorage.removeItem('token')
    sessionStorage.removeItem('user')
  },

  // Gestion du profil
  async updateProfile(userData) {
    const response = await api.patch('/users/profile/', userData);
    
    // Mettre à jour les informations utilisateur stockées localement
    const currentUser = JSON.parse(sessionStorage.getItem('user') || '{}');
    const updatedUser = { ...currentUser, ...userData };
    sessionStorage.setItem('user', JSON.stringify(updatedUser));
    
    return response.data;
  },

  async updateUserProfile(userId, profileData) {
    // Créer un objet avec uniquement les données à mettre à jour
    const updateData = {
      name: profileData.name,
      email: profileData.email,
      address: profileData.address || '',
      experience: profileData.experience || '',
      capacity: profileData.capacity || null
    };
    
    // Si un nouveau mot de passe est fourni, l'ajouter aux données
    if (profileData.newPassword) {
      updateData.current_password = profileData.currentPassword;
      updateData.new_password = profileData.newPassword;
    }
    
    const response = await api.patch(`/users/profile/`, updateData);
    return response.data;
  },

  async requestPasswordReset(email) {
    const response = await api.post('/users/password-reset/', { email })
    return response.data
  },

  async verifyResetCode(email, code) {
    const response = await api.post('/users/verify-reset-code/', { email, code })
    return response.data
  },

  async resetPassword(email, code, newPassword) {
    const response = await api.post('/users/reset-password/', {
      email,
      code,
      new_password: newPassword
    })
    return response.data
  },

  // Utilisateurs
  async getAllUsers() {
    const response = await api.get('/users/')
    return response.data
  },

  async getUserById(id) {
    const response = await api.get(`/users/${id}/`)
    return response.data
  },

  async getUsersByRole(role) {
    const response = await api.get(`/users/?role=${role}`)
    return response.data
  },
  
  async getAvailableCompanies() {
    const response = await api.get('/users/available_companies/')
    return response.data
  },

  // Animaux
  async getAllAnimals() {
    const response = await api.get('/animals/')
    return response.data
  },

  async getAnimalById(id) {
    const response = await api.get(`/animals/${id}/`)
    return response.data
  },

  async getAnimalsByOwner(ownerId) {
    const response = await api.get(`/animals/?owner=${ownerId}`)
    return response.data
  },
  
  async createAnimal(animalData) {
    const response = await api.post('/animals/', animalData)
    return response.data
  },

  // Réservations
  async getAllBookings() {
    const response = await api.get('/bookings/')
    return response.data
  },

  async getBookingById(id) {
    const response = await api.get(`/bookings/${id}/`)
    return response.data
  },

  async createBooking(bookingData) {
    const response = await api.post('/bookings/', bookingData)
    return response.data
  },
  
  async updateBookingStatus(bookingId, status) {
    const response = await api.patch(`/bookings/${bookingId}/update_status/`, { status })
    return response.data
  },

  async deleteBooking(bookingId) {
    const response = await api.delete(`/bookings/${bookingId}/`)
    return response.data
  },

  // Réservations spécifiques pour les pet sitters avec les entreprises
  async createPetSitterCompanyBooking(bookingData) {
    const response = await api.post('/petsitter-company-bookings/', bookingData)
    return response.data
  },
  
  async getPetSitterCompanyBookings(petsitterId, companyId) {
    let url = '/petsitter-company-bookings/';
    const params = [];
    
    if (petsitterId) {
      params.push(`petsitter=${petsitterId}`);
    }
    if (companyId) {
      params.push(`company=${companyId}`);
    }
    
    if (params.length > 0) {
      url += '?' + params.join('&');
    }
    
    const response = await api.get(url);
    return response.data;
  },

  async updatePetSitterCompanyBookingStatus(bookingId, newStatus) {
    const response = await api.patch(`/petsitter-company-bookings/${bookingId}/update_status/`, { status: newStatus });
    return response.data;
  },

  // Paiements
  async processPayment(paymentData) {
    const response = await api.post('/payments/process_payment/', paymentData)
    return response.data
  },
  
  async processCompanyPayment(bookingId, paymentType) {
    try {
      // Étape 1: initialisation du paiement pour obtenir les détails
      const initResponse = await api.post(`/process-company-payment/${bookingId}/`, {
        payment_stage: 'init'
      });
      
      console.log('Initialisation du paiement:', initResponse.data);
      
      // Étape 2: traitement du paiement avec les informations de la carte
      const processResponse = await api.post(`/process-company-payment/${bookingId}/`, {
        payment_stage: 'process',
        payment_type: paymentType
      });
      
      console.log('Phave successfully treated:', processResponse.data);
      return processResponse.data;
    } catch (error) {
      console.error('Error processing payment:', error);
      throw error;
    }
  },
  
  async processSharedPayment(bookingId, paymentData) {
    const response = await api.post(`/petsitter-company-bookings/${bookingId}/shared_payment/`, paymentData)
    return response.data
  },
  
  async getMyPayments() {
    const response = await api.get('/payments/my_payments/')
    return response.data
  },
  
  async getPaymentById(id) {
    const response = await api.get(`/payments/${id}/`)
    return response.data
  },

  // Test functions 
  async createTestPendingBooking(animalId, sitterId) {
    const today = new Date();
    const nextWeek = new Date();
    nextWeek.setDate(today.getDate() + 7);
    
    const bookingData = {
      animal: animalId,
      sitter: sitterId,
      start_date: today.toISOString().split('T')[0],
      end_date: nextWeek.toISOString().split('T')[0],
    };
    
    try {
      console.log('Creating test pending booking with:', bookingData);
      const response = await api.post('/bookings/', bookingData);
      console.log('Test booking created successfully:', response.data);
      return response.data;
    } catch (error) {
      console.error('Error creating test booking:', error);
      throw error;
    }
  },
}
