from urllib import response

from django.shortcuts import redirect
from .models import User
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import UserSerializer, PasswordSerializer
from rest_framework import status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.reverse import reverse

@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def api_root(request, format=None):
    return Response({
        'users' : reverse('user-detail', request=request, format=format),
        'question' : reverse('question-detail', request=request, format=format)
    })

class UserListView(APIView):
    permission_classes =[permissions.IsAuthenticatedOrReadOnly]
    
    def get(self, request):
        user = User.objects.all()
        context = {'request': request}
        
        serializer = UserSerializer(user, many=True, context=context)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    
        
class SignupUserView(APIView):
    permission_classes = [permissions.AllowAny]
    def post(self, request, *args, **kwargs):
        
        user = User.objects.create_user(
            email=request.data['email'], password=request.data['password']
        )
        
        return Response({'message':'user created successfully!'}, status.HTTP_201_CREATED)
    

class UserDetail(APIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
    def get(self, request, pk, **args):
        user = User.objects.get(id=pk)
        
        serializer = UserSerializer(user, many=False, context={'request':request})
        
        return Response(serializer.data, status.HTTP_200_OK)
        
    def put(self, request, **args):
        user = request.user
        
        serializer = UserSerializer(instance=user, data=request.data, many=False, context={'request':request})
        
        if serializer.is_valid():
            serializer.save(email=user.email)
            
            return Response({'message':'user updated.', 'data':serializer.data}, status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)

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
            return Response({'message':'password changed.', 'data':[]}, status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)
            