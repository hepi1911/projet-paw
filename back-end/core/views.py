from rest_framework import viewsets, filters, status
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth.hashers import make_password
from django_filters.rest_framework import DjangoFilterBackend
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from datetime import datetime, timedelta
import random
import string

from .models import Animal, Booking, CompanyBooking, PetSitterCompanyBooking, Payment
from .serializers import UserSerializer, AnimalSerializer, BookingSerializer, CompanyBookingSerializer, PetSitterCompanyBookingSerializer, PaymentSerializer

User = get_user_model()

# Fonction d'aide pour envoyer des emails à chaque étape du processus de réservation
def send_booking_status_email(booking, status, booking_type='standard'):
    """
    Envoie un email de notification pour informer les utilisateurs d'un changement de statut de réservation
    
    Args:
        booking: L'objet de réservation (Booking ou CompanyBooking)
        status: Le nouveau statut de la réservation
        booking_type: Le type de réservation ('standard', 'company', ou 'petsitter_company')
    """
    try:
        # Préparer les détails selon le type de réservation
        if booking_type == 'standard':
            # Réservation standard (pet owner -> pet sitter)
            pet_owner = booking.animal.owner
            pet_sitter = booking.sitter
            animal = booking.animal
            start_date = booking.start_date
            end_date = booking.end_date
            
            # Email au propriétaire de l'animal
            owner_subject = f"Mise à jour de votre réservation - {animal.name}"
            owner_message = f"""Bonjour {pet_owner.name},

Le statut de votre réservation pour {animal.name} avec {pet_sitter.name} a été mis à jour.

Nouveau statut: {status}
Dates: {start_date} au {end_date}

"""
            if status == 'pending':
                owner_message += "Votre demande de réservation a été enregistrée et est en attente de confirmation par le pet sitter."
            elif status == 'accepted':
                owner_message += "Votre réservation a été acceptée par le pet sitter. Vous pouvez maintenant procéder au paiement."
            elif status == 'refused':
                owner_message += "Nous sommes désolés, mais votre demande de réservation a été refusée par le pet sitter."
            elif status == 'cancelled':
                owner_message += "Votre réservation a été annulée comme demandé."
            elif status == 'paid':
                owner_message += "Votre paiement a été confirmé. Votre réservation est maintenant finalisée."
            
            owner_message += "\n\nMerci d'utiliser Pet at Work!"
            
            send_mail(
                owner_subject,
                owner_message,
                settings.DEFAULT_FROM_EMAIL,
                [pet_owner.email],
                fail_silently=True,
            )
            
            # Email au pet sitter
            sitter_subject = f"Mise à jour de réservation - {animal.name}"
            sitter_message = f"""Bonjour {pet_sitter.name},

Le statut d'une réservation pour l'animal {animal.name} de {pet_owner.name} a été mis à jour.

Nouveau statut: {status}
Dates: {start_date} au {end_date}

"""
            if status == 'pending':
                sitter_message += "Une nouvelle demande de réservation a été enregistrée. Veuillez l'accepter ou la refuser depuis votre espace personnel."
            elif status == 'accepted':
                sitter_message += "Vous avez accepté cette réservation. Le propriétaire de l'animal a été notifié."
            elif status == 'refused':
                sitter_message += "Vous avez refusé cette réservation. Le propriétaire de l'animal a été notifié."
            elif status == 'cancelled':
                sitter_message += "Cette réservation a été annulée par le propriétaire de l'animal."
            elif status == 'paid':
                sitter_message += "Le paiement pour cette réservation a été confirmé. La réservation est maintenant finalisée."
            
            sitter_message += "\n\nMerci d'utiliser Pet at Work!"
            
            send_mail(
                sitter_subject,
                sitter_message,
                settings.DEFAULT_FROM_EMAIL,
                [pet_sitter.email],
                fail_silently=True,
            )
            
        elif booking_type == 'company':
            # Réservation auprès d'une entreprise (pet owner -> company)
            pet_owner = booking.animal.owner
            company = booking.company
            animal = booking.animal
            start_date = booking.start_date
            end_date = booking.end_date
            
            # Email au propriétaire de l'animal
            owner_subject = f"Mise à jour de votre réservation d'entreprise - {animal.name}"
            owner_message = f"""Bonjour {pet_owner.name},

Le statut de votre réservation pour {animal.name} auprès de {company.name} a été mis à jour.

Nouveau statut: {status}
Dates: {start_date} au {end_date}

"""
            if status == 'pending':
                owner_message += "Votre demande de réservation a été enregistrée et est en attente de confirmation par l'entreprise."
            elif status == 'accepted':
                owner_message += "Votre réservation a été acceptée par l'entreprise. Vous pouvez maintenant procéder au paiement."
            elif status == 'refused':
                owner_message += "Nous sommes désolés, mais votre demande de réservation a été refusée par l'entreprise."
            elif status == 'cancelled':
                owner_message += "Votre réservation a été annulée comme demandé."
            elif status == 'paid':
                owner_message += "Votre paiement a été confirmé. Votre réservation est maintenant finalisée."
            
            owner_message += "\n\nMerci d'utiliser Pet at Work!"
            
            send_mail(
                owner_subject,
                owner_message,
                settings.DEFAULT_FROM_EMAIL,
                [pet_owner.email],
                fail_silently=True,
            )
            
            # Email à l'entreprise
            company_subject = f"Mise à jour de réservation - {animal.name}"
            company_message = f"""Bonjour {company.name},

Le statut d'une réservation pour l'animal {animal.name} de {pet_owner.name} a été mis à jour.

Nouveau statut: {status}
Dates: {start_date} au {end_date}

"""
            if status == 'pending':
                company_message += "Une nouvelle demande de réservation a été enregistrée. Veuillez l'accepter ou la refuser depuis votre espace entreprise."
            elif status == 'accepted':
                company_message += "Vous avez accepté cette réservation. Le propriétaire de l'animal a été notifié."
            elif status == 'refused':
                company_message += "Vous avez refusé cette réservation. Le propriétaire de l'animal a été notifié."
            elif status == 'cancelled':
                company_message += "Cette réservation a été annulée par le propriétaire de l'animal."
            elif status == 'paid':
                company_message += "Le paiement pour cette réservation a été confirmé. La réservation est maintenant finalisée."
            
            company_message += "\n\nMerci d'utiliser Pet at Work!"
            
            send_mail(
                company_subject,
                company_message,
                settings.DEFAULT_FROM_EMAIL,
                [company.email],
                fail_silently=True,
            )
            
        elif booking_type == 'petsitter_company':
            # Réservation pet sitter -> company
            pet_sitter = booking.petsitter
            company = booking.company
            start_date = booking.start_date
            end_date = booking.end_date
            
            # Email au pet sitter
            sitter_subject = f"Mise à jour de votre réservation avec {company.name}"
            sitter_message = f"""Bonjour {pet_sitter.name},

Le statut de votre réservation auprès de {company.name} a été mis à jour.

Nouveau statut: {status}
Dates: {start_date} au {end_date}
Service: {booking.get_service_type_display()}

"""
            if status == 'pending':
                sitter_message += "Votre demande de réservation a été enregistrée et est en attente de confirmation par l'entreprise."
            elif status == 'accepted':
                sitter_message += "Votre réservation a été acceptée par l'entreprise."
            elif status == 'refused':
                sitter_message += "Nous sommes désolés, mais votre demande de réservation a été refusée par l'entreprise."
            elif status == 'cancelled':
                sitter_message += "Votre réservation a été annulée comme demandé."
            elif status == 'finished':
                sitter_message += "Votre réservation est maintenant terminée."
            
            sitter_message += "\n\nMerci d'utiliser Pet at Work!"
            
            send_mail(
                sitter_subject,
                sitter_message,
                settings.DEFAULT_FROM_EMAIL,
                [pet_sitter.email],
                fail_silently=True,
            )
            
            # Email à l'entreprise
            company_subject = f"Mise à jour de réservation avec {pet_sitter.name}"
            company_message = f"""Bonjour {company.name},

Le statut d'une réservation de la part du pet sitter {pet_sitter.name} a été mis à jour.

Nouveau statut: {status}
Dates: {start_date} au {end_date}
Service: {booking.get_service_type_display()}

"""
            if status == 'pending':
                company_message += "Une nouvelle demande de réservation a été enregistrée. Veuillez l'accepter ou la refuser depuis votre espace entreprise."
            elif status == 'accepted':
                company_message += "Vous avez accepté cette réservation. Le pet sitter a été notifié."
            elif status == 'refused':
                company_message += "Vous avez refusé cette réservation. Le pet sitter a été notifié."
            elif status == 'cancelled':
                company_message += "Cette réservation a été annulée par le pet sitter."
            elif status == 'finished':
                company_message += "Cette réservation est maintenant terminée."
            
            company_message += "\n\nMerci d'utiliser Pet at Work!"
            
            send_mail(
                company_subject,
                company_message,
                settings.DEFAULT_FROM_EMAIL,
                [company.email],
                fail_silently=True,
            )
    
    except Exception as e:
        print(f"Erreur lors de l'envoi de l'email de notification: {str(e)}")
        # Ne pas faire échouer l'opération si l'envoi d'email échoue

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['role']

    @action(detail=False, methods=['get'])
    def debug_filter(self, request):
        role = request.query_params.get('role')
        if role:
            queryset = User.objects.filter(role=role)
        else:
            queryset = User.objects.all()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def available_companies(self, request):
        """
        Renvoie uniquement les compagnies qui ne sont pas complètes (capacité disponible)
        """
        # Récupérer toutes les compagnies
        companies = User.objects.filter(role='company')
        
        # Liste pour stocker les compagnies avec de la capacité disponible
        available_companies = []
        
        for company in companies:
            # Vérifier si la compagnie a défini une capacité
            if not company.capacity or company.capacity <= 0:
                continue
                
            # Compter les réservations acceptées actuelles
            accepted_bookings_count = CompanyBooking.objects.filter(
                company=company, 
                status='accepted'
            ).count()
            
            # Vérifier si la compagnie a encore de la capacité disponible
            if accepted_bookings_count < company.capacity:
                available_companies.append(company)
        
        serializer = self.get_serializer(available_companies, many=True)
        return Response(serializer.data)
        
    @action(detail=False, methods=['put'], permission_classes=[IsAuthenticated])
    def profile(self, request):
        user = request.user
        serializer = self.get_serializer(user, data=request.data, partial=True)
        
        if serializer.is_valid():
            if 'new_password' in request.data:
                # Vérifier si la méthode check_password existe sur l'objet user
                if hasattr(user, 'check_password') and callable(getattr(user, 'check_password')):
                    if not user.check_password(request.data.get('current_password', '')):
                        return Response({'error': 'Mot de passe actuel incorrect'}, status=status.HTTP_400_BAD_REQUEST)
                    user.set_password(request.data['new_password'])
                else:
                    return Response({'error': 'Méthode de vérification du mot de passe non disponible'}, 
                                   status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'])
    def password_reset(self, request):
        email = request.data.get('email').lower()
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({'message': 'Si cet email existe, un code de réinitialisation sera envoyé.'})

        reset_code = ''.join(random.choices(string.digits, k=6))
        user.reset_code = reset_code
        user.reset_code_expiry = timezone.now() + timedelta(minutes=15)
        user.save()

        send_mail(
            'Réinitialisation de mot de passe',
            f'Votre code de réinitialisation est : {reset_code}\nCe code expirera dans 15 minutes.',
            settings.DEFAULT_FROM_EMAIL,
            [email],
            fail_silently=False,
        )

        return Response({'message': 'Code de réinitialisation envoyé'})

    @action(detail=False, methods=['post'])
    def verify_reset_code(self, request):
        email = request.data.get('email').lower()
        code = request.data.get('code')

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({'error': 'Code invalide'}, status=status.HTTP_400_BAD_REQUEST)

        if not user.reset_code or user.reset_code != code or user.reset_code_expiry < timezone.now():
            return Response({'error': 'Code invalide ou expiré'}, status=status.HTTP_400_BAD_REQUEST)

        return Response({'message': 'Code validé'})

    @action(detail=False, methods=['post'])
    def reset_password(self, request):
        email = request.data.get('email').lower()
        code = request.data.get('code')
        new_password = request.data.get('new_password')

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({'error': 'Données invalides'}, status=status.HTTP_400_BAD_REQUEST)

        if not user.reset_code or user.reset_code != code or user.reset_code_expiry < timezone.now():
            return Response({'error': 'Code invalide ou expiré'}, status=status.HTTP_400_BAD_REQUEST)

        user.set_password(new_password)
        user.reset_code = None
        user.reset_code_expiry = None
        user.save()

        return Response({'message': 'Mot de passe réinitialisé avec succès'})

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def companies(self, request):
        """
        Permet aux pet sitters de lister toutes les compagnies disponibles
        pour faire des réservations
        """
        user = request.user
        
        # Vérifier que l'utilisateur est un pet sitter
        if user.role != 'petsitter' and not (user.is_staff or user.is_superuser):
            return Response(
                {'error': 'Seuls les pet sitters peuvent accéder à cette ressource'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Récupérer toutes les compagnies
        companies = User.objects.filter(role='company')
        
        serializer = self.get_serializer(companies, many=True)
        return Response(serializer.data)

class AnimalViewSet(viewsets.ModelViewSet):
    queryset = Animal.objects.all()
    serializer_class = AnimalSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['owner']

    def get_queryset(self):
        user = self.request.user
        
        # Les administrateurs peuvent voir tous les animaux
        if user.is_staff or user.is_superuser:
            return Animal.objects.all()
        
        # Les propriétaires d'animaux ne voient que leurs propres animaux
        if user.role == 'petowner':
            return Animal.objects.filter(owner=user)
        
        # Les pet sitters et les compagnies peuvent voir tous les animaux
        # pour faciliter la prise de réservation
        # ou on pourrait restreindre cette vue aux animaux liés à leurs réservations
        return Animal.objects.all()

    def create(self, request, *args, **kwargs):
        """
        Surcharge de la méthode create pour définir automatiquement le propriétaire
        de l'animal comme étant l'utilisateur connecté (si c'est un pet owner)
        """
        user = request.user
        
        # Vérifier que l'utilisateur est un pet owner
        if user.role != 'petowner' and not (user.is_staff or user.is_superuser):
            return Response(
                {'error': 'Seuls les propriétaires d\'animaux peuvent ajouter des animaux'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Ajouter le propriétaire actuel aux données
        data = request.data.copy()
        data['owner'] = user.id
        
        # Créer l'animal avec les données complétées
        serializer = self.get_serializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def my_animals(self, request):
        """
        Renvoie la liste des animaux appartenant à l'utilisateur connecté (pet owner)
        """
        user = request.user
        
        # Vérifier que l'utilisateur est un pet owner
        if user.role != 'petowner':
            return Response(
                {'error': 'Seuls les propriétaires d\'animaux peuvent accéder à cette ressource'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Récupérer tous les animaux du pet owner
        animals = Animal.objects.filter(owner=user)
        
        serializer = self.get_serializer(animals, many=True)
        return Response(serializer.data)

class BookingViewSet(viewsets.ModelViewSet):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['status']

    def get_queryset(self):
        user = self.request.user
        
        # Les administrateurs peuvent tout voir
        if user.is_staff or user.is_superuser:
            return Booking.objects.all()
        
        # Les propriétaires d'animaux voient les réservations de leurs animaux
        if user.role == 'petowner':
            return Booking.objects.filter(animal__owner=user)
        
        # Les pet sitters voient les réservations qui les concernent
        elif user.role == 'petsitter':
            return Booking.objects.filter(sitter=user)
        
        # Par défaut, retourner une queryset vide
        return Booking.objects.none()

    def create(self, request, *args, **kwargs):
        """
        Surcharge de la méthode create pour valider que l'animal appartient bien
        au pet owner qui fait la réservation
        """
        user = request.user
        data = request.data.copy()
        
        # Vérifier que l'utilisateur est un pet owner
        if user.role != 'petowner' and not (user.is_staff or user.is_superuser):
            return Response(
                {'error': 'Seuls les propriétaires d\'animaux peuvent créer des réservations'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Vérifier que l'animal appartient bien au pet owner
        animal_id = data.get('animal')
        if animal_id:
            try:
                animal = Animal.objects.get(id=animal_id)
                if animal.owner.id != user.id and not (user.is_staff or user.is_superuser):
                    return Response(
                        {'error': 'Vous ne pouvez réserver que pour vos propres animaux'}, 
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
                # Récupérer les dates de la nouvelle réservation
                start_date = data.get('start_date')
                end_date = data.get('end_date')
                
                if not start_date or not end_date:
                    return Response(
                        {'error': 'Les dates de début et de fin sont obligatoires'}, 
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
                # Vérifier si l'animal a déjà une réservation active qui chevauche les dates demandées
                from django.db.models import Q
                from datetime import datetime
                
                # Convertir les dates en objets datetime pour la comparaison
                start_date_obj = datetime.strptime(start_date, '%Y-%m-%d').date() if isinstance(start_date, str) else start_date
                end_date_obj = datetime.strptime(end_date, '%Y-%m-%d').date() if isinstance(end_date, str) else end_date
                
                # Vérifier les réservations existantes avec le pet sitter qui chevauchent les dates
                overlapping_bookings = Booking.objects.filter(
                    animal=animal,
                    status__in=['pending', 'accepted', 'paid'],  # Exclure les réservations 'cancelled'
                ).filter(
                    # Critères de chevauchement de dates:
                    # (début1 <= fin2) ET (fin1 >= début2)
                    Q(start_date__lte=end_date_obj) & Q(end_date__gte=start_date_obj)
                )
                
                if overlapping_bookings.exists():
                    return Response(
                        {'error': 'Cet animal a déjà une réservation qui chevauche ces dates. Veuillez choisir d\'autres dates.'}, 
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
                # Vérifier également si l'animal est réservé auprès d'une compagnie sur les mêmes dates
                overlapping_company_bookings = CompanyBooking.objects.filter(
                    animal=animal,
                    status__in=['pending', 'accepted', 'paid'],  # Exclure les réservations 'cancelled'
                ).filter(
                    # Critères de chevauchement de dates:
                    # (début1 <= fin2) ET (fin1 >= début2)
                    Q(start_date__lte=end_date_obj) & Q(end_date__gte=start_date_obj)
                )
                
                if overlapping_company_bookings.exists():
                    return Response(
                        {'error': 'Cet animal a déjà une réservation auprès d\'une compagnie qui chevauche ces dates. Veuillez choisir d\'autres dates.'}, 
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
            except Animal.DoesNotExist:
                return Response(
                    {'error': 'Animal introuvable'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
        else:
            return Response(
                {'error': 'Veuillez spécifier un animal pour la réservation'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Créer la réservation
        serializer = self.get_serializer(data=data)
        if serializer.is_valid():
            serializer.save()
            # Envoyer un email de notification
            send_booking_status_email(serializer.instance, serializer.instance.status)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def my_bookings(self, request):
        """
        Renvoie la liste des réservations pour les animaux du pet owner connecté
        """
        user = request.user
        
        # Vérifier que l'utilisateur est un pet owner
        if user.role != 'petowner':
            return Response(
                {'error': 'Seuls les propriétaires d\'animaux peuvent accéder à cette ressource'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Récupérer toutes les réservations des animaux du pet owner
        bookings = Booking.objects.filter(animal__owner=user)
        
        serializer = self.get_serializer(bookings, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['patch'], permission_classes=[IsAuthenticated])
    def update_status(self, request, pk=None):
        """
        Permet aux pet sitters et aux propriétaires d'animaux de mettre à jour le statut d'une réservation.
        Si c'est le pet owner qui annule, toutes les réservations associées seront également annulées.
        En mode test, les propriétaires d'animaux peuvent également marquer leurs réservations comme 'accepted'
        sans passer par le processus de paiement.
        """
        booking = self.get_object()
        user = request.user
        
        # Vérifier que l'utilisateur est soit le pet sitter concerné, soit le propriétaire de l'animal (mode test)
        is_authorized = (
            (user.role == 'petsitter' and booking.sitter.id == user.id) or
            (user.role == 'petowner' and booking.animal.owner.id == user.id) or
            (user.is_staff or user.is_superuser)
        )
        
        if not is_authorized:
            return Response(
                {'error': 'Vous n\'êtes pas autorisé à modifier cette réservation'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Récupérer le nouveau statut de la requête
        new_status = request.data.get('status')
        
        # Vérifier que le statut est valide
        valid_statuses = [status_tuple[0] for status_tuple in Booking.STATUS_CHOICES]
        if new_status not in valid_statuses:
            return Response(
                {'error': f'Statut invalide. Les statuts valides sont: {", ".join(valid_statuses)}'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Si c'est le pet owner qui met à jour le statut en 'accepted' en mode test, permettre cette action
        is_test_owner_accept = (
            user.role == 'petowner' and 
            booking.animal.owner.id == user.id and 
            new_status == 'accepted'
        )
        
        # Si c'est le pet sitter qui n'a pas accès à certains statuts, bloquer
        if user.role == 'petsitter' and booking.sitter.id == user.id and new_status not in ['accepted', 'refused', 'cancelled']:
            return Response(
                {'error': f'Les pet sitters ne peuvent mettre à jour le statut qu\'en: accepted, refused, cancelled'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Si le pet owner annule une réservation, annuler également toutes les réservations associées
        is_pet_owner_cancelling = (
            user.role == 'petowner' and 
            booking.animal.owner.id == user.id and 
            new_status == 'cancelled'
        )
        
        if is_pet_owner_cancelling:
            # Trouver toutes les réservations pet sitter → compagnie associées
            from .models import PetSitterCompanyBooking
            associated_bookings = PetSitterCompanyBooking.objects.filter(
                petsitter=booking.sitter,
                start_date__gte=booking.start_date,
                end_date__lte=booking.end_date
            )
            
            # Annuler toutes ces réservations associées (changement de statut au lieu de supprimer)
            for assoc_booking in associated_bookings:
                assoc_booking.status = 'cancelled'
                assoc_booking.save()
                
                # Envoyer un email pour chaque réservation associée annulée
                send_booking_status_email(assoc_booking, 'cancelled', booking_type='petsitter_company')
                
                # Log pour le débogage
                print(f"Réservation associée annulée (ID: {assoc_booking.id})")
        
        # Mettre à jour le statut de la réservation (au lieu de supprimer)
        old_status = booking.status
        booking.status = new_status
        booking.save()
        
        # Envoyer l'email de notification de changement de statut
        send_booking_status_email(booking, new_status)
        
        # Message spécifique pour le mode test
        if is_test_owner_accept:
            message = "Réservation acceptée avec succès (mode test - sans paiement)"
        else:
            status_labels = {
                'accepted': 'acceptée',
                'refused': 'refusée', 
                'cancelled': 'annulée',
                'finished': 'terminée',
                'paid': 'payée'
            }
            status_label = status_labels.get(new_status, new_status)
            message = f"Réservation {status_label} avec succès"
        
        # Renvoyer les données mises à jour
        serializer = self.get_serializer(booking)
        return Response({
            'message': message,
            'booking': serializer.data
        })

class CompanyBookingViewSet(viewsets.ModelViewSet):
    queryset = CompanyBooking.objects.all()
    serializer_class = CompanyBookingSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['status']

    def get_queryset(self):
        user = self.request.user
        
        # Les administrateurs peuvent tout voir
        if user.is_staff or user.is_superuser:
            return CompanyBooking.objects.all()
        
        # Les propriétaires d'animaux voient les réservations de leurs animaux
        if user.role == 'petowner':
            return CompanyBooking.objects.filter(animal__owner=user)
        
        # Les compagnies voient les réservations qui les concernent
        elif user.role == 'company':
            return CompanyBooking.objects.filter(company=user)
        
        # Par défaut, retourner une queryset vide
        return CompanyBooking.objects.none()

    def create(self, request, *args, **kwargs):
        """
        Surcharge de la méthode create pour valider que l'animal appartient bien
        au pet owner qui fait la réservation auprès d'une compagnie
        """
        user = request.user
        data = request.data.copy()
        
        # Vérifier que l'utilisateur est un pet owner
        if user.role != 'petowner' and not (user.is_staff or user.is_superuser):
            return Response(
                {'error': 'Seuls les propriétaires d\'animaux peuvent créer des réservations'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Vérifier que l'animal appartient bien au pet owner
        animal_id = data.get('animal')
        if animal_id:
            try:
                animal = Animal.objects.get(id=animal_id)
                if animal.owner.id != user.id and not (user.is_staff or user.is_superuser):
                    return Response(
                        {'error': 'Vous ne pouvez réserver que pour vos propres animaux'}, 
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
                # Récupérer les dates de la nouvelle réservation
                start_date = data.get('start_date')
                end_date = data.get('end_date')
                
                if not start_date or not end_date:
                    return Response(
                        {'error': 'Les dates de début et de fin sont obligatoires'}, 
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
                # Vérifier si l'animal a déjà une réservation active qui chevauche les dates demandées
                from django.db.models import Q
                from datetime import datetime
                
                # Convertir les dates en objets datetime pour la comparaison
                start_date_obj = datetime.strptime(start_date, '%Y-%m-%d').date() if isinstance(start_date, str) else start_date
                end_date_obj = datetime.strptime(end_date, '%Y-%m-%d').date() if isinstance(end_date, str) else end_date
                
                # Vérifier les réservations existantes avec la compagnie qui chevauchent les dates
                overlapping_company_bookings = CompanyBooking.objects.filter(
                    animal=animal,
                    status__in=['pending', 'accepted', 'paid'],  # Exclure les réservations 'cancelled'
                ).filter(
                    # Critères de chevauchement de dates:
                    # (début1 <= fin2) ET (fin1 >= début2)
                    Q(start_date__lte=end_date_obj) & Q(end_date__gte=start_date_obj)
                )
                
                if overlapping_company_bookings.exists():
                    return Response(
                        {'error': 'Cet animal a déjà une réservation auprès d\'une compagnie qui chevauche ces dates. Veuillez choisir d\'autres dates.'}, 
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
                # Vérifier également si l'animal a une réservation chez un pet sitter sur les mêmes dates
                overlapping_bookings = Booking.objects.filter(
                    animal=animal,
                    status__in=['pending', 'accepted', 'paid'],
                ).filter(
                    Q(start_date__lte=end_date_obj) & Q(end_date__gte=start_date_obj)
                )
                
                if overlapping_bookings.exists():
                    return Response(
                        {'error': 'Cet animal a déjà une réservation avec un pet sitter qui chevauche ces dates. Veuillez choisir d\'autres dates.'}, 
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
            except Animal.DoesNotExist:
                return Response(
                    {'error': 'Animal introuvable'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
        else:
            return Response(
                {'error': 'Veuillez spécifier un animal pour la réservation'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Créer la réservation
        serializer = self.get_serializer(data=data)
        if serializer.is_valid():
            serializer.save()
            # Envoyer un email de notification
            send_booking_status_email(serializer.instance, serializer.instance.status, booking_type='company')
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def my_bookings(self, request):
        """
        Renvoie la liste des réservations auprès des compagnies pour les animaux du pet owner connecté
        """
        user = request.user
        
        # Vérifier que l'utilisateur est un pet owner
        if user.role != 'petowner':
            return Response(
                {'error': 'Seuls les propriétaires d\'animaux peuvent accéder à cette ressource'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Récupérer toutes les réservations des animaux du pet owner
        bookings = CompanyBooking.objects.filter(animal__owner=user)
        
        serializer = self.get_serializer(bookings, many=True)
        return Response(serializer.data)

class PetSitterCompanyBookingViewSet(viewsets.ModelViewSet):
    queryset = PetSitterCompanyBooking.objects.all()
    serializer_class = PetSitterCompanyBookingSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['status', 'service_type']

    def get_queryset(self):
        user = self.request.user
        
        # Les administrateurs peuvent tout voir
        if user.is_staff or user.is_superuser:
            return PetSitterCompanyBooking.objects.all()
        
        # Les pet sitters voient les réservations qui les concernent
        if user.role == 'petsitter':
            return PetSitterCompanyBooking.objects.filter(petsitter=user)
        
        # Les compagnies voient les réservations qui les concernent
        elif user.role == 'company':
            return PetSitterCompanyBooking.objects.filter(company=user)
        
        # Par défaut, retourner une queryset vide
        return PetSitterCompanyBooking.objects.none()

    def create(self, request, *args, **kwargs):
        """
        Surcharge de la méthode create pour définir automatiquement le pet sitter
        """
        user = request.user
        
        # Vérifier que l'utilisateur est un pet sitter
        if user.role != 'petsitter':
            return Response(
                {'error': 'Seuls les pet sitters peuvent créer ces réservations'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Ajouter le pet sitter actuel aux données
        data = request.data.copy()
        data['petsitter'] = user.id
        
        # Créer la réservation avec les données complétées
        serializer = self.get_serializer(data=data)
        if serializer.is_valid():
            serializer.save()
            # Envoyer un email de notification
            send_booking_status_email(serializer.instance, serializer.instance.status, booking_type='petsitter_company')
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['patch'], permission_classes=[IsAuthenticated])
    def update_status(self, request, pk=None):
        """
        Permet aux compagnies et aux pet sitters de mettre à jour le statut d'une réservation.
        Les réservations annulées sont conservées avec le statut 'cancelled'.
        """
        booking = self.get_object()
        user = request.user
        
        # Vérifier que l'utilisateur est soit le pet sitter, soit la compagnie concernée
        is_authorized = (
            (user.role == 'petsitter' and booking.petsitter.id == user.id) or
            (user.role == 'company' and booking.company.id == user.id)
        )
        
        if not is_authorized and not (user.is_staff or user.is_superuser):
            return Response(
                {'error': 'Vous n\'êtes pas autorisé à modifier cette réservation'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Récupérer le nouveau statut de la requête
        new_status = request.data.get('status')
        
        # Vérifier que le statut est valide
        valid_statuses = [status_tuple[0] for status_tuple in PetSitterCompanyBooking.STATUS_CHOICES]
        if new_status not in valid_statuses:
            return Response(
                {'error': f'Statut invalide. Les statuts valides sont: {", ".join(valid_statuses)}'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Mettre à jour le statut de la réservation (conserver même si annulée)
        old_status = booking.status
        booking.status = new_status
        booking.save()
        
        # Envoyer email de notification
        send_booking_status_email(booking, new_status, booking_type='petsitter_company')
        
        # Créer un message de retour adapté
        status_labels = {
            'pending': 'en attente',
            'accepted': 'acceptée',
            'refused': 'refusée', 
            'cancelled': 'annulée',
            'finished': 'terminée'
        }
        status_label = status_labels.get(new_status, new_status)
        
        # Renvoyer les données mises à jour
        serializer = self.get_serializer(booking)
        return Response({
            'message': f'La réservation a été {status_label} avec succès',
            'booking': serializer.data
        })

class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['payment_status', 'payment_type']

    def get_queryset(self):
        user = self.request.user
        
        # Les administrateurs peuvent tout voir
        if user.is_staff or user.is_superuser:
            return Payment.objects.all()
        
        # Les propriétaires d'animaux voient leurs paiements
        if user.role == 'petowner':
            return Payment.objects.filter(
                # Paiements liés aux réservations de leurs animaux
                booking__animal__owner=user
            ) | Payment.objects.filter(
                # Paiements liés aux réservations d'entreprise pour leurs animaux
                company_booking__animal__owner=user
            )
        
        # Les pet sitters voient les paiements qui les concernent
        elif user.role == 'petsitter':
            return Payment.objects.filter(booking__sitter=user)
        
        # Les entreprises voient les paiements qui les concernent
        elif user.role == 'company':
            return Payment.objects.filter(company_booking__company=user)
        
        # Par défaut, retourner une queryset vide
        return Payment.objects.none()

    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def process_payment(self, request):
        """
        Traite un nouveau paiement pour une réservation
        """
        user = request.user
        data = request.data.copy()
        
        # Vérifier que l'utilisateur est un pet owner
        if user.role != 'petowner' and not (user.is_staff or user.is_superuser):
            return Response(
                {'error': 'Seuls les propriétaires d\'animaux peuvent effectuer des paiements'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Récupérer les détails de la réservation
        booking_id = data.get('booking')
        company_booking_id = data.get('company_booking')
        
        if not booking_id and not company_booking_id:
            return Response(
                {'error': 'Veuillez spécifier une réservation à payer'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Obtenir le montant à payer et vérifier la propriété de la réservation
            if booking_id:
                booking = Booking.objects.get(id=booking_id)
                
                # Vérifier que l'animal appartient au pet owner
                if booking.animal.owner.id != user.id and not (user.is_staff or user.is_superuser):
                    return Response(
                        {'error': 'Vous ne pouvez payer que pour vos propres réservations'}, 
                        status=status.HTTP_403_FORBIDDEN
                    )
                
                # Calculer le montant total
                amount = booking.total_price
                
                # Vérifier si la réservation est déjà payée
                if booking.status == 'paid':
                    return Response(
                        {'error': 'Cette réservation a déjà été payée'}, 
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
                # Mettre à jour le statut de la réservation une fois le paiement effectué
                booking.status = 'paid'
                booking.save()
                
            elif company_booking_id:
                company_booking = CompanyBooking.objects.get(id=company_booking_id)
                
                # Vérifier que l'animal appartient au pet owner
                if company_booking.animal.owner.id != user.id and not (user.is_staff or user.is_superuser):
                    return Response(
                        {'error': 'Vous ne pouvez payer que pour vos propres réservations'}, 
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
                # Calculer le montant total
                amount = company_booking.total_price
                
                # Vérifier si la réservation est déjà payée
                if company_booking.status == 'paid':
                    return Response(
                        {'error': 'Cette réservation a déjà été payée'}, 
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
                # Mettre à jour le statut de la réservation une fois le paiement effectué
                company_booking.status = 'paid'
                company_booking.save()
                
        except (Booking.DoesNotExist, CompanyBooking.DoesNotExist):
            return Response(
                {'error': 'Réservation introuvable'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Créer le paiement
        payment_data = {
            'booking': booking_id,
            'company_booking': company_booking_id,
            'amount': amount,
            'payment_status': 'completed',  # On suppose que le paiement est réussi immédiatement pour cet exemple
            'payment_type': data.get('payment_type', 'card'),
            'transaction_id': f"TR-{timezone.now().strftime('%Y%m%d%H%M%S')}-{random.randint(1000, 9999)}"
        }
        
        serializer = self.get_serializer(data=payment_data)
        if serializer.is_valid():
            payment = serializer.save()
            
            # Envoyer un email de confirmation de paiement
            if booking_id:
                subject = f"Confirmation de paiement - Réservation #{booking_id}"
                message = f"Bonjour {user.name},\n\nVotre paiement de {amount}€ pour la réservation de {booking.animal.name} avec {booking.sitter.name} a été accepté.\n\nIdentifiant de transaction: {payment.transaction_id}\n\nMerci d'utiliser Pet at Work!"
            else:
                subject = f"Confirmation de paiement - Réservation d'entreprise #{company_booking_id}"
                message = f"Bonjour {user.name},\n\nVotre paiement de {amount}€ pour la réservation de {company_booking.animal.name} auprès de {company_booking.company.name} a été accepté.\n\nIdentifiant de transaction: {payment.transaction_id}\n\nMerci d'utiliser Pet at Work!"
            
            try:
                send_mail(
                    subject,
                    message,
                    settings.DEFAULT_FROM_EMAIL,
                    [user.email],
                    fail_silently=True,
                )
            except Exception as e:
                print(f"Erreur lors de l'envoi de l'email de confirmation: {str(e)}")
            
            return Response({
                'message': 'Paiement effectué avec succès',
                'payment': serializer.data
            }, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def my_payments(self, request):
        """
        Renvoie la liste des paiements effectués par l'utilisateur
        """
        user = request.user
        
        # Vérifier que l'utilisateur est un pet owner
        if user.role != 'petowner':
            return Response(
                {'error': 'Seuls les propriétaires d\'animaux peuvent accéder à cette ressource'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Récupérer tous les paiements de l'utilisateur
        payments = Payment.objects.filter(
            booking__animal__owner=user
        ) | Payment.objects.filter(
            company_booking__animal__owner=user
        )
        
        serializer = self.get_serializer(payments, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def refund(self, request, pk=None):
        """
        Permet aux administrateurs de rembourser un paiement
        """
        user = request.user
        payment = self.get_object()
        
        # Vérifier que l'utilisateur est un administrateur
        if not (user.is_staff or user.is_superuser):
            return Response(
                {'error': 'Seuls les administrateurs peuvent effectuer des remboursements'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Vérifier que le paiement peut être remboursé
        if payment.payment_status != 'completed':
            return Response(
                {'error': 'Seuls les paiements complétés peuvent être remboursés'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Mettre à jour le statut du paiement
        payment.payment_status = 'refunded'
        payment.save()
        
        # Mettre à jour la réservation associée
        if payment.booking:
            booking = payment.booking
            booking.status = 'cancelled'
            booking.save()
        elif payment.company_booking:
            company_booking = payment.company_booking
            company_booking.status = 'cancelled'
            company_booking.save()
        
        # Envoyer un email de confirmation de remboursement
        try:
            owner_email = payment.booking.animal.owner.email if payment.booking else payment.company_booking.animal.owner.email
            owner_name = payment.booking.animal.owner.name if payment.booking else payment.company_booking.animal.owner.name
            
            subject = "Confirmation de remboursement"
            message = f"Bonjour {owner_name},\n\nVotre paiement de {payment.amount}€ a été remboursé.\n\nIdentifiant de transaction: {payment.transaction_id}\n\nMerci d'utiliser Pet at Work!"
            
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [owner_email],
                fail_silently=True,
            )
        except Exception as e:
            print(f"Erreur lors de l'envoi de l'email de remboursement: {str(e)}")
        
        serializer = self.get_serializer(payment)
        return Response({
            'message': 'Remboursement effectué avec succès',
            'payment': serializer.data
        })

@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    from rest_framework_simplejwt.tokens import RefreshToken
    from django.contrib.auth import authenticate
    import logging

    logger = logging.getLogger(__name__)
    
    email = request.data.get('email')
    password = request.data.get('password')
    
    # Logs détaillés pour le débogage
    logger.info(f"Tentative de connexion pour l'email: {email}")
    print(f"Tentative de connexion pour l'email: {email}")

    if not email or not password:
        logger.warning("Échec de connexion: Email ou mot de passe manquant")
        print("Échec de connexion: Email ou mot de passe manquant")
        return Response({'error': 'Email et mot de passe requis'}, status=status.HTTP_400_BAD_REQUEST)

    # Convertir email en minuscules pour éviter les problèmes de casse
    email_lower = email.lower()
    
    # Vérifier si l'utilisateur existe
    try:
        # affiche la liste des utilisateurs pour le débogage
        all_users = User.objects.all()
        logger.debug(f"Liste des utilisateurs: {[user.email for user in all_users]}")
        print(f"Liste des utilisateurs: {[user.email for user in all_users]}")

        # Vérifier si l'utilisateur existe dans la base de données
        user_exists = User.objects.filter(email=email_lower).exists()
        if not user_exists:
            logger.warning(f"Échec de connexion: Aucun utilisateur trouvé avec l'email {email_lower}")
            print(f"Échec de connexion: Aucun utilisateur trouvé avec l'email {email_lower}")
            return Response({'error': 'Identifiants incorrects. Veuillez vérifier votre email et mot de passe.'}, 
                          status=status.HTTP_401_UNAUTHORIZED)
    except Exception as e:
        logger.error(f"Erreur lors de la vérification de l'utilisateur: {str(e)}")
        print(f"Erreur lors de la vérification de l'utilisateur: {str(e)}")

    # Tentative d'authentification
    user = authenticate(request, email=email_lower, password=password)
    
    if user is not None:
        logger.info(f"Connexion réussie pour l'utilisateur: {user.email}")
        print(f"Connexion réussie pour l'utilisateur: {user.email}")
        
        # Vérifier explicitement le statut admin
        is_admin = user.is_staff or user.is_superuser
        
        refresh = RefreshToken.for_user(user)
        return Response({
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'user_id': user.id,
            'email': user.email,
            'name': user.name,
            'role': user.role,
            'is_staff': user.is_staff,
            'is_superuser': user.is_superuser,
            'is_admin': is_admin,  # Ajout d'un champ explicite pour faciliter la vérification côté frontend
            'admin_status': {      # Informations détaillées sur le statut admin pour le débogage
                'is_staff': user.is_staff,
                'is_superuser': user.is_superuser,
                'permissions': list(user.get_all_permissions())
            }
        })
    else:
        logger.warning(f"Échec d'authentification pour l'email: {email_lower}")
        print(f"Échec d'authentification pour l'email: {email_lower}")
        
        # Message plus détaillé pour aider au débogage
        return Response({'error': 'Identifiants incorrects. Veuillez vérifier votre email et mot de passe.'}, 
                       status=status.HTTP_401_UNAUTHORIZED)

@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    data = request.data.copy()
    data['email'] = data.get('email', '').lower()
    # Ne pas hasher le mot de passe ici, le serializer s'en occupera
    
    serializer = UserSerializer(data=data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_profile(request):
    user = request.user
    data = request.data

    if 'email' in data:
        user.email = data['email'].lower()
    if 'first_name' in data:
        user.first_name = data['first_name']
    if 'last_name' in data:
        user.last_name = data['last_name']

    user.save()
    return Response({'message': 'Profile updated successfully'})

@api_view(['GET'])
@permission_classes([AllowAny])
def test_auth(request):
    """
    Vue de diagnostic pour tester l'authentification.
    Accessible via /api/test-auth/?email=user@example.com&password=yourpassword
    """
    from django.contrib.auth import authenticate
    
    email = request.query_params.get('email')
    password = request.query_params.get('password')
    
    print(f"Test d'authentification pour l'email: {email}")
    
    if not email or not password:
        return Response({'error': 'Email et mot de passe requis'}, status=status.HTTP_400_BAD_REQUEST)
    
    # Vérifier si l'utilisateur existe
    try:
        user_exists = User.objects.filter(email=email.lower()).exists()
        if not user_exists:
            print(f"Test auth: Aucun utilisateur trouvé avec l'email {email.lower()}")
            return Response({
                'error': 'Utilisateur non trouvé',
                'email_tested': email.lower(),
                'user_exists': False
            }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        print(f"Test auth: Erreur lors de la vérification de l'utilisateur: {str(e)}")
    
    # Tentative d'authentification
    user = authenticate(request, email=email.lower(), password=password)
    
    if user is not None:
        print(f"Test auth: Authentification réussie pour {email.lower()}")
        return Response({
            'success': True,
            'message': 'Authentification réussie',
            'user_id': user.id,
            'email': user.email,
            'name': user.name,
            'role': user.role
        })
    else:
        # Tenter de récupérer l'utilisateur pour comparer manuellement les mots de passe
        try:
            user = User.objects.get(email=email.lower())
            print(f"Test auth: Utilisateur trouvé, mais échec d'authentification pour {email.lower()}")
            return Response({
                'error': 'Mot de passe incorrect',
                'user_exists': True,
                'email_tested': email.lower(),
                'auth_result': 'Échec de l\'authentification avec le mot de passe fourni'
            }, status=status.HTTP_401_UNAUTHORIZED)
        except User.DoesNotExist:
            print(f"Test auth: Utilisateur non trouvé (double vérification) pour {email.lower()}")
            return Response({
                'error': 'Utilisateur introuvable',
                'user_exists': False,
                'email_tested': email.lower()
            }, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
@permission_classes([AllowAny])
def list_users_test(request):
    """
    Vue de test pour lister tous les utilisateurs.
    Cette API est en mode AllowAny pour faciliter les tests.
    En production, vous devriez restreindre l'accès.
    """
    try:
        users = User.objects.all()
        # Limit to 20 users for performance
        users = users[:20]
        
        # Créer une liste simplifiée des données utilisateur
        user_data = []
        for user in users:
            # Récupérer le mot de passe haché pour le débogage
            # ATTENTION: Ceci est uniquement pour le débogage et ne devrait jamais
            # être fait en production!
            user_data.append({
                'id': user.id,
                'email': user.email,
                'name': user.name,
                'role': user.role,
                'is_staff': user.is_staff,
                'is_superuser': user.is_superuser,
                'password_hash': user.password  # Le mot de passe haché pour le débogage
            })
        
        print(f"Liste de {len(user_data)} utilisateurs récupérée avec succès")
        return Response({
            'success': True,
            'count': len(user_data),
            'users': user_data
        })
    except Exception as e:
        print(f"Erreur lors de la récupération des utilisateurs: {str(e)}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
