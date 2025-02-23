from django.contrib.auth import get_user_model
from django.db import models
from django.core.exceptions import ValidationError

user = get_user_model()

class Property(models.Model):
    host = models.ForeignKey(user, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField()
    price_per_night = models.DecimalField(max_digits=10, decimal_places=2)
    bedrooms = models.IntegerField()
    location = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

class Booking(models.Model):
    guest = models.ForeignKey(user, on_delete=models.CASCADE)
    property = models.ForeignKey(Property, on_delete=models.CASCADE)
    check_in = models.DateField()
    check_out = models.DateField()
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    def clean(self):
        # Verifica conflito de datas
        conflicts = Booking.objects.filter(
            property=self.property,
            check_out__gt=self.check_in,
            check_in__lt=self.check_out
        ).exclude(pk=self.pk)
        
        if conflicts.exists():
            raise ValidationError('Já existe uma reserva para este período')

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)