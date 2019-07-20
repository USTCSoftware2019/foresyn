from django.urls import path

from . import views

app_name = 'cobra'
urlpatterns = [
    path('models/', views.CobraModelApi.as_view(), name='models'),
    path('reactions/', views.CobraReactionApi.as_view(), name='reactions'),
    path('metabolites/', views.CobraMetaboliteApi.as_view(), name='metabolites'),
    path('del_model/', views.delete_model, name='del_model'),
    path('del_metabolite', views.delete_metabolite, name='del_metabolite'),
    path('del_reaction', views.delete_reaction, name='del_reaction'),
    
]
