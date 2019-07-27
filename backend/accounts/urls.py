from django.urls import path

from . import views

app_name = 'accounts'
urlpatterns = [
    path('signup/', views.UserSignUp.as_view(), name='signup'),
]
