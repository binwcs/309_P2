from django.http import Http404
from rest_framework import generics, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404

from .models import Property
from ..account.models import Comment
from .serializers import PropertySerializer, CommentSerializer, PropertyImageSerializer


class PropertyList(generics.ListCreateAPIView):
    queryset = Property.objects.all()
    serializer_class = PropertySerializer


class PropertyDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Property.objects.all()
    serializer_class = PropertySerializer


class PropertyImageUploadView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def put(self, request, pk, format=None):
        property = self.get_object(pk)
        if property.owner != request.user:
            return Response({'message': 'You are not the owner of this property'}, status=status.HTTP_403_FORBIDDEN)
        serializer = PropertyImageSerializer(property, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get_object(self, pk):
        try:
            return Property.objects.get(pk=pk)
        except Property.DoesNotExist:
            raise Http404


class PropertyImageDeleteView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request, pk, format=None):
        property = self.get_object(pk)
        if property.owner != request.user:
            return Response({'message': 'You are not the owner of this property'}, status=status.HTTP_403_FORBIDDEN)
        property.image.delete()
        return Response({'message': 'Image successfully deleted.'}, status=status.HTTP_204_NO_CONTENT)

    def get_object(self, pk):
        try:
            return Property.objects.get(pk=pk)
        except Property.DoesNotExist:
            raise Http404


class PropertyCommentListView(generics.ListAPIView):
    serializer_class = CommentSerializer

    def get_queryset(self):
        property_id = self.kwargs['property_id']
        return Comment.objects.filter(property=property_id)


class PropertyCommentCreateView(generics.CreateAPIView):
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        property_id = self.kwargs['property_id']
        property = get_object_or_404(Property, id=property_id)
        serializer.save(user=self.request.user, property=property)


def IsCommentOwnerOrAdmin(request, view, obj):
    if request.user.is_staff or obj.user == request.user:
        return True
    return False


class CommentDeleteView(generics.DestroyAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated, IsCommentOwnerOrAdmin]


class CommentUpdateView(generics.UpdateAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated, IsCommentOwnerOrAdmin]
