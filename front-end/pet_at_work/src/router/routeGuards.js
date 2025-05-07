// Gardes de route pour limiter l'accès selon le rôle de l'utilisateur

/**
 * Vérifie si l'utilisateur est connecté et a le rôle requis.
 * Uniquement pour les routes qui nécessitent absolument un rôle spécifique.
 * @param {string} requiredRole - Le rôle requis pour accéder à la route (petowner, petsitter, company)
 * @returns {Function} - Une fonction de garde de route
 */
export function requireRole(requiredRole) {
  return (to, from, next) => {
    // Vérifier si l'utilisateur est connecté
    const userDataString = sessionStorage.getItem('user');
    if (!userDataString) {
      // L'utilisateur n'est pas connecté, rediriger vers la page de connexion
      return next({ name: 'Login', query: { redirect: to.fullPath } });
    }

    try {
      // Récupérer les données de l'utilisateur
      const userData = JSON.parse(userDataString);
      const userRole = userData.role;

      // Vérifier si le rôle de l'utilisateur correspond au rôle requis
      if (userRole === requiredRole) {
        // L'utilisateur a le bon rôle, permettre l'accès
        return next();
      } else {
        // L'utilisateur n'a pas le bon rôle, rediriger vers sa page d'accueil
        switch (userRole) {
          case 'petowner':
            return next({ name: 'PetOwner' });
          case 'petsitter':
            return next({ name: 'PetSitter' });
          case 'company':
            return next({ name: 'Company' });
          default:
            // Si le rôle n'est pas reconnu, déconnecter l'utilisateur
            sessionStorage.removeItem('token');
            sessionStorage.removeItem('user');
            return next({ name: 'Login' });
        }
      }
    } catch (error) {
      console.error('Error verifying role:', error);
      sessionStorage.removeItem('token');
      sessionStorage.removeItem('user');
      return next({ name: 'Login' });
    }
  };
}

/**
 * Vérifie si l'utilisateur est connecté
 * Pour les routes qui nécessitent une connexion mais pas un rôle spécifique
 */
export function requireAuth(to, from, next) {
  // Vérifier si l'utilisateur est connecté
  const userDataString = sessionStorage.getItem('user');
  const token = sessionStorage.getItem('token');
  
  if (!userDataString || !token) {
    // L'utilisateur n'est pas connecté, rediriger vers la page de connexion
    return next({ name: 'Login', query: { redirect: to.fullPath } });
  }
  
  // L'utilisateur est connecté, permettre l'accès
  next();
}

/**
 * Redirige l'utilisateur connecté vers sa page d'accueil en fonction de son rôle
 */
export function redirectLoggedIn(to, from, next) {
  // Vérifier si l'utilisateur est connecté
  const userDataString = sessionStorage.getItem('user');
  
  if (userDataString) {
    try {
      // Récupérer les données de l'utilisateur
      const userData = JSON.parse(userDataString);
      const userRole = userData.role;
      
      // Rediriger vers la page d'accueil correspondant au rôle
      switch (userRole) {
        case 'petowner':
          return next({ name: 'PetOwner' });
        case 'petsitter':
          return next({ name: 'PetSitter' });
        case 'company':
          return next({ name: 'Company' });
        default:
          return next();
      }
    } catch (error) {
      console.error('Error while redirecting:', error);
      return next();
    }
  }
  
  // L'utilisateur n'est pas connecté, permettre l'accès
  next();
}

/**
 * Vérifie si l'utilisateur est connecté et a le rôle requis pour faire une réservation
 * @param {string} requiredRole - Le rôle requis pour la réservation
 * @returns {Function} - Une fonction de garde de route
 */
export function requireRoleForBooking(requiredRole) {
  return (to, from, next) => {
    // Permet la navigation à tous sans connexion
    // La vérification du rôle se fera au niveau du composant pour les actions réservées
    next();
  };
}