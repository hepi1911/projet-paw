from django.core.management.base import BaseCommand
from core.models import User, Animal
import random

class Command(BaseCommand):
    help = 'Creates test animals for existing pet owners'

    def handle(self, *args, **kwargs):
        # Liste de noms d'animaux
        animal_names = [
            'Luna', 'Max', 'Bella', 'Charlie', 'Lucy', 'Leo', 'Milo', 'Lily', 'Oscar', 'Daisy',
            'Rocky', 'Sophie', 'Jack', 'Molly', 'Simba', 'Coco', 'Tiger', 'Lola', 'Shadow', 'Ruby'
        ]

        # Liste de races de chiens
        dog_breeds = [
            'Labrador', 'Berger Allemand', 'Golden Retriever', 'Bulldog', 'Beagle',
            'Caniche', 'Husky', 'Yorkshire', 'Boxer', 'Carlin'
        ]

        # Liste de races de chats
        cat_breeds = [
            'Siamois', 'Persan', 'Maine Coon', 'Bengal', 'Ragdoll',
            'British Shorthair', 'Sphynx', 'Abyssin', 'Sacré de Birmanie', 'Norvégien'
        ]

        # Liste de maladies possibles (incluant None pour les animaux en bonne santé)
        maladies = [
            None, None, None,  # Plus de chances de ne pas avoir de maladie
            'Arthrite', 'Diabète', 'Allergie alimentaire', 'Problèmes dentaires',
            'Otite', 'Problèmes respiratoires', 'Dermatite'
        ]

        # Récupérer tous les pet owners
        pet_owners = User.objects.filter(role='petowner')

        for owner in pet_owners:
            # Générer un nombre aléatoire d'animaux (1 à 3) pour chaque propriétaire
            num_animals = random.randint(1, 3)
            
            for _ in range(num_animals):
                # Décider aléatoirement si c'est un chien ou un chat
                is_dog = random.choice([True, False])
                breed = random.choice(dog_breeds if is_dog else cat_breeds)
                
                # Créer l'animal
                animal = Animal.objects.create(
                    owner=owner,
                    name=random.choice(animal_names),
                    breed=breed,
                    age=str(random.randint(1, 15)) + ' ans',
                    maladie=random.choice(maladies)
                )
                
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Created {animal.name} ({animal.breed}) for {owner.name}'
                        f'{" with " + animal.maladie if animal.maladie else " in perfect health"}'
                    )
                )