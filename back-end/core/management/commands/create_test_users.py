from django.core.management.base import BaseCommand
from core.models import User
import random

class Command(BaseCommand):
    help = 'Creates 30 test users (10 of each type)'

    def handle(self, *args, **kwargs):
        # Pet Sitters
        pet_sitters = [
            {
                'name': 'Sophie Martin',
                'email': 'sophie.martin@example.com',
                'password': 'password123',
                'role': 'petsitter',
                'experience': '5 ans d\'expérience avec les chiens et chats. Spécialisée dans les soins pour animaux âgés.'
            },
            {
                'name': 'Lucas Bernard',
                'email': 'lucas.bernard@example.com',
                'password': 'password123',
                'role': 'petsitter',
                'experience': 'Ancien vétérinaire assistant, 7 ans d\'expérience avec tous types d\'animaux.'
            },
            {
                'name': 'Emma Dubois',
                'email': 'emma.dubois@example.com',
                'password': 'password123',
                'role': 'petsitter',
                'experience': 'Étudiante en médecine vétérinaire, passionnée par les animaux depuis l\'enfance.'
            },
            {
                'name': 'Thomas Petit',
                'email': 'thomas.petit@example.com',
                'password': 'password123',
                'role': 'petsitter',
                'experience': 'Dresseur canin certifié, spécialisé dans les races de grande taille.'
            },
            {
                'name': 'Julie Moreau',
                'email': 'julie.moreau@example.com',
                'password': 'password123',
                'role': 'petsitter',
                'experience': '3 ans d\'expérience, spécialisée dans les soins aux chats et NAC.'
            },
            {
                'name': 'Nicolas Lambert',
                'email': 'nicolas.lambert@example.com',
                'password': 'password123',
                'role': 'petsitter',
                'experience': 'Expert en comportement animal, 10 ans d\'expérience avec tous types d\'animaux.'
            },
            {
                'name': 'Marie Rousseau',
                'email': 'marie.rousseau@example.com',
                'password': 'password123',
                'role': 'petsitter',
                'experience': '4 ans d\'expérience, spécialisée dans les soins d\'urgence.'
            },
            {
                'name': 'Antoine Durand',
                'email': 'antoine.durand@example.com',
                'password': 'password123',
                'role': 'petsitter',
                'experience': 'Ancien soigneur de zoo, expert en animaux exotiques.'
            },
            {
                'name': 'Léa Martin',
                'email': 'lea.martin@example.com',
                'password': 'password123',
                'role': 'petsitter',
                'experience': 'Comportementaliste canin diplômée, 6 ans d\'expérience.'
            },
            {
                'name': 'Paul Lefebvre',
                'email': 'paul.lefebvre@example.com',
                'password': 'password123',
                'role': 'petsitter',
                'experience': 'Spécialiste en rééducation animale, 8 ans d\'expérience.'
            }
        ]

        # Companies
        companies = [
            {
                'name': 'PawCare Enterprise',
                'email': 'contact@pawcare.com',
                'password': 'password123',
                'role': 'company',
                'address': '15 rue de la Paix, Paris',
                'capacity': random.randint(1, 10)
            },
            {
                'name': 'Animal Haven Corp',
                'email': 'contact@animalhaven.com',
                'password': 'password123',
                'role': 'company',
                'address': '25 avenue des Champs-Élysées, Paris',
                'capacity': random.randint(1, 10)
            },
            {
                'name': 'PetLux Services',
                'email': 'contact@petlux.com',
                'password': 'password123',
                'role': 'company',
                'address': '8 rue du Commerce, Lyon',
                'capacity': random.randint(1, 10)
            },
            {
                'name': 'Happy Tails Inc',
                'email': 'contact@happytails.com',
                'password': 'password123',
                'role': 'company',
                'address': '42 boulevard Victor Hugo, Nice',
                'capacity': random.randint(1, 10)
            },
            {
                'name': 'FurFriends Solutions',
                'email': 'contact@furfriends.com',
                'password': 'password123',
                'role': 'company',
                'address': '12 rue de la République, Marseille',
                'capacity': random.randint(1, 10)
            },
            {
                'name': 'VetCare Plus',
                'email': 'contact@vetcareplus.com',
                'password': 'password123',
                'role': 'company',
                'address': '3 avenue Pasteur, Bordeaux',
                'capacity': random.randint(1, 10)
            },
            {
                'name': 'PetParadise Pro',
                'email': 'contact@petparadise.com',
                'password': 'password123',
                'role': 'company',
                'address': '18 rue des Fleurs, Toulouse',
                'capacity': random.randint(1, 10)
            },
            {
                'name': 'AnimalCare Elite',
                'email': 'contact@animalcare-elite.com',
                'password': 'password123',
                'role': 'company',
                'address': '27 boulevard de la Liberté, Lille',
                'capacity': random.randint(1, 10)
            },
            {
                'name': 'PetGuard Services',
                'email': 'contact@petguard.com',
                'password': 'password123',
                'role': 'company',
                'address': '55 rue de la Gare, Strasbourg',
                'capacity': random.randint(1, 10)
            },
            {
                'name': 'CompanionCare Pro',
                'email': 'contact@companioncare.com',
                'password': 'password123',
                'role': 'company',
                'address': '9 place Bellecour, Lyon',
                'capacity': random.randint(1, 10)
            }
        ]

        # Pet Owners
        pet_owners = [
            {
                'name': 'Marie Lambert',
                'email': 'marie.lambert@example.com',
                'password': 'password123',
                'role': 'petowner',
                'address': '3 rue des Fleurs, Paris'
            },
            {
                'name': 'Pierre Dupont',
                'email': 'pierre.dupont@example.com',
                'password': 'password123',
                'role': 'petowner',
                'address': '18 avenue Victor Hugo, Lyon'
            },
            {
                'name': 'Claire Martin',
                'email': 'claire.martin@example.com',
                'password': 'password123',
                'role': 'petowner',
                'address': '27 rue de la Liberté, Marseille'
            },
            {
                'name': 'Antoine Rousseau',
                'email': 'antoine.rousseau@example.com',
                'password': 'password123',
                'role': 'petowner',
                'address': '5 place Bellecour, Lyon'
            },
            {
                'name': 'Sarah Michel',
                'email': 'sarah.michel@example.com',
                'password': 'password123',
                'role': 'petowner',
                'address': '14 rue du Vieux Port, Marseille'
            },
            {
                'name': 'Thomas Garcia',
                'email': 'thomas.garcia@example.com',
                'password': 'password123',
                'role': 'petowner',
                'address': '22 rue de la République, Nice'
            },
            {
                'name': 'Julie Blanc',
                'email': 'julie.blanc@example.com',
                'password': 'password123',
                'role': 'petowner',
                'address': '7 avenue des Ternes, Paris'
            },
            {
                'name': 'François Leroy',
                'email': 'francois.leroy@example.com',
                'password': 'password123',
                'role': 'petowner',
                'address': '31 rue Saint-Pierre, Bordeaux'
            },
            {
                'name': 'Sophie Dubois',
                'email': 'sophie.dubois@example.com',
                'password': 'password123',
                'role': 'petowner',
                'address': '12 place du Capitole, Toulouse'
            },
            {
                'name': 'Marc Petit',
                'email': 'marc.petit@example.com',
                'password': 'password123',
                'role': 'petowner',
                'address': '8 rue de la Grande Armée, Lille'
            }
        ]

        # Suppression des utilisateurs existants
        User.objects.all().delete()

        # Création des nouveaux utilisateurs
        for user_data in pet_sitters + companies + pet_owners:
            User.objects.create(**user_data)
            self.stdout.write(
                self.style.SUCCESS(f'Successfully created {user_data["role"]}: {user_data["name"]}'))