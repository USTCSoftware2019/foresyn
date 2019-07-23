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
    path('gene/<int:pk>', views.GeneDetailView.as_view(),
         name='gene_detail'),
    path('model/<int:pk>/genes', views.GenesInModel.as_view(),
         name='genes_in_model'),
    path('model/<int:pk>/metabolites', views.MetaboliteInModel.as_view(),
         name='metabolites_in_model'),
    path('model/<int:pk>/reactions', views.ReactionsInModel.as_view(),
         name='reactions_in'),
    path('reaction/<int:pk>/metabolites', views.MetaboliteInReaction.as_view(),
         name='metabolites_in_reaction'),
    path('reaction/<int:pk>/genes', views.GenesInReaction.as_view(),
         name='genes_in_reaction')
]
