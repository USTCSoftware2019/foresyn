from django.urls import path

from . import views

app_name = 'cobra'
urlpatterns = [
    path('models/', views.ModelsView.as_view(), name='models'),
]
