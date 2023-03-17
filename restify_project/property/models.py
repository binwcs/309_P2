from django.db import models


class Property(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    location = models.CharField(max_length=255)
    price_per_night = models.IntegerField()
    max_guests = models.IntegerField()
    number_of_beds = models.IntegerField()
    number_of_baths = models.IntegerField()
    amenities = models.ManyToManyField('Amenity')

    def __str__(self):
        return self.name


class Amenity(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name
