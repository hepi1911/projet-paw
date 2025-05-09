# Pet At Work - Installation and Launch Guide

This project is a web application for managing pet sitting services. It allows pet owners to find pet sitters or specialized companies, and pet sitters to offer their services.

## Project Architecture

The project is divided into two main parts:
- **Backend**: A REST API developed with Django (version 5.2)
- **Frontend**: A Vue.js application

## Prerequisites

Before starting, make sure you have the following installed on your machine:

- [Python](https://www.python.org/) (version 3.8 or higher)
- [Django](https://www.djangoproject.com/) (version 5.2)
- [Django REST framework](https://www.django-rest-framework.org/) (version 3.14 or higher)
- [Simple JWT](https://django-rest-framework-simplejwt.readthedocs.io/) for authentication
- [Node.js](https://nodejs.org/) (version 14 or higher)
- [npm](https://www.npmjs.com/) or [yarn](https://yarnpkg.com/)
- [Git](https://git-scm.com/) (optional, for cloning the repository)

## Backend Setup (Django)

1. Navigate to the backend directory:
```bash
cd back-end
```

2. Create a Python virtual environment:
```bash
# On Windows
python -m venv venv
venv\Scripts\activate

# On macOS/Linux
python -m venv venv
source venv/bin/activate
```

3. Install the required Python dependencies:
```bash
pip install -r requirements.txt
```

Main dependencies include:
- Django 5.2
- Django REST framework
- djangorestframework-simplejwt
- django-filter
- django-cors-headers

4. Apply database migrations:
```bash
python manage.py makemigrations
python manage.py migrate
```

5. (Optional) Create a superuser to access the admin interface:
```bash
python manage.py createsuperuser
```

6. Start the Django server:
```bash
python manage.py runserver
```

The backend will be available at: http://localhost:8000/

## Frontend Setup (Vue.js)

1. In a new terminal, navigate to the frontend directory:
```bash
cd front-end/pet_at_work
```

2. Install NPM dependencies:
```bash
npm install
```

3. Start the Vue.js development server:
```bash
npm run dev
```

The frontend will be available at: http://localhost:5173/

## Using the Application

Once both servers are running, access the application via your browser at http://localhost:5173/

### Available User Roles

The application supports three types of users:
- **Pet Owners**: Can book pet sitting services and manage their pets
- **Pet Sitters**: Can offer pet sitting services and accept/decline booking requests
- **Companies**: Can offer specialized services and manage their capacity

### Main Features

- Registration and login with different roles
- Pet management for owners
- Complete booking system
- Payment processing
- Availability management
- Multilingual support (French/English)

## Technical Notes

- The Django backend uses Django REST Framework and JWT for authentication via `djangorestframework-simplejwt`
- The default database is SQLite
- The frontend uses Vue 3 with Composition API and Pinia for state management
- The application handles translations via vue-i18n
- Payment services are simulated for the development environment

## Troubleshooting Common Issues

- If you encounter CORS issues, make sure the backend is running on port 8000
- Verify that all migrations have been properly applied
- To completely reset the database: delete the db.sqlite3 file and redo the migrations

## Contact

For any questions or assistance regarding this project, please contact the development team.