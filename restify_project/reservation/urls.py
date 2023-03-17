from django.urls import path, include
from rest_framework import routers
from .views import ReservationViewSet

router = routers.DefaultRouter()
router.register(r'reservations', ReservationViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
