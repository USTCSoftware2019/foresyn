from django.urls import path

from . import views

app_name = 'cobra'
urlpatterns = [
    path('models/', views.CobraModelApi.as_view(), name='models'),
    path('reactions/', views.CobraReactionApi.as_view(), name='reactions'),
    path('metabolites/', views.CobraMetaboliteApi.as_view(), name='metabolites'),
    path('models/<int:model_id>/<str:method>/', views.CobraComputeApi.as_view(), name='compute')
]
