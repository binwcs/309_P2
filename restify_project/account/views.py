from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.models import User
from django.contrib.auth import logout
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from .serializers import RegisterSerializer
from django.core.mail import send_mail
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from .serializers import ForgotPasswordSerializer, LoginSerializer, UserSerializer
from .forms import UserProfileForm
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Booking, Comment
from .forms import CommentForm


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    自定义权限，只允许对象的所有者编辑它
    """

    def has_object_permission(self, request, view, obj):
        # 对于GET、HEAD或OPTIONS请求，始终允许访问
        if request.method in permissions.SAFE_METHODS:
            return True

        # 只有对象的所有者才能编辑
        return obj.host == request.user


# -----------------------------Login Page-----------------------
def reservation(request):
    return render(request, '../reservation.html')


def log_in(request):
    return render(request, '../templates/account/log_in.html')


class RegisterView(generics.GenericAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        account = serializer.save()
        return Response({
            "account": serializer.data,
            "message": "User created successfully",
        }, status=status.HTTP_201_CREATED)


class LogoutView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        logout(request)
        return Response({"message": "User logged out successfully"})


class ForgotPasswordView(generics.GenericAPIView):
    queryset = User.objects.all()
    serializer_class = ForgotPasswordSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        email = request.data.get('email')
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"error": "User with this email does not exist."},
                            status=status.HTTP_400_BAD_REQUEST)

        # Generate the token and encode the account's ID
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))

        # Construct the password reset link
        reset_link = f"{request.scheme}://{request.get_host()}/reset-password/{uid}/{token}/"

        # Send the email
        send_mail(
            'Password Reset',
            f'Click the following link to reset your password: {reset_link}',
            'noreply@example.com',
            [email],
            fail_silently=False,
        )

        return Response({"message": "Password reset email sent."})


class LoginView(generics.GenericAPIView):
    serializer_class = LoginSerializer

    def post(self, request):
        print(request.data)  # 打印请求数据
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data
        refresh = RefreshToken.for_user(user)
        return Response({
            "access": str(refresh.access_token),
            "refresh": str(refresh),
        })


# -----------------------------Profile Page-----------------------
class UserUpdateView(generics.UpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user

    def put(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data, status=status.HTTP_200_OK)


class UserDetailView(generics.RetrieveAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user


@login_required
def my_profile(request):
    user = request.user
    profile = user.profile
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
    else:
        form = UserProfileForm(instance=profile)
    return render(request, 'account/my_profile.html', {'form': form, 'account': user})


# User Comment System

@login_required
def user_comment_system(request):
    user = request.user
    if request.method == 'POST':
        comment_text = request.POST.get('comment')
        if comment_text:
            comment = Comment.objects.create(user=user, text=comment_text)
            return JsonResponse({'id': comment.id, 'text': comment.text, 'account': user.username})
    comments = Comment.objects.filter(user=user).order_by('-created_at')
    return render(request, 'account/user_comment_system.html', {'comments': comments})


@login_required
def leave_comment(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            rating = form.cleaned_data['rating']
            comment_text = form.cleaned_data['comment']
            Comment.objects.create(
                booking=booking, rating=rating, comment=comment_text)
            messages.success(request, 'Your comment has been submitted.')
            return redirect('account:order_history')
    else:
        form = CommentForm()
    return render(request, 'account/comment_form.html', {'form': form, 'booking': booking})
