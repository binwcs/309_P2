from rest_framework import serializers
from .models import Property, Amenity
from ..account.models import Comment


class AmenitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Amenity
        fields = '__all__'


class PropertySerializer(serializers.ModelSerializer):
    amenities = AmenitySerializer(many=True)

    class Meta:
        model = Property
        fields = '__all__'

    def create(self, validated_data):
        amenities_data = validated_data.pop('amenities')
        property = Property.objects.create(**validated_data)
        for amenity_data in amenities_data:
            amenity, _ = Amenity.objects.get_or_create(name=amenity_data['name'])
            property.amenities.add(amenity)
        return property

    def update(self, instance, validated_data):
        amenities_data = validated_data.pop('amenities')
        amenities = []
        for amenity_data in amenities_data:
            amenity, _ = Amenity.objects.get_or_create(name=amenity_data['name'])
            amenities.append(amenity)
        instance.amenities.set(amenities)
        return super().update(instance, validated_data)


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['id', 'account', 'property', 'comment', 'reply', 'timestamp']


class PropertyImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Property
        fields = ['image']

    def validate_image(self, value):
        """
        Check if image size is larger than 10MB
        """
        if value.size > 10485760:
            raise serializers.ValidationError("Image size is larger than 10MB")
        return value

    def save(self):
        property = self.instance
        property.image.delete()
        property.image = self.validated_data['image']
        property.save()
        return property
