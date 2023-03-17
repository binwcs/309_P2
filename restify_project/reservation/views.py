# views.py
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import Reservation
from .serializers import ReservationSerializer
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Booking


class ReservationViewSet(viewsets.ModelViewSet):
    serializer_class = ReservationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Reservation.objects.filter(user=user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user, state='Pending')

    def perform_update(self, serializer):
        reservation = serializer.instance
        if 'state' in serializer.validated_data:
            new_state = serializer.validated_data['state']
            if new_state == 'Cancelled':
                reservation.state = 'Cancelled'
                reservation.save()
            elif new_state == 'Approved':
                reservation.state = 'Approved'
                reservation.save()
                # Perform any additional actions needed after approval
            elif new_state == 'Denied':
                reservation.state = 'Denied'
                reservation.save()
                # Perform any additional actions needed after denial
        else:
            serializer.save()

    def perform_destroy(self, instance):
        reservation = instance
        if reservation.state in ('Pending', 'Approved'):
            reservation.state = 'Cancelled'
            reservation.save()
        else:
            instance.delete()


def reservations(request):
    reservations = Reservation.objects.filter(user=request.user)
    context = {'reservations': reservations}
    return render(request, 'reservation/reservations.html', context)


@login_required
def reservation_list(request):
    bookings = Booking.objects.filter(guest=request.user)
    return render(request, 'reservation/reservation_list.html', {'bookings': bookings})


@login_required
def leave_comment(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, guest=request.user)
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            booking.comment = form.cleaned_data['comment']
            booking.save()
            messages.success(request, 'Your comment has been saved.')
    else:
        form = CommentForm()
    return render(request, 'reservation/leave_comment.html', {'booking': booking, 'form': form})
