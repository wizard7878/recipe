from django.urls import path
from .views import CreateTokenView
from user import views
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
app_name = 'user'

urlpatterns = [
    path('create/', views.CreateUserView.as_view(), name='create'),
    # path('token/', views.CreateTokenView.as_view(), name='token'),
    path('token/', TokenObtainPairView.as_view(), name='token'),
    path('me/', views.ManageUserView.as_view(), name='me')
]