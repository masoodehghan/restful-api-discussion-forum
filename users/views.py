from rest_framework import status, permissions, generics
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import User
from .serializers import UserSerializer, PasswordSerializer, RegisterSerializer
from .permissions import IsOwner
from django.shortcuts import get_object_or_404


class UserListView(APIView):
    permission_classes = [permissions.IsAdminUser]
    
    def get(self, request):
        user = User.objects.all()
        
        serializer = UserSerializer(user, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    

class RegisterView(generics.CreateAPIView):

    permission_classes = [permissions.AllowAny]
    serializer_class = RegisterSerializer


class UserDetail(generics.RetrieveAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    queryset = User.objects.all()

    # def get(self, request, pk, **args):
    #     user = User.objects.get(id=pk)
    #
    #     serializer = UserSerializer(user, many=False)
    #
    #     return Response(serializer.data, status.HTTP_200_OK)
    #
    # def put(self, request, **args):
    #     user = request.user
    #
    #     serializer = UserSerializer(instance=user, data=request.data, many=False)
    #
    #     if serializer.is_valid():
    #         serializer.save(email=user.email)
    #
    #         return Response({'message': 'user updated.', 'data': serializer.data}, status.HTTP_200_OK)
    #     else:
    #         return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)


class UserProfile(generics.RetrieveAPIView, generics.UpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsOwner]
    queryset = User.objects.all()

    def get_object(self):
        queryset = self.queryset
        obj = get_object_or_404(queryset, id=self.request.user.id)
        self.check_object_permissions(self.request, obj)
        return obj


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
            