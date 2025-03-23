from django.urls import path
from .import views

urlpatterns = [
    path('register/',views.UserRegistrationView.as_view(),name='register'),
    path('profile/',views.UpdateProfileView.as_view(),name='profile'),
    path('login/',views.UserLoginView.as_view(),name='login'),
    # path('logout/',views.CustomLogoutView.as_view(http_method_names = ['post', 'get']),name='logout'),
    path('logout/',views.CustomLogoutView.as_view(),name='logout'),
]