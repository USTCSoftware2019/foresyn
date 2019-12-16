from django.urls import path

from . import views

app_name = 'data_wrapper'
urlpatterns = [
    path('add_models/', views.AddDataModelToCobra.as_view(), name='add_models'),
    path('add_reactions/', views.AddDataReactionToCobra.as_view(), name='add_reactions'),
    # path('add_metabolites/', views.AddDataMetaboliteToCobra.as_view(), name='add_metabolites'),
]
