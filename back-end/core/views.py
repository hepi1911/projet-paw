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
import logging
import sys

from .models import Animal, Booking, CompanyBooking, PetSitterCompanyBooking, Payment
from .serializers import UserSerializer, AnimalSerializer, BookingSerializer, CompanyBookingSerializer, PetSitterCompanyBookingSerializer, PaymentSerializer

User = get_user_model()

# Helper function to send emails at each step of the booking process
def send_booking_status_email(booking, status, booking_type='standard'):
    """
    Sends a notification email to inform users about a change in booking status.
    
    Args:
        booking: The booking object (Booking, CompanyBooking or PetSitterCompanyBooking)
        status: The new status of the booking
        booking_type: The type of booking ('standard', 'company', or 'petsitter_company')
    """
    try:
        # Prepare details based on booking type
        if booking_type == 'standard':
            # Standard booking (pet owner -> pet sitter)
            pet_owner = booking.animal.owner
            pet_sitter = booking.sitter
            animal = booking.animal
            start_date = booking.start_date
            end_date = booking.end_date
            
            # Email to pet owner
            owner_subject = f"Booking update - {animal.name}"
            owner_message = f"""Hello {pet_owner.name},

The status of your booking for {animal.name} with {pet_sitter.name} has been updated.

New status: {status}
Dates: {start_date} to {end_date}

"""
            if status == 'pending':
                owner_message += "Your booking request has been registered and is awaiting confirmation from the pet sitter."
            elif status == 'accepted':
                owner_message += "Your booking has been accepted by the pet sitter. You can now proceed to payment."
            elif status == 'refused':
                owner_message += "We're sorry, but your booking request has been declined by the pet sitter."
            elif status == 'cancelled':
                owner_message += "Your booking has been cancelled as requested."
            elif status == 'paid':
                owner_message += "Your payment has been confirmed. Your booking is now finalized."
            
            owner_message += "\n\nThank you for using Pet at Work!"
            
            send_mail(
                owner_subject,
                owner_message,
                settings.DEFAULT_FROM_EMAIL,
                [pet_owner.email],
                fail_silently=True,
            )
            
            # Email to pet sitter
            sitter_subject = f"Booking update - {animal.name}"
            sitter_message = f"""Hello {pet_sitter.name},

The status of a booking for the pet {animal.name} from {pet_owner.name} has been updated.

New status: {status}
Dates: {start_date} to {end_date}

"""
            if status == 'pending':
                sitter_message += "A new booking request has been registered. Please accept or decline it from your personal area."
            elif status == 'accepted':
                sitter_message += "You have accepted this booking. The pet owner has been notified."
            elif status == 'refused':
                sitter_message += "You have declined this booking. The pet owner has been notified."
            elif status == 'cancelled':
                sitter_message += "This booking has been cancelled by the pet owner."
            elif status == 'paid':
                sitter_message += "Payment for this booking has been confirmed. The booking is now finalized."
            
            sitter_message += "\n\nThank you for using Pet at Work!"
            
            send_mail(
                sitter_subject,
                sitter_message,
                settings.DEFAULT_FROM_EMAIL,
                [pet_sitter.email],
                fail_silently=True,
            )
            
        elif booking_type == 'company':
            # Company booking (pet owner -> company)
            pet_owner = booking.animal.owner
            company = booking.company
            animal = booking.animal
            start_date = booking.start_date
            end_date = booking.end_date
            
            # Email to pet owner
            owner_subject = f"Company booking update - {animal.name}"
            owner_message = f"""Hello {pet_owner.name},

The status of your booking for {animal.name} with {company.name} has been updated.

New status: {status}
Dates: {start_date} to {end_date}

"""
            if status == 'pending':
                owner_message += "Your booking request has been registered and is awaiting confirmation from the company."
            elif status == 'accepted':
                owner_message += "Your booking has been accepted by the company. You can now proceed to payment."
            elif status == 'refused':
                owner_message += "We're sorry, but your booking request has been declined by the company."
            elif status == 'cancelled':
                owner_message += "Your booking has been cancelled as requested."
            elif status == 'paid':
                owner_message += "Your payment has been confirmed. Your booking is now finalized."
            
            owner_message += "\n\nThank you for using Pet at Work!"
            
            send_mail(
                owner_subject,
                owner_message,
                settings.DEFAULT_FROM_EMAIL,
                [pet_owner.email],
                fail_silently=True,
            )
            
            # Email to company
            company_subject = f"Booking update - {animal.name}"
            company_message = f"""Hello {company.name},

The status of a booking for the pet {animal.name} from {pet_owner.name} has been updated.

New status: {status}
Dates: {start_date} to {end_date}

"""
            if status == 'pending':
                company_message += "A new booking request has been registered. Please accept or decline it from your company dashboard."
            elif status == 'accepted':
                company_message += "You have accepted this booking. The pet owner has been notified."
            elif status == 'refused':
                company_message += "You have declined this booking. The pet owner has been notified."
            elif status == 'cancelled':
                company_message += "This booking has been cancelled by the pet owner."
            elif status == 'paid':
                company_message += "Payment for this booking has been confirmed. The booking is now finalized."
            
            company_message += "\n\nThank you for using Pet at Work!"
            
            send_mail(
                company_subject,
                company_message,
                settings.DEFAULT_FROM_EMAIL,
                [company.email],
                fail_silently=True,
            )
            
        elif booking_type == 'petsitter_company':
            # Pet sitter -> company booking
            pet_sitter = booking.petsitter
            company = booking.company
            start_date = booking.start_date
            end_date = booking.end_date
            
            # Email to pet sitter
            sitter_subject = f"Booking update with {company.name}"
            sitter_message = f"""Hello {pet_sitter.name},

The status of your booking with {company.name} has been updated.

New status: {status}
Dates: {start_date} to {end_date}
Service: {booking.get_service_type_display()}

"""
            if status == 'pending':
                sitter_message += "Your booking request has been registered and is awaiting confirmation from the company."
            elif status == 'accepted':
                sitter_message += "Your booking has been accepted by the company."
            elif status == 'refused':
                sitter_message += "We're sorry, but your booking request has been declined by the company."
            elif status == 'cancelled':
                sitter_message += "Your booking has been cancelled as requested."
            elif status == 'finished':
                sitter_message += "Your booking is now completed."
            
            sitter_message += "\n\nThank you for using Pet at Work!"
            
            send_mail(
                sitter_subject,
                sitter_message,
                settings.DEFAULT_FROM_EMAIL,
                [pet_sitter.email],
                fail_silently=True,
            )
            
            # Email to company
            company_subject = f"Booking update with {pet_sitter.name}"
            company_message = f"""Hello {company.name},

The status of a booking from pet sitter {pet_sitter.name} has been updated.

New status: {status}
Dates: {start_date} to {end_date}
Service: {booking.get_service_type_display()}

"""
            if status == 'pending':
                company_message += "A new booking request has been registered. Please accept or decline it from your company dashboard."
            elif status == 'accepted':
                company_message += "You have accepted this booking. The pet sitter has been notified."
            elif status == 'refused':
                company_message += "You have declined this booking. The pet sitter has been notified."
            elif status == 'cancelled':
                company_message += "This booking has been cancelled by the pet sitter."
            elif status == 'finished':
                company_message += "This booking is now completed."
            
            company_message += "\n\nThank you for using Pet at Work!"
            
            send_mail(
                company_subject,
                company_message,
                settings.DEFAULT_FROM_EMAIL,
                [company.email],
                fail_silently=True,
            )
    
    except Exception as e:
        print(f"Error sending notification email: {str(e)}")
        # Don't fail the operation if email sending fails

