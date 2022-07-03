from rest_framework import permissions, generics


from .serializers import UserSerializer
from .permissions import IsOwner
from .models import User


# class RegisterView(generics.CreateAPIView):
#
#     permission_classes = [permissions.AllowAny]
#     serializer_class = RegisterSerializer


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
