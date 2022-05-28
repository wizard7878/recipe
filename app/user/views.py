from rest_framework import generics , permissions, authentication
from user.serializers import UserSerializer, AuthTokenSerializer
# Create your views here.


class CreateUserView(generics.CreateAPIView):
    serializer_class = UserSerializer


class ManageUserView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = (permissions.IsAuthenticated, )

    def get_object(self):
        return self.request.user