class UserViewSet(viewsets.ModelViewSet):
    """
    ViewSet to manage users (creation, modification, deletion).
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['role']

    @action(detail=False, methods=['get'])
    def debug_filter(self, request):
        """
        Debug method to filter users by role.
        """
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
        Returns only companies that are not full (available capacity).
        """
        # Get all companies
        companies = User.objects.filter(role='company')
        
        # List to store companies with available capacity
        available_companies = []
        
        for company in companies:
            # Check if the company has defined a capacity
            if not company.capacity or company.capacity <= 0:
                continue
                
            # Count current accepted bookings
            accepted_bookings_count = CompanyBooking.objects.filter(
                company=company, 
                status='accepted'
            ).count()
            
            # Check if the company still has available capacity
            if accepted_bookings_count < company.capacity:
                available_companies.append(company)
        
        serializer = self.get_serializer(available_companies, many=True)
        return Response(serializer.data)
        
    @action(detail=False, methods=['put'], permission_classes=[IsAuthenticated])
    def profile(self, request):
        """
        Allows the logged-in user to update their profile, including password.
        """
        user = request.user
        serializer = self.get_serializer(user, data=request.data, partial=True)
        
        if serializer.is_valid():
            if 'new_password' in request.data:
                # Check if the check_password method exists on the user object
                if hasattr(user, 'check_password') and callable(getattr(user, 'check_password')):
                    if not user.check_password(request.data.get('current_password', '')):
                        return Response({'error': 'Incorrect current password'}, status=status.HTTP_400_BAD_REQUEST)
                    user.set_password(request.data['new_password'])
                else:
                    return Response({'error': 'Password verification method not available'}, 
                                   status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'])
    def password_reset(self, request):
        """
        Initiates the password reset process by sending a code to the user.
        """
        email = request.data.get('email').lower()
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({'message': 'If this email exists, a reset code will be sent.'})

        reset_code = ''.join(random.choices(string.digits, k=6))
        user.reset_code = reset_code
        user.reset_code_expiry = timezone.now() + timedelta(minutes=15)
        user.save()

        send_mail(
            'Password Reset',
            f'Your reset code is: {reset_code}\nThis code will expire in 15 minutes.',
            settings.DEFAULT_FROM_EMAIL,
            [email],
            fail_silently=False,
        )

        return Response({'message': 'Reset code sent'})

    @action(detail=False, methods=['post'])
    def verify_reset_code(self, request):
        """
        Verifies the validity of the password reset code.
        """
        email = request.data.get('email').lower()
        code = request.data.get('code')

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({'error': 'Invalid code'}, status=status.HTTP_400_BAD_REQUEST)

        if not user.reset_code or user.reset_code != code or user.reset_code_expiry < timezone.now():
            return Response({'error': 'Invalid or expired code'}, status=status.HTTP_400_BAD_REQUEST)

        return Response({'message': 'Code validated'})

    @action(detail=False, methods=['post'])
    def reset_password(self, request):
        """
        Resets the password after validating the reset code.
        """
        email = request.data.get('email').lower()
        code = request.data.get('code')
        new_password = request.data.get('new_password')

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({'error': 'Invalid data'}, status=status.HTTP_400_BAD_REQUEST)

        if not user.reset_code or user.reset_code != code or user.reset_code_expiry < timezone.now():
            return Response({'error': 'Invalid or expired code'}, status=status.HTTP_400_BAD_REQUEST)

        user.set_password(new_password)
        user.reset_code = None
        user.reset_code_expiry = None
        user.save()

        return Response({'message': 'Password reset successful'})

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def companies(self, request):
        """
        Allows pet sitters to list all available companies to make bookings.
        """
        user = request.user
        
        # Check that the user is a pet sitter
        if user.role != 'petsitter' and not (user.is_staff or user.is_superuser):
            return Response(
                {'error': 'Only pet sitters can access this resource'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Get all companies
        companies = User.objects.filter(role='company')
        
        serializer = self.get_serializer(companies, many=True)
        return Response(serializer.data)

class AnimalViewSet(viewsets.ModelViewSet):
    """
    ViewSet to manage pets (creation, modification, deletion).
    """
    queryset = Animal.objects.all()
    serializer_class = AnimalSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['owner']

    def get_queryset(self):
        """
        Limits visible animals based on user role.
        """
        user = self.request.user
        
        # Administrators can see all animals
        if user.is_staff or user.is_superuser:
            return Animal.objects.all()
        
        # Pet owners can only see their own animals
        if user.role == 'petowner':
            return Animal.objects.filter(owner=user)
        
        # Pet sitters and companies can see all animals
        # to facilitate booking management
        return Animal.objects.all()

    def create(self, request, *args, **kwargs):
        """
        Creates a new animal and automatically assigns it to the logged-in owner.
        """
        user = request.user
        
        # Check that the user is a pet owner
        if user.role != 'petowner' and not (user.is_staff or user.is_superuser):
            return Response(
                {'error': 'Only pet owners can add animals'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Add the current owner to the data
        data = request.data.copy()
        data['owner'] = user.id
        
        # Create the animal with the completed data
        serializer = self.get_serializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def my_animals(self, request):
        """
        Returns the list of animals belonging to the logged-in owner.
        """
        user = request.user
        
        # Check that the user is a pet owner
        if user.role != 'petowner':
            return Response(
                {'error': 'Only pet owners can access this resource'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Get all animals of the pet owner
        animals = Animal.objects.filter(owner=user)
        
        serializer = self.get_serializer(animals, many=True)
        return Response(serializer.data)

class BookingViewSet(viewsets.ModelViewSet):
    """
    ViewSet to manage bookings between pet owners and pet sitters.
    """
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['status']

    def get_queryset(self):
        """
        Filters bookings based on the user's role.
        """
        user = self.request.user
        
        # Administrators can see all bookings
        if user.is_staff or user.is_superuser:
            return Booking.objects.all()
        
        # Pet owners can see bookings for their animals
        if user.role == 'petowner':
            return Booking.objects.filter(animal__owner=user)
        
        # Pet sitters can see bookings that concern them
        elif user.role == 'petsitter':
            return Booking.objects.filter(sitter=user)
        
        # By default, return an empty queryset
        return Booking.objects.none()

    def create(self, request, *args, **kwargs):
        """
        Override create method to validate that the animal belongs to the pet owner making the booking.
        """
        user = request.user
        data = request.data.copy()
        
        # Check that the user is a pet owner
        if user.role != 'petowner' and not (user.is_staff or user.is_superuser):
            return Response(
                {'error': 'Only pet owners can create bookings'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Verify that the animal belongs to the pet owner
        animal_id = data.get('animal')
        if animal_id:
            try:
                animal = Animal.objects.get(id=animal_id)
                if animal.owner.id != user.id and not (user.is_staff or user.is_superuser):
                    return Response(
                        {'error': 'You can only book for your own animals'}, 
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
                # Get the dates for the new booking
                start_date = data.get('start_date')
                end_date = data.get('end_date')
                
                if not start_date or not end_date:
                    return Response(
                        {'error': 'Start and end dates are required'}, 
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
                # Check if the animal already has an active booking that overlaps with the requested dates
                from django.db.models import Q
                from datetime import datetime
                
                # Convert dates to datetime objects for comparison
                start_date_obj = datetime.strptime(start_date, '%Y-%m-%d').date() if isinstance(start_date, str) else start_date
                end_date_obj = datetime.strptime(end_date, '%Y-%m-%d').date() if isinstance(end_date, str) else end_date
                
                # Check existing bookings with pet sitters that overlap with the dates
                overlapping_bookings = Booking.objects.filter(
                    animal=animal,
                    status__in=['pending', 'accepted', 'paid'],  # Exclude 'cancelled' bookings
                ).filter(
                    # Date overlap criteria:
                    # (start1 <= end2) AND (end1 >= start2)
                    Q(start_date__lte=end_date_obj) & Q(end_date__gte=start_date_obj)
                )
                
                if overlapping_bookings.exists():
                    return Response(
                        {'error': 'This animal already has a booking that overlaps with these dates. Please choose other dates.'}, 
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
                # Also check if the animal is booked with a company on the same dates
                overlapping_company_bookings = CompanyBooking.objects.filter(
                    animal=animal,
                    status__in=['pending', 'accepted', 'paid'],  # Exclude 'cancelled' bookings
                ).filter(
                    # Date overlap criteria:
                    # (start1 <= end2) AND (end1 >= start2)
                    Q(start_date__lte=end_date_obj) & Q(end_date__gte=start_date_obj)
                )
                
                if overlapping_company_bookings.exists():
                    return Response(
                        {'error': 'This animal already has a company booking that overlaps with these dates. Please choose other dates.'}, 
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
            except Animal.DoesNotExist:
                return Response(
                    {'error': 'Animal not found'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
        else:
            return Response(
                {'error': 'Please specify an animal for the booking'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create the booking
        serializer = self.get_serializer(data=data)
        if serializer.is_valid():
            serializer.save()
            # Send notification email
            send_booking_status_email(serializer.instance, serializer.instance.status)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def my_bookings(self, request):
        """
        Returns the list of bookings for the connected pet owner's animals.
        """
        user = request.user
        
        # Check that the user is a pet owner
        if user.role != 'petowner':
            return Response(
                {'error': 'Only pet owners can access this resource'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Get all bookings for the pet owner's animals
        bookings = Booking.objects.filter(animal__owner=user)
        
        serializer = self.get_serializer(bookings, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['patch'], permission_classes=[IsAuthenticated])
    def update_status(self, request, pk=None):
        """
        Allows pet sitters and pet owners to update a booking's status.
        - Pet sitters can accept or decline a booking (status 'accepted' or 'refused')
        - Pet owners can cancel their bookings (status 'cancelled')
        - Administrators can modify any status
        """
        booking = self.get_object()
        user = request.user
        
        # Verify that the user is either the pet sitter or the animal owner
        is_authorized = (
            (user.role == 'petsitter' and booking.sitter.id == user.id) or
            (user.role == 'petowner' and booking.animal.owner.id == user.id) or
            (user.is_staff or user.is_superuser)
        )
        
        if not is_authorized:
            return Response(
                {'error': 'You are not authorized to modify this booking'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Get the new status from the request
        new_status = request.data.get('status')
        
        # Check that the status is valid
        valid_statuses = [status_tuple[0] for status_tuple in Booking.STATUS_CHOICES]
        if new_status not in valid_statuses:
            return Response(
                {'error': f'Invalid status. Valid statuses are: {", ".join(valid_statuses)}'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check permissions based on the user's role
        if user.role == 'petsitter' and booking.sitter.id == user.id:
            # Pet sitters can only accept or decline
            if new_status not in ['accepted', 'refused']:
                return Response(
                    {'error': 'Pet sitters can only change the status to "accepted" or "refused"'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
        elif user.role == 'petowner' and booking.animal.owner.id == user.id:
            # Pet owners can only cancel
            if new_status != 'cancelled':
                return Response(
                    {'error': 'Pet owners can only cancel their bookings'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
        # If a pet owner cancels a booking, also cancel all associated bookings
        is_pet_owner_cancelling = (
            user.role == 'petowner' and 
            booking.animal.owner.id == user.id and 
            new_status == 'cancelled'
        )
        
        if is_pet_owner_cancelling:
            # Find all pet sitter → company bookings associated
            from .models import PetSitterCompanyBooking
            associated_bookings = PetSitterCompanyBooking.objects.filter(
                petsitter=booking.sitter,
                start_date__gte=booking.start_date,
                end_date__lte=booking.end_date
            )
            
            # Cancel all these associated bookings
            for assoc_booking in associated_bookings:
                assoc_booking.status = 'cancelled'
                assoc_booking.save()
                
                # Send an email for each cancelled associated booking
                send_booking_status_email(assoc_booking, 'cancelled', booking_type='petsitter_company')
                
                # Debug log
                print(f"Associated booking cancelled (ID: {assoc_booking.id})")
        
        # Update the booking status
        old_status = booking.status
        booking.status = new_status
        booking.save()
        
        # Send status change notification email
        send_booking_status_email(booking, new_status)
        
        # Prepare an appropriate response message
        status_labels = {
            'accepted': 'accepted',
            'refused': 'declined', 
            'cancelled': 'cancelled',
            'paid': 'paid'
        }
        status_label = status_labels.get(new_status, new_status)
        message = f"Booking successfully {status_label}"
        
        # Return the updated data
        serializer = self.get_serializer(booking)
        return Response({
            'message': message,
            'booking': serializer.data
        })

class CompanyBookingViewSet(viewsets.ModelViewSet):
    """
    ViewSet to manage bookings between pet owners and companies.
    """
    queryset = CompanyBooking.objects.all()
    serializer_class = CompanyBookingSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['status']

    def get_queryset(self):
        """
        Filters bookings based on the user's role.
        """
        user = self.request.user
        
        # Administrators can see all bookings
        if user.is_staff or user.is_superuser:
            return CompanyBooking.objects.all()
        
        # Pet owners can see bookings for their animals
        if user.role == 'petowner':
            return CompanyBooking.objects.filter(animal__owner=user)
        
        # Companies can see bookings that concern them
        elif user.role == 'company':
            return CompanyBooking.objects.filter(company=user)
        
        # By default, return an empty queryset
        return CompanyBooking.objects.none()

    def create(self, request, *args, **kwargs):
        """
        Override create method to validate that the animal belongs to the pet owner making the booking with a company.
        """
        user = request.user
        data = request.data.copy()
        
        # Check that the user is a pet owner
        if user.role != 'petowner' and not (user.is_staff or user.is_superuser):
            return Response(
                {'error': 'Only pet owners can create bookings'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Verify that the animal belongs to the pet owner
        animal_id = data.get('animal')
        if animal_id:
            try:
                animal = Animal.objects.get(id=animal_id)
                if animal.owner.id != user.id and not (user.is_staff or user.is_superuser):
                    return Response(
                        {'error': 'You can only book for your own animals'}, 
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
                # Get the dates for the new booking
                start_date = data.get('start_date')
                end_date = data.get('end_date')
                
                if not start_date or not end_date:
                    return Response(
                        {'error': 'Start and end dates are required'}, 
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
                # Check if the animal already has an active booking that overlaps with the requested dates
                from django.db.models import Q
                from datetime import datetime
                
                # Convert dates to datetime objects for comparison
                start_date_obj = datetime.strptime(start_date, '%Y-%m-%d').date() if isinstance(start_date, str) else start_date
                end_date_obj = datetime.strptime(end_date, '%Y-%m-%d').date() if isinstance(end_date, str) else end_date
                
                # Check existing company bookings that overlap with the dates
                overlapping_company_bookings = CompanyBooking.objects.filter(
                    animal=animal,
                    status__in=['pending', 'accepted', 'paid'],  # Exclude 'cancelled' bookings
                ).filter(
                    # Date overlap criteria:
                    # (start1 <= end2) AND (end1 >= start2)
                    Q(start_date__lte=end_date_obj) & Q(end_date__gte=start_date_obj)
                )
                
                if overlapping_company_bookings.exists():
                    return Response(
                        {'error': 'This animal already has a company booking that overlaps with these dates. Please choose other dates.'}, 
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
                # Also check if the animal has a booking with a pet sitter on the same dates
                overlapping_bookings = Booking.objects.filter(
                    animal=animal,
                    status__in=['pending', 'accepted', 'paid'],
                ).filter(
                    Q(start_date__lte=end_date_obj) & Q(end_date__gte=start_date_obj)
                )
                
                if overlapping_bookings.exists():
                    return Response(
                        {'error': 'This animal already has a booking with a pet sitter that overlaps with these dates. Please choose other dates.'}, 
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
            except Animal.DoesNotExist:
                return Response(
                    {'error': 'Animal not found'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
        else:
            return Response(
                {'error': 'Please specify an animal for the booking'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create the booking
        serializer = self.get_serializer(data=data)
        if serializer.is_valid():
            serializer.save()
            # Send notification email
            send_booking_status_email(serializer.instance, serializer.instance.status, booking_type='company')
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def my_bookings(self, request):
        """
        Returns the list of company bookings for the connected pet owner's animals.
        """
        user = request.user
        
        # Check that the user is a pet owner
        if user.role != 'petowner':
            return Response(
                {'error': 'Only pet owners can access this resource'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Get all bookings for the pet owner's animals
        bookings = CompanyBooking.objects.filter(animal__owner=user)
        
        serializer = self.get_serializer(bookings, many=True)
        return Response(serializer.data)

class PetSitterCompanyBookingViewSet(viewsets.ModelViewSet):
    """
    ViewSet to manage bookings between pet sitters and companies.
    """
    queryset = PetSitterCompanyBooking.objects.all()
    serializer_class = PetSitterCompanyBookingSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['status', 'service_type']

    def get_queryset(self):
        """
        Filters bookings based on the user's role.
        """
        user = self.request.user
        
        # Administrators can see all bookings
        if user.is_staff or user.is_superuser:
            return PetSitterCompanyBooking.objects.all()
        
        # Pet sitters can see bookings that concern them
        if user.role == 'petsitter':
            return PetSitterCompanyBooking.objects.filter(petsitter=user)
        
        # Companies can see bookings that concern them
        elif user.role == 'company':
            return PetSitterCompanyBooking.objects.filter(company=user)
        
        # By default, return an empty queryset
        return PetSitterCompanyBooking.objects.none()

    def create(self, request, *args, **kwargs):
        """
        Override create method to automatically set the pet sitter.
        """
        user = request.user
        
        # Check that the user is a pet sitter
        if user.role != 'petsitter':
            return Response(
                {'error': 'Only pet sitters can create these bookings'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Add the current pet sitter to the data
        data = request.data.copy()
        data['petsitter'] = user.id
        
        # Create the booking with the completed data
        serializer = self.get_serializer(data=data)
        if serializer.is_valid():
            serializer.save()
            # Send notification email
            send_booking_status_email(serializer.instance, serializer.instance.status, booking_type='petsitter_company')
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['patch'], permission_classes=[IsAuthenticated])
    def update_status(self, request, pk=None):
        """
        Allows companies and pet sitters to update a booking's status.
        Cancelled bookings are kept with the status 'cancelled'.
        """
        booking = self.get_object()
        user = request.user
        
        # Verify that the user is either the pet sitter or the company concerned
        is_authorized = (
            (user.role == 'petsitter' and booking.petsitter.id == user.id) or
            (user.role == 'company' and booking.company.id == user.id)
        )
        
        if not is_authorized and not (user.is_staff or user.is_superuser):
            return Response(
                {'error': 'You are not authorized to modify this booking'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Get the new status from the request
        new_status = request.data.get('status')
        
        # Check that the status is valid
        valid_statuses = [status_tuple[0] for status_tuple in PetSitterCompanyBooking.STATUS_CHOICES]
        if new_status not in valid_statuses:
            return Response(
                {'error': f'Invalid status. Valid statuses are: {", ".join(valid_statuses)}'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Update the booking status (keep even if cancelled)
        old_status = booking.status
        booking.status = new_status
        booking.save()
        
        # Send notification email
        send_booking_status_email(booking, new_status, booking_type='petsitter_company')
        
        # Create an adapted return message
        status_labels = {
            'pending': 'pending',
            'accepted': 'accepted',
            'refused': 'declined', 
            'cancelled': 'cancelled',
            'finished': 'completed'
        }
        status_label = status_labels.get(new_status, new_status)
        
        # Return the updated data
        serializer = self.get_serializer(booking)
        return Response({
            'message': f'Booking successfully {status_label}',
            'booking': serializer.data
        })

class PaymentViewSet(viewsets.ModelViewSet):
    """
    ViewSet to manage payments related to bookings.
    """
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['payment_status', 'payment_type']

    def get_queryset(self):
        """
        Filters payments based on the user's role.
        """
        user = self.request.user
        
        # Administrators can see all payments
        if user.is_staff or user.is_superuser:
            return Payment.objects.all()
        
        # Pet owners can see their own payments
        if user.role == 'petowner':
            return Payment.objects.filter(
                # Payments linked to bookings for their animals
                booking__animal__owner=user
            ) | Payment.objects.filter(
                # Payments linked to company bookings for their animals
                company_booking__animal__owner=user
            )
        
        # Pet sitters can see payments that concern them
        elif user.role == 'petsitter':
            return Payment.objects.filter(booking__sitter=user)
        
        # Companies can see payments that concern them
        elif user.role == 'company':
            return Payment.objects.filter(company_booking__company=user)
        
        # By default, return an empty queryset
        return Payment.objects.none()

    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def process_payment(self, request):
        """
        Process a new payment for a booking.
        """
        user = request.user
        data = request.data.copy()
        
        # Check that the user is a pet owner
        if user.role != 'petowner' and not (user.is_staff or user.is_superuser):
            return Response(
                {'error': 'Only pet owners can make payments'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Get booking details
        booking_id = data.get('booking')
        company_booking_id = data.get('company_booking')
        
        if not booking_id and not company_booking_id:
            return Response(
                {'error': 'Please specify a booking to pay for'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Get amount to pay and verify booking ownership
            if booking_id:
                booking = Booking.objects.get(id=booking_id)
                
                # Verify that the animal belongs to the pet owner
                if booking.animal.owner.id != user.id and not (user.is_staff or user.is_superuser):
                    return Response(
                        {'error': 'You can only pay for your own bookings'}, 
                        status=status.HTTP_403_FORBIDDEN
                    )
                
                # Calculate total amount
                amount = booking.total_price
                
                # Check if booking is already paid
                if booking.status == 'paid':
                    return Response(
                        {'error': 'This booking has already been paid'}, 
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
                # Update booking status once payment is made
                booking.status = 'paid'
                booking.save()
                
            elif company_booking_id:
                company_booking = CompanyBooking.objects.get(id=company_booking_id)
                
                # Verify that the animal belongs to the pet owner
                if company_booking.animal.owner.id != user.id and not (user.is_staff or user.is_superuser):
                    return Response(
                        {'error': 'You can only pay for your own bookings'}, 
                        status=status.HTTP_403_FORBIDDEN
                    )
                
                # Calculate total amount
                amount = company_booking.total_price
                
                # Check if booking is already paid
                if company_booking.status == 'paid':
                    return Response(
                        {'error': 'This booking has already been paid'}, 
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
                # Update booking status once payment is made
                company_booking.status = 'paid'
                company_booking.save()
                
        except (Booking.DoesNotExist, CompanyBooking.DoesNotExist):
            return Response(
                {'error': 'Booking not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Create payment
        payment_data = {
            'booking': booking_id,
            'company_booking': company_booking_id,
            'amount': amount,
            'payment_status': 'completed',  # Assuming payment is immediately successful for this example
            'payment_type': data.get('payment_type', 'card'),
            'transaction_id': f"TR-{timezone.now().strftime('%Y%m%d%H%M%S')}-{random.randint(1000, 9999)}"
        }
        
        serializer = self.get_serializer(data=payment_data)
        if serializer.is_valid():
            payment = serializer.save()
            
            # Send payment confirmation email
            if booking_id:
                subject = f"Payment Confirmation - Booking #{booking_id}"
                message = f"Hello {user.name},\n\nYour payment of {amount}€ for the booking of {booking.animal.name} with {booking.sitter.name} has been accepted.\n\nTransaction ID: {payment.transaction_id}\n\nThank you for using Pet at Work!"
            else:
                subject = f"Payment Confirmation - Company Booking #{company_booking_id}"
                message = f"Hello {user.name},\n\nYour payment of {amount}€ for the booking of {company_booking.animal.name} with {company_booking.company.name} has been accepted.\n\nTransaction ID: {payment.transaction_id}\n\nThank you for using Pet at Work!"

            try:
                send_mail(
                    subject,
                    message,
                    settings.DEFAULT_FROM_EMAIL,
                    [user.email],
                    fail_silently=True,
                )
            except Exception as e:
                print(f"Error sending confirmation email: {str(e)}")
            
            return Response({
                'message': 'Payment processed successfully',
                'payment': serializer.data
            }, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def my_payments(self, request):
        """
        Returns the list of payments made by the user.
        """
        user = request.user
        
        # Check that the user is a pet owner
        if user.role != 'petowner':
            return Response(
                {'error': 'Only pet owners can access this resource'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Get all payments for the user
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
        Allows administrators to refund a payment.
        """
        user = request.user
        payment = self.get_object()
        
        # Check that the user is an administrator
        if not (user.is_staff or user.is_superuser):
            return Response(
                {'error': 'Only administrators can process refunds'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Check that the payment can be refunded
        if payment.payment_status != 'completed':
            return Response(
                {'error': 'Only completed payments can be refunded'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Update the payment status
        payment.payment_status = 'refunded'
        payment.save()
        
        # Update the associated booking
        if payment.booking:
            booking = payment.booking
            booking.status = 'cancelled'
            booking.save()
        elif payment.company_booking:
            company_booking = payment.company_booking
            company_booking.status = 'cancelled'
            company_booking.save()
        
        # Send refund confirmation email
        try:
            owner_email = payment.booking.animal.owner.email if payment.booking else payment.company_booking.animal.owner.email
            owner_name = payment.booking.animal.owner.name if payment.booking else payment.company_booking.animal.owner.name
            
            subject = "Refund Confirmation"
            message = f"Hello {owner_name},\n\nYour payment of {payment.amount}€ has been refunded.\n\nTransaction ID: {payment.transaction_id}\n\nThank you for using Pet at Work!"

            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [owner_email],
                fail_silently=True,
            )
        except Exception as e:
            print(f"Error sending refund email: {str(e)}")
        
        serializer = self.get_serializer(payment)
        return Response({
            'message': 'Refund processed successfully',
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
    
    # Detailed logs for debugging
    logger.info(f"Login attempt for email: {email}")
    print(f"Login attempt for email: {email}")

    if not email or not password:
        logger.warning("Login failed: Email or password missing")
        print("Login failed: Email or password missing")
        return Response({'error': 'Email and password required'}, status=status.HTTP_400_BAD_REQUEST)

    # Convert email to lowercase to avoid case sensitivity issues
    email_lower = email.lower()
    
    # Check if user exists
    try:
        # display user list for debugging
        all_users = User.objects.all()
        logger.debug(f"User list: {[user.email for user in all_users]}")
        print(f"User list: {[user.email for user in all_users]}")

        # Check if user exists in database
        user_exists = User.objects.filter(email=email_lower).exists()
        if not user_exists:
            logger.warning(f"Login failed: No user found with email {email_lower}")
            print(f"Login failed: No user found with email {email_lower}")
            return Response({'error': 'Invalid credentials. Please check your email and password.'}, 
                          status=status.HTTP_401_UNAUTHORIZED)
    except Exception as e:
        logger.error(f"Error while checking user: {str(e)}")
        print(f"Error while checking user: {str(e)}")

    # Authentication attempt
    user = authenticate(request, email=email_lower, password=password)
    
    if user is not None:
        logger.info(f"Login successful for user: {user.email}")
        print(f"Login successful for user: {user.email}")
        
        # Explicitly check admin status
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
            'is_admin': is_admin,  # Add explicit field to facilitate frontend verification
            'admin_status': {      # Detailed information about admin status for debugging
                'is_staff': user.is_staff,
                'is_superuser': user.is_superuser,
                'permissions': list(user.get_all_permissions())
            }
        })
    else:
        logger.warning(f"Authentication failed for email: {email_lower}")
        print(f"Authentication failed for email: {email_lower}")
        
        # More detailed message to help with debugging
        return Response({'error': 'Invalid credentials. Please check your email and password.'}, 
                       status=status.HTTP_401_UNAUTHORIZED)

@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    """
    Register a new user with email, password and role.
    """
    data = request.data.copy()
    data['email'] = data.get('email', '').lower()
    # Don't hash the password here, the serializer will take care of it
    
    serializer = UserSerializer(data=data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_profile(request):
    """
    Update the profile of the authenticated user.
    """
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
    Diagnostic view to test authentication.
    Accessible via /api/test-auth/?email=user@example.com&password=yourpassword
    """
    from django.contrib.auth import authenticate
    
    email = request.query_params.get('email')
    password = request.query_params.get('password')
    
    print(f"Authentication test for email: {email}")
    
    if not email or not password:
        return Response({'error': 'Email and password required'}, status=status.HTTP_400_BAD_REQUEST)
    
    # Check if user exists
    try:
        user_exists = User.objects.filter(email=email.lower()).exists()
        if not user_exists:
            print(f"Test auth: No user found with email {email.lower()}")
            return Response({
                'error': 'User not found',
                'email_tested': email.lower(),
                'user_exists': False
            }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        print(f"Test auth: Error while checking user: {str(e)}")
    
    # Authentication attempt
    user = authenticate(request, email=email.lower(), password=password)
    
    if user is not None:
        print(f"Test auth: Authentication successful for {email.lower()}")
        return Response({
            'success': True,
            'message': 'Authentication successful',
            'user_id': user.id,
            'email': user.email,
            'name': user.name,
            'role': user.role
        })
    else:
        # Try to retrieve the user to manually compare passwords
        try:
            user = User.objects.get(email=email.lower())
            print(f"Test auth: User found, but authentication failed for {email.lower()}")
            return Response({
                'error': 'Incorrect password',
                'user_exists': True,
                'email_tested': email.lower(),
                'auth_result': 'Authentication failed with the provided password'
            }, status=status.HTTP_401_UNAUTHORIZED)
        except User.DoesNotExist:
            print(f"Test auth: User not found (double check) for {email.lower()}")
            return Response({
                'error': 'User not found',
                'user_exists': False,
                'email_tested': email.lower()
            }, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
@permission_classes([AllowAny])
def list_users_test(request):
    """
    Test view to list all users.
    This API is in AllowAny mode for testing purposes.
    In production, you should restrict access.
    """
    try:
        users = User.objects.all()
        # Limit to 20 users for performance
        users = users[:20]
        
        # Create a simplified list of user data
        user_data = []
        for user in users:
            # Get the hashed password for debugging
            # WARNING: This is only for debugging and should never
            # be done in production!
            user_data.append({
                'id': user.id,
                'email': user.email,
                'name': user.name,
                'role': user.role,
                'is_staff': user.is_staff,
                'is_superuser': user.is_superuser,
                'password_hash': user.password  # The hashed password for debugging
            })
        
        print(f"List of {len(user_data)} users retrieved successfully")
        return Response({
            'success': True,
            'count': len(user_data),
            'users': user_data
        })
    except Exception as e:
        print(f"Error retrieving users: {str(e)}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([AllowAny])
def debug_login(request):
    """
    Advanced diagnostic view that tests authentication and returns detailed information
    about each step of the authentication process.
    """
    from rest_framework_simplejwt.tokens import RefreshToken
    from django.contrib.auth import authenticate
    import sys
    
    # Get credentials
    email = request.data.get('email')
    password = request.data.get('password')
    
    response_data = {
        'debug_info': {
            'email_received': email,
            'password_received': '***' if password else None,
            'password_length': len(password) if password else 0,
            'steps': []
        }
    }
    
    # Step 1: Check that email and password are provided
    if not email or not password:
        response_data['debug_info']['steps'].append({
            'step': 'input_validation',
            'status': 'failed',
            'reason': 'Email or password missing'
        })
        response_data['error'] = 'Email and password required'
        return Response(response_data, status=status.HTTP_400_BAD_REQUEST)
    
    response_data['debug_info']['steps'].append({
        'step': 'input_validation',
        'status': 'success'
    })
    
    # Standardize email to lowercase
    email_lower = email.lower()
    response_data['debug_info']['normalized_email'] = email_lower
    
    # Step 2: Check if the user exists
    try:
        user_exists = User.objects.filter(email=email_lower).exists()
        
        if user_exists:
            user = User.objects.get(email=email_lower)
            response_data['debug_info']['user_found'] = True
            response_data['debug_info']['user_id'] = user.id
            response_data['debug_info']['is_active'] = user.is_active
            response_data['debug_info']['password_hash_start'] = user.password[:20] + '...' if user.password else None
        else:
            response_data['debug_info']['user_found'] = False
            response_data['debug_info']['steps'].append({
                'step': 'user_verification',
                'status': 'failed',
                'reason': f'No user found with email {email_lower}'
            })
            response_data['error'] = 'Invalid credentials'
            return Response(response_data, status=status.HTTP_401_UNAUTHORIZED)
        
        response_data['debug_info']['steps'].append({
            'step': 'user_verification',
            'status': 'success'
        })
    except Exception as e:
        response_data['debug_info']['steps'].append({
            'step': 'user_verification',
            'status': 'error',
            'exception': str(e),
            'traceback': str(sys.exc_info())
        })
        response_data['error'] = f'Error checking user: {str(e)}'
        return Response(response_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    # Step 3: Authentication attempt
    try:
        auth_user = authenticate(request, email=email_lower, password=password)
        
        if auth_user is not None:
            response_data['debug_info']['authentication'] = 'successful'
            response_data['debug_info']['auth_user_id'] = auth_user.id
            
            # Create JWT tokens
            refresh = RefreshToken.for_user(auth_user)
            
            response_data['debug_info']['steps'].append({
                'step': 'authentication',
                'status': 'success'
            })
            
            # Successful login information
            response_data['success'] = True
            response_data['access'] = str(refresh.access_token)
            response_data['refresh'] = str(refresh)
            response_data['user_id'] = auth_user.id
            response_data['email'] = auth_user.email
            response_data['name'] = auth_user.name
            response_data['role'] = auth_user.role
            
            return Response(response_data)
        else:
            # Authentication failed
            response_data['debug_info']['authentication'] = 'failed'
            
            # Manual password verification
            if hasattr(user, 'check_password'):
                pw_check = user.check_password(password)
                response_data['debug_info']['check_password'] = pw_check
            else:
                response_data['debug_info']['check_password'] = 'method not available'
            
            response_data['debug_info']['steps'].append({
                'step': 'authentication',
                'status': 'failed',
                'reason': 'Incorrect password or issue with authenticate()'
            })
            
            response_data['error'] = 'Invalid credentials'
            return Response(response_data, status=status.HTTP_401_UNAUTHORIZED)
    except Exception as e:
        response_data['debug_info']['steps'].append({
            'step': 'authentication',
            'status': 'error',
            'exception': str(e),
            'traceback': str(sys.exc_info())
        })
        response_data['error'] = f'Authentication error: {str(e)}'
        return Response(response_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
