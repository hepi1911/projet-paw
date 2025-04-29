from django.contrib import admin
from .models import User, Animal, Booking

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'role')
    list_filter = ('role',)
    search_fields = ('name', 'email')

@admin.register(Animal)
class AnimalAdmin(admin.ModelAdmin):
    list_display = ('name', 'breed', 'age', 'owner')
    list_filter = ('breed',)
    search_fields = ('name', 'breed')

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('animal', 'sitter', 'start_date', 'end_date', 'status')
    list_filter = ('status', 'start_date', 'end_date')
    search_fields = ('animal__name', 'sitter__name')
