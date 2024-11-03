from django.shortcuts import render
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.decorators import permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from django.contrib.auth.hashers import check_password
from django.shortcuts import get_object_or_404
import json
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from .models import User
from rest_framework.decorators import api_view
# Create your views here.

User = get_user_model()

@api_view(['POST',])
@permission_classes([AllowAny, ])
def signup(request):
    data = json.loads(request.body)
    email = data.get('email')
    password = data.get('password')
    first_name = data.get('first_name')
    last_name = data.get('last_name')
    if not all([email, password, first_name, last_name]):
        return Response({'error': 'Email, password, first name and last name are required'}, status=400)
    if User.objects.filter(email=email).exists():
        return Response({'error': 'A user with this email already exists'}, status=400)
    user_obj = User.objects.create_user(email=email, password=password, first_name=first_name, last_name=last_name)
    return Response({'message': 'Registration successful', 'user_email': user_obj.email}, status=201)

@api_view(['POST',])
@permission_classes([AllowAny, ])
def login(request):
    data = json.loads(request.body)
    email = data.get('email')
    password = data.get('password')
    if email is None or password is None:
        return Response({'error': 'Email and password are required'}, status=400)
    user = authenticate(request, username=email, password=password)
    if not user:
        return Response({'error': 'Invalid credentials'}, status=400)
    refresh_token = RefreshToken.for_user(user)
    access_token = refresh_token.access_token    
    response_data = {
        "user_details": {"email": user.email},
        "tokens": {"refresh": str(refresh_token), "access": str(access_token)}
    }
    return Response(response_data)

@api_view(['POST',])
@permission_classes([IsAuthenticated, ])
def logout(request):
    try:
        refresh_token = request.data["refresh"]
        token = RefreshToken(refresh_token)
        token.blacklist()
        return Response({'message': 'Logout Successfully!'}, status=status.HTTP_205_RESET_CONTENT)
    except Exception as e:
        return Response(status=status.HTTP_400_BAD_REQUEST)

@api_view(['PUT',])
@permission_classes([IsAuthenticated, ])
def change_password(request):
    data = json.loads(request.body)
    user_obj = get_object_or_404(User, id=request.user.id)
    old_password = data.get('old_password')
    new_password = data.get('new_password')
    if old_password is None or new_password is None:
        return Response({'error': 'Old password and New password are required'}, status=400)
    if not check_password(old_password, user_obj.password):
        return Response({'error': 'Old password is incorrect'}, status=400)
    user_obj.set_password(new_password)
    user_obj.save()
    return Response({'message': 'Password Updated Successfully!'})