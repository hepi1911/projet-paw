from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone
from datetime import datetime

class CustomUserManager(BaseUserManager):
    """
    Gestionnaire personnalisé pour le modèle User permettant la création d'utilisateurs et de superutilisateurs.
    Custom manager for the User model allowing the creation of users and superusers.
    """
    def create_user(self, email, name, role, password=None, **extra_fields):
        """
        Crée et sauvegarde un nouvel utilisateur avec l'email, le nom, le rôle et le mot de passe donnés.
        Creates and saves a new user with the given email, name, role and password.
        """
        if not email:
            raise ValueError('L\'email est obligatoire')
        if not name:
            raise ValueError('Le nom est obligatoire')
        if not role:
            raise ValueError('Le rôle est obligatoire')

        email = self.normalize_email(email)
        user = self.model(email=email, name=name, role=role, **extra_fields)

        if password:
            user.set_password(password)

        user.save(using=self._db)
        return user

    def create_superuser(self, email, name, role, password=None, **extra_fields):
        """
        Crée et sauvegarde un superutilisateur avec l'email, le nom, le rôle et le mot de passe donnés.
        Creates and saves a superuser with the given email, name, role and password.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if not extra_fields.get('is_staff'):
            raise ValueError('Le superuser doit avoir is_staff=True')
        if not extra_fields.get('is_superuser'):
            raise ValueError('Le superuser doit avoir is_superuser=True')

        return self.create_user(email, name, role, password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
    """
    Modèle d'utilisateur personnalisé avec différents rôles: propriétaire d'animal, pet-sitter, ou entreprise.
    Custom user model with different roles: pet owner, pet sitter, or company.
    """
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=255)
    role = models.CharField(max_length=20, choices=[
        ('petowner', 'Pet Owner'),
        ('petsitter', 'Pet Sitter'),
        ('company', 'Company'),
    ])
    address = models.CharField(max_length=255, blank=True, default="")
    experience = models.TextField(blank=True, default="")
    capacity = models.IntegerField(null=True, blank=True, default=0)
    created_at = models.DateTimeField(default=timezone.now)

    # Champs pour la réinitialisation du mot de passe
    reset_code = models.CharField(max_length=6, null=True, blank=True)
    reset_code_expiry = models.DateTimeField(null=True, blank=True)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    # Fix clash with PermissionsMixin
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='custom_user_set',
        blank=True,
        help_text='The groups this user belongs to.',
        verbose_name='groups',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='custom_user_set',
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions',
    )

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name', 'role']

    def clean(self):
        """
        Valide les champs en fonction du rôle de l'utilisateur.
        Validates fields based on the user's role.
        """
        from django.core.exceptions import ValidationError

        # Ignorer les validations pour les superutilisateurs
        if self.is_superuser:
            return

        if self.role == 'petowner':
            if not self.address:
                raise ValidationError('Address is required for Pet Owners')
            if self.experience or self.capacity:
                raise ValidationError('Pet Owners should not have experience or capacity')

        elif self.role == 'petsitter':
            if not self.experience:
                raise ValidationError('Experience is required for Pet Sitters')
            if self.address or self.capacity:
                raise ValidationError('Pet Sitters should not have address or capacity')

        elif self.role == 'company':
            if not self.address:
                raise ValidationError('Address is required for Companies')
            if not self.capacity:
                raise ValidationError('Capacity is required for Companies')
            if self.experience:
                raise ValidationError('Companies should not have experience')

    def save(self, *args, **kwargs):
        """
        Sauvegarde l'utilisateur après validation des champs.
        Saves the user after validating the fields.
        """
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        """
        Renvoie l'adresse e-mail comme représentation textuelle de l'utilisateur.
        Returns the email as string representation of the user.
        """
        return self.email

class Animal(models.Model):
    """
    Modèle pour les animaux de compagnie enregistrés dans l'application.
    Model for pets registered in the application.
    """
    ANIMAL_TYPE_CHOICES = [
        ('dog', 'Dog'),
        ('cat', 'Cat'),
        ('other', 'Other'),
    ]
    
    owner = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'role': 'petowner'})
    name = models.CharField(max_length=100)
    animal_type = models.CharField(max_length=10, choices=ANIMAL_TYPE_CHOICES, default='dog')
    breed = models.CharField(max_length=100, default="Non spécifiée")
    age = models.CharField(max_length=50, default="Non spécifié")
    maladie = models.CharField(max_length=200, null=True, blank=True, default="Aucune maladie connue")

    def __str__(self):
        """
        Renvoie une représentation textuelle de l'animal (nom et race).
        Returns a string representation of the animal (name and breed).
        """
        return f"{self.name} ({self.breed})"

class Booking(models.Model):
    """
    Modèle pour les réservations de garde d'animaux entre propriétaires et pet-sitters.
    Model for pet sitting bookings between pet owners and pet sitters.
    """
    STATUS_CHOICES = [
        ('pending', 'En attente'),
        ('accepted', 'Acceptée'),
        ('refused', 'Refusée'),
        ('cancelled', 'Annulée'),
        ('paid', 'Payée'),  # Nouvel état pour les réservations payées
    ]

    animal = models.ForeignKey(Animal, on_delete=models.CASCADE)
    sitter = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'role': 'petsitter'})
    start_date = models.DateField()
    end_date = models.DateField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    
    @property
    def total_days(self):
        """
        Calcule le nombre total de jours de garde (inclut le premier et le dernier jour).
        Calculates the total number of days for the booking (includes first and last day).
        """
        start_date = self.start_date
        end_date = self.end_date
        delta = end_date - start_date
        return delta.days + 1  # Inclure le premier jour
    
    @property
    def total_price(self):
        """
        Calcule le prix total de la réservation (10€ par jour).
        Calculates the total price of the booking (10€ per day).
        """
        return self.total_days * 10
    
    def __str__(self):
        """
        Renvoie une représentation textuelle de la réservation.
        Returns a string representation of the booking.
        """
        return f"{self.animal.name} avec {self.sitter.name} du {self.start_date} au {self.end_date}"

class CompanyBooking(models.Model):
    """
    Modèle pour les réservations de services entre propriétaires d'animaux et entreprises.
    Model for service bookings between pet owners and companies.
    """
    STATUS_CHOICES = [
        ('pending', 'En attente'),
        ('accepted', 'Acceptée'),
        ('refused', 'Refusée'),
        ('cancelled', 'Annulée'),
        ('paid', 'Payée'),  # Added 'paid' status to match Booking model
    ]

    animal = models.ForeignKey(Animal, on_delete=models.CASCADE)
    company = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'role': 'company'})
    start_date = models.DateField()
    end_date = models.DateField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def total_days(self):
        """
        Calcule le nombre total de jours de garde (inclut le premier et le dernier jour).
        Calculates the total number of days for the booking (includes first and last day).
        """
        start_date = self.start_date
        end_date = self.end_date
        delta = end_date - start_date
        return delta.days + 1  # Inclure le premier jour
    
    @property
    def total_price(self):
        """
        Calcule le prix total de la réservation (10€ par jour).
        Calculates the total price of the booking (10€ per day).
        """
        return self.total_days * 10

    def __str__(self):
        """
        Renvoie une représentation textuelle de la réservation d'entreprise.
        Returns a string representation of the company booking.
        """
        return f"{self.animal.name} à {self.company.name} du {self.start_date} au {self.end_date}"

class PetSitterCompanyBooking(models.Model):
    """
    Modèle pour les réservations de services professionnels entre pet-sitters et entreprises.
    Model for professional service bookings between pet sitters and companies.
    """
    STATUS_CHOICES = [
        ('pending', 'En attente'),
        ('accepted', 'Acceptée'),
        ('refused', 'Refusée'),
        ('cancelled', 'Annulée'),
    ]
    
    SERVICE_CHOICES = [
        ('formation', 'Formation spécialisée'),
        ('consultation', 'Consultation professionnelle'),
        ('collaboration', 'Collaboration pour garde d\'animaux'),
    ]

    petsitter = models.ForeignKey(User, on_delete=models.CASCADE, related_name='petsitter_bookings', limit_choices_to={'role': 'petsitter'})
    company = models.ForeignKey(User, on_delete=models.CASCADE, related_name='company_petsitter_bookings', limit_choices_to={'role': 'company'})
    service_type = models.CharField(max_length=20, choices=SERVICE_CHOICES)
    start_date = models.DateField()
    end_date = models.DateField()
    details = models.TextField(blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        """
        Renvoie une représentation textuelle de la réservation entre pet-sitter et entreprise.
        Returns a string representation of the booking between pet sitter and company.
        """
        return f"{self.petsitter.name} avec {self.company.name} ({self.get_service_type_display()}) du {self.start_date} au {self.end_date}"

class Payment(models.Model):
    """
    Modèle pour stocker les informations de paiement pour les réservations.
    Model for storing payment information for bookings.
    """
    PAYMENT_STATUS_CHOICES = [
        ('pending', 'En attente'),
        ('completed', 'Complété'),
        ('failed', 'Échoué'),
        ('refunded', 'Remboursé'),
    ]
    
    PAYMENT_TYPE_CHOICES = [
        ('card', 'Carte bancaire'),
        ('paypal', 'PayPal'),
        ('transfer', 'Virement bancaire'),
    ]
    
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name='payments', null=True, blank=True)
    company_booking = models.ForeignKey(CompanyBooking, on_delete=models.CASCADE, related_name='payments', null=True, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateTimeField(auto_now_add=True)
    payment_status = models.CharField(max_length=10, choices=PAYMENT_STATUS_CHOICES, default='pending')
    payment_type = models.CharField(max_length=10, choices=PAYMENT_TYPE_CHOICES, default='card')
    transaction_id = models.CharField(max_length=100, null=True, blank=True)
    
    def __str__(self):
        """
        Renvoie une représentation textuelle du paiement.
        Returns a string representation of the payment.
        """
        if self.booking:
            return f"Paiement de {self.amount}€ pour la réservation #{self.booking.id}"
        elif self.company_booking:
            return f"Paiement de {self.amount}€ pour la réservation d'entreprise #{self.company_booking.id}"
        return f"Paiement de {self.amount}€"
