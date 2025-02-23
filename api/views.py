from datetime import datetime
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework import viewsets, permissions, generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from .models import Property, Booking
from .serializers import (
    UserSerializer,
    PropertySerializer,
    BookingSerializer,
    CustomTokenObtainPairSerializer,
    
)

User = get_user_model()

# ------------------------------------------
# Autenticação e Usuários
# ------------------------------------------
class VerifyTokenView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({"valid": True}, status=status.HTTP_200_OK)

class UserRegistrationView(generics.CreateAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        refresh = RefreshToken.for_user(user)
        return Response({
            "refresh": str(refresh),
            "access": str(refresh.access_token),
            "user": UserSerializer(user).data
        }, status=status.HTTP_201_CREATED)

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

# ------------------------------------------
# Propriedades
# ------------------------------------------
class PropertyViewSet(viewsets.ModelViewSet):
    queryset = Property.objects.all()
    serializer_class = PropertySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(host=self.request.user)

    def get_queryset(self):
        # Filtra propriedades do usuário logado
        if self.action == 'my_properties':
            return Property.objects.filter(host=self.request.user)
        return super().get_queryset()

    @action(detail=False, methods=['get'])
    def my_properties(self, request):
        properties = self.get_queryset().filter(host=request.user)
        serializer = self.get_serializer(properties, many=True)
        return Response(serializer.data)
# ------------------------------------------
# Reservas
# ------------------------------------------
class BookingViewSet(viewsets.ModelViewSet):
    serializer_class = BookingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Booking.objects.filter(guest=self.request.user)

    def perform_create(self, serializer):
        property = serializer.validated_data['property']
        check_in = serializer.validated_data['check_in']
        check_out = serializer.validated_data['check_out']
        
        if property.host == self.request.user:
            raise serializers.ValidationError("Você não pode alugar sua própria propriedade")
        
        # Verifica conflito de datas
        conflicts = Booking.objects.filter(
            property=property,
            check_out__gt=check_in,
            check_in__lt=check_out
        ).exists()

        if conflicts:
            raise ValidationError("Já existe reserva para estas datas")

        # Cálculo do preço 
        days = (serializer.validated_data['check_out'] - serializer.validated_data['check_in']).days
        total_price = days * property.price_per_night
        
        serializer.save(
            guest=self.request.user,
            total_price=total_price
        )

# ------------------------------------------
# Listagens Específicas
# ------------------------------------------
class UserBookingsView(generics.ListAPIView):
    serializer_class = BookingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Booking.objects.filter(guest=self.request.user)

class UserPropertiesView(generics.ListAPIView):
    serializer_class = PropertySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Property.objects.filter(host=self.request.user)

class HostBookingsView(generics.ListAPIView):
    serializer_class = BookingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Booking.objects.filter(property__host=self.request.user)