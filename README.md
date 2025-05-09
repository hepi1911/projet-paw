# Pet At Work - Guide d'installation et de lancement

Ce projet est une application web pour la gestion de services de garde d'animaux de compagnie. Il permet aux propriétaires d'animaux de trouver des pet sitters ou des entreprises spécialisées, et aux pet sitters de proposer leurs services.

## Architecture du projet

Le projet est divisé en deux parties principales :
- **Backend** : Une API REST développée avec Django (version 5.2)
- **Frontend** : Une application Vue.js

## Prérequis

Avant de commencer, assurez-vous d'avoir les éléments suivants installés sur votre machine :

- [Python](https://www.python.org/) (version 3.8 ou supérieure)
- [Django](https://www.djangoproject.com/) (version 5.2)
- [Django REST framework](https://www.django-rest-framework.org/) (version 3.14 ou supérieure)
- [Simple JWT](https://django-rest-framework-simplejwt.readthedocs.io/) pour l'authentification
- [Node.js](https://nodejs.org/) (version 14 ou supérieure)
- [npm](https://www.npmjs.com/) ou [yarn](https://yarnpkg.com/)
- [Git](https://git-scm.com/) (optionnel, pour cloner le dépôt)

## Installation et configuration du backend (Django)

1. Naviguez vers le répertoire du backend :
```bash
cd back-end
```

2. Créez un environnement virtuel Python :
```bash
# Sur Windows
python -m venv venv
venv\Scripts\activate

# Sur macOS/Linux
python -m venv venv
source venv/bin/activate
```

3. Installez les dépendances Python requises :
```bash
pip install -r requirements.txt
```

Les dépendances principales incluent :
- Django 5.2
- Django REST framework
- djangorestframework-simplejwt
- django-filter
- django-cors-headers

4. Appliquez les migrations de la base de données :
```bash
python manage.py makemigrations
python manage.py migrate
```

5. (Optionnel) Créez un super utilisateur pour accéder à l'interface d'administration :
```bash
python manage.py createsuperuser
```

6. Démarrez le serveur Django :
```bash
python manage.py runserver
```

Le backend sera disponible à l'adresse : http://localhost:8000/

## Installation et configuration du frontend (Vue.js)

1. Dans un nouveau terminal, naviguez vers le répertoire du frontend :
```bash
cd front-end/pet_at_work
```

2. Installez les dépendances NPM :
```bash
npm install
```

3. Démarrez le serveur de développement Vue.js :
```bash
npm run dev
```

Le frontend sera disponible à l'adresse : http://localhost:5173/

## Utilisation de l'application

Une fois les deux serveurs lancés, accédez à l'application via votre navigateur à l'adresse http://localhost:5173/

### Rôles utilisateur disponibles

L'application prend en charge trois types d'utilisateurs :
- **Propriétaires d'animaux** : Peuvent réserver des services de garde et gérer leurs animaux
- **Pet Sitters** : Peuvent offrir des services de garde et accepter/refuser des réservations
- **Entreprises** : Peuvent offrir des services spécialisés et gérer leurs capacités

### Fonctionnalités principales

- Inscription et connexion avec différents rôles
- Gestion des animaux pour les propriétaires
- Système de réservation complet 
- Traitement des paiements
- Gestion des disponibilités
- Support multilingue (Français/Anglais)

## Notes techniques

- Le backend Django utilise Django REST Framework et JWT pour l'authentification via `djangorestframework-simplejwt`
- La base de données par défaut est SQLite
- Le frontend utilise Vue 3 avec Composition API et Pinia pour la gestion d'état
- L'application gère les traductions via vue-i18n
- Les services de paiement sont simulés pour l'environnement de développement

## Résolution des problèmes courants

- Si vous rencontrez des problèmes de CORS, assurez-vous que le backend est bien lancé sur le port 8000
- Vérifiez que toutes les migrations ont été correctement appliquées
- Pour réinitialiser complètement la base de données : supprimez le fichier db.sqlite3 et refaites les migrations

## Contacts

Pour toute question ou assistance concernant ce projet, veuillez contacter l'équipe de développement.