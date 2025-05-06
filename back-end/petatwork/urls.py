from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from core.views import (
    UserViewSet, AnimalViewSet, BookingViewSet, CompanyBookingViewSet, 
    PetSitterCompanyBookingViewSet, PaymentViewSet, login, register, 
    test_auth, list_users_test, debug_login, process_company_payment
)
from django.views.generic.base import RedirectView
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'animals', AnimalViewSet)
router.register(r'bookings', BookingViewSet)
router.register(r'company-bookings', CompanyBookingViewSet, basename='company-booking')
router.register(r'petsitter-company-bookings', PetSitterCompanyBookingViewSet)
router.register(r'payments', PaymentViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('api/login/', login, name='login'),
    path('api/register/', register, name='register'),
    path('api/test-auth/', test_auth, name='test_auth'),
    path('api/list-users-test/', list_users_test, name='list_users_test'),
    path('api/debug-login/', debug_login, name='debug_login'),
    
    # Anciennes routes pour le paiement des entreprises
    path('api/company-bookings/<int:pk>/company_payment/', 
         CompanyBookingViewSet.as_view({'post': 'company_payment'}), 
         name='company-booking-payment'),
    
    # Route simplifiée pour le paiement des entreprises - correction pour correspondre à l'appel frontend
    path('api/process-company-payment/<int:booking_id>/', process_company_payment, name='process-company-payment'),
    
    # Ajout d'une route alternative au cas où le frontend utiliserait un format différent
    path('process-company-payment/<int:booking_id>/', process_company_payment, name='process-company-payment-alt'),
    
    # Ajout des routes JWT standard
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    # API authentication browsable
    path('api-auth/', include('rest_framework.urls')),
    path('', RedirectView.as_view(url='/api/', permanent=False), name='index'),
]