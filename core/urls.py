from django.urls import include, path
from rest_framework import routers
from api.views import (
    UserRegistrationView,
    CustomTokenObtainPairView,
    PropertyViewSet,
    BookingViewSet,
    UserBookingsView,
    HostBookingsView,
    UserPropertiesView,
    VerifyTokenView,
)

router = routers.DefaultRouter()
router.register(r'properties', PropertyViewSet)
router.register(r'bookings', BookingViewSet, basename='booking')

urlpatterns = [
    path('api/', include(router.urls)),
    
    # Autenticação
    path('api/auth/register/', UserRegistrationView.as_view(), name='register'),
    path('api/auth/login/', CustomTokenObtainPairView.as_view(), name='login'),
    path('api/auth/verify/', VerifyTokenView.as_view(), name='verify-token'),

    # Listagens
    path('api/my-bookings/', UserBookingsView.as_view(), name='user-bookings'),
    path('api/host-bookings/', HostBookingsView.as_view(), name='host-bookings'),
    path('api/my-properties/', UserPropertiesView.as_view(), name='user-properties'),
]