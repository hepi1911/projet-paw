from django.core.management.base import BaseCommand
from core.models import Company
import random

class Command(BaseCommand):
    help = 'Creates 15 test companies'

    def handle(self, *args, **kwargs):
        companies_data = [
            {
                'name': 'PawCare Enterprise',
                'capacity': random.randint(1, 10),
                'referent': 'Dr. Marie Lambert'
            },
            {
                'name': 'Animal Haven Corp',
                'capacity': random.randint(1, 10),
                'referent': 'Thomas Dubois'
            },
            {
                'name': 'PetLux Services',
                'capacity': random.randint(1, 10),
                'referent': 'Sophie Bernard'
            },
            {
                'name': 'Happy Tails Inc',
                'capacity': random.randint(1, 10),
                'referent': 'Lucas Martin'
            },
            {
                'name': 'FurFriends Solutions',
                'capacity': random.randint(1, 10),
                'referent': 'Emma Rousseau'
            },
            {
                'name': 'PetPro Services',
                'capacity': random.randint(1, 10),
                'referent': 'Pierre Dupont'
            },
            {
                'name': 'Pawsome Care',
                'capacity': random.randint(1, 10),
                'referent': 'Claire Moreau'
            },
            {
                'name': 'Animal Experts SA',
                'capacity': random.randint(1, 10),
                'referent': 'Jean-Marc Leroy'
            },
            {
                'name': 'Pet Paradise Plus',
                'capacity': random.randint(1, 10),
                'referent': 'Sarah Petit'
            },
            {
                'name': 'VetCare Solutions',
                'capacity': random.randint(1, 10),
                'referent': 'Michel Durand'
            },
            {
                'name': 'CompaniPet Services',
                'capacity': random.randint(1, 10),
                'referent': 'Julie Roux'
            },
            {
                'name': 'PetGuard Elite',
                'capacity': random.randint(1, 10),
                'referent': 'Antoine Blanc'
            },
            {
                'name': 'AnimalCare Pro',
                'capacity': random.randint(1, 10),
                'referent': 'Isabelle Simon'
            },
            {
                'name': 'PetFirst Enterprise',
                'capacity': random.randint(1, 10),
                'referent': 'Nicolas Garcia'
            },
            {
                'name': 'FureverCare Corp',
                'capacity': random.randint(1, 10),
                'referent': 'Marie-Claire Lefebvre'
            }
        ]

        for company_data in companies_data:
            Company.objects.create(**company_data)
            self.stdout.write(self.style.SUCCESS(f'Successfully created company: {company_data["name"]} (Capacity: {company_data["capacity"]})'))