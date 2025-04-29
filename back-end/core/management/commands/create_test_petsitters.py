from django.core.management.base import BaseCommand
from core.models import PetSitter

class Command(BaseCommand):
    help = 'Creates 15 test pet sitters'

    def handle(self, *args, **kwargs):
        pet_sitters_data = [
            {
                'name': 'Sophie Martin',
                'age': 28,
                'experience': '5 ans d\'expérience avec les chiens et chats. Spécialisée dans les soins pour animaux âgés.'
            },
            {
                'name': 'Lucas Bernard',
                'age': 32,
                'experience': 'Ancien vétérinaire assistant, 7 ans d\'expérience avec tous types d\'animaux.'
            },
            {
                'name': 'Emma Dubois',
                'age': 24,
                'experience': 'Étudiante en médecine vétérinaire, passionnée par les animaux depuis l\'enfance.'
            },
            {
                'name': 'Thomas Petit',
                'age': 35,
                'experience': 'Dresseur canin certifié, spécialisé dans les races de grande taille.'
            },
            {
                'name': 'Julie Moreau',
                'age': 29,
                'experience': '3 ans d\'expérience, spécialisée dans les soins aux chats et NAC.'
            },
            {
                'name': 'Antoine Lambert',
                'age': 41,
                'experience': 'Propriétaire d\'une pension canine pendant 10 ans, expert en comportement animal.'
            },
            {
                'name': 'Marie Rousseau',
                'age': 27,
                'experience': 'Formation en premiers secours animaliers, 4 ans d\'expérience.'
            },
            {
                'name': 'Paul Lefebvre',
                'age': 31,
                'experience': 'Spécialiste des reptiles et amphibiens, 6 ans d\'expérience.'
            },
            {
                'name': 'Chloé Simon',
                'age': 26,
                'experience': 'Passionnée d\'équitation, expérience avec les grands animaux.'
            },
            {
                'name': 'Nicolas Dupont',
                'age': 38,
                'experience': 'Ancien responsable de refuge, expert en réhabilitation d\'animaux.'
            },
            {
                'name': 'Sarah Leroy',
                'age': 33,
                'experience': 'Spécialiste en nutrition animale, 5 ans d\'expérience en pet-sitting.'
            },
            {
                'name': 'Marc Girard',
                'age': 45,
                'experience': 'Éleveur canin à la retraite, passionné par le bien-être animal.'
            },
            {
                'name': 'Laura Mercier',
                'age': 30,
                'experience': 'Photographe animalière et pet-sitter expérimentée.'
            },
            {
                'name': 'David Roux',
                'age': 36,
                'experience': 'Spécialiste en comportement félin, 8 ans d\'expérience.'
            },
            {
                'name': 'Isabelle Blanc',
                'age': 34,
                'experience': 'Formatrice en école de dressage, experte en éducation canine.'
            }
        ]

        for sitter_data in pet_sitters_data:
            PetSitter.objects.create(**sitter_data)
            self.stdout.write(self.style.SUCCESS(f'Successfully created pet sitter: {sitter_data["name"]}'))