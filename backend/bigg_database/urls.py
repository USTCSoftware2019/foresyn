from django.urls import path

from . import views

app_name = 'bigg_database'
urlpatterns = [
    path('search/reaction', views.ReactionSearchView.as_view(),
         name='search_reaction'),
    path('search/metabolite', views.MetaboliteSearchView.as_view(),
         name='search_metabolite'),
    path('search/model', views.ModelSearchView.as_view(),
         name='search_model'),
    path('search/gene', views.GeneSearchView.as_view(),
         name='search_gene'),
    path('model/<int:pk>', views.ModelDetailView.as_view(),
         name='model_detail'),
    path('reaction/<int:pk>', views.ReactionDetailView.as_view(),
         name='reaction_detail'),
    path('metabolite/<int:pk>', views.MetaboliteDetailView.as_view(),
         name='metabolite_detail'),
]
