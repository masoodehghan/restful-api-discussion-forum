from rest_framework import status, permissions, generics
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import UserSerializer, PasswordSerializer, RegisterSerializer
from .permissions import IsOwner
from .models import User


class RegisterView(generics.CreateAPIView):

    permission_classes = [permissions.AllowAny]
    serializer_class = RegisterSerializer


class UserDetail(generics.RetrieveAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]
    queryset = User.objects.defer('password', 'is_active', 'is_staff', 'date_joined')

    lookup_field = 'uuid'


class UserProfile(generics.RetrieveAPIView, generics.UpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsOwner]

    queryset = User.objects.defer('password', 'is_active', 'is_staff', 'date_joined')

    def get_object(self):
        return self.request.user


class ChangePasswordView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def put(self, request, *args, **kwargs):
        user = request.user
        serializer = PasswordSerializer(data=request.data, many=False)
        
        if serializer.is_valid():
            
            if not user.check_password(serializer.data.get('old_password')):
                return Response({'old_password': ['Wrong Password']}, status.HTTP_400_BAD_REQUEST)
            
            user.set_password(serializer.data.get('new_password'))
            user.save()
            return Response({'message': 'password changed.', 'data': []}, status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)
            