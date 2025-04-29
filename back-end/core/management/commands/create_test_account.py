from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()

class Command(BaseCommand):
    help = 'Crée un utilisateur de test avec un mot de passe connu'

    def handle(self, *args, **kwargs):
        # Définir les données pour l'utilisateur de test
        email = 'test@example.com'
        password = 'Test1234!'
        name = 'Test User'
        role = 'petowner'  # Utilisez 'petowner', 'petsitter', ou 'company' selon vos besoins
        address = '123 Rue de Test, 75000 Paris'  # Ajout d'une adresse pour satisfaire la validation
        
        # Vérifier si l'utilisateur existe déjà
        if User.objects.filter(email=email).exists():
            self.stdout.write(self.style.WARNING(f'L\'utilisateur avec l\'email {email} existe déjà. Mise à jour du mot de passe...'))
            user = User.objects.get(email=email)
            user.set_password(password)
            user.address = address  # Mise à jour de l'adresse également
            user.save()
        else:
            # Créer un nouvel utilisateur
            user = User.objects.create_user(
                email=email,
                name=name,
                role=role,
                password=password,
                address=address,  # Ajout de l'adresse
                is_staff=True,  # Donner des droits administratifs (optionnel)
            )
            self.stdout.write(self.style.SUCCESS(f'Utilisateur créé avec succès : {email}'))
        
        # Afficher les informations détaillées
        self.stdout.write(self.style.SUCCESS(f'Email: {email}'))
        self.stdout.write(self.style.SUCCESS(f'Mot de passe: {password}'))
        self.stdout.write(self.style.SUCCESS(f'Rôle: {role}'))