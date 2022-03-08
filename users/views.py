from urllib import response

from django.shortcuts import redirect
from .models import User
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializations import UserSerializer
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
    
