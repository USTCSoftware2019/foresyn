from django.urls import path

from . import views

app_name = 'share'
urlpatterns = [
    path('create', views.CreateShareLinkView.as_view(), name='create_share'),
    path('model', views.ModelShareView.as_view(), name='shared_cobra_model'),
    path('reaction', views.ReactionShareView.as_view(), name='shared_cobra_reaction'),
    path('metabolite', views.MetaboliteShareView.as_view(), name='shared_cobra_metabolite'),
]
