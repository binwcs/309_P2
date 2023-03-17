# models.py
from django.db import models
from django.contrib.auth.models import User
from property.models import Property


class Reservation(models.Model):
    # Fields for the Reservation model
    hotel_name = models.CharField(max_length=200)
    hotel_image = models.ImageField(upload_to='reservation/hotel_images/')
    check_in = models.DateField()
    check_out = models.DateField()
    room_type = models.CharField(max_length=50)
    num_rooms = models.IntegerField()
    num_guests = models.IntegerField()
    total_price = models.DecimalField(max_digits=8, decimal_places=2)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    state = models.ForeignKey('ReservationState', on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.hotel_name} - {self.check_in} to {self.check_out}"


class ReservationState(models.Model):
    # Fields for the ReservationState model
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class Booking(models.Model):
    property = models.ForeignKey(Property, on_delete=models.CASCADE)
    guest = models.ForeignKey(User, on_delete=models.CASCADE)
    check_in_date = models.DateField()
    check_out_date = models.DateField()
    comment = models.TextField(blank=True)

    def __str__(self):
        return f"{self.property} - {self.guest.username}"
