from rest_framework import serializers
from .models import User, Animal, Booking, CompanyBooking, PetSitterCompanyBooking, Payment

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'name', 'email', 'password', 'role', 'address', 'experience', 'capacity']
        extra_kwargs = {
            'password': {'write_only': True},
            'address': {'required': False},
            'experience': {'required': False},
            'capacity': {'required': False}
        }

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        user = User(**validated_data)
        if password:
            user.set_password(password)
        user.save()
        return user

class AnimalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Animal
        fields = '__all__'
        extra_kwargs = {
            'name': {'required': True, 'error_messages': {'required': 'Le nom de l\'animal est obligatoire'}},
            'owner': {'required': True, 'error_messages': {'required': 'Le propriétaire est obligatoire'}},
            'breed': {'required': False},
            'age': {'required': False},
            'maladie': {'required': False}
        }

class BookingSerializer(serializers.ModelSerializer):
    total_days = serializers.IntegerField(read_only=True)
    total_price = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Booking
        fields = ['id', 'animal', 'sitter', 'start_date', 'end_date', 'status', 'total_days', 'total_price']

class CompanyBookingSerializer(serializers.ModelSerializer):
    total_days = serializers.IntegerField(read_only=True)
    total_price = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = CompanyBooking
        fields = ['id', 'animal', 'company', 'start_date', 'end_date', 'status', 'created_at', 'total_days', 'total_price']

class PetSitterCompanyBookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = PetSitterCompanyBooking
        fields = '__all__'

class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ['id', 'booking', 'company_booking', 'amount', 'payment_date', 'payment_status', 'payment_type', 'transaction_id']
        read_only_fields = ['payment_date', 'transaction_id']
