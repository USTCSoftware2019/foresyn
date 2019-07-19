from django.urls import path

from . import views

app_name = 'cobra'
urlpatterns = [
    path('models/', views.ModelView.as_view(), name='models'),
    path('reactions/', views.ReactionView.as_view(), name='reactions'),
    path('metabolites/', views.MetaboliteView.as_view(), name='metabolites'),
]
