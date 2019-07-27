from django.urls import path

from . import views

app_name = 'bigg_database'
urlpatterns = [
    path('search', views.SearchView.as_view(),
         name='search'),
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
    path('model/<int:pk>/metabolites', views.MetabolitesInModel.as_view(),
         name='metabolites_in_model'),
    path('model/<int:pk>/reactions', views.ReactionsInModel.as_view(),
         name='reactions_in_model'),
    path('reaction/<int:pk>/metabolites', views.MetabolitesInReaction.as_view(),
         name='metabolites_in_reaction'),
    path('reaction/<int:pk>/genes', views.GenesInReaction.as_view(),
         name='genes_in_reaction'),
    path('gene/<int:pk>/models', views.GeneFromModels.as_view(),
         name='gene_from_models'),
    path('metabolite/<int:pk>/models', views.MetaboliteFromModels.as_view(),
         name='metabolite_from_models'),
    path('reaction/<int:pk>/models', views.ReactionFromModels.as_view(),
         name='reaction_from_models'),
    path('gene/<int:pk>/reactions', views.GeneFromReactions.as_view(),
         name='gene_from_reactions'),
    path('metabolite/<int:pk>/reactions', views.MetaboliteFromReactions.as_view(),
         name='metabolite_from_reactions'),
]